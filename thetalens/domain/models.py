from datetime import date, datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from thetalens.domain.enums import SentimentLabel


class ThetaLensModel(BaseModel):
    """Base model for project-wide Pydantic settings."""

    model_config = ConfigDict(str_strip_whitespace=True)


class ResearchRequest(ThetaLensModel):
    ticker: str = Field(..., min_length=1, max_length=12)
    start_date: date
    end_date: date
    include_options: bool = False
    include_earnings: bool = False

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.upper()

    @model_validator(mode="after")
    def validate_date_range(self) -> "ResearchRequest":
        if self.start_date > self.end_date:
            raise ValueError("start_date must be before or equal to end_date")
        return self


class MarketSnapshot(ThetaLensModel):
    ticker: str = Field(..., min_length=1, max_length=12)
    company_name: str | None = None
    current_price: float | None = Field(default=None, ge=0)
    market_cap: float | None = Field(default=None, ge=0)
    pe_ratio: float | None = None
    source: str
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.upper()


class PriceBar(ThetaLensModel):
    ticker: str = Field(..., min_length=1, max_length=12)
    date: date
    open: float = Field(..., ge=0)
    high: float = Field(..., ge=0)
    low: float = Field(..., ge=0)
    close: float = Field(..., ge=0)
    volume: int = Field(..., ge=0)

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.upper()


class NewsArticle(ThetaLensModel):
    article_id: str
    ticker: str = Field(..., min_length=1, max_length=12)
    title: str = Field(..., min_length=1)
    summary: str | None = None
    source: str
    url: str | None = None
    published_at: datetime

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.upper()


class SentimentResult(ThetaLensModel):
    text_id: str
    label: SentimentLabel
    positive_score: float = Field(..., ge=0, le=1)
    neutral_score: float = Field(..., ge=0, le=1)
    negative_score: float = Field(..., ge=0, le=1)


class BusinessEvent(ThetaLensModel):
    event_id: str
    ticker: str = Field(..., min_length=1, max_length=12)
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    article_ids: list[str] = Field(default_factory=list)
    first_seen: datetime
    last_seen: datetime

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        return value.upper()


class EventImpactScore(ThetaLensModel):
    event_id: str
    impact_score: float = Field(..., ge=0, le=10)
    sentiment_label: SentimentLabel
    price_reaction_pct: float | None = None
    volume_reaction_pct: float | None = None
    recency_score: float | None = Field(default=None, ge=0, le=1)
    explanation: str


class InvestmentNarrative(ThetaLensModel):
    company_story: str
    market_story: str
    investor_story: str
    risk_story: str
    opportunity_context: str
    disclaimer: str = "ThetaLens provides research assistance, not financial advice."


class ResearchReport(ThetaLensModel):
    request: ResearchRequest
    market_snapshot: MarketSnapshot
    price_history: list[PriceBar] = Field(default_factory=list)
    news_articles: list[NewsArticle] = Field(default_factory=list)
    key_events: list[BusinessEvent] = Field(default_factory=list)
    event_impact_scores: list[EventImpactScore] = Field(default_factory=list)
    sentiment_results: list[SentimentResult] = Field(default_factory=list)
    narrative: InvestmentNarrative
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

