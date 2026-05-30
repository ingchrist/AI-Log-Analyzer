import json
from pathlib import Path
from datetime import datetime

class IncidentStore:
    def __init__(self, storage_dir: str):
        self.path = Path(storage_dir) / "incidents.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._incidents = self._load()

    def _load(self):
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text())

    def add(self, **kwargs):
        incident = {"timestamp": datetime.now().isoformat(), **kwargs}
        self._incidents.append(incident)
        self.path.write_text(json.dumps(self._incidents, indent=2))

    def get_recent(self, n=5):
        return self._incidents[-n:]

    def format_for_prompt(self, incidents):
        if not incidents:
            return ""
        lines = ["PAST INCIDENTS (from memory):\n"]
        for inc in incidents:
            lines.append(f"- [{inc['severity']}] {inc['summary']} ({inc['timestamp'][:10]})")
            if inc.get('resolution'):
                lines.append(f"  Resolution: {inc['resolution']}")
        return "\n".join(lines)
