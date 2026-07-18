import json
from pathlib import Path

from schemas.event import ClassifiedEvent, OllamaResponse
from services.ollama_service import ollama_service


PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    prompt_path = PROMPTS_DIR / name
    return prompt_path.read_text(encoding="utf-8")


SYSTEM_PROMPT = _load_prompt("classify.txt")
REPAIR_PROMPT = (
    "Предыдущий ответ содержал некорректный JSON. "
    "Исправь JSON так, чтобы он был валидным. "
    "Не изменяй извлечённые данные."
)


class Classifier:
    async def classify(self, user_text: str) -> OllamaResponse | None:
        """Classify user text into structured events via Ollama.

        Returns None if Ollama is unavailable or parsing fails.
        """
        full_prompt = SYSTEM_PROMPT + "\n\nСобытие:\n" + user_text

        raw_response = await ollama_service.generate(full_prompt)

        if not raw_response:
            return None

        parsed = ollama_service.parse_json_response(raw_response)

        if parsed:
            return self._validate_and_return(parsed, raw_response)

        # Retry with repair prompt
        repair_full_prompt = REPAIR_PROMPT + "\n\n" + raw_response
        raw_retry = await ollama_service.generate(repair_full_prompt)

        if not raw_retry:
            return None

        parsed_retry = ollama_service.parse_json_response(raw_retry)

        if parsed_retry:
            return self._validate_and_return(parsed_retry, raw_retry)

        return None

    def _validate_and_return(
        self, data: dict, raw_response: str
    ) -> OllamaResponse | None:
        try:
            response = OllamaResponse(**data)
            return response
        except Exception:
            return None


classifier = Classifier()