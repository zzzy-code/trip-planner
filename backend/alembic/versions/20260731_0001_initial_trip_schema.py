"""initial trip schema

Revision ID: 20260731_0001
Revises:
Create Date: 2026-07-31
"""

from alembic import op
import sqlalchemy as sa

revision = "20260731_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "trip_plans",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("city", sa.String(length=80), nullable=False),
        sa.Column("start_date", sa.String(length=20), nullable=False),
        sa.Column("end_date", sa.String(length=20), nullable=False),
        sa.Column("travel_days", sa.Integer(), nullable=False),
        sa.Column("transportation", sa.String(length=80), nullable=False),
        sa.Column("accommodation", sa.String(length=80), nullable=False),
        sa.Column("preferences", sa.JSON(), nullable=False),
        sa.Column("free_text_input", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("overall_suggestions", sa.Text(), nullable=False),
        sa.Column("budget_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_trip_plans_city", "trip_plans", ["city"])
    op.create_index("ix_trip_plans_status", "trip_plans", ["status"])

    op.create_table(
        "day_plans",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("trip_plan_id", sa.String(length=36), sa.ForeignKey("trip_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.String(length=20), nullable=False),
        sa.Column("day_index", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("transportation", sa.String(length=80), nullable=False),
        sa.Column("accommodation", sa.String(length=80), nullable=False),
        sa.Column("hotel_json", sa.JSON(), nullable=True),
    )
    op.create_index("ix_day_plans_trip_plan_id", "day_plans", ["trip_plan_id"])

    op.create_table(
        "attractions",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("day_plan_id", sa.String(length=36), sa.ForeignKey("day_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("visit_duration", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=True),
        sa.Column("rating", sa.Float(), nullable=True),
        sa.Column("ticket_price", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
    )
    op.create_index("ix_attractions_day_plan_id", "attractions", ["day_plan_id"])

    op.create_table(
        "meals",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("day_plan_id", sa.String(length=36), sa.ForeignKey("day_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("estimated_cost", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
    )
    op.create_index("ix_meals_day_plan_id", "meals", ["day_plan_id"])

    op.create_table(
        "weather_info",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("trip_plan_id", sa.String(length=36), sa.ForeignKey("trip_plans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("date", sa.String(length=20), nullable=False),
        sa.Column("day_weather", sa.String(length=80), nullable=False),
        sa.Column("night_weather", sa.String(length=80), nullable=False),
        sa.Column("day_temp", sa.Integer(), nullable=False),
        sa.Column("night_temp", sa.Integer(), nullable=False),
        sa.Column("wind_direction", sa.String(length=80), nullable=False),
        sa.Column("wind_power", sa.String(length=80), nullable=False),
    )
    op.create_index("ix_weather_info_trip_plan_id", "weather_info", ["trip_plan_id"])


def downgrade() -> None:
    op.drop_table("weather_info")
    op.drop_table("meals")
    op.drop_table("attractions")
    op.drop_table("day_plans")
    op.drop_table("trip_plans")
