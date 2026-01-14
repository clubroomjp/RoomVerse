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

def log_visit(session: Session, visitor_id: str, visitor_name: str, callback_url: str | None):
    # Log the visit
    visit = VisitLog(visitor_id=visitor_id, visitor_name=visitor_name, callback_url=callback_url)
    session.add(visit)
    
    # Update Relationship
    relation = session.get(Relationship, visitor_id)
    if not relation:
        relation = Relationship(visitor_id=visitor_id, visitor_name=visitor_name)
        session.add(relation)
    else:
        relation.last_met = datetime.datetime.utcnow()
        if relation.visitor_name != visitor_name:
            relation.visitor_name = visitor_name # Update name if changed
        session.add(relation)
            
    session.commit()
    session.refresh(relation)
    return relation

def get_relationship(session: Session, visitor_id: str) -> Optional[Relationship]:
    return session.get(Relationship, visitor_id)
