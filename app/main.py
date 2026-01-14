from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Annotated
from app.core.llm import llm_client
from app.core.config import config, Config, save_config
from app.core.translator import translator

from contextlib import asynccontextmanager
from app.core.tunnel import start_tunnel

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    public_url = start_tunnel(8001)
    if public_url:
        print(f"!!! RoomVerse Node is LIVE at: {public_url} !!!")
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

class VisitRequest(BaseModel):
    visitor_id: str
    visitor_name: str
    message: str
    callback_url: str | None = None
    context: list[dict] = []

class VisitResponse(BaseModel):
    host_name: str
    response: str

@app.get("/")
async def root():
    return {"status": "online", "character": config.character.name}

# --- Config API ---
@app.get("/api/config")
async def get_config():
    return config

@app.post("/api/config")
async def update_config(new_config: Config):
    # Update global config object
    global config
    # We update fields manually or re-assign. Re-assigning works for pydantic models locally
    config.character = new_config.character
    config.llm = new_config.llm
    config.translation = new_config.translation
    # Note: Security and Ngrok settings updates might require restart to take full effect
    
    # Save to disk
    save_config(config)
    
    # Update LLM client as well
    llm_client.character = config.character
    llm_client.model = config.llm.model
    # Note: Client connection details (base_url, api_key) might require re-init
    
    return {"status": "updated"}
# ------------------

@app.post("/visit", response_model=VisitResponse, dependencies=[Depends(verify_api_key)])
async def visit(request: VisitRequest):
    """
    Endpoint for incoming visitors.
    """
    visitor_msg = request.message
    
    print(f"--- Incoming Visit ---")
    print(f"ID: {request.visitor_id}")
    print(f"Name: {request.visitor_name}")
    if request.callback_url:
        print(f"Callback: {request.callback_url}")
    
    # Auto-Translation Logic
    if config.translation.enabled:
        print(f"Translating incoming message from {request.visitor_name}...")
        visitor_msg = translator.translate(visitor_msg, target_lang=config.translation.target_lang)
        print(f"Translated: {visitor_msg}")

    print(f"Message: {visitor_msg}")
    print(f"----------------------")
    
    response_text = llm_client.generate_response(
        visitor_name=request.visitor_name,
        message=visitor_msg, # Send translated or original message
        context=request.context
    )
    
    return VisitResponse(
        host_name=config.character.name,
        response=response_text
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
