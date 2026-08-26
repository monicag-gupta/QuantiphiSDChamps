from datetime import date

import pytest

from src.domain.entities import Project, Risk, Task, TaskStatus


def test_project_rejects_invalid_dates():
    with pytest.raises(ValueError):
        Project("p1", "Bad", date(2026, 10, 1), date(2026, 9, 1))


def test_task_transition_state_machine():
    task = Task("t1", "Build", TaskStatus.TODO)
    task.transition_to(TaskStatus.IN_PROGRESS)
    task.transition_to(TaskStatus.DONE)
    assert task.status == TaskStatus.DONE


def test_illegal_domain_transition():
    task = Task("t1", "Build", TaskStatus.TODO)
    with pytest.raises(ValueError):
        task.transition_to(TaskStatus.DONE)


def test_project_completion_percentage():
    project = Project("p1", "Demo", date(2026, 1, 1), date(2026, 12, 31))
    project.tasks = [Task("1", "A", TaskStatus.DONE), Task("2", "B", TaskStatus.TODO)]
    assert project.completion_percentage == 50.0


def test_risk_score():
    assert Risk("r1", "Vendor", 4, 5).score == 20
