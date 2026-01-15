import json
import os
import uuid
from pydantic import BaseModel

class CharacterConfig(BaseModel):
    name: str
    persona: str
    system_prompt: str

class LLMConfig(BaseModel):
    base_url: str
    api_key: str
    model: str

class NgrokConfig(BaseModel):
    authtoken: str = None

class CloudflareConfig(BaseModel):
    enabled: bool = True
    binary_path: str = None
    
class RoomConfig(BaseModel):
    name: str = "My Room"
    max_visitors: int = 5
    discovery_api_url: str = None

class SecurityConfig(BaseModel):
    ngrok_basic_auth: str = None
    api_key: str = None

class TranslationConfig(BaseModel):
    enabled: bool = False
    target_lang: str = "ja"

class DashboardConfig(BaseModel):
    language: str = "en"

class Config(BaseModel):
    instance_id: str
    character: CharacterConfig
    llm: LLMConfig
    ngrok: NgrokConfig = None
    security: SecurityConfig = None
    translation: TranslationConfig = TranslationConfig()
    dashboard: DashboardConfig = DashboardConfig()
    cloudflare: CloudflareConfig = CloudflareConfig()
    room: RoomConfig = RoomConfig()

def load_config(path: str = "app/config.json") -> Config:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found at {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Auto-generate instance_id if missing
    if "instance_id" not in data:
        data["instance_id"] = str(uuid.uuid4())
        # Save immediately so the ID persists
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save auto-generated instance_id: {e}")

    return Config(**data)

def save_config(config_obj: Config, path: str = "app/config.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config_obj.model_dump(), f, indent=2, ensure_ascii=False)


# Global config instance
try:
    config = load_config()
except FileNotFoundError:
    config = None
