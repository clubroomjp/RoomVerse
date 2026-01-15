from typing import Dict, List, Optional
import html
from app.core.config import config
import time

class RoomManager:
    def __init__(self):
        self.visitors: Dict[str, dict] = {} # visitor_id -> {info}
        self.chat_history: List[dict] = []
        self._max_capacity = config.room.max_visitors
        
    def can_accept_visitor(self, visitor_id: str) -> bool:
        if visitor_id in self.visitors:
            return True
        return len(self.visitors) < self._max_capacity

    def register_visitor(self, visitor_id: str, name: str, callback_url: str = None):
        """Registers a visitor and updates their heartbeat/info."""
        self.visitors[visitor_id] = {
            "name": self.sanitize(name),
            "callback_url": callback_url,
            "last_seen": time.time()
        }

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
            "timestamp": time.time(),
            "sender_id": sender_id,
            "sender_name": self.sanitize(sender_name),
            "content": safe_content,
            "is_human": is_human
        })
        # Keep history manageable
        if len(self.chat_history) > 100:
            self.chat_history.pop(0)

    def get_online_visitors(self) -> List[dict]:
        # Simple timeout logic could be added here (e.g. remove if unseen for 5 mins)
        return list(self.visitors.values())

# Global instance
room_manager = RoomManager()
