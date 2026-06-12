from collections import Counter
from typing import Sequence

from thetalens.domain.enums import SentimentLabel
from thetalens.domain.models import NewsArticle, SentimentResult
from thetalens.ports.sentiment_provider import SentimentProvider


class SentimentEngine:
    def __init__(self, provider: SentimentProvider) -> None:
        self._provider = provider

    def analyze_articles(self, articles: Sequence[NewsArticle]) -> list[SentimentResult]:
        texts = [(article.article_id, article.title) for article in articles]
        return list(self._provider.analyze(texts))

    def summarize(self, results: Sequence[SentimentResult]) -> dict[SentimentLabel, int]:
        counts = Counter(result.label for result in results)
        return {label: counts.get(label, 0) for label in SentimentLabel}

