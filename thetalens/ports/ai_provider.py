from abc import ABC, abstractmethod
from typing import Sequence

from thetalens.domain.models import (
    BusinessEvent,
    EventImpactScore,
    InvestmentNarrative,
    MarketSnapshot,
    NewsArticle,
    PriceBar,
    SentimentResult,
)


class AIProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        """Generate unstructured text from a prompt."""

    @abstractmethod
    def extract_events(self, articles: Sequence[NewsArticle]) -> Sequence[BusinessEvent]:
        """Extract business events from normalized news articles."""

    @abstractmethod
    def generate_investment_narrative(
        self,
        market_snapshot: MarketSnapshot,
        price_history: Sequence[PriceBar],
        articles: Sequence[NewsArticle],
        events: Sequence[BusinessEvent],
        impact_scores: Sequence[EventImpactScore],
        sentiment_results: Sequence[SentimentResult],
    ) -> InvestmentNarrative:
        """Generate a financial-safety-compliant investment narrative."""

