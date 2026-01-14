import json
import os
from pydantic import BaseModel

class CharacterConfig(BaseModel):
    name: str
    persona: str
    system_prompt: str

class LLMConfig(BaseModel):
    base_url: str
    api_key: str
    model: str

class Config(BaseModel):
    character: CharacterConfig
    llm: LLMConfig

def load_config(path: str = "app/config.json") -> Config:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found at {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return Config(**data)

# Global config instance
try:
    config = load_config()
except FileNotFoundError:
    config = None
