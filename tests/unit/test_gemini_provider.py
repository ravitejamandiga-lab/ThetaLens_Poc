from datetime import datetime, timezone

import pytest

from thetalens.domain.errors import AIOutputValidationError
from thetalens.domain.enums import SentimentLabel
from thetalens.domain.models import (
    BusinessEvent,
    EventImpactScore,
    MarketSnapshot,
    NewsArticle,
    PriceBar,
    SentimentResult,
)
from thetalens.infrastructure.ai.gemini_provider import GeminiProvider


class FakeResponse:
    def __init__(self, text: str) -> None:
        self.text = text


class FakeModels:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.last_model: str | None = None
        self.last_contents: str | None = None

    def generate_content(self, model: str, contents: str) -> FakeResponse:
        self.last_model = model
        self.last_contents = contents
        return FakeResponse(self.response_text)


class FakeClient:
    def __init__(self, response_text: str) -> None:
        self.models = FakeModels(response_text)


def test_generate_text_calls_gemini_model() -> None:
    client = FakeClient("hello")
    provider = GeminiProvider(client=client, model="test-model")

    result = provider.generate_text("Say hello")

    assert result == "hello"
    assert client.models.last_model == "test-model"
    assert client.models.last_contents == "Say hello"


def test_extract_events_parses_valid_json() -> None:
    published_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    client = FakeClient(
        """
        {
          "events": [
            {
              "event_id": "event-1",
              "ticker": "nvda",
              "name": "AI Demand",
              "description": "Demand for AI infrastructure increased.",
              "article_ids": ["article-1"],
              "first_seen": "2026-01-01T00:00:00+00:00",
              "last_seen": "2026-01-01T00:00:00+00:00"
            }
          ]
        }
        """
    )
    provider = GeminiProvider(client=client)

    events = provider.extract_events(
        [
            NewsArticle(
                article_id="article-1",
                ticker="nvda",
                title="NVIDIA AI demand rises",
                source="test",
                published_at=published_at,
            )
        ]
    )

    assert len(events) == 1
    assert events[0].ticker == "NVDA"
    assert events[0].article_ids == ["article-1"]


def test_generate_investment_narrative_validates_json() -> None:
    client = FakeClient(
        """
        ```json
        {
          "company_story": "The company story centers on AI demand.",
          "market_story": "The market reaction was positive in context.",
          "investor_story": "Investors may research demand durability.",
          "risk_story": "Risks include competition and demand normalization.",
          "opportunity_context": "This is research context only.",
          "disclaimer": "ThetaLens provides research assistance, not financial advice."
        }
        ```
        """
    )
    provider = GeminiProvider(client=client)
    published_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    article = NewsArticle(
        article_id="article-1",
        ticker="NVDA",
        title="NVIDIA AI demand rises",
        source="test",
        published_at=published_at,
    )
    event = BusinessEvent(
        event_id="event-1",
        ticker="NVDA",
        name="AI Demand",
        description="Demand for AI infrastructure increased.",
        article_ids=["article-1"],
        first_seen=published_at,
        last_seen=published_at,
    )

    narrative = provider.generate_investment_narrative(
        market_snapshot=MarketSnapshot(ticker="NVDA", source="test"),
        price_history=[
            PriceBar(
                ticker="NVDA",
                date=published_at.date(),
                open=100,
                high=110,
                low=95,
                close=105,
                volume=1000,
            )
        ],
        articles=[article],
        events=[event],
        impact_scores=[
            EventImpactScore(
                event_id="event-1",
                impact_score=7.5,
                sentiment_label=SentimentLabel.POSITIVE,
                explanation="Positive event coverage.",
            )
        ],
        sentiment_results=[
            SentimentResult(
                text_id="article-1",
                label=SentimentLabel.POSITIVE,
                positive_score=0.8,
                neutral_score=0.15,
                negative_score=0.05,
            )
        ],
    )

    assert "not financial advice" in narrative.disclaimer


def test_invalid_json_raises_validation_error() -> None:
    provider = GeminiProvider(client=FakeClient("not json"))

    with pytest.raises(AIOutputValidationError):
        provider.extract_events(
            [
                NewsArticle(
                    article_id="article-1",
                    ticker="NVDA",
                    title="News title",
                    source="test",
                    published_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
                )
            ]
        )
