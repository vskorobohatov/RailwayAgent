from pydantic import BaseModel


class ReportResponse(BaseModel):
    content: str
    file_path: str