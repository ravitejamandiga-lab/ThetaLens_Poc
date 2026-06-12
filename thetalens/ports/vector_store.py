from abc import ABC, abstractmethod
from typing import Any, Sequence


class VectorStore(ABC):
    @abstractmethod
    def add_documents(
        self,
        ids: Sequence[str],
        texts: Sequence[str],
        embeddings: Sequence[list[float]],
        metadata: Sequence[dict[str, Any]],
    ) -> None:
        """Store embedded documents."""

    @abstractmethod
    def search(self, embedding: list[float], limit: int = 5) -> Sequence[dict[str, Any]]:
        """Return nearest documents for an embedding."""

