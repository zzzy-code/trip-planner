"""Trip CRUD and SSE routes."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from ...agents.trip_planner_agent import get_trip_planner_agent
from ...crud.trips import (
    create_trip_placeholder,
    delete_trip_plan,
    get_trip_plan,
    list_trip_plans,
    pagination_meta,
    save_full_plan,
    update_trip_plan,
    update_trip_status,
)
from ...db.session import get_db
from ...models.schemas import TripPlan, TripRequest

router = APIRouter(prefix="/trips", tags=["trips"])


def encode_sse_data(event: str, data: dict) -> dict:
    return {"event": event, "data": json.dumps(data, ensure_ascii=False)}


def response(data=None, error=None, meta=None, success: bool | None = None) -> dict:
    ok = error is None if success is None else success
    return {"success": ok, "data": data, "error": error, "meta": meta}


@router.get("")
async def list_trips(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    items, total = await list_trip_plans(session, page=page, size=size)
    return response(data=items, meta=pagination_meta(page, size, total))


@router.get("/plan/stream")
async def stream_trip_plan(
    request: Request,
    params: str = Query(..., description="URL-encoded JSON TripRequest"),
    session: AsyncSession = Depends(get_db),
):
    try:
        trip_request = TripRequest(**json.loads(params))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Invalid params: {exc}") from exc

    async def event_generator() -> AsyncGenerator[dict, None]:
        trip = await create_trip_placeholder(session, trip_request)
        yield encode_sse_data("plan_started", {"trip_plan_id": trip.id})

        queue: asyncio.Queue[dict] = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def agent_callback(event_name: str, payload: dict):
            loop.call_soon_threadsafe(queue.put_nowait, encode_sse_data(event_name, payload))

        def run_agent():
            agent = get_trip_planner_agent()
            return agent.plan_trip(trip_request, callback=agent_callback)

        task = asyncio.create_task(asyncio.to_thread(run_agent))

        try:
            while not task.done() or not queue.empty():
                if await request.is_disconnected():
                    task.cancel()
                    return
                try:
                    item = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield item
                except asyncio.TimeoutError:
                    yield encode_sse_data("heartbeat", {"status": "alive"})

            plan = await task
            await save_full_plan(session, trip.id, plan)
            yield encode_sse_data("plan_completed", {"trip_plan_id": trip.id})
        except Exception as exc:
            await update_trip_status(session, trip.id, "failed")
            yield encode_sse_data("plan_failed", {"error_code": "GENERATION_FAILED", "message": str(exc)})

    return EventSourceResponse(event_generator(), ping=15)


@router.get("/{trip_id}")
async def get_trip(trip_id: str, session: AsyncSession = Depends(get_db)):
    trip = await get_trip_plan(session, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip plan not found")
    return response(data=trip)


@router.put("/{trip_id}")
async def update_trip(trip_id: str, plan: TripPlan, session: AsyncSession = Depends(get_db)):
    try:
        trip = await update_trip_plan(session, trip_id, plan)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return response(data=trip)


@router.delete("/{trip_id}")
async def delete_trip(trip_id: str, session: AsyncSession = Depends(get_db)):
    deleted = await delete_trip_plan(session, trip_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Trip plan not found")
    return response(data={"deleted": True})

