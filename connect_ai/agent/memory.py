from datetime import datetime

from flask_login import current_user


def _is_authenticated_user():
    try:
        return bool(current_user.is_authenticated)
    except Exception:
        return False


class Memory:
    """In-memory conversation and tool log store."""

    def __init__(self, max_items=300):
        self.logs = []
        self.max_items = max_items

    def add(self, role, content, meta=None):
        meta = dict(meta or {})
        if _is_authenticated_user():
            meta.setdefault("user_id", current_user.id)

        entry = {
            "role": role,
            "content": content,
            "meta": meta,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.logs.append(entry)
        if len(self.logs) > self.max_items:
            self.logs = self.logs[-self.max_items:]

    def get(self):
        return self._visible_logs()

    def get_recent(self, limit=10):
        return self._visible_logs()[-limit:]

    def clear(self):
        if _is_authenticated_user():
            self.logs = [
                item for item in self.logs if item.get("meta", {}).get("user_id") != current_user.id
            ]
        else:
            self.logs = []

    def search(self, keyword: str, limit=10):
        keyword = (keyword or "").lower().strip()
        if not keyword:
            return []

        results = []
        for item in reversed(self._visible_logs()):
            content = str(item.get("content", "")).lower()
            if keyword in content:
                results.append(item)
            if len(results) >= limit:
                break
        return list(reversed(results))

    def _visible_logs(self):
        if not _is_authenticated_user():
            return list(self.logs)
        return [item for item in self.logs if item.get("meta", {}).get("user_id") == current_user.id]
