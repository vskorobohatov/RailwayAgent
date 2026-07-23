from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.train_arrivals import TrainArrival
from models.train_departures import TrainDeparture
from models.evacuations import Evacuation
from models.waiting_room import WaitingRoom
from models.other_events import OtherEvent
from models.request_logs import RequestLog


TABLE_MAP = {
    "train_arrivals": TrainArrival,
    "train_departures": TrainDeparture,
    "evacuations": Evacuation,
    "waiting_room": WaitingRoom,
    "other_events": OtherEvent,
}


class DatabaseService:
    """CRUD operations for all event tables."""

    async def save_event(
        self,
        session: AsyncSession,
        table: str,
        row_data: dict,
    ) -> int | None:
        """Insert a single row into the given table. Returns the new row id."""
        model = TABLE_MAP.get(table)
        if model is None:
            return None

        now = date.today()
        db_row = model(date=now, **row_data)
        session.add(db_row)
        await session.flush()
        return db_row.id

    async def save_request_log(
        self,
        session: AsyncSession,
        input_text: str,
        ollama_response: str | None,
        success: bool,
    ) -> None:
        log = RequestLog(
            input_text=input_text,
            ollama_response=ollama_response,
            success=success,
        )
        session.add(log)

    async def get_recent_events(
        self,
        session: AsyncSession,
        limit: int = 50,
    ) -> list[dict]:
        """Return the N most recent rows across all event tables."""
        results = []

        for model in TABLE_MAP.values():
            stmt = (
                select(model)
                .order_by(model.created_at.desc())
                .limit(limit)
            )
            rows = await session.execute(stmt)
            for row in rows.scalars().all():
                data = {}
                for col in model.__table__.columns:
                    val = getattr(row, col.name)
                    if isinstance(val, date):
                        val = val.isoformat()
                    data[col.name] = val
                data["__table__"] = model.__tablename__
                results.append(data)

        results.sort(key=lambda r: r["created_at"], reverse=True)
        return results[:limit]

    async def get_all_events(self, session: AsyncSession) -> dict[str, list[dict]]:
        """Return all rows grouped by table name."""
        data: dict[str, list[dict]] = {}

        for model in TABLE_MAP.values():
            stmt = select(model).order_by(model.created_at.desc())
            rows = await session.execute(stmt)
            items = []
            for row in rows.scalars().all():
                row_dict = {}
                for col in model.__table__.columns:
                    val = getattr(row, col.name)
                    if isinstance(val, date):
                        val = val.isoformat()
                    row_dict[col.name] = val
                items.append(row_dict)
            data[model.__tablename__] = items

        return data


db_service = DatabaseService()