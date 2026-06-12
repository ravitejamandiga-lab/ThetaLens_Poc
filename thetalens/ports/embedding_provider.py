from abc import ABC, abstractmethod
from typing import Sequence


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_texts(self, texts: Sequence[str]) -> Sequence[list[float]]:
        """Return vector embeddings for text chunks."""

