import json
from pathlib import Path
from datetime import datetime

class ChatStore:
    def __init__(self, storage_dir: str, session_id: str = "default"):
        self.path = Path(storage_dir) / f"session_{session_id}.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id

    def load(self) -> list:
        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text())["messages"]
        except (OSError, IOError, json.JSONDecodeError, KeyError):
            return []

    def save(self, messages: list):
        data = {"session_id": self.session_id, "messages": messages}
        self.path.write_text(json.dumps(data, indent=2, default=str))

    def clear(self):
        if self.path.exists():
            self.path.unlink()
