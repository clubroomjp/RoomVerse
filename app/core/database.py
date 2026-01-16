from typing import Optional, List
from sqlmodel import Field, Session, SQLModel, create_engine, select
import datetime

# --- Models ---

class VisitLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    visitor_id: str = Field(index=True)
    visitor_name: str
    callback_url: Optional[str] = None

class Relationship(SQLModel, table=True):
    visitor_id: str = Field(primary_key=True)
    visitor_name: str
    affinity: int = Field(default=0)
    first_met: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    last_met: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    memory_summary: Optional[str] = Field(default=None) # Summary of past interactions

class ConversationLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    session_id: str = Field(index=True) # UUID for the chat session
    visitor_id: str = Field(index=True)
    sender: str # "visitor" or "host"
    message: str
    model: Optional[str] = None

class LoreEntry(SQLModel, table=True):
    keyword: str = Field(primary_key=True)
    keyword_en: Optional[str] = None # Auto-translated keyword
    content: str
    
    # V2 Enhancements
    book: str = Field(default="Default", index=True)
    secondary_keys: Optional[str] = None # Comma-separated alias
    constant: bool = Field(default=False) # Always active
    enabled: bool = Field(default=True)
    content_en: Optional[str] = None # Auto-translated description
    source: str = Field(default="host") # "host" or "visitor"
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class CharacterCard(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None # Description
    personality: Optional[str] = None # Personality
    scenario: Optional[str] = None # Scenario
    first_mes: Optional[str] = None # First Message
    mes_example: Optional[str] = None # Message Examples
    creator_notes: Optional[str] = None
    system_prompt: Optional[str] = None # Card specific system prompt
    tags: Optional[str] = None # JSON list or comma separated
    creator: Optional[str] = None
    character_version: Optional[str] = None
    image_path: Optional[str] = None # Path to avatar image (filename in static/cards/)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

# --- Database Connection ---

sqlite_file_name = "logs.sqlite"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- Helpers ---

def log_visit(session: Session, visitor_id: str, visitor_name: str, callback_url: str | None, message: str = None, sender: str = None, model: str = None, session_id: str = None):
    # Log the visit (Only if it's a new visit or heartbeat? Actually we call this for every message usually?)
    # If it's just a message log, maybe we shouldn't spam VisitLog?
    # But current usage implies we might want to update "last_seen" every time.
    
    # Update Relationship
    relation = session.get(Relationship, visitor_id)
    if not relation:
        relation = Relationship(visitor_id=visitor_id, visitor_name=visitor_name)
        session.add(relation)
    else:
        relation.last_met = datetime.datetime.utcnow()
        relation.affinity += 1 # Increment affinity on visit/interaction
        if relation.visitor_name != visitor_name:
            relation.visitor_name = visitor_name # Update name if changed
        session.add(relation)
            
    # Save Message to ConversationLog if provided
    if message and sender:
        # Use provided session_id or default to visitor_id (legacy behavior)
        # If session_id is provided (like "HOST_SESSION"), usage is clear.
        log_session_id = session_id if session_id else visitor_id
        
        log = ConversationLog(
            session_id=log_session_id,
            visitor_id=visitor_id,
            sender=sender,
            message=message,
            timestamp=datetime.datetime.utcnow(),
            model=model
        )
        session.add(log)
        
    session.commit()
    session.refresh(relation)
    return relation

def get_relationship(session: Session, visitor_id: str) -> Optional[Relationship]:
    return session.get(Relationship, visitor_id)
