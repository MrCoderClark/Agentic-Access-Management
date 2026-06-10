"""Embedding service — generates vector embeddings via OpenAI API."""

import httpx

from app.config import settings


class EmbeddingService:
    """Generates embeddings using OpenAI's text-embedding API."""

    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.embedding_model
        self.dimension = settings.embedding_dimension
        self.base_url = "https://api.openai.com/v1/embeddings"

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text string."""
        result = await self.embed_batch([text])
        return result[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not configured")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "input": texts,
                    "model": self.model,
                    "dimensions": self.dimension,
                },
            )
            response.raise_for_status()
            data = response.json()

        # Sort by index to maintain order
        embeddings = sorted(data["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in embeddings]


embedding_service = EmbeddingService()
