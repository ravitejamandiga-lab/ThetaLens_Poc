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
from thetalens.ports.ai_provider import AIProvider


class InvestmentNarrativeEngine:
    def __init__(self, ai_provider: AIProvider) -> None:
        self._ai_provider = ai_provider

    def generate(
        self,
        market_snapshot: MarketSnapshot,
        price_history: Sequence[PriceBar],
        articles: Sequence[NewsArticle],
        events: Sequence[BusinessEvent],
        impact_scores: Sequence[EventImpactScore],
        sentiment_results: Sequence[SentimentResult],
    ) -> InvestmentNarrative:
        return self._ai_provider.generate_investment_narrative(
            market_snapshot=market_snapshot,
            price_history=price_history,
            articles=articles,
            events=events,
            impact_scores=impact_scores,
            sentiment_results=sentiment_results,
        )

