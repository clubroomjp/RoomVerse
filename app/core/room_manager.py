from typing import Dict, List, Optional
import html
from app.core.config import config
import time

import asyncio

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

# Global instance
room_manager = RoomManager()
