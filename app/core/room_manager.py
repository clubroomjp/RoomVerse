from typing import Dict, List, Optional
import html
from app.core.config import config
import time
import asyncio
import httpx
from app.core.llm import llm_client

class RoomManager:
    def __init__(self):
        # Visitor ID -> { name, callback_url, last_seen }
        self.active_visitors: Dict[str, dict] = {}
        # List of { timestamp, sender_id, sender_name, message }
        self.chat_history: List[dict] = []
        self._max_capacity = config.room.max_visitors
        
        # New Feature: Room Status & Locking
        self.is_open = True
        self.processing_lock = asyncio.Lock()
        
        # Track outgoing agents: target_url -> task
        self.active_agents: Dict[str, asyncio.Task] = {}

    def can_accept_visitor(self, visitor_id: str) -> bool:
        if not self.is_open:
            return False
        
        # If already registered, allow
        if visitor_id in self.active_visitors:
            return True
            
        # Cleanup old visitors (e.g. inactive for 10 mins)
        self._cleanup_inactive()
        
        return len(self.active_visitors) < self._max_capacity

    def register_visitor(self, visitor_id: str, name: str, callback_url: str = None):
        """Registers a visitor and updates their heartbeat/info."""
        self.active_visitors[visitor_id] = {
            "name": self.sanitize(name),
            "callback_url": callback_url,
            "last_seen": time.time()
        }

    def remove_visitor(self, visitor_id: str):
        """Explicitly removes a visitor."""
        if visitor_id in self.active_visitors:
            del self.active_visitors[visitor_id]

    def sanitize(self, text: str) -> str:
        """
        Sanitizes input text to prevent XSS/injection.
        Escapes HTML characters.
        """
        if not text:
            return ""
        return html.escape(str(text))

    def add_message(self, sender_id: str, sender_name: str, content: str, is_human: bool = False):
        safe_content = self.sanitize(content)
        self.chat_history.append({
            "id": str(time.time()), # Simple ID
            "timestamp": time.time(),
            "sender_id": sender_id,
            "sender_name": self.sanitize(sender_name),
            "content": safe_content,
            "is_human": is_human
        })
        # Keep history manageable
        if len(self.chat_history) > 100:
            self.chat_history.pop(0)

    def _cleanup_inactive(self):
        """Removes visitors who haven't been seen in the last 10 minutes."""
        now = time.time()
        expired = [vid for vid, data in self.active_visitors.items() if now - data["last_seen"] > 600]
        for vid in expired:
            del self.active_visitors[vid]

    def get_active_visitor_count(self) -> int:
        self._cleanup_inactive()
        return len(self.active_visitors)

    def get_online_visitors(self) -> List[dict]:
        self._cleanup_inactive()
        return list(self.active_visitors.values())

    def get_recent_context_text(self, limit=5, window_seconds=300) -> str:
        """
        Retrieves recent chat history as a formatted text block for LLM context.
        Filters by time window (e.g. last 5 mins) to keep it relevant.
        """
        now = time.time()
        recent_msgs = [
            m for m in self.chat_history 
            if now - m["timestamp"] < window_seconds
        ]
        # Take the last N messages
        recent_msgs = recent_msgs[-limit:]
        
        if not recent_msgs:
            return ""
            
        context_str = "Recent Room Conversation:\n"
        for m in recent_msgs:
            context_str += f"- {m['sender_name']}: {m['content']}\n"
            
        return context_str

    async def start_agent_visit(self, target_url: str):
        """Starts a background task to visit another room."""
        if target_url in self.active_agents:
            return # Already visiting
            
        task = asyncio.create_task(self._agent_loop(target_url))
        self.active_agents[target_url] = task
        # Remove when done
        task.add_done_callback(lambda t: self.active_agents.pop(target_url, None))
        
    async def _agent_loop(self, target_url: str):
        try:
            my_id = config.instance_id
            my_name = config.character.name
            
            self.add_message("SYSTEM", "System", f"🚀 Agent departing for: {target_url}")

            async with httpx.AsyncClient() as client:
                # 1. Knock (Visit)
                payload = {
                    "visitor_id": my_id,
                    "visitor_name": my_name,
                    "message": "Hello! I am an AI visiting from another room.",
                    "callback_url": "" # Not used yet
                }
                
                try:
                    resp = await client.post(f"{target_url.rstrip('/')}/visit", json=payload, timeout=10.0)
                    resp.raise_for_status()
                    data = resp.json()
                    
                    # Session ID from their room
                    their_session_id = data.get("session_id")
                    their_reply = data.get("response", "")
                    their_host_name = data.get("host_name", "Host")
                    
                    # Log Their Reply (Monitor)
                    self.add_message("REMOTE", f"{their_host_name} (Remote)", f"「{their_reply}」")

                except Exception as e:
                    self.add_message("SYSTEM", "System", f"❌ Failed to connect: {e}")
                    return

                # Conversation Loop
                max_turns = config.agent.max_turns
                self.add_message("SYSTEM", "System", f"Starting conversation (Max turns: {max_turns})")

                for i in range(max_turns):
                    await asyncio.sleep(2) # Natural pause
                    
                    # 2. My Turn (Generate Response)
                    # We reuse log_visit logic conceptually or just generate
                    my_reply = llm_client.generate_response(
                        visitor_name=their_host_name,
                        message=their_reply,
                        context=[], 
                        relationship_context=f"You are visiting {target_url}. Be polite and curious."
                    )
                    
                    # Log My Reply (Monitor)
                    self.add_message("AGENT", f"{my_name} (Agent)", f"「{my_reply}」")
                    
                    # Stop Check
                    if "bye" in my_reply.lower() or "goodbye" in my_reply.lower():
                         self.add_message("SYSTEM", "System", "👋 Agent finished conversation.")
                         break

                    # 3. Send to Them
                    chat_payload = {
                        "visitor_id": my_id,
                        "session_id": their_session_id,
                        "message": my_reply
                    }
                    
                    try:
                        c_resp = await client.post(f"{target_url.rstrip('/')}/chat", json=chat_payload, timeout=30.0)
                        c_resp.raise_for_status()
                        c_data = c_resp.json()
                        
                        their_reply = c_data.get("response", "")
                        self.add_message("REMOTE", f"{their_host_name} (Remote)", f"「{their_reply}」")
                        
                        if "bye" in their_reply.lower():
                            self.add_message("SYSTEM", "System", "👋 Host ended conversation.")
                            break
                            
                    except Exception as e:
                        self.add_message("SYSTEM", "System", f"⚠️ Connection lost: {e}")
                        break
        
        except Exception as e:
             self.add_message("SYSTEM", "System", f"❌ System Error during visit: {e}")

# Global instance
room_manager = RoomManager()
