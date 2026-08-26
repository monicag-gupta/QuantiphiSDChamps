# STATUS.md — Week 6 Submission

| Field | Value |
|---|---|
| Project | ProjectFlow Project Management System |
| Week | 06 |
| Capstone scope | Projects, membership/RBAC, tasks, task workflow, audit, health summary |
| Python | 3.11+ |
| API | FastAPI |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.x |
| Target DB | MySQL 8 |
| Test DB | SQLite in-memory |
| Required tests | Passing in packaged repository |
| Database seed | Exactly 10 rows in each of 9 persisted tables |
| Migration | Alembic initial migration included |
| Docker | Dockerfile + docker-compose included |
| CI | GitHub Actions workflow included |
| SDD evidence | Design specification committed before implementation |
| Git tag | week-06 |
| Known limitation | Live MySQL integration is configured but not executed in the build container; tests validate application behavior with SQLite compatibility DB. Header identity is intentionally a teaching substitute for production OAuth/JWT. |
| Submission state | Complete |
