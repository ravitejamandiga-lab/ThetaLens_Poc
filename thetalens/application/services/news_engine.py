from datetime import date

from thetalens.domain.models import NewsArticle
from thetalens.ports.news_provider import NewsProvider


class NewsEngine:
    def __init__(self, provider: NewsProvider) -> None:
        self._provider = provider

    def get_company_news(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> list[NewsArticle]:
        articles = self._provider.get_company_news(ticker, start_date, end_date)
        return self._deduplicate_articles(list(articles))

    def _deduplicate_articles(self, articles: list[NewsArticle]) -> list[NewsArticle]:
        seen: set[str] = set()
        deduplicated: list[NewsArticle] = []

        for article in articles:
            key = article.url or f"{article.source}:{article.title}".lower()
            if key in seen:
                continue
            seen.add(key)
            deduplicated.append(article)

        return deduplicated

