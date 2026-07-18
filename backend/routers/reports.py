import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from database import get_session
from schemas.report import ReportResponse
from services.report_service import report_service
from services.database_service import db_service
from services.ollama_service import ollama_service


router = APIRouter(prefix="/api/reports", tags=["reports"])


PROGRESS_STEPS = [
    ("collecting_data", "Сбор данных из базы..."),
    ("building_prompt", "Формирование промпта..."),
    ("calling_ollama", "Отправка запроса в Ollama..."),
    ("receiving_response", "Получение Markdown от модели..."),
    ("saving_file", "Сохранение файла..."),
    ("done", "Готово!"),
]


def _sse_event(step: str, message: str, data: dict | None = None) -> str:
    payload = json.dumps({"step": step, "message": message})
    if data is not None:
        payload = json.dumps({"step": step, "message": message, **data})
    return f"data: {payload}\n\n"


async def report_stream_generator():
    """Generate SSE events for report generation progress."""
    from datetime import datetime
    from pathlib import Path

    REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "reports"
    PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
    REPORT_PROMPT_TEMPLATE = (PROMPTS_DIR / "report.txt").read_text(encoding="utf-8")

    try:
        async with get_session() as session:
            # Step 1: Collect data
            yield _sse_event("collecting_data", "Сбор данных из базы...")
            all_events = await db_service.get_all_events(session)

            # Step 2: Build prompt
            yield _sse_event("building_prompt", "Формирование промпта...")
            events_text = report_service._format_events_for_prompt(all_events)
            full_prompt = REPORT_PROMPT_TEMPLATE + "\n\nДанные:\n" + events_text

            # Step 3: Call Ollama
            yield _sse_event("calling_ollama", "Отправка запроса в Ollama...")

            # Step 4: Receive response (stream tokens as SSE)
            yield _sse_event("receiving_response", "Получение Markdown от модели...")
            raw_chunks: list[str] = []
            async for chunk, accumulated in ollama_service.generate_stream(full_prompt):
                if chunk:
                    raw_chunks.append(chunk)
                    # Send partial content to frontend every few chunks
                    yield _sse_event(
                        "receiving_response",
                        "Получение Markdown от модели...",
                        data={"content": "".join(raw_chunks)},
                    )

            raw_response = "".join(raw_chunks) if raw_chunks else None

            if raw_response is None or raw_response.strip() == "":
                yield _sse_event("error", "Ollama не ответила. Проверьте что Ollama запущен и доступен.")
                return

            # Strip code fences if present
            md_content = raw_response.strip()
            if md_content.startswith("```"):
                parts = md_content.split("```")
                if len(parts) >= 2:
                    md_content = parts[1]
                    if md_content.startswith("md"):
                        md_content = md_content[2:]

            # Step 5: Save file
            yield _sse_event("saving_file", "Сохранение файла...")
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = REPORTS_DIR / f"report_{timestamp}.md"
            file_path.write_text(md_content, encoding="utf-8")

            latest_path = REPORTS_DIR / "report.md"
            latest_path.write_text(md_content, encoding="utf-8")

            # Step 6: Done
            yield _sse_event(
                "done",
                "Готово!",
                data={"content": md_content, "file_path": str(latest_path)},
            )

    except Exception as exc:
        yield _sse_event("error", f"Ошибка генерации отчёта: {exc}")


@router.get("")
async def generate_report():
    """Generate a Markdown report from all database data via Ollama."""
    try:
        async with get_session() as session:
            content, file_path = await report_service.generate(session)

        return ReportResponse(content=content, file_path=file_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации отчета: {exc}")


@router.get("/stream")
async def generate_report_stream():
    """Generate a Markdown report with SSE progress streaming."""
    return StreamingResponse(
        report_stream_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Content-Encoding": "identity",
        },
    )
