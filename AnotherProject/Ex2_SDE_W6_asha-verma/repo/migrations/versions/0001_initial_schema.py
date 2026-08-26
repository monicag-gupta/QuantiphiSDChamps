"""Initial ProjectFlow schema.

Revision ID: 0001
Revises: None
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("name", sa.String(120), nullable=False),
        sa.Column("email", sa.String(180), nullable=False, unique=True), sa.Column("job_title", sa.String(120)),
        sa.Column("active", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))
    op.create_table("projects",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text()), sa.Column("manager_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False), sa.Column("start_date", sa.Date(), nullable=False), sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))
    op.create_table("project_members",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False), sa.Column("role", sa.String(20), nullable=False),
        sa.Column("joined_at", sa.DateTime(), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("project_id", "user_id", name="uq_project_member"))
    op.create_table("milestones",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(120), nullable=False), sa.Column("due_date", sa.Date(), nullable=False), sa.Column("status", sa.String(20), nullable=False))
    op.create_table("tasks",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("milestone_id", sa.String(36), sa.ForeignKey("milestones.id", ondelete="SET NULL")), sa.Column("title", sa.String(180), nullable=False),
        sa.Column("description", sa.Text()), sa.Column("assignee_id", sa.String(36), sa.ForeignKey("users.id")), sa.Column("status", sa.String(20), nullable=False),
        sa.Column("priority", sa.String(20), nullable=False), sa.Column("due_date", sa.Date()), sa.Column("estimate_hours", sa.Float()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))
    op.create_table("comments",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("task_id", sa.String(36), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False), sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))
    op.create_table("time_entries",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("task_id", sa.String(36), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False), sa.Column("hours", sa.Float(), nullable=False),
        sa.Column("work_date", sa.Date(), nullable=False), sa.Column("note", sa.String(255)))
    op.create_table("risks",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(180), nullable=False), sa.Column("probability", sa.Integer(), nullable=False), sa.Column("impact", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False), sa.Column("owner_id", sa.String(36), sa.ForeignKey("users.id")))
    op.create_table("activity_logs",
        sa.Column("id", sa.String(36), primary_key=True), sa.Column("project_id", sa.String(36), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False), sa.Column("action", sa.String(80), nullable=False),
        sa.Column("entity_type", sa.String(40), nullable=False), sa.Column("entity_id", sa.String(36), nullable=False), sa.Column("details", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False))


def downgrade():
    for table in ["activity_logs", "risks", "time_entries", "comments", "tasks", "milestones", "project_members", "projects", "users"]:
        op.drop_table(table)
