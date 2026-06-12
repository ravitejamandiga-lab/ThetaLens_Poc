from abc import ABC, abstractmethod
from typing import Sequence

from thetalens.domain.models import SentimentResult


class SentimentProvider(ABC):
    @abstractmethod
    def analyze(self, texts: Sequence[tuple[str, str]]) -> Sequence[SentimentResult]:
        """Analyze sentiment for `(text_id, text)` pairs."""

