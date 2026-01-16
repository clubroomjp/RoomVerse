from fastapi import FastAPI, HTTPException, Header, Depends, Query, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Annotated
import shutil
import os
from sqlmodel import Session
from app.core.llm import llm_client
from app.core.config import config, Config, save_config
from app.core.translator import translator
from app.core.database import create_db_and_tables, get_session, log_visit, get_relationship, ConversationLog, LoreEntry, CharacterCard

from contextlib import asynccontextmanager
from app.core.tunnel import start_tunnel
from app.core.room_manager import room_manager
from app.core.discovery import get_discovery_client
import uuid

import asyncio

# Global state
GLOBAL_PUBLIC_URL = None

async def announce_presence_task():
    """Background task to periodically announce presence to Discovery Service."""
    while True:
        try:
            if config.room.auto_announce and GLOBAL_PUBLIC_URL:
                from app.core.discovery import get_discovery_client
                client = get_discovery_client(config)
                metadata = {
                    "name": config.room.name,
                    "description": config.room.description,
                    "max_visitors": config.room.max_visitors,
                    "character": config.character.name,
                    "model": config.llm.model,
                    "locked": bool(config.security.api_key)
                }
                client.announce(config.instance_id, GLOBAL_PUBLIC_URL, metadata)
                # print(f"[Heartbeat] Announced presence.") # Optional: noisy log
        except Exception as e:
            print(f"[Heartbeat] Error: {e}")
        
        await asyncio.sleep(60) # Announce every minute

@asynccontextmanager
async def lifespan(app: FastAPI):
    global GLOBAL_PUBLIC_URL
    # Startup
    # Ensure static cards dir exists
    os.makedirs("app/static/cards", exist_ok=True)
    
    create_db_and_tables()
    GLOBAL_PUBLIC_URL = start_tunnel(PORT)
    if GLOBAL_PUBLIC_URL:
        print(f"!!! RoomVerse Node is LIVE at: {GLOBAL_PUBLIC_URL} !!!")
    
    # Start Heartbeat
    asyncio.create_task(announce_presence_task())
    
    yield
    # Shutdown logic if needed

app = FastAPI(title="RoomVerse Node", version="0.1.0", lifespan=lifespan)

# Mount static files for Dashboard
app.mount("/dashboard", StaticFiles(directory="app/static", html=True), name="static")

async def verify_api_key(
    x_roomverse_key: Annotated[str | None, Header()] = None,
    key: Annotated[str | None, Query()] = None
):
    if not config.security or not config.security.api_key:
        return # Open if no key configured
    
    # Check Header OR Query Param
    provided_key = x_roomverse_key or key
    
    if provided_key != config.security.api_key:
        print(f"Unauthorized access attempt. Key provided: {provided_key}")
        raise HTTPException(status_code=403, detail="Invalid API Key")

# --- Models ---

class VisitRequest(BaseModel):
    visitor_id: str
    visitor_name: str
    message: str
    callback_url: str | None = None
    context: list[dict] = []
    model: str | None = None

class VisitResponse(BaseModel):
    host_name: str
    response: str

class ChatRequest(BaseModel):
    visitor_id: str
    session_id: str | None = None
    message: str
    model: str | None = None

class ChatResponse(BaseModel):
    session_id: str
    response: str

class HostChatRequest(BaseModel):
    message: str



@app.get("/")
async def root():
    return FileResponse('app/static/visitor.html')



# --- Discovery API Proxy ---
@app.get("/api/discovery/rooms")
async def list_rooms():
    """
    Fetches the list of active rooms from the configured Discovery Service.
    """
    client = get_discovery_client(config)
    rooms = client.list_rooms()
    return rooms

# --- Config API ---
@app.get("/api/llm/detect")
async def detect_llms():
    """
    Scans local ports for running LLM services (Ollama, LM Studio, etc).
    """
    from app.core.scanner import scanner
    results = await scanner.scan_all()
    return results

@app.get("/api/config")
async def get_config():
    return config

@app.post("/api/config")
async def update_config(new_config: Config):
    # Update global config object
    global config
    config.character = new_config.character
    config.llm = new_config.llm
    config.translation = new_config.translation
    config.room = new_config.room
    config.dashboard = new_config.dashboard
    config.security = new_config.security
    config.agent = new_config.agent
    save_config(config)
    
    llm_client.character = config.character
    llm_client.character = config.character
    llm_client.model = config.llm.model
    
    # Trigger Announcement if enabled and URL exists
    if config.room.auto_announce and GLOBAL_PUBLIC_URL:
        from app.core.discovery import get_discovery_client
        client = get_discovery_client(config)
        metadata = {
            "name": config.room.name,
            "description": config.room.description,
            "max_visitors": config.room.max_visitors,
            "character": config.character.name,
            "model": config.llm.model
        }
        success = client.announce(config.instance_id, GLOBAL_PUBLIC_URL, metadata)
        print(f"[ConfigUpdate] Announced presence: {success}")

    return {"status": "updated"}

@app.get("/api/room/messages")
async def get_room_messages(since: float = 0):
    """
    Returns chat messages since the given timestamp.
    """
    messages = [m for m in room_manager.chat_history if m["timestamp"] > since]
    return messages

# ------------------

# ------------------
# --- Log API ---
@app.get("/api/logs/sessions")
async def get_log_sessions():
    """
    Returns a list of 'Virtual Sessions' grouped by time gaps (> 15 min).
    """
    from app.core import database
    from sqlmodel import select, desc
    
    GAP_THRESHOLD = 900  # 15 minutes
    
    with database.Session(database.engine) as session:
        # Fetch ALL logs ordered by time (Newest first)
        statement = (
            select(database.ConversationLog)
            .order_by(desc(database.ConversationLog.timestamp))
        )
        logs = session.exec(statement).all()
        
        sessions_list = []
        if not logs:
            return []
            
        # Grouping Logic
        current_group = []
        
        for i, msg in enumerate(logs):
            current_group.append(msg)
            
            # Check if next message exists and if there is a gap
            is_last = (i == len(logs) - 1)
            gap_detected = False
            
            if not is_last:
                next_msg = logs[i+1]
                # Calculate diff (current is newer than next)
                diff = (msg.timestamp - next_msg.timestamp).total_seconds()
                if diff > GAP_THRESHOLD:
                    gap_detected = True
            
            if is_last or gap_detected:
                # Commit current group as a session
                # Group is ordered Newest -> Oldest
                # Sessiom Timestamp = Time of the NEWEST message (start of the session from user perspective)
                # OR Time of the OLDEST message?
                # Usually list shows "When it happened". Let's use the Start Time (Oldest in group) or End Time?
                # Let's use the Start of the conversation (Oldest message in group).
                
                group_start_msg = current_group[-1] # Oldest
                group_end_msg = current_group[0]    # Newest
                
                # Get unique names
                visitors = set()
                # We need to resolve names.
                # Optimization: creating a map of visitor_id -> name?
                # For now, just simplistic lookup or using what's in logs if we had it.
                # ConversationLog doesn't have names. We must look up.
                # Efficient lookup:
                processed_ids = set()
                names_list = []
                
                for m in current_group:
                    if m.sender == "host":
                         if "Host" not in names_list: names_list.append("Host")
                    else:
                        if m.visitor_id not in processed_ids:
                            # Try simple lookup
                            # For speed, we might want to cache? 
                            # But N is small usually.
                            names_list.append(m.visitor_id[:8]) # Fallback
                            processed_ids.add(m.visitor_id)

                # Fetch real names for visitors (Optimized would be bulk fetch)
                # Let's just fix descriptions for now.
                
                # Create ID: start_ts _ end_ts
                sess_id = f"{group_start_msg.timestamp.timestamp()}_{group_end_msg.timestamp.timestamp()}"
                
                sessions_list.append({
                    "session_id": sess_id,
                    "timestamp": group_start_msg.timestamp, # Show when it STARTED
                    "visitor_name": f"Session ({len(current_group)} msgs)", # Placeholder, ideally "User A, User B"
                    "visitor_id": "group",
                    "preview": group_start_msg.message[:50] + "..." 
                })
                
                current_group = []

    # Post-process names (Slow but correct)
    with database.Session(database.engine) as session:
        for sess in sessions_list:
            # We want to show participants.
            # Ideally we stored this during the loop but we didn't want to query DB inside loop.
            # Actually we already queried ALL logs.
            pass 

    # Re-sort? They are already roughly sorted by Newest group first because we iterated Newest->Oldest.
    return sessions_list

@app.get("/api/logs/messages/{session_id}")
async def get_log_messages(session_id: str):
    from app.core import database
    from sqlmodel import select, col
    import datetime
    
    # Parse format: start_end
    try:
        start_ts_str, end_ts_str = session_id.split("_")
        start_ts = datetime.datetime.fromtimestamp(float(start_ts_str))
        end_ts = datetime.datetime.fromtimestamp(float(end_ts_str))
        
        # Add small buffer for float precision issues
        start_ts -= datetime.timedelta(seconds=0.1)
        end_ts += datetime.timedelta(seconds=0.1)
        
    except ValueError:
        return []

    with database.Session(database.engine) as session:
        statement = (
            select(database.ConversationLog)
            .where(database.ConversationLog.timestamp >= start_ts)
            .where(database.ConversationLog.timestamp <= end_ts)
            .order_by(database.ConversationLog.timestamp)
        )
        results = session.exec(statement).all()
        
        # We need names here too!
        # Enrich results with sender names
        enriched = []
        visitor_cache = {}
        
        for msg in results:
            sender_name = "Unknown"
            if msg.sender == "host":
                sender_name = config.character.name
            else:
                if msg.visitor_id in visitor_cache:
                    sender_name = visitor_cache[msg.visitor_id]
                else:
                    relation = session.get(database.Relationship, msg.visitor_id)
                    sender_name = relation.visitor_name if relation else msg.visitor_id[:8]
                    visitor_cache[msg.visitor_id] = sender_name
            
            # Return dict
            msg_dict = msg.model_dump()
            msg_dict["sender_name"] = sender_name
            enriched.append(msg_dict)
            
        return enriched

@app.delete("/api/logs/sessions/{session_id}")
async def delete_log_session(session_id: str):
    from app.core import database
    from sqlmodel import delete
    import datetime

    # Parse format: start_end
    try:
        start_ts_str, end_ts_str = session_id.split("_")
        start_ts = datetime.datetime.fromtimestamp(float(start_ts_str))
        end_ts = datetime.datetime.fromtimestamp(float(end_ts_str))
        
        # Add small buffer
        start_ts -= datetime.timedelta(seconds=0.1)
        end_ts += datetime.timedelta(seconds=0.1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid session ID format")

    with database.Session(database.engine) as session:
        statement = delete(database.ConversationLog).where(
            database.ConversationLog.timestamp >= start_ts,
            database.ConversationLog.timestamp <= end_ts
        )
        session.exec(statement)
        session.commit()
    
    return {"status": "deleted", "session_id": session_id}

@app.delete("/api/logs")
async def delete_all_logs():
    """Delete all logs but preserve relationships (affinity)."""
    from app.core import database
    from sqlmodel import delete
    
    with database.Session(database.engine) as session:
        session.exec(delete(database.ConversationLog))
        session.exec(delete(database.VisitLog))
        session.commit()
    return {"status": "deleted"}

@app.get("/api/lore")
async def list_lore_entries():
    """List all lorebook entries."""
    with get_session_wrapper() as session:
        from sqlmodel import select
        entries = session.exec(select(LoreEntry)).all()
        return entries

class LoreEntryRequest(BaseModel):
    keyword: str
    content: str
    source: str = "host"
    keyword_en: Annotated[str | None, "English Translation of Keyword"] = None
    content_en: Annotated[str | None, "English Translation of Description"] = None

@app.post("/api/lore")
async def save_lore_entry(entry: LoreEntryRequest):
    """Create or update a lore entry."""
    
    # Auto-translate if needed
    kw_en = entry.keyword_en
    cnt_en = entry.content_en
    
    if config.translation.enabled:
        if not kw_en and entry.keyword:
             try:
                 kw_en = translator.translate(entry.keyword, target_lang="en")
             except: pass
        if not cnt_en and entry.content:
             try:
                 cnt_en = translator.translate(entry.content, target_lang="en")
             except: pass

    with get_session_wrapper() as session:
        existing = session.get(LoreEntry, entry.keyword)
        if existing:
            existing.content = entry.content
            existing.source = entry.source
            if kw_en: existing.keyword_en = kw_en
            if cnt_en: existing.content_en = cnt_en
            session.add(existing)
        else:
            new_entry = LoreEntry(
                keyword=entry.keyword, 
                content=entry.content, 
                source=entry.source,
                keyword_en=kw_en,
                content_en=cnt_en
            )
            session.add(new_entry)
        session.commit()
    return {"status": "saved", "keyword": entry.keyword}

# --- Character Card API ---

class CardCreate(BaseModel):
    name: str
    description: str | None = None
    personality: str | None = None
    scenario: str | None = None
    first_mes: str | None = None
    mes_example: str | None = None
    creator_notes: str | None = None
    system_prompt: str | None = None
    tags: str | None = None
    creator: str | None = None
    character_version: str | None = None

@app.get("/api/cards")
async def get_cards():
    """List all character cards."""
    with get_session_wrapper() as session:
        from sqlmodel import select
        cards = session.exec(select(CharacterCard)).all()
        return cards

@app.post("/api/cards")
async def create_card(card: CardCreate):
    """Create a new character card."""
    with get_session_wrapper() as session:
        new_card = CharacterCard(**card.model_dump())
        session.add(new_card)
        session.commit()
        session.refresh(new_card)
        return new_card

@app.put("/api/cards/{card_id}")
async def update_card(card_id: int, card_data: CardCreate):
    """Update a character card."""
    with get_session_wrapper() as session:
        card = session.get(CharacterCard, card_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        card_dict = card_data.model_dump(exclude_unset=True)
        for key, value in card_dict.items():
            setattr(card, key, value)
            
        session.add(card)
        session.commit()
        session.refresh(card)
        return card

@app.delete("/api/cards/{card_id}")
async def delete_card(card_id: int):
    """Delete a character card."""
    with get_session_wrapper() as session:
        card = session.get(CharacterCard, card_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # If active, unset active
        if config.character.active_card_id == card_id:
            config.character.active_card_id = None
            save_config(config)
            
        session.delete(card)
        session.commit()
        return {"status": "deleted", "id": card_id}

@app.post("/api/cards/{card_id}/activate")
async def activate_card(card_id: int):
    """Set a card as active."""
    with get_session_wrapper() as session:
        card = session.get(CharacterCard, card_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # Update config
        config.character.active_card_id = card_id
        # Also auto-update character name? User might want to keep custom name.
        # Decision: Sync name to keep consistency, but maybe user wants override.
        # For now, just link ID. Logic will use Card Name if linked.
        config.character.name = card.name 
        save_config(config)
        return {"status": "activated", "card": card}

@app.post("/api/cards/deactivate")
async def deactivate_card():
    """Unset active card."""
    config.character.active_card_id = None
    save_config(config)
    return {"status": "deactivated"}

@app.post("/api/cards/{card_id}/image")
async def upload_card_image(card_id: int, file: UploadFile = File(...)):
    """Upload an avatar image for a card."""
    with get_session_wrapper() as session:
        card = session.get(CharacterCard, card_id)
        if not card:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # Validate PNG?
        if file.content_type != "image/png":
             raise HTTPException(status_code=400, detail="Only PNG images allowed")

        # Save file
        filename = f"card_{card_id}_{uuid.uuid4().hex[:8]}.png"
        path = f"app/static/cards/{filename}"
        
        # Remove old image if exists
        if card.image_path:
             old_path = f"app/static/cards/{card.image_path}"
             if os.path.exists(old_path):
                 os.remove(old_path)
                 
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        card.image_path = filename
        session.add(card)
        session.commit()
        session.refresh(card)
        return {"status": "uploaded", "image_path": filename}


@app.delete("/api/lore/{keyword}")
async def delete_lore_entry(keyword: str):
    """Delete a lore entry."""
    from sqlmodel import delete
    with get_session_wrapper() as session:
        session.exec(delete(LoreEntry).where(LoreEntry.keyword == keyword))
        session.commit()
    return {"status": "deleted", "keyword": keyword}

# Helper wrapper for session since dependency might not work in simple calls
def get_session_wrapper():
    from app.core.database import engine
    return Session(engine)

def get_lore_context(session: Session, message: str, depth: int = 2) -> str:
    """
    Recursively find lore entries matching keywords in the message.
    Supports bilingual search (keyword or keyword_en).
    """
    from sqlmodel import select
    
    found_entries = {} # keyword -> content_to_use
    search_text = message.lower()
    
    # Get all keywords first (Optimization: valid if DB is small. For large DB, use FTS or specific search)
    all_lore = session.exec(select(LoreEntry)).all()
    if not all_lore:
        return ""
        
    for _ in range(depth):
        new_found = False
        for entry in all_lore:
            # Check native keyword
            matched = False
            if entry.keyword.lower() in search_text:
                matched = True
            # Check English keyword if available
            elif entry.keyword_en and entry.keyword_en.lower() in search_text:
                matched = True
            
            if matched and entry.keyword not in found_entries:
                # Use English content if available, else native
                use_content = entry.content_en if entry.content_en else entry.content
                found_entries[entry.keyword] = (entry.keyword_en, use_content)
                
                search_text += f" {use_content}".lower() # Append content to search for nested keywords
                new_found = True
        
        if not new_found:
            break
            
    if not found_entries:
        return ""
        
    context_str = "[Lorebook Info]\n"
    for k, (k_en, v) in found_entries.items():
        label = f"{k} ({k_en})" if k_en else k
        context_str += f"- {label}: {v}\n"
    
    return context_str

# --- Public Endpoints ---

@app.get("/card", response_model=CharacterCard)
async def get_card():
    """
    Return the character card/profile.
    """
    # Try to get active card from DB
    if config.character.active_card_id:
        with get_session_wrapper() as session:
             from app.core.database import CharacterCard
             card = session.get(CharacterCard, config.character.active_card_id)
             if card:
                 # Ensure instance_id is included (it's not in DB model, but response needs it maybe? 
                 # Wait, response_model is CharacterCard (SQLModel). It doesn't have instance_id field.
                 # The previous code injected it but CharacterCard definition (Lines 38-52 in database.py) does NOT have instance_id.
                 # So the previous code was probably failing validation or Pydantic was ignoring extras?
                 # Actually, if I return a DB model, it validates against DB model.
                 return card
    
    # Fallback to config
    return CharacterCard(
        name=config.character.name,
        description=config.character.persona, # Fallback
        personality=config.character.system_prompt,
        # instance_id is not in CharacterCard model, so we can't return it here unless we change valid schema.
        # But for viewing, we just need name/desc/image.
    )

@app.post("/leave")
async def leave_room(request: dict):
    """
    Endpoint for visitor to explicitly leave the room.
    Expects {"visitor_id": "..."}
    """
    vid = request.get("visitor_id")
    if vid:
        room_manager.remove_visitor(vid)
        print(f"--- Visitor Left: {vid} ---")
    return {"status": "left"}

@app.post("/visit", response_model=VisitResponse, dependencies=[Depends(verify_api_key)])
@app.post("/visit", response_model=VisitResponse, dependencies=[Depends(verify_api_key)])
async def visit(request: VisitRequest, session: Session = Depends(get_session)):
    """
    Endpoint for incoming visitors. Records the visit and starts a conversation.
    """
    visitor_msg_original = request.message
    
    # 1. Capacity Check & Security
    if not room_manager.can_accept_visitor(request.visitor_id):
        raise HTTPException(status_code=503, detail="Room is full")
        
    # Register & Sanitize
    room_manager.register_visitor(request.visitor_id, request.visitor_name, request.callback_url, request.model)
    
    # 2. Log Visit & Update Relationship
    relation = log_visit(session, request.visitor_id, room_manager.sanitize(request.visitor_name), request.callback_url)
    
    print(f"--- Incoming Visit ---")
    print(f"ID: {request.visitor_id}")
    print(f"Name: {request.visitor_name} (Affinity: {relation.affinity})")
    
    # 3. Prepare Display Message (Translated)
    display_msg = visitor_msg_original
    if config.translation.enabled:
        # Translate for Dashboard View
        display_msg = translator.translate(visitor_msg_original, target_lang=config.translation.target_lang)
    
    # Add to Dashboard (Sanitized)
    room_manager.add_message(request.visitor_id, request.visitor_name, room_manager.sanitize(display_msg), model=request.model)

    print(f"Message (Original): {visitor_msg_original}")

    # 4. Generate Response with Relationship Context
    
    # Translate Input for LLM if enabled (Human -> English)
    llm_input_msg = visitor_msg_original
    if config.translation.enabled:
        llm_input_msg = translator.translate(visitor_msg_original, target_lang="en")

    # --- Lorebook Logic (Command & Context) ---
    lore_context = ""
    
    # 1. Command Check (!learn)
    if llm_input_msg.startswith("!learn "):
        # Format: !learn <keyword> <content>
        parts = llm_input_msg.split(" ", 2)
        if len(parts) == 3:
            kw = parts[1]
            cnt = parts[2]
            
            # Auto-translate
            kw_en = None
            cnt_en = None
            if config.translation.enabled:
                try: kw_en = translator.translate(kw, target_lang="en")
                except: pass
                try: cnt_en = translator.translate(cnt, target_lang="en")
                except: pass

            # Save to DB
            existing = session.get(LoreEntry, kw)
            if existing:
                 existing.content = cnt
                 existing.source = "visitor"
                 if kw_en: existing.keyword_en = kw_en
                 if cnt_en: existing.content_en = cnt_en
                 session.add(existing)
            else:
                 new_entry = LoreEntry(
                     keyword=kw, 
                     content=cnt, 
                     source="visitor",
                     keyword_en=kw_en,
                     content_en=cnt_en
                 )
                 session.add(new_entry)
            session.commit()
            
            # System Response
            room_manager.add_message(config.instance_id, "System", f"Learned: {kw}")
            return VisitResponse(host_name="System", response=f"Allowed access to Lorebook. Registered '{kw}'.")
    
    # 2. Context Lookup
    lore_context = get_lore_context(session, llm_input_msg)
    
    rel_context = f"Affinity Score: {relation.affinity}\n"
    if relation.memory_summary:
        rel_context += f"Memory of past interactions: {relation.memory_summary}\n"
    
    if lore_context:
        rel_context += f"\n{lore_context}\n"
    
    async with room_manager.processing_lock:
        visitor_count = room_manager.get_active_visitor_count()
        if visitor_count > 1:
            scene_context = room_manager.get_recent_context_text()
            rel_context += f"\n[Scene Context - The room is active with {visitor_count} visitors]\n{scene_context}\n"

        response_text = llm_client.generate_response(
            visitor_name=request.visitor_name,
            message=llm_input_msg, 
            context=request.context,
            relationship_context=rel_context
        )
    
        # 5. Handle Response Translation for Dashboard AND Client
        display_response = response_text
        if config.translation.enabled:
            display_response = translator.translate(response_text, target_lang=config.translation.target_lang)
        
        room_manager.add_message(config.instance_id, config.character.name, room_manager.sanitize(display_response))
        
        # --- Log to DB (Visitor & Host) ---
        # 1. Visitor Translated Message
        # We use a temp session ID or just timestamp-based grouping later
        temp_session_id = str(uuid.uuid4()) 
        
        log_in = database.ConversationLog(
            session_id=temp_session_id, 
            visitor_id=request.visitor_id, 
            sender="visitor", 
            message=room_manager.sanitize(display_msg) # Save TRANSLATED (or original if disabled)
        )
        session.add(log_in)

        # 2. Host Translated Response
        log_out = database.ConversationLog(
            session_id=temp_session_id, 
            visitor_id=request.visitor_id, 
            sender="host", 
            message=room_manager.sanitize(display_response) # Save TRANSLATED
        )
        session.add(log_out)
        session.commit()
    
    return VisitResponse(
        host_name=config.character.name,
        response=display_response # Return TRANSLATED response
    )

@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
async def chat(request: ChatRequest, session: Session = Depends(get_session)):
    """
    Endpoint for continuing a conversation.
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get relationship first to get the Name
    relation = get_relationship(session, request.visitor_id)
    visitor_name = relation.visitor_name if relation else "Unknown Visitor"

    # Prepare Display Message
    visitor_msg_original = request.message
    display_msg = visitor_msg_original
    
    if config.translation.enabled:
        display_msg = translator.translate(visitor_msg_original, target_lang=config.translation.target_lang)

    # Log incoming message to Room Manager (Sanitized)
    room_manager.add_message(request.visitor_id, visitor_name, room_manager.sanitize(display_msg), model=request.model)

    # Log to DB (Save Translated Content) 
    log_in = ConversationLog(
        session_id=session_id, visitor_id=request.visitor_id, 
        sender="visitor", message=room_manager.sanitize(display_msg)
    )
    session.add(log_in)
    
    rel_context = ""
    if relation:
         rel_context = f"Affinity Score: {relation.affinity}\n"
         if relation.memory_summary:
            rel_context += f"Memory of past interactions: {relation.memory_summary}\n"

    # Translate Input for LLM if enabled (Human -> English)
    llm_input_msg = visitor_msg_original
    if config.translation.enabled:
        llm_input_msg = translator.translate(visitor_msg_original, target_lang="en")

    # --- Lorebook Logic (Command & Context) ---
    lore_context = ""
    
    # 1. Command Check (!learn)
    if llm_input_msg.startswith("!learn "):
        parts = llm_input_msg.split(" ", 2)
        if len(parts) == 3:
            kw = parts[1]
            cnt = parts[2]
            
            # Auto-translate
            kw_en = None
            cnt_en = None
            if config.translation.enabled:
                try: kw_en = translator.translate(kw, target_lang="en")
                except: pass
                try: cnt_en = translator.translate(cnt, target_lang="en")
                except: pass
            
            existing = session.get(LoreEntry, kw)
            if existing:
                 existing.content = cnt
                 existing.source = "visitor"
                 if kw_en: existing.keyword_en = kw_en
                 if cnt_en: existing.content_en = cnt_en
                 session.add(existing)
            else:
                 new_entry = LoreEntry(
                     keyword=kw, 
                     content=cnt, 
                     source="visitor",
                     keyword_en=kw_en,
                     content_en=cnt_en
                 )
                 session.add(new_entry)
            session.commit()
            
            room_manager.add_message(config.instance_id, "System", f"Learned: {kw}")
            return ChatResponse(session_id=session_id, response=f"Learned: {kw}")

    # 2. Context Lookup
    lore_context = get_lore_context(session, llm_input_msg)

    async with room_manager.processing_lock:
        visitor_count = room_manager.get_active_visitor_count()
        scene_context = ""
        # If more than 1 visitor (or just to be safe, if > 0 and we want shared context), inject history
        if visitor_count > 1:
            scene_context = room_manager.get_recent_context_text()
            rel_context += f"\n[Scene Context - The room is active with {visitor_count} visitors]\n{scene_context}\n"
        
        if lore_context:
            rel_context += f"\n{lore_context}\n"

        # Generate Response (English Logic)
        response_text = llm_client.generate_response(
            visitor_name=visitor_name,
            message=llm_input_msg,
            context=[], 
            relationship_context=rel_context
        )
    
        # Handle Response Translation for Dashboard AND Client
        display_response = response_text
        if config.translation.enabled:
            display_response = translator.translate(response_text, target_lang=config.translation.target_lang)
            
        # Log Host Response to DB (Translated)
        log_out = ConversationLog(
            session_id=session_id, 
            visitor_id=request.visitor_id, 
            sender="host", 
            message=room_manager.sanitize(display_response)
        )
        session.add(log_out)
        session.commit()
        display_response = response_text
        if config.translation.enabled:
            display_response = translator.translate(response_text, target_lang=config.translation.target_lang)

        room_manager.add_message(config.instance_id, config.character.name, room_manager.sanitize(display_response))
        
        # Log response to DB
        log_out = ConversationLog(
            session_id=session_id, visitor_id=request.visitor_id,
            sender="host", message=room_manager.sanitize(response_text)
        )
        session.add(log_out)
        session.commit()
    
    return ChatResponse(session_id=session_id, response=display_response)

@app.post("/api/room/toggle")
async def toggle_room(data: dict = None):
    """
    Toggles the room open/closed status.
    """
    # Simple security check: enforce host-only rule if needed, but for now open to dashboard
    room_manager.is_open = not room_manager.is_open
    status = "open" if room_manager.is_open else "closed"
    return {
        "status": status, 
        "is_open": room_manager.is_open,
        "public_url": GLOBAL_PUBLIC_URL
    }

@app.post("/api/room/connect_agent")
async def connect_agent(data: dict):
    """
    Triggers the Host Agent to visit a target URL.
    Expects {"url": "..."}
    """
    target_url = data.get("url")
    if not target_url:
        raise HTTPException(status_code=400, detail="Missing URL")
    
    await room_manager.start_agent_visit(target_url)
    return {"status": "Agent dispatched", "target": target_url}

@app.get("/api/room/status")
async def get_room_status():
    return {
        "is_open": room_manager.is_open, 
        "active_visitors": room_manager.get_active_visitor_count(),
        "public_url": GLOBAL_PUBLIC_URL
    }

@app.post("/api/host/chat")
async def host_chat(request: HostChatRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    """
    Endpoint for the Host User to send a message to the room.
    """
    # Sanitize and add to room manager
    safe_msg = room_manager.sanitize(request.message)
    # Use "Host" as name for human user, not character name
    room_manager.add_message("HOST", "Host", safe_msg, is_human=True)
    
    # Log to DB (Special visitor_id for host?)
    # For now, we might just log it as a system event or associated with a 'HOST' session
    # Simpler: just acknowledge. The visitors will need to poll or receive this.
    # Current architecture is request-response, so visitors won't "receive" this 
    # unless they are polling or we verify the stream/websocket later.
    # For now, this just adds to the room log/context.
    
    print(f"[HOST]: {safe_msg}")
    
    # Trigger AI Reply
    background_tasks.add_task(process_host_reply, safe_msg)
    
    return {"status": "sent", "message": safe_msg}

def process_host_reply(message: str):
    """
    Background task to generate AI response for Host.
    """
    try:
        # Import dependencies here if needed or ensure global
        from app.core.translator import translator
        from app.core.database import log_visit
        
        # 1. Build Context from Room History (Last 10 messages)
        recent_history = room_manager.chat_history[-10:] 
        llm_context = []
        for msg in recent_history:
            role = "user" if msg["is_human"] or msg["sender_id"] != config.instance_id else "assistant"
            # Skip duplications
            if msg["content"] == message and msg["sender_name"] == "Host":
                continue 
            llm_context.append({"role": role, "content": msg["content"]})

        # 2. Generate Response
        reply = llm_client.generate_response(
            visitor_name="Host",
            message=message,
            context=llm_context, 
            relationship_context="You are speaking with the Host (Owner) of this room."
        )
        
        # 3. Translate if enabled
        final_reply = reply
        if config.translation and config.translation.enabled:
             # Just translate the output for now as per user request (Auto-translation ON -> Japanese)
             target = config.translation.target_lang or "ja"
             final_reply = translator.translate(reply, target)
        
        # 4. Post to Room (Ephemerally)
        room_manager.add_message(config.instance_id, config.character.name, final_reply, model=config.llm.model)
        
        # 5. Log to DB (Persist)
        # We need to log both the Host's trigger message and the AI's reply
        # Using a special session ID "HOST_SESSION"
        with get_session_wrapper() as session:
             # Log Host Message
             log_visit(session, "HOST_SESSION", "Host", "HOST_URL", message, "host")
             # Log AI Reply
             log_visit(session, "HOST_SESSION", "Host", "HOST_URL", final_reply, "ai", model=config.llm.model)
             
    except Exception as e:
        print(f"Error in process_host_reply: {e}")


PORT = 22022

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
