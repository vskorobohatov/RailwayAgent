from datetime import datetime
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from services.ollama_service import ollama_service
from services.database_service import db_service


REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "reports"
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_report_prompt() -> str:
    prompt_path = PROMPTS_DIR / "report.txt"
    return prompt_path.read_text(encoding="utf-8")


REPORT_PROMPT_TEMPLATE = _load_report_prompt()


class ReportService:
    async def generate(
        self,
        session: AsyncSession,
    ) -> tuple[str, str]:
        """Generate a Markdown report from database data via Ollama.

        Returns:
            (markdown_content, file_path)
        """
        all_events = await db_service.get_all_events(session)
        events_text = self._format_events_for_prompt(all_events)

        full_prompt = REPORT_PROMPT_TEMPLATE + "\n\nДанные:\n" + events_text

        raw_response = await ollama_service.generate(full_prompt)

        if raw_response is None:
            raise RuntimeError("Ollama не ответила. Проверьте что Ollama запущен и доступен.")

        # Strip code fences if present
        md_content = raw_response.strip()
        if md_content.startswith("```"):
            parts = md_content.split("```")
            if len(parts) >= 2:
                md_content = parts[1]
                if md_content.startswith("md"):
                    md_content = md_content[2:]

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = REPORTS_DIR / f"report_{timestamp}.md"
        file_path.write_text(md_content, encoding="utf-8")

        # Also write the latest report.md
        latest_path = REPORTS_DIR / "report.md"
        latest_path.write_text(md_content, encoding="utf-8")

        return md_content, str(latest_path)

    def _format_events_for_prompt(self, data: dict[str, list[dict]]) -> str:
        """Convert database records into a readable text block for the LLM."""
        lines = []

        table_names = {
            "train_arrivals": "Прибытие поездов",
            "train_departures": "Отправление поездов",
            "evacuations": "Эвакуации",
            "waiting_room": "Зал ожидания",
        }

        for table, title in table_names.items():
            records = data.get(table, [])
            if not records:
                lines.append(f"## {title} — нет данных\n")
                continue

            lines.append(f"## {title}")
            for rec in records:
                line_parts = [f"{k}: {v}" for k, v in rec.items()]
                lines.append("  - " + ", ".join(line_parts))
            lines.append("")

        return "\n".join(lines)


report_service = ReportService()