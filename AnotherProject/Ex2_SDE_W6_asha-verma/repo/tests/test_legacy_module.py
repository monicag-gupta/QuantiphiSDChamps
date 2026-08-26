from datetime import date, timedelta

from refactor.legacy_module.task_metrics import task_health_label


def test_task_health_labels():
    today = date(2026, 8, 26)
    assert task_health_label("done", today - timedelta(days=2), today) == "closed"
    assert task_health_label("blocked", today + timedelta(days=2), today) == "blocked"
    assert task_health_label("todo", today - timedelta(days=1), today) == "overdue"
    assert task_health_label("todo", today + timedelta(days=1), today) == "on_track"
