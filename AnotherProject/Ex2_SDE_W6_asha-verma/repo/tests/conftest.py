from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.base import Base
from src.db.session import get_db
from src.main import app
from src.models.orm import Project, ProjectMember, Risk, Task, TimeEntry, User

USER1 = "11111111-1111-1111-1111-111111111111"
USER2 = "22222222-2222-2222-2222-222222222222"
USER3 = "33333333-3333-3333-3333-333333333333"
USER4 = "44444444-4444-4444-4444-444444444444"
PROJECT1 = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1"
TASK1 = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1"

engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False, class_=Session)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestingSessionLocal() as db:
        db.add_all([
            User(id=USER1, name="Asha Verma", email="asha@example.com", job_title="Project Manager", active=True),
            User(id=USER2, name="Rahul Mehta", email="rahul@example.com", job_title="Developer", active=True),
            User(id=USER3, name="Inactive User", email="inactive@example.com", job_title="QA", active=False),
            User(id=USER4, name="Outside User", email="outside@example.com", job_title="Consultant", active=True),
        ])
        db.add(Project(
            id=PROJECT1, name="Retail Platform Upgrade", description="Core commerce upgrade",
            manager_id=USER1, status="active", start_date=date(2026, 8, 1), end_date=date(2026, 12, 31)
        ))
        db.flush()
        db.add_all([
            ProjectMember(id="cccccccc-cccc-cccc-cccc-ccccccccccc1", project_id=PROJECT1, user_id=USER1, role="manager"),
            ProjectMember(id="cccccccc-cccc-cccc-cccc-ccccccccccc2", project_id=PROJECT1, user_id=USER2, role="contributor"),
        ])
        db.add(Task(
            id=TASK1, project_id=PROJECT1, title="Design API", assignee_id=USER2,
            status="todo", priority="high", due_date=date(2026, 9, 15), estimate_hours=12.0
        ))
        db.add(Risk(
            id="dddddddd-dddd-dddd-dddd-ddddddddddd1", project_id=PROJECT1,
            title="Vendor dependency", probability=3, impact=4, status="open", owner_id=USER1
        ))
        db.add(TimeEntry(
            id="eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee1", task_id=TASK1, user_id=USER2,
            hours=2.5, work_date=date(2026, 8, 20), note="API discovery"
        ))
        db.commit()
    yield


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)
