from datetime import date, datetime, timezone
from typing import Sequence

from thetalens.application.services.investment_narrative_engine import (
    InvestmentNarrativeEngine,
)
from thetalens.application.services.market_data_engine import MarketDataEngine
from thetalens.application.services.news_engine import NewsEngine
from thetalens.application.services.news_impact_engine import NewsImpactEngine
from thetalens.application.services.sentiment_engine import SentimentEngine
from thetalens.application.use_cases.generate_research_report import GenerateResearchReport
from thetalens.domain.enums import SentimentLabel
from thetalens.domain.models import (
    BusinessEvent,
    InvestmentNarrative,
    MarketSnapshot,
    NewsArticle,
    PriceBar,
    ResearchRequest,
    SentimentResult,
)
from thetalens.ports.ai_provider import AIProvider
from thetalens.ports.market_data_provider import MarketDataProvider
from thetalens.ports.news_provider import NewsProvider
from thetalens.ports.sentiment_provider import SentimentProvider


class FakeMarketDataProvider(MarketDataProvider):
    def get_stock_profile(self, ticker: str) -> MarketSnapshot:
        return MarketSnapshot(
            ticker=ticker,
            company_name="NVIDIA Corporation",
            current_price=100,
            source="fake",
        )

    def get_price_history(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Sequence[PriceBar]:
        return [
            PriceBar(
                ticker=ticker,
                date=start_date,
                open=90,
                high=101,
                low=89,
                close=100,
                volume=1_000_000,
            ),
            PriceBar(
                ticker=ticker,
                date=end_date,
                open=100,
                high=112,
                low=99,
                close=110,
                volume=1_500_000,
            ),
        ]


class FakeNewsProvider(NewsProvider):
    def get_company_news(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Sequence[NewsArticle]:
        published_at = datetime(2026, 5, 1, tzinfo=timezone.utc)
        return [
            NewsArticle(
                article_id="news-1",
                ticker=ticker,
                title="NVIDIA announces strong AI infrastructure demand",
                source="fake-news",
                url="https://example.com/news-1",
                published_at=published_at,
            )
        ]


class FakeSentimentProvider(SentimentProvider):
    def analyze(self, texts: Sequence[tuple[str, str]]) -> Sequence[SentimentResult]:
        return [
            SentimentResult(
                text_id=text_id,
                label=SentimentLabel.POSITIVE,
                positive_score=0.8,
                neutral_score=0.15,
                negative_score=0.05,
            )
            for text_id, _ in texts
        ]


class FakeAIProvider(AIProvider):
    def generate_text(self, prompt: str) -> str:
        return "Generated text"

    def extract_events(self, articles: Sequence[NewsArticle]) -> Sequence[BusinessEvent]:
        article = articles[0]
        return [
            BusinessEvent(
                event_id="event-1",
                ticker=article.ticker,
                name="AI Infrastructure Demand",
                description="Demand for AI infrastructure improved investor attention.",
                article_ids=[article.article_id],
                first_seen=article.published_at,
                last_seen=article.published_at,
            )
        ]

    def generate_investment_narrative(
        self,
        market_snapshot: MarketSnapshot,
        price_history: Sequence[PriceBar],
        articles: Sequence[NewsArticle],
        events: Sequence[BusinessEvent],
        impact_scores: Sequence,
        sentiment_results: Sequence[SentimentResult],
    ) -> InvestmentNarrative:
        return InvestmentNarrative(
            company_story="The company story centers on AI infrastructure demand.",
            market_story="The market reacted positively over the selected period.",
            investor_story="Investors may want to research demand durability.",
            risk_story="Key risks include demand normalization and competition.",
            opportunity_context="This is research context, not a recommendation.",
        )


def test_generate_research_report_orchestrates_core_engines() -> None:
    ai_provider = FakeAIProvider()
    use_case = GenerateResearchReport(
        market_data_engine=MarketDataEngine(FakeMarketDataProvider()),
        news_engine=NewsEngine(FakeNewsProvider()),
        sentiment_engine=SentimentEngine(FakeSentimentProvider()),
        news_impact_engine=NewsImpactEngine(ai_provider),
        investment_narrative_engine=InvestmentNarrativeEngine(ai_provider),
    )

    report = use_case.execute(
        ResearchRequest(
            ticker="nvda",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 1),
        )
    )

    assert report.request.ticker == "NVDA"
    assert report.market_snapshot.company_name == "NVIDIA Corporation"
    assert len(report.news_articles) == 1
    assert len(report.key_events) == 1
    assert len(report.event_impact_scores) == 1
    assert report.sentiment_results[0].label == SentimentLabel.POSITIVE
    assert "not financial advice" in report.narrative.disclaimer
