import json
import logging
import re
from typing import Any, Sequence

from google import genai
from pydantic import ValidationError

from thetalens.domain.errors import AIOutputValidationError, ProviderError
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

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    """Gemini-backed implementation of the AI provider port."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-2.5-flash",
        client: Any | None = None,
    ) -> None:
        self._model = model
        self._client = client or genai.Client(api_key=api_key)

    def generate_text(self, prompt: str) -> str:
        logger.info("Calling Gemini text generation", extra={"model": self._model})
        response = self._generate_content(prompt)
        return self._response_text(response)

    def extract_events(self, articles: Sequence[NewsArticle]) -> list[BusinessEvent]:
        if not articles:
            return []

        prompt = self._build_event_extraction_prompt(articles)
        logger.info(
            "Calling Gemini event extraction",
            extra={"model": self._model, "article_count": len(articles)},
        )
        response = self._generate_content(prompt)
        payload = self._parse_json_response(self._response_text(response))

        try:
            events_payload = payload.get("events", payload)
            return [BusinessEvent.model_validate(event) for event in events_payload]
        except (AttributeError, TypeError, ValidationError) as exc:
            raise AIOutputValidationError("Gemini event output failed validation") from exc

    def generate_investment_narrative(
        self,
        market_snapshot: MarketSnapshot,
        price_history: Sequence[PriceBar],
        articles: Sequence[NewsArticle],
        events: Sequence[BusinessEvent],
        impact_scores: Sequence[EventImpactScore],
        sentiment_results: Sequence[SentimentResult],
    ) -> InvestmentNarrative:
        prompt = self._build_narrative_prompt(
            market_snapshot=market_snapshot,
            price_history=price_history,
            articles=articles,
            events=events,
            impact_scores=impact_scores,
            sentiment_results=sentiment_results,
        )
        logger.info(
            "Calling Gemini narrative generation",
            extra={
                "model": self._model,
                "ticker": market_snapshot.ticker,
                "event_count": len(events),
            },
        )
        response = self._generate_content(prompt)
        payload = self._parse_json_response(self._response_text(response))

        try:
            return InvestmentNarrative.model_validate(payload)
        except ValidationError as exc:
            raise AIOutputValidationError("Gemini narrative output failed validation") from exc

    def _generate_content(self, prompt: str) -> Any:
        try:
            return self._client.models.generate_content(
                model=self._model,
                contents=prompt,
            )
        except Exception as exc:
            raise ProviderError("Gemini generate_content request failed") from exc

    def _response_text(self, response: Any) -> str:
        text = getattr(response, "text", None)
        if not text:
            raise ProviderError("Gemini returned an empty response")
        return text

    def _parse_json_response(self, text: str) -> Any:
        cleaned = self._strip_markdown_fence(text.strip())
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\}|\[.*\])", cleaned, flags=re.DOTALL)
            if not match:
                raise AIOutputValidationError("Gemini response did not contain JSON")

            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError as exc:
                raise AIOutputValidationError("Gemini response JSON could not be parsed") from exc

    def _strip_markdown_fence(self, text: str) -> str:
        if text.startswith("```"):
            lines = text.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            return "\n".join(lines).strip()
        return text

    def _build_event_extraction_prompt(self, articles: Sequence[NewsArticle]) -> str:
        article_payload = [
            {
                "article_id": article.article_id,
                "ticker": article.ticker,
                "title": article.title,
                "summary": article.summary,
                "source": article.source,
                "published_at": article.published_at.isoformat(),
            }
            for article in articles
        ]

        return (
            "You are extracting business events for ThetaLens, an investment research "
            "assistant. Return JSON only. Do not include markdown.\n\n"
            "Task: group related company news into meaningful business events.\n"
            "Financial safety: do not provide investment advice, recommendations, "
            "price targets, or predictions.\n\n"
            "Output schema:\n"
            "{\n"
            '  "events": [\n'
            "    {\n"
            '      "event_id": "stable-event-id",\n'
            '      "ticker": "NVDA",\n'
            '      "name": "Short event name",\n'
            '      "description": "One sentence explaining the event",\n'
            '      "article_ids": ["article-id"],\n'
            '      "first_seen": "2026-01-01T00:00:00+00:00",\n'
            '      "last_seen": "2026-01-02T00:00:00+00:00"\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            f"Articles JSON:\n{json.dumps(article_payload, indent=2)}"
        )

    def _build_narrative_prompt(
        self,
        market_snapshot: MarketSnapshot,
        price_history: Sequence[PriceBar],
        articles: Sequence[NewsArticle],
        events: Sequence[BusinessEvent],
        impact_scores: Sequence[EventImpactScore],
        sentiment_results: Sequence[SentimentResult],
    ) -> str:
        payload = {
            "market_snapshot": market_snapshot.model_dump(mode="json"),
            "price_history": [bar.model_dump(mode="json") for bar in price_history],
            "articles": [article.model_dump(mode="json") for article in articles],
            "events": [event.model_dump(mode="json") for event in events],
            "impact_scores": [score.model_dump(mode="json") for score in impact_scores],
            "sentiment_results": [
                sentiment.model_dump(mode="json") for sentiment in sentiment_results
            ],
        }

        return (
            "You are generating a research narrative for ThetaLens, an AI-powered "
            "investment research assistant. Return JSON only. Do not include markdown.\n\n"
            "Use the provided structured data. Separate facts from interpretation. "
            "Be concise and explain uncertainty.\n\n"
            "Financial safety rules:\n"
            "- Do not provide buy, sell, or hold recommendations.\n"
            "- Do not predict stock prices.\n"
            "- Do not provide price targets.\n"
            "- Do not guarantee outcomes.\n"
            "- Frame all output as research context.\n\n"
            "Output schema:\n"
            "{\n"
            '  "company_story": "What happened to the company",\n'
            '  "market_story": "How the market reacted",\n'
            '  "investor_story": "Why investors may want to research it",\n'
            '  "risk_story": "What could invalidate or weaken the thesis",\n'
            '  "opportunity_context": "Research context only, not advice",\n'
            '  "disclaimer": "ThetaLens provides research assistance, not financial advice."\n'
            "}\n\n"
            f"Input JSON:\n{json.dumps(payload, indent=2)}"
        )



def main():
    from thetalens.infrastructure.ai.gemini_provider import GeminiProvider
    from thetalens.infrastructure.config import load_settings

    settings = load_settings()

    provider = GeminiProvider(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
    )

    ticker = "INFQ"

    prompt = f"""
    You are ThetaLens, an investment research assistant.

    Ticker: {ticker}

    Explain what kind of research questions ThetaLens should answer for this ticker.
    Do not provide buy/sell recommendations.
    Do not predict stock prices.
    Keep it concise.
    """

    response = provider.generate_text(prompt)

    print(response)

