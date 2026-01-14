from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Annotated
from app.core.llm import llm_client
from app.core.config import config


from contextlib import asynccontextmanager
from app.core.tunnel import start_tunnel

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Hardcoded port for MVP, ideally should match the server port
    public_url = start_tunnel(8001)
    if public_url:
        print(f"!!! RoomVerse Node is LIVE at: {public_url} !!!")
    yield
    # Shutdown logic if needed

app = FastAPI(title="RoomVerse Node", version="0.1.0", lifespan=lifespan)

async def verify_api_key(x_roomverse_key: Annotated[str | None, Header()] = None):
    if not config.security or not config.security.api_key:
        return # Open if no key configured
    
    if x_roomverse_key != config.security.api_key:
        print(f"Unauthorized access attempt. Key provided: {x_roomverse_key}")
        raise HTTPException(status_code=403, detail="Invalid API Key")

class VisitRequest(BaseModel):
    visitor_name: str
    message: str
    context: list[dict] = []

class VisitResponse(BaseModel):
    host_name: str
    response: str

@app.get("/")
async def root():
    return {"status": "online", "character": config.character.name}

@app.post("/visit", response_model=VisitResponse, dependencies=[Depends(verify_api_key)])
async def visit(request: VisitRequest):
    """
    Endpoint for incoming visitors.
    """
    print(f"Visitor: {request.visitor_name} says: {request.message}")
    
    response_text = llm_client.generate_response(
        visitor_name=request.visitor_name,
        message=request.message,
        context=request.context
    )
    
    return VisitResponse(
        host_name=config.character.name,
        response=response_text
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
