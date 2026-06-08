from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase
    supabase_url: str = "http://localhost:8000"
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    database_url: str = "postgresql://postgres:postgres@localhost:6543/postgres"

    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8001
    backend_cors_origins: str = "http://localhost:3000"

    # LLM
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-20250514"
    openai_api_key: str = ""
    openai_fallback_model: str = "gpt-4o"

    # Embeddings
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    # Agent
    agent_confidence_threshold: float = 0.6
    agent_max_retries: int = 3
    agent_timeout_seconds: int = 30

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",")]

    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
