"""CRUD helpers for trip plans."""

from __future__ import annotations

from math import ceil
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..db.models import AttractionModel, DayPlanModel, MealModel, TripPlanModel, WeatherInfoModel
from ..models.schemas import Attraction, Budget, DayPlan, Hotel, Location, Meal, TripPlan, TripRequest, WeatherInfo


def _dump(model: Any) -> dict:
    return model.model_dump(mode="json", exclude_none=True) if model is not None else {}


async def create_trip_placeholder(session: AsyncSession, request: TripRequest) -> TripPlanModel:
    trip = TripPlanModel(
        city=request.city,
        start_date=request.start_date,
        end_date=request.end_date,
        travel_days=request.travel_days,
        transportation=request.transportation,
        accommodation=request.accommodation,
        preferences=request.preferences,
        free_text_input=request.free_text_input or "",
        status="generating",
    )
    session.add(trip)
    await session.commit()
    await session.refresh(trip)
    return trip


def _detail_options():
    return (
        selectinload(TripPlanModel.days).selectinload(DayPlanModel.attractions),
        selectinload(TripPlanModel.days).selectinload(DayPlanModel.meals),
        selectinload(TripPlanModel.weather),
    )


async def _get_model(session: AsyncSession, trip_id: str) -> TripPlanModel | None:
    result = await session.execute(
        select(TripPlanModel).where(TripPlanModel.id == str(trip_id)).options(*_detail_options())
    )
    return result.scalar_one_or_none()


def model_to_plan(trip: TripPlanModel) -> TripPlan:
    days = []
    for day in sorted(trip.days, key=lambda item: item.day_index):
        attractions = [
            Attraction(
                name=item.name,
                address=item.address,
                location=Location(longitude=item.longitude, latitude=item.latitude),
                visit_duration=item.visit_duration,
                description=item.description,
                category=item.category,
                rating=item.rating,
                image_url=item.image_url,
                ticket_price=item.ticket_price,
            )
            for item in sorted(day.attractions, key=lambda item: item.sort_order)
        ]
        meals = [
            Meal(
                type=item.type,
                name=item.name,
                address=item.address,
                description=item.description,
                estimated_cost=item.estimated_cost,
            )
            for item in sorted(day.meals, key=lambda item: item.sort_order)
        ]
        days.append(
            DayPlan(
                date=day.date,
                day_index=day.day_index,
                description=day.description,
                transportation=day.transportation,
                accommodation=day.accommodation,
                hotel=Hotel(**day.hotel_json) if day.hotel_json else None,
                attractions=attractions,
                meals=meals,
            )
        )

    weather_info = [
        WeatherInfo(
            date=item.date,
            day_weather=item.day_weather,
            night_weather=item.night_weather,
            day_temp=item.day_temp,
            night_temp=item.night_temp,
            wind_direction=item.wind_direction,
            wind_power=item.wind_power,
        )
        for item in sorted(trip.weather, key=lambda item: item.date)
    ]

    return TripPlan(
        city=trip.city,
        start_date=trip.start_date,
        end_date=trip.end_date,
        days=days,
        weather_info=weather_info,
        overall_suggestions=trip.overall_suggestions,
        budget=Budget(**trip.budget_json) if trip.budget_json else None,
    )


def model_to_detail(trip: TripPlanModel) -> dict:
    return {
        "id": trip.id,
        "city": trip.city,
        "start_date": trip.start_date,
        "end_date": trip.end_date,
        "travel_days": trip.travel_days,
        "transportation": trip.transportation,
        "accommodation": trip.accommodation,
        "preferences": trip.preferences,
        "free_text_input": trip.free_text_input,
        "status": trip.status,
        "created_at": trip.created_at.isoformat() if trip.created_at else None,
        "updated_at": trip.updated_at.isoformat() if trip.updated_at else None,
        "data": model_to_plan(trip),
    }


async def get_trip_plan(session: AsyncSession, trip_id: str) -> dict | None:
    trip = await _get_model(session, str(trip_id))
    return model_to_detail(trip) if trip else None


async def list_trip_plans(session: AsyncSession, page: int = 1, size: int = 10) -> tuple[list[dict], int]:
    page = max(page, 1)
    size = min(max(size, 1), 100)
    total_result = await session.execute(select(func.count()).select_from(TripPlanModel))
    total = total_result.scalar_one()
    result = await session.execute(
        select(TripPlanModel)
        .order_by(TripPlanModel.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    items = [
        {
            "id": trip.id,
            "city": trip.city,
            "start_date": trip.start_date,
            "end_date": trip.end_date,
            "travel_days": trip.travel_days,
            "status": trip.status,
            "created_at": trip.created_at.isoformat() if trip.created_at else None,
        }
        for trip in result.scalars().all()
    ]
    return items, total


async def save_full_plan(session: AsyncSession, trip_id: str, plan: TripPlan) -> None:
    trip = await _get_model(session, str(trip_id))
    if trip is None:
        return

    trip.city = plan.city
    trip.start_date = plan.start_date
    trip.end_date = plan.end_date
    trip.overall_suggestions = plan.overall_suggestions
    trip.budget_json = _dump(plan.budget) if plan.budget else None
    trip.status = "completed"
    trip.days.clear()
    trip.weather.clear()
    await session.flush()

    for day in plan.days:
        day_model = DayPlanModel(
            trip_plan_id=trip.id,
            date=day.date,
            day_index=day.day_index,
            description=day.description,
            transportation=day.transportation,
            accommodation=day.accommodation,
            hotel_json=_dump(day.hotel) if day.hotel else None,
        )
        for index, attraction in enumerate(day.attractions):
            day_model.attractions.append(
                AttractionModel(
                    name=attraction.name,
                    address=attraction.address,
                    longitude=attraction.location.longitude,
                    latitude=attraction.location.latitude,
                    visit_duration=attraction.visit_duration,
                    description=attraction.description,
                    category=attraction.category,
                    rating=attraction.rating,
                    ticket_price=attraction.ticket_price or 0,
                    image_url=attraction.image_url,
                    sort_order=index,
                )
            )
        for index, meal in enumerate(day.meals):
            day_model.meals.append(
                MealModel(
                    type=meal.type,
                    name=meal.name,
                    address=meal.address,
                    description=meal.description,
                    estimated_cost=meal.estimated_cost or 0,
                    sort_order=index,
                )
            )
        trip.days.append(day_model)

    for weather in plan.weather_info:
        trip.weather.append(
            WeatherInfoModel(
                date=weather.date,
                day_weather=weather.day_weather,
                night_weather=weather.night_weather,
                day_temp=int(weather.day_temp or 0),
                night_temp=int(weather.night_temp or 0),
                wind_direction=weather.wind_direction,
                wind_power=weather.wind_power,
            )
        )

    await session.commit()


async def update_trip_status(session: AsyncSession, trip_id: str, status: str) -> None:
    trip = await session.get(TripPlanModel, str(trip_id))
    if trip:
        trip.status = status
        await session.commit()


async def update_trip_plan(session: AsyncSession, trip_id: str, plan: TripPlan) -> dict:
    await save_full_plan(session, str(trip_id), plan)
    updated = await get_trip_plan(session, str(trip_id))
    if updated is None:
        raise ValueError("Trip plan not found")
    return updated


async def delete_trip_plan(session: AsyncSession, trip_id: str) -> bool:
    result = await session.execute(delete(TripPlanModel).where(TripPlanModel.id == str(trip_id)))
    await session.commit()
    return bool(result.rowcount)


def pagination_meta(page: int, size: int, total: int) -> dict:
    return {
        "page": page,
        "size": size,
        "total": total,
        "total_pages": ceil(total / size) if size else 0,
    }

