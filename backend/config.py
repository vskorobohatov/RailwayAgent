from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    database_url: str = "sqlite:///./railway_agent.db"

    model_config = {"env_file": ".env"}


settings = Settings()