from collections import defaultdict
from datetime import datetime
from typing import Sequence

from thetalens.domain.enums import SentimentLabel
from thetalens.domain.models import (
    BusinessEvent,
    EventImpactScore,
    NewsArticle,
    PriceBar,
    SentimentResult,
)
from thetalens.ports.ai_provider import AIProvider


class NewsImpactEngine:
    def __init__(self, ai_provider: AIProvider) -> None:
        self._ai_provider = ai_provider

    def extract_events(self, articles: Sequence[NewsArticle]) -> list[BusinessEvent]:
        events = self._ai_provider.extract_events(articles)
        return list(events)

    def score_event_impact(
        self,
        events: Sequence[BusinessEvent],
        price_history: Sequence[PriceBar],
        sentiment_results: Sequence[SentimentResult],
    ) -> list[EventImpactScore]:
        sentiment_by_text_id = {result.text_id: result for result in sentiment_results}
        scores: list[EventImpactScore] = []

        for event in events:
            event_sentiments = [
                sentiment_by_text_id[article_id]
                for article_id in event.article_ids
                if article_id in sentiment_by_text_id
            ]
            sentiment_label = self._dominant_sentiment(event_sentiments)
            sentiment_boost = self._sentiment_boost(sentiment_label)
            recency_score = self._recency_score(event.last_seen)
            price_reaction_pct = self._price_reaction_pct(price_history)
            price_boost = min(abs(price_reaction_pct or 0) / 3, 3)
            source_boost = min(len(set(event.article_ids)) * 0.5, 2)
            impact_score = min(10, 2 + sentiment_boost + price_boost + source_boost + recency_score)

            scores.append(
                EventImpactScore(
                    event_id=event.event_id,
                    impact_score=round(impact_score, 2),
                    sentiment_label=sentiment_label,
                    price_reaction_pct=price_reaction_pct,
                    recency_score=round(recency_score, 2),
                    explanation=(
                        "Impact score combines event sentiment, article coverage, "
                        "recent timing, and broad price movement context."
                    ),
                )
            )

        return scores

    def _dominant_sentiment(self, results: Sequence[SentimentResult]) -> SentimentLabel:
        if not results:
            return SentimentLabel.NEUTRAL

        grouped: defaultdict[SentimentLabel, float] = defaultdict(float)
        for result in results:
            grouped[SentimentLabel.POSITIVE] += result.positive_score
            grouped[SentimentLabel.NEUTRAL] += result.neutral_score
            grouped[SentimentLabel.NEGATIVE] += result.negative_score

        return max(grouped, key=grouped.get)

    def _sentiment_boost(self, label: SentimentLabel) -> float:
        if label == SentimentLabel.POSITIVE:
            return 2
        if label == SentimentLabel.NEGATIVE:
            return 1.5
        return 0.5

    def _recency_score(self, last_seen: datetime) -> float:
        age_days = max((datetime.now(last_seen.tzinfo) - last_seen).days, 0)
        return max(0, 2 - (age_days / 30))

    def _price_reaction_pct(self, price_history: Sequence[PriceBar]) -> float | None:
        if len(price_history) < 2:
            return None

        first_close = price_history[0].close
        last_close = price_history[-1].close
        if first_close == 0:
            return None

        return round(((last_close - first_close) / first_close) * 100, 2)

