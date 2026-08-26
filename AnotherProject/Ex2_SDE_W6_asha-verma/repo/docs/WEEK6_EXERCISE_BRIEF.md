# Week 6 Capstone Exercise — ProjectFlow Project Management System

## Scenario
Your delivery team has been asked to replace spreadsheet-based project tracking with a small Project Management microservice. Build the project, membership and task-management capabilities from the provided specification.

## Deliverables
- domain/entity analysis
- project/member/task API
- MySQL schema + exactly 10 rows per table
- business rules and task state machine
- RBAC using the exercise identity dependency
- project summary endpoint
- tests for happy/error paths
- migration, Docker, CI, README, STATUS, DECISIONS and Git tag `week-06`

## Required endpoints
See `specs/design_spec.md` for the complete contract.

## Required command
```bash
pytest tests/test_projects.py tests/test_tasks.py -q
```

## Submission convention
Use `SDE_W6_<firstname>-<lastname>.zip` if your facilitator requires learner-specific naming.
