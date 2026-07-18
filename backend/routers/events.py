from fastapi import APIRouter, HTTPException

from database import get_session
from schemas.event import EventInput
from services.database_service import db_service
from services.task_store import task_store

router = APIRouter(prefix="/api", tags=["events"])


@router.post("/events")
async def add_event(payload: EventInput):
    """Submit text → create async task → return task_id immediately."""
    task = await task_store.create(payload.text)
    return {"task_id": task.id}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Poll task status, step, result or error."""
    task = await task_store.get(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return {
        "task_id": task.id,
        "status": task.status.value,
        "step": task.step,
        "result": task.result,
        "error": task.error,
    }


@router.get("/events")
async def list_events():
    """Return the 50 most recent events across all tables."""
    async with get_session() as session:
        events = await db_service.get_recent_events(session, limit=50)

    return {"events": events, "count": len(events)}