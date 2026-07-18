import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    CLASSIFYING = "classifying"
    SAVING = "saving"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    id: str
    input_text: str
    status: TaskStatus = TaskStatus.PENDING
    step: str = ""
    result: Any = None
    error: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)


class TaskStore:
    def __init__(self, max_concurrent: int = 1):
        self._tasks: dict[str, Task] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def create(self, input_text: str) -> Task:
        task_id = uuid.uuid4().hex[:12]
        task = Task(id=task_id, input_text=input_text)
        self._tasks[task_id] = task
        asyncio.create_task(self._process(task))
        return task

    async def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    async def _process(self, task: Task):
        async with self._semaphore:
            try:
                task.status = TaskStatus.PROCESSING
                task.step = "Подготовка данных"
                await asyncio.sleep(0.1)

                # Import here to avoid circular deps
                from services.classifier import classifier
                from services.database_service import db_service
                from database import get_session

                task.status = TaskStatus.CLASSIFYING
                task.step = "Отправка запроса в AI (Ollama)"
                result = await classifier.classify(task.input_text)

                if result is None:
                    raise RuntimeError(
                        "Не удалось обработать запрос. Проверьте доступность Ollama."
                    )

                saved_ids: list[dict] = []
                task.status = TaskStatus.SAVING
                task.step = "Сохранение данных в базу"

                async with get_session() as session:
                    for event in result.events:
                        row_id = await db_service.save_event(
                            session=session,
                            table=event.table,
                            row_data=event.row,
                        )
                        if row_id is not None:
                            saved_ids.append({"table": event.table, "id": row_id})

                    await db_service.save_request_log(
                        session=session,
                        input_text=task.input_text,
                        ollama_response=f"Событий: {len(result.events)}",
                        success=True,
                    )
                    await session.commit()

                task.status = TaskStatus.COMPLETED
                task.step = "Готово"
                task.result = {
                    "message": "События сохранены",
                    "saved": saved_ids,
                    "count": len(saved_ids),
                }

            except Exception as exc:
                task.status = TaskStatus.FAILED
                task.step = ""
                task.error = str(exc)
                # Log failure
                try:
                    from database import get_session
                    from services.database_service import db_service
                    async with get_session() as session:
                        await db_service.save_request_log(
                            session=session,
                            input_text=task.input_text,
                            ollama_response=None,
                            success=False,
                        )
                        await session.commit()
                except Exception:
                    pass


task_store = TaskStore()