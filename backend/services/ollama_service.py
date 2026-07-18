import json

import httpx

from config import settings


class OllamaService:
    def __init__(self) -> None:
        self.base_url = settings.ollama_url.rstrip("/")
        self.model = settings.ollama_model

    async def generate(self, prompt: str) -> str | None:
        """Send a prompt to Ollama and return the full response text."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                return data.get("response", "")
        except httpx.HTTPStatusError as exc:
            print(f"[OllamaError] HTTP {exc.response.status_code}: {exc.response.text[:200]}")
            return None
        except httpx.ConnectError as exc:
            print(f"[OllamaError] Cannot connect to {url}: {exc}")
            return None
        except httpx.TimeoutException as exc:
            print(f"[OllamaError] Timeout after 180s: {exc}")
            return None
        except Exception as exc:
            print(f"[OllamaError] Unexpected error ({type(exc).__name__}): {exc}")
            return None

    async def generate_stream(self, prompt: str):
        """Stream tokens from Ollama one by one. Yields (chunk, full_text) tuples."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": 0.1,
            },
        }

        full_text = ""
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                async with client.stream("POST", url, json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            data = json.loads(line)
                            chunk = data.get("response", "")
                            if chunk:
                                full_text += chunk
                                yield chunk, full_text
                        except json.JSONDecodeError:
                            continue
        except httpx.HTTPStatusError as exc:
            print(f"[OllamaError] HTTP {exc.response.status_code}: {exc.response.text[:200]}")
            return
        except httpx.ConnectError as exc:
            print(f"[OllamaError] Cannot connect to {url}: {exc}")
            return
        except httpx.TimeoutException as exc:
            print(f"[OllamaError] Timeout after 180s: {exc}")
            return
        except Exception as exc:
            print(f"[OllamaError] Unexpected error ({type(exc).__name__}): {exc}")
            return

    def parse_json_response(self, raw: str) -> dict | None:
        """Try to extract valid JSON from the model's raw response."""
        if not raw:
            return None

        raw = raw.strip()

        try:
            if raw.startswith("{"):
                return json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            pass

        fence_out = raw.split("```")
        for block in fence_out:
            block = block.strip()
            try:
                if block.startswith("{"):
                    return json.loads(block)
            except (json.JSONDecodeError, ValueError):
                continue

        return None


ollama_service = OllamaService()