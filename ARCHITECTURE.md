# ThetaLens Architecture

## Purpose

ThetaLens is a modular AI-powered investment research platform. It helps retail investors understand company events, market reactions, sentiment, risk, and investment narratives without providing buy/sell recommendations or financial advice.

The platform is designed around clean architecture so business logic remains independent from data vendors, AI providers, storage systems, UI frameworks, and future MCP integrations.

## High-Level Architecture

```text
User Interface / API / Future MCP Server
                |
                v
        Application Use Cases
                |
                v
       Investment Intelligence Layer
                |
    +-----------+-----------+-----------+-----------+
    |           |           |           |           |
 Market     News      News Impact   Sentiment   Narrative
 Engine     Engine       Engine      Engine      Engine
    |           |           |           |           |
    +-----------+-----------+-----------+-----------+
                |
                v
          Domain Models
                |
                v
   Ports / Interfaces / Provider Abstractions
                |
    +-----------+-----------+-----------+-----------+
    |           |           |           |           |
 Market     News        AI/LLM     Embeddings   Storage
 Providers  Providers   Providers  Providers    Providers
```

## Clean Architecture Layers

### 1. Domain Layer

Contains the core business concepts and rules.

Responsibilities:

- Define Pydantic models for tickers, prices, news, events, sentiment, impact scores, and narratives.
- Represent investment research concepts without depending on external APIs.
- Keep financial safety constraints close to the domain, such as avoiding price predictions or recommendations.

### 2. Application Layer

Coordinates use cases.

Responsibilities:

- Orchestrate engines for a ticker research request.
- Combine market data, news, sentiment, impact scoring, and narrative generation.
- Enforce input validation and output contracts.
- Expose use cases such as `GenerateCompanyResearchReport`.

### 3. Interface / Ports Layer

Defines contracts between application logic and external systems.

Responsibilities:

- Define interfaces for market data providers, news providers, AI providers, embedding providers, vector stores, and persistence.
- Allow implementations to be swapped without changing business logic.

### 4. Infrastructure Layer

Contains concrete integrations.

Responsibilities:

- Implement Yahoo Finance, Finnhub, NewsAPI, Gemini, FinBERT, ChromaDB, and future MCP adapters.
- Handle API keys, rate limits, retries, pagination, and provider-specific response mapping.

### 5. Presentation Layer

Contains user-facing entry points.

Responsibilities:

- CLI, notebook, web app, REST API, or future MCP server.
- Convert user requests into application use case calls.
- Render structured results into readable research output.

## Folder Structure

```text
thetalens/
  __init__.py

  domain/
    __init__.py
    models.py
    enums.py
    errors.py

  application/
    __init__.py
    use_cases/
      generate_research_report.py
      analyze_news_impact.py
      generate_investment_narrative.py
    services/
      market_data_engine.py
      news_engine.py
      news_impact_engine.py
      sentiment_engine.py
      investment_narrative_engine.py

  ports/
    __init__.py
    market_data_provider.py
    news_provider.py
    ai_provider.py
    sentiment_provider.py
    embedding_provider.py
    vector_store.py
    repository.py

  infrastructure/
    __init__.py
    config.py
    market_data/
      yahoo_finance_provider.py
      finnhub_market_provider.py
    news/
      finnhub_news_provider.py
      newsapi_provider.py
    ai/
      gemini_provider.py
      provider_factory.py
    sentiment/
      finbert_provider.py
    storage/
      sqlite_repository.py
      chroma_vector_store.py

  presentation/
    __init__.py
    cli.py
    api.py
    mcp_server.py

  agents/
    __init__.py
    news_agent.py
    risk_agent.py
    earnings_agent.py
    options_agent.py

  rag/
    __init__.py
    transcript_loader.py
    chunker.py
    earnings_rag_engine.py

  options/
    __init__.py
    options_intelligence_engine.py
    strategy_explainer.py

tests/
  unit/
  integration/

README.md
ARCHITECTURE.md
requirements.txt
```

## Current Module Responsibilities

### Market Data Engine

Purpose:

- Collect and normalize market data for a ticker.

Responsibilities:

- Fetch stock profile, current price, historical prices, valuation metrics, and optional options chain data.
- Normalize provider-specific market responses into domain models.
- Provide market reaction context for news impact scoring and narrative generation.

Primary interfaces:

- `MarketDataProvider`
- `MarketDataEngine`

### News Engine

Purpose:

- Collect historical company news.

Responsibilities:

- Fetch company news from providers such as Finnhub and NewsAPI.
- Normalize articles into a consistent `NewsArticle` model.
- Deduplicate obvious duplicates.
- Provide article collections to sentiment and news impact engines.

Primary interfaces:

- `NewsProvider`
- `NewsEngine`

### News Impact Engine

Purpose:

- Identify which events mattered most.

Responsibilities:

- Extract business events from article headlines and summaries.
- Cluster similar articles into event groups.
- Score event impact using sentiment, price movement, volume, source count, and recency.
- Produce event-level explanations.

Primary interfaces:

- `NewsImpactEngine`
- `AIProvider`
- `MarketDataEngine`
- `SentimentEngine`

### Sentiment Engine

Purpose:

- Analyze financial sentiment from news, events, and earnings excerpts.

Responsibilities:

- Score individual articles and event clusters.
- Return positive, neutral, and negative distributions.
- Support provider implementations such as FinBERT or LLM-based classification.

Primary interfaces:

- `SentimentProvider`
- `SentimentEngine`

### Investment Narrative Engine

Purpose:

- Convert structured research signals into an explainable investment narrative.

Responsibilities:

- Generate company story, market story, investor story, risk story, and opportunity context.
- Use structured inputs from market, news, impact, and sentiment engines.
- Avoid financial advice, price targets, or direct buy/sell recommendations.
- Cite the key events and signals that shaped the narrative.

Primary interfaces:

- `InvestmentNarrativeEngine`
- `AIProvider`

## Data Flow

```text
Ticker Input
    |
    v
Validate ResearchRequest
    |
    v
Market Data Engine -----> MarketSnapshot / PriceHistory
    |
    v
News Engine ------------> NewsArticle[]
    |
    v
Sentiment Engine -------> SentimentResult[]
    |
    v
News Impact Engine -----> BusinessEvent[] / EventImpactScore[]
    |
    v
Investment Narrative Engine
    |
    v
ResearchReport
```

Detailed flow:

1. User submits a ticker and time horizon.
2. Application use case validates the request.
3. Market Data Engine fetches profile, price, valuation, and historical movement.
4. News Engine fetches and normalizes company news.
5. Sentiment Engine scores article sentiment.
6. News Impact Engine clusters news into business events and scores impact.
7. Investment Narrative Engine generates explainable stories from structured inputs.
8. Presentation layer returns the final `ResearchReport`.

## Interfaces Between Modules

```python
from abc import ABC, abstractmethod
from datetime import date
from typing import Sequence

from thetalens.domain.models import (
    BusinessEvent,
    MarketSnapshot,
    NewsArticle,
    PriceBar,
    SentimentResult,
)


class MarketDataProvider(ABC):
    @abstractmethod
    def get_stock_profile(self, ticker: str) -> MarketSnapshot:
        pass

    @abstractmethod
    def get_price_history(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Sequence[PriceBar]:
        pass


class NewsProvider(ABC):
    @abstractmethod
    def get_company_news(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Sequence[NewsArticle]:
        pass


class SentimentProvider(ABC):
    @abstractmethod
    def analyze(self, texts: Sequence[str]) -> Sequence[SentimentResult]:
        pass


class AIProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass

    @abstractmethod
    def extract_events(self, articles: Sequence[NewsArticle]) -> Sequence[BusinessEvent]:
        pass
```

## Pydantic Models

```python
from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SentimentLabel(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class ResearchRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=12)
    start_date: date
    end_date: date
    include_options: bool = False
    include_earnings: bool = False


class MarketSnapshot(BaseModel):
    ticker: str
    company_name: Optional[str] = None
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    source: str
    fetched_at: datetime


class PriceBar(BaseModel):
    ticker: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class NewsArticle(BaseModel):
    ticker: str
    title: str
    summary: Optional[str] = None
    source: str
    url: Optional[str] = None
    published_at: datetime


class SentimentResult(BaseModel):
    text_id: str
    label: SentimentLabel
    positive_score: float = Field(..., ge=0, le=1)
    neutral_score: float = Field(..., ge=0, le=1)
    negative_score: float = Field(..., ge=0, le=1)


class BusinessEvent(BaseModel):
    event_id: str
    ticker: str
    name: str
    description: str
    article_urls: list[str] = Field(default_factory=list)
    first_seen: datetime
    last_seen: datetime


class EventImpactScore(BaseModel):
    event_id: str
    impact_score: float = Field(..., ge=0, le=10)
    sentiment_label: SentimentLabel
    price_reaction_pct: Optional[float] = None
    volume_reaction_pct: Optional[float] = None
    recency_score: Optional[float] = Field(default=None, ge=0, le=1)
    explanation: str


class InvestmentNarrative(BaseModel):
    company_story: str
    market_story: str
    investor_story: str
    risk_story: str
    opportunity_context: str
    disclaimer: str = "ThetaLens provides research assistance, not financial advice."


class ResearchReport(BaseModel):
    request: ResearchRequest
    market_snapshot: MarketSnapshot
    key_events: list[BusinessEvent]
    event_impact_scores: list[EventImpactScore]
    sentiment_summary: dict[SentimentLabel, int]
    narrative: InvestmentNarrative
    generated_at: datetime
```

## AI Provider Abstraction Layer

The AI provider layer prevents the application from depending directly on Gemini or any single model vendor.

Responsibilities:

- Provide a common interface for text generation, event extraction, summarization, classification, and narrative generation.
- Allow Gemini today and future providers later.
- Centralize prompt templates, model configuration, temperature, token limits, retries, and safety settings.
- Keep API keys in environment variables or configuration objects, never in source code.

Recommended structure:

```text
ports/ai_provider.py
infrastructure/ai/gemini_provider.py
infrastructure/ai/provider_factory.py
```

Example:

```python
class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model

    def generate_text(self, prompt: str) -> str:
        ...

    def extract_events(self, articles: Sequence[NewsArticle]) -> Sequence[BusinessEvent]:
        ...
```

## Future Support

### Earnings RAG

Future earnings intelligence should use a retrieval-augmented generation pipeline.

Components:

- `TranscriptLoader`
- `TranscriptChunker`
- `EmbeddingProvider`
- `VectorStore`
- `EarningsRagEngine`

Flow:

```text
Earnings Transcript
    -> Chunking
    -> Embeddings
    -> Vector Store
    -> Retrieval
    -> LLM Answer
```

Target questions:

- What risks did management discuss?
- What changed from last quarter?
- What did management say about AI demand?

### Options Intelligence

Future options intelligence should be isolated from the current research engines.

Responsibilities:

- Analyze covered calls, cash secured puts, LEAPS, bullish structures, and risk/reward profiles.
- Explain max gain, max loss, break-even, assignment risk, and scenario outcomes.
- Avoid recommending trades; present educational research context only.

### Agents

Agents should be introduced after core engines are stable.

Planned agents:

- `NewsAgent`: monitors company news and momentum.
- `RiskAgent`: monitors emerging risks.
- `EarningsAgent`: monitors earnings updates and transcript changes.
- `OptionsAgent`: monitors options activity and strategy candidates.

Agent rules:

- Agents call application use cases, not infrastructure providers directly.
- Agents emit structured observations.
- Agents should be auditable and deterministic where possible.

### MCP Server

ThetaLens can later expose its capabilities as an MCP server.

Planned MCP tools:

- `market_data_tool`
- `news_impact_tool`
- `sentiment_tool`
- `earnings_rag_tool`
- `options_tool`

MCP design rule:

- MCP tools should wrap application use cases and return Pydantic-validated outputs.
- MCP should be treated as a presentation adapter, not as a replacement for application logic.

## Initial Implementation Order

1. Create domain models and ports.
2. Implement Gemini AI provider behind `AIProvider`.
3. Implement Market Data Engine with one provider.
4. Implement News Engine with one provider.
5. Implement Sentiment Engine.
6. Implement News Impact Engine.
7. Implement Investment Narrative Engine.
8. Add CLI or API entry point.
9. Add tests around domain models, use cases, and provider adapters.

## Design Principles

- Keep business logic independent from external vendors.
- Use Pydantic models for every boundary between modules.
- Prefer provider interfaces over direct SDK calls in application code.
- Keep AI outputs structured and validated.
- Preserve explainability: every narrative should trace back to events, sentiment, and market data.
- Avoid financial advice, predictions, and direct recommendations.
- Build current engines first while leaving clear extension points for RAG, agents, options, and MCP.
