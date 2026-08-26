from __future__ import annotations

from datetime import date


def task_health_label(status: str, due_date: date | None, today: date | None = None) -> str:
    """Behaviour-preserved refactor of a legacy nested-conditional helper."""
    today = today or date.today()
    if status in {"done", "cancelled"}:
        return "closed"
    if status == "blocked":
        return "blocked"
    if due_date and due_date < today:
        return "overdue"
    return "on_track"
