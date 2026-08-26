# ProjectFlow — Week 6 Project Management Capstone

A complete teaching repository for a Project Management System built with FastAPI, Pydantic v2, SQLAlchemy 2.x and MySQL.

## What Week 6 adds
Compared with a simple CRUD service, this capstone includes nested project/task resources, project membership, role-based authorization, task state transitions, audit logging, relational reporting, project health summaries, database migrations, tests, Docker and CI.

## Explore in this order
1. `specs/design_spec.md` — domain model, API, RBAC, state machine, decisions.
2. `src/domain/entities.py` — framework-independent project/task/risk rules.
3. `src/models/orm.py` — SQLAlchemy database mappings.
4. `src/service/project_service.py` and `task_service.py` — business logic.
5. `src/api/routes/` — thin FastAPI routes.
6. `db/schema.sql`, `db/seed.sql`, `db/query.sql` — MySQL creation, 10-row sample data, useful reporting SQL.
7. `tests/` — executable contract and business-rule tests.

## Requirements
- Python 3.11+
- MySQL 8.x for the target database
- Docker / Docker Compose optional

## Setup
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Default environment:
```env
DATABASE_URL=mysql+pymysql://projectflow:projectflow@localhost:3306/projectflow
```

## Start MySQL
```bash
docker compose up -d db
```
The MySQL container runs `db/schema.sql` and `db/seed.sql` on first initialization.

## Create tables using SQLAlchemy
```bash
python scripts/create_all.py
```

## Run Alembic
```bash
alembic upgrade head
```

## Start API
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```
Open `http://localhost:8000/docs`.

## Authentication model for the exercise
Write endpoints expect an `X-User-Id` header. Use one of the seeded users, for example:

```text
11111111-1111-1111-1111-111111111111
```

This is a teaching mechanism for dependency injection and RBAC, not production authentication.

## Example calls
```bash
curl 'http://localhost:8000/v1/projects?page=1&page_size=5'

curl -X POST 'http://localhost:8000/v1/projects' \
  -H 'Content-Type: application/json' \
  -H 'X-User-Id: 11111111-1111-1111-1111-111111111111' \
  -d '{"name":"ERP Modernisation","description":"Replace legacy ERP integrations","start_date":"2026-09-01","end_date":"2026-12-15"}'
```

## Test commands
```bash
pytest tests/test_projects.py tests/test_tasks.py -q
pytest -q
```

## Git/SDD evidence
The specification is committed before the skeleton. The completed submission is tagged `week-06`.

## Production evolution
Replace header-based identity with OAuth2/OIDC/JWT, add tenant isolation, optimistic locking, richer audit/event delivery, background notifications, search, observability, and load/security testing before using this architecture as a real SaaS platform.
