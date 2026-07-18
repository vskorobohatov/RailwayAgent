from datetime import datetime

from pydantic import BaseModel


class RequestLogRead(BaseModel):
    id: int
    input_text: str
    ollama_response: str | None
    success: bool
    processed_at: datetime

    model_config = {"from_attributes": True}