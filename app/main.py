from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.core.llm import llm_client
from app.core.config import config

app = FastAPI(title="RoomVerse Node", version="0.1.0")

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

@app.post("/visit", response_model=VisitResponse)
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
