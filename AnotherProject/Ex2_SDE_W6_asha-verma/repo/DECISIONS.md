# DECISIONS.md — Week 6 Design Choices and AI Use

## D1 — Project is the primary aggregate
The project provides the transaction/context boundary for membership, milestones, tasks, risks and summaries. This makes authorization and date validation easier to reason about.

## D2 — Membership is an entity, not a bare link table
`ProjectMember` contains a role and join timestamp. That allows RBAC rules to live on explicit business data.

## D3 — Thin routes
Routes parse HTTP input, inject dependencies, call services and return responses. Business rules stay in services/domain objects and database queries stay in repositories.

## D4 — Header-based identity is intentionally non-production
`X-User-Id` is used only to teach dependency injection and authorization without adding an external identity provider to the exercise. Production should use OAuth2/OIDC/JWT and tenant-aware authorization.

## D5 — Explicit task state transitions
Task status is not free-form. A transition table makes invalid workflow changes observable and testable.

## D6 — Audit writes share the business transaction
Activity logs are inserted in the same SQLAlchemy session/transaction as the change. This avoids a successful business write with a missing audit row in the teaching implementation.

## D7 — SQLAlchemy 2.x style
Mappings use `Mapped`/`mapped_column()` and queries use `select()`. This avoids the legacy query style and matches modern SQLAlchemy 2.x documentation.

## D8 — SQLite for automated tests, MySQL for target deployment
The API/service/repository stack is tested without an external service dependency. MySQL-specific DDL, seed scripts, Alembic configuration and Docker setup are included for the real lab database.

## D9 — 10 seed records per persisted table
The project includes 9 tables and exactly 10 seed rows in each so students can explore joins and reports immediately.

## AI use disclosure
AI assistance was used to draft the teaching skeleton, test cases, documentation structure and sample data. All generated code was executed in the build environment, tests were run, seed row counts were checked programmatically, and the documentation was rendered for visual QA. Students should be able to explain every submitted design choice and line they keep.
