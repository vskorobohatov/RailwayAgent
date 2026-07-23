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


@router.get("/tasks")
async def list_tasks():
    """Return all tasks in the queue."""
    tasks = await task_store.list_all()
    return {"tasks": tasks, "count": len(tasks)}


@router.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """Cancel a pending or processing task."""
    ok = await task_store.cancel(task_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Не удалось отменить задачу (уже завершена или не найдена)")
    return {"ok": True}


@router.post("/tasks/{task_id}/retry")
async def retry_task(task_id: str):
    """Retry a failed or cancelled task."""
    ok = await task_store.retry(task_id)
    if not ok:
        raise HTTPException(status_code=400, detail="Не удалось перезапустить задачу (не найдена или не в статусе failed/cancelled)")
    return {"ok": True}


@router.get("/events")
async def list_events():
    """Return the 50 most recent events across all tables."""
    async with get_session() as session:
        events = await db_service.get_recent_events(session, limit=50)

    return {"events": events, "count": len(events)}
