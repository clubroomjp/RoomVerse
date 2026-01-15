from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Annotated
from sqlmodel import Session
from app.core.llm import llm_client
from app.core.config import config, Config, save_config
from app.core.translator import translator
from app.core.database import create_db_and_tables, get_session, log_visit, get_relationship, ConversationLog

from contextlib import asynccontextmanager
from app.core.tunnel import start_tunnel
from app.core.room_manager import room_manager
from app.core.discovery import get_discovery_client
import uuid

# Global state
GLOBAL_PUBLIC_URL = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global GLOBAL_PUBLIC_URL
    # Startup
    create_db_and_tables()
    GLOBAL_PUBLIC_URL = start_tunnel(PORT)
    if GLOBAL_PUBLIC_URL:
        print(f"!!! RoomVerse Node is LIVE at: {GLOBAL_PUBLIC_URL} !!!")
    yield
    # Shutdown logic if needed

app = FastAPI(title="RoomVerse Node", version="0.1.0", lifespan=lifespan)

# Mount static files for Dashboard
app.mount("/dashboard", StaticFiles(directory="app/static", html=True), name="static")

async def verify_api_key(x_roomverse_key: Annotated[str | None, Header()] = None):
    if not config.security or not config.security.api_key:
        return # Open if no key configured
    
    if x_roomverse_key != config.security.api_key:
        print(f"Unauthorized access attempt. Key provided: {x_roomverse_key}")
        raise HTTPException(status_code=403, detail="Invalid API Key")

# --- Models ---

class VisitRequest(BaseModel):
    visitor_id: str
    visitor_name: str
    message: str
    callback_url: str | None = None
    context: list[dict] = []

class VisitResponse(BaseModel):
    host_name: str
    response: str

class ChatRequest(BaseModel):
    visitor_id: str
    session_id: str | None = None
    message: str

class ChatResponse(BaseModel):
    session_id: str
    response: str

class HostChatRequest(BaseModel):
    message: str

class CharacterCard(BaseModel):
    name: str
    description: str
    instance_id: str
    # Add other fields as needed (e.g. topics, gender, etc.)

@app.get("/")
async def root():
    return {"status": "online", "character": config.character.name}



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
            "character": config.character.name,
            "max_visitors": config.room.max_visitors
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

# --- Public Endpoints ---

@app.get("/card", response_model=CharacterCard)
async def get_card():
    """
    Return the character card/profile.
    """
    return CharacterCard(
        name=config.character.name,
        description=config.character.persona, # Simple mapping for now
        instance_id=config.instance_id
    )

@app.post("/visit", response_model=VisitResponse, dependencies=[Depends(verify_api_key)])
async def visit(request: VisitRequest, session: Session = Depends(get_session)):
    """
    Endpoint for incoming visitors. Records the visit and starts a conversation.
    """
    visitor_msg = request.message
    
    # 1. Capacity Check & Security
    if not room_manager.can_accept_visitor(request.visitor_id):
        raise HTTPException(status_code=503, detail="Room is full")
        
    # Register & Sanitize
    room_manager.register_visitor(request.visitor_id, request.visitor_name, request.callback_url)
    
    # 2. Log Visit & Update Relationship
    relation = log_visit(session, request.visitor_id, room_manager.sanitize(request.visitor_name), request.callback_url)
    
    print(f"--- Incoming Visit ---")
    print(f"ID: {request.visitor_id}")
    print(f"Name: {request.visitor_name} (Affinity: {relation.affinity})")
    
    # 3. Translate if needed
    if config.translation.enabled:
        visitor_msg = translator.translate(visitor_msg, target_lang=config.translation.target_lang)
    
    # Sanitize message before processing
    visitor_msg = room_manager.sanitize(visitor_msg)
    room_manager.add_message(request.visitor_id, request.visitor_name, visitor_msg)

    print(f"Message: {visitor_msg}")

    # 3. Generate Response with Relationship Context
    rel_context = f"Affinity Score: {relation.affinity}\n"
    if relation.memory_summary:
        rel_context += f"Memory of past interactions: {relation.memory_summary}\n"
    
    response_text = llm_client.generate_response(
        visitor_name=request.visitor_name,
        message=visitor_msg, 
        context=request.context,
        relationship_context=rel_context
    )
    
    return VisitResponse(
        host_name=config.character.name,
        response=response_text
    )

@app.post("/chat", response_model=ChatResponse, dependencies=[Depends(verify_api_key)])
async def chat(request: ChatRequest, session: Session = Depends(get_session)):
    """
    Endpoint for continuing a conversation.
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    # Log incoming message (Sanitized via RoomManager)
    safe_message = room_manager.sanitize(request.message)
    room_manager.add_message(request.visitor_id, "visitor", safe_message)

    log_in = ConversationLog(
        session_id=session_id, visitor_id=request.visitor_id, 
        sender="visitor", message=safe_message
    )
    session.add(log_in)
    
    # Get relationship for context
    relation = get_relationship(session, request.visitor_id)
    visitor_name = relation.visitor_name if relation else "Unknown"
    
    rel_context = ""
    if relation:
         rel_context = f"Affinity Score: {relation.affinity}\n"
         if relation.memory_summary:
            rel_context += f"Memory of past interactions: {relation.memory_summary}\n"

    # Generate Response
    response_text = llm_client.generate_response(
        visitor_name=visitor_name,
        message=safe_message,
        context=[], # TODO: Fetch recent history from DB for this session_id?
        relationship_context=rel_context
    )
    
    # Sanitize response just in case
    response_text = room_manager.sanitize(response_text)
    room_manager.add_message(config.instance_id, config.character.name, response_text)
    
    # Log response
    log_out = ConversationLog(
        session_id=session_id, visitor_id=request.visitor_id,
        sender="host", message=response_text
    )
    session.add(log_out)
    session.commit()
    
    return ChatResponse(session_id=session_id, response=response_text)

@app.post("/api/host/chat")
async def host_chat(request: HostChatRequest, session: Session = Depends(get_session)):
    """
    Endpoint for the Host User to send a message to the room.
    """
    # Sanitize and add to room manager
    safe_msg = room_manager.sanitize(request.message)
    room_manager.add_message("HOST", config.character.name, safe_msg, is_human=True)
    
    # Log to DB (Special visitor_id for host?)
    # For now, we might just log it as a system event or associated with a 'HOST' session
    # Simpler: just acknowledge. The visitors will need to poll or receive this.
    # Current architecture is request-response, so visitors won't "receive" this 
    # unless they are polling or we verify the stream/websocket later.
    # For now, this just adds to the room log/context.
    
    print(f"[HOST]: {safe_msg}")
    return {"status": "sent", "message": safe_msg}


PORT = 22022

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
