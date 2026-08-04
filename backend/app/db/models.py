"""SQLAlchemy ORM models for persisted trip plans."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def uuid_str() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class TripPlanModel(Base):
    __tablename__ = "trip_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    city: Mapped[str] = mapped_column(String(80), index=True)
    start_date: Mapped[str] = mapped_column(String(20))
    end_date: Mapped[str] = mapped_column(String(20))
    travel_days: Mapped[int] = mapped_column(Integer)
    transportation: Mapped[str] = mapped_column(String(80))
    accommodation: Mapped[str] = mapped_column(String(80))
    preferences: Mapped[list[str]] = mapped_column(JSON, default=list)
    free_text_input: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(20), default="generating", index=True)
    overall_suggestions: Mapped[str] = mapped_column(Text, default="")
    budget_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    days: Mapped[list["DayPlanModel"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan", order_by="DayPlanModel.day_index"
    )
    weather: Mapped[list["WeatherInfoModel"]] = relationship(
        back_populates="trip", cascade="all, delete-orphan", order_by="WeatherInfoModel.date"
    )


class DayPlanModel(Base):
    __tablename__ = "day_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    trip_plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("trip_plans.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[str] = mapped_column(String(20))
    day_index: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text, default="")
    transportation: Mapped[str] = mapped_column(String(80), default="")
    accommodation: Mapped[str] = mapped_column(String(80), default="")
    hotel_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    trip: Mapped[TripPlanModel] = relationship(back_populates="days")
    attractions: Mapped[list["AttractionModel"]] = relationship(
        back_populates="day", cascade="all, delete-orphan", order_by="AttractionModel.sort_order"
    )
    meals: Mapped[list["MealModel"]] = relationship(
        back_populates="day", cascade="all, delete-orphan", order_by="MealModel.sort_order"
    )


class AttractionModel(Base):
    __tablename__ = "attractions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    day_plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("day_plans.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(160))
    address: Mapped[str] = mapped_column(String(255), default="")
    longitude: Mapped[float] = mapped_column(Float, default=0.0)
    latitude: Mapped[float] = mapped_column(Float, default=0.0)
    visit_duration: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str | None] = mapped_column(String(80), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    ticket_price: Mapped[int] = mapped_column(Integer, default=0)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    day: Mapped[DayPlanModel] = relationship(back_populates="attractions")


class MealModel(Base):
    __tablename__ = "meals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    day_plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("day_plans.id", ondelete="CASCADE"), index=True
    )
    type: Mapped[str] = mapped_column(String(30))
    name: Mapped[str] = mapped_column(String(160))
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_cost: Mapped[int] = mapped_column(Integer, default=0)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    day: Mapped[DayPlanModel] = relationship(back_populates="meals")


class WeatherInfoModel(Base):
    __tablename__ = "weather_info"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_str)
    trip_plan_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("trip_plans.id", ondelete="CASCADE"), index=True
    )
    date: Mapped[str] = mapped_column(String(20))
    day_weather: Mapped[str] = mapped_column(String(80), default="")
    night_weather: Mapped[str] = mapped_column(String(80), default="")
    day_temp: Mapped[int] = mapped_column(Integer, default=0)
    night_temp: Mapped[int] = mapped_column(Integer, default=0)
    wind_direction: Mapped[str] = mapped_column(String(80), default="")
    wind_power: Mapped[str] = mapped_column(String(80), default="")

    trip: Mapped[TripPlanModel] = relationship(back_populates="weather")

