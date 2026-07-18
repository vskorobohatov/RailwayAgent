from typing import Any, Literal

from pydantic import BaseModel


class TrainArrivalRow(BaseModel):
    time: str | None = None
    train_number: str | None = None
    platform: int | None = None
    delay_minutes: float | None = None
    notes: str | None = None


class TrainDepartureRow(BaseModel):
    time: str | None = None
    train_number: str | None = None
    platform: int | None = None
    delay_minutes: float | None = None
    notes: str | None = None


class EvacuationRow(BaseModel):
    start_time: str | None = None
    end_time: str | None = None
    reason: str | None = None
    notes: str | None = None


class WaitingRoomRow(BaseModel):
    visitors: int | None = None
    notes: str | None = None


class ClassifiedEvent(BaseModel):
    table: Literal[
        "train_arrivals",
        "train_departures",
        "evacuations",
        "waiting_room",
    ]
    row: dict[str, Any]


class OllamaResponse(BaseModel):
    events: list[ClassifiedEvent]


class EventInput(BaseModel):
    text: str