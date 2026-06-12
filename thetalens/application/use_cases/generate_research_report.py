from thetalens.application.services.investment_narrative_engine import (
    InvestmentNarrativeEngine,
)
from thetalens.application.services.market_data_engine import MarketDataEngine
from thetalens.application.services.news_engine import NewsEngine
from thetalens.application.services.news_impact_engine import NewsImpactEngine
from thetalens.application.services.sentiment_engine import SentimentEngine
from thetalens.domain.models import ResearchReport, ResearchRequest


class GenerateResearchReport:
    def __init__(
        self,
        market_data_engine: MarketDataEngine,
        news_engine: NewsEngine,
        sentiment_engine: SentimentEngine,
        news_impact_engine: NewsImpactEngine,
        investment_narrative_engine: InvestmentNarrativeEngine,
    ) -> None:
        self._market_data_engine = market_data_engine
        self._news_engine = news_engine
        self._sentiment_engine = sentiment_engine
        self._news_impact_engine = news_impact_engine
        self._investment_narrative_engine = investment_narrative_engine

    def execute(self, request: ResearchRequest) -> ResearchReport:
        market_snapshot = self._market_data_engine.get_stock_profile(request.ticker)
        price_history = self._market_data_engine.get_price_history(
            request.ticker,
            request.start_date,
            request.end_date,
        )
        articles = self._news_engine.get_company_news(
            request.ticker,
            request.start_date,
            request.end_date,
        )
        sentiment_results = self._sentiment_engine.analyze_articles(articles)
        events = self._news_impact_engine.extract_events(articles)
        impact_scores = self._news_impact_engine.score_event_impact(
            events,
            price_history,
            sentiment_results,
        )
        narrative = self._investment_narrative_engine.generate(
            market_snapshot,
            price_history,
            articles,
            events,
            impact_scores,
            sentiment_results,
        )

        return ResearchReport(
            request=request,
            market_snapshot=market_snapshot,
            price_history=price_history,
            news_articles=articles,
            key_events=events,
            event_impact_scores=impact_scores,
            sentiment_results=sentiment_results,
            narrative=narrative,
        )

