"""
GreenPulse AI Copilot - Session Memory
Maintains multi-turn conversational context with sliding window pruning.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any


class SessionMemoryManager:
    """Stores in-memory conversation turns per session ID."""

    def __init__(self, max_turns: int = 8):
        self.max_turns = max_turns
        self._sessions: Dict[str, List[Dict[str, Any]]] = {}

    def add_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        sources: Optional[List[Dict[str, Any]]] = None
    ):
        """Appends a user-assistant turn to the session history."""
        if session_id not in self._sessions:
            self._sessions[session_id] = []

        now = datetime.now().isoformat()
        self._sessions[session_id].append({
            "role": "user",
            "content": user_message,
            "timestamp": now,
        })
        self._sessions[session_id].append({
            "role": "assistant",
            "content": assistant_response,
            "timestamp": now,
            "sources": sources or [],
        })

        # Sliding window pruning
        if len(self._sessions[session_id]) > self.max_turns * 2:
            self._sessions[session_id] = self._sessions[session_id][-self.max_turns * 2:]

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Returns the conversation history for the session."""
        return self._sessions.get(session_id, [])

    def format_history_for_prompt(self, session_id: str, max_messages: int = 6) -> str:
        """Formats the last N messages into a clean prompt string."""
        history = self.get_history(session_id)
        if not history:
            return ""

        recent = history[-max_messages:]
        lines = []
        for msg in recent:
            prefix = "User" if msg["role"] == "user" else "Copilot"
            lines.append(f"{prefix}: {msg['content']}")

        return "\n".join(lines)

    def clear_session(self, session_id: str):
        """Clears memory for a specific session."""
        if session_id in self._sessions:
            del self._sessions[session_id]


session_memory = SessionMemoryManager()
