# AGENTS.md

## Project Mission

ThetaLens is an AI-powered investment research copilot for retail investors. Its purpose is to transform market data, news, sentiment, earnings information, and options context into explainable investment intelligence.

ThetaLens should help users answer:

- What happened to a company?
- Why did the stock move?
- Which events mattered most?
- What risks exist today?
- What investment opportunities may be worth researching?
- What information from the last 6-12 months is still relevant?

ThetaLens must not predict stock prices, produce price targets, or provide buy/sell recommendations. All generated output must be framed as research assistance, not financial advice.

## Design Principles

- Follow clean architecture.
- Keep domain and application logic independent from external vendors.
- Depend on ports/interfaces, not concrete SDKs.
- Use Pydantic models at module boundaries.
- Keep AI output structured, validated, and explainable.
- Prefer small focused modules over large mixed-responsibility files.
- Preserve traceability from final narratives back to source data, events, sentiment, and market movement.
- Treat Gemini, market data vendors, news APIs, vector databases, and MCP as replaceable infrastructure adapters.
- Do not hard-code API keys, credentials, model names, or vendor-specific assumptions in business logic.

## Current Focus

Prioritize these engines first:

- Market Data Engine
- News Engine
- News Impact Engine
- Sentiment Engine
- Investment Narrative Engine

Future phases should remain supported by architecture, but should not drive premature implementation complexity:

- Earnings RAG
- Options Intelligence
- Agents
- MCP Server

## Technology Stack

Current baseline:

- Python 3.12
- `google-genai` for Gemini access
- Pydantic for data contracts
- pytest for tests

Planned or optional technologies:

- Yahoo Finance and Finnhub for market data
- Finnhub and NewsAPI for news
- FinBERT or LLM-based classification for sentiment
- ChromaDB or another vector store for earnings RAG
- FastAPI or CLI for presentation
- MCP server adapter for external tool access

## Folder Ownership

Use the folder structure defined in `ARCHITECTURE.md`.

### `thetalens/domain/`

Owns core models, enums, and domain errors.

Rules:

- No network calls.
- No SDK imports.
- No environment variable reads.
- No prompt text.
- No persistence logic.

### `thetalens/application/`

Owns use cases and service orchestration.

Rules:

- Coordinate engines and ports.
- Accept and return Pydantic models.
- Do not import concrete infrastructure adapters directly unless wiring in a composition root.
- Do not contain provider-specific response parsing.

### `thetalens/ports/`

Owns interfaces between application logic and external systems.

Rules:

- Define abstract provider contracts.
- Keep method names stable and domain-oriented.
- Return domain models, not raw API payloads.

### `thetalens/infrastructure/`

Owns concrete integrations.

Rules:

- SDK imports belong here.
- API key loading belongs in config or provider construction.
- Map raw provider responses into domain models before returning them.
- Handle retries, rate limits, pagination, and provider errors here.

### `thetalens/presentation/`

Owns user-facing entry points.

Rules:

- CLI, API, notebook helpers, and future MCP adapter live here.
- Presentation code should call application use cases.
- Keep formatting separate from research logic.

### `thetalens/rag/`

Owns future earnings transcript RAG workflows.

Rules:

- Keep chunking, embedding, retrieval, and answer generation modular.
- Use vector store and embedding provider interfaces.
- Do not bypass application use cases for final research reports.

### `thetalens/options/`

Owns future options intelligence.

Rules:

- Keep options calculations separate from narrative generation.
- Explain risk/reward, break-even, max loss, max gain, and assignment risk.
- Avoid trade recommendations.

### `thetalens/agents/`

Owns future autonomous or scheduled research agents.

Rules:

- Agents call application use cases.
- Agents should emit structured observations.
- Agents must be auditable.
- Avoid hidden side effects.

### `tests/`

Owns unit and integration tests.

Rules:

- Unit tests should mock ports.
- Integration tests may use real providers only when explicitly marked and configured.
- Never require live API keys for normal unit tests.

## Coding Standards

- Use Python type hints for all public functions and methods.
- Prefer `list[T]`, `dict[K, V]`, and `str | None` style typing.
- Keep functions small and purpose-driven.
- Use dependency injection for providers and engines.
- Avoid global mutable state.
- Avoid direct `print()` in library code; use logging.
- Keep scripts or CLI entry points thin.
- Use clear exceptions rather than returning ambiguous `None` for failures.
- Keep comments concise and useful.
- Use ASCII text unless a file already requires non-ASCII characters.

## Naming Conventions

Files:

- Use lowercase snake case: `market_data_engine.py`.
- Provider implementations should end with `_provider.py`.
- Use cases should use verb phrases: `generate_research_report.py`.

Classes:

- Pydantic models use nouns: `ResearchRequest`, `MarketSnapshot`.
- Engines end with `Engine`: `NewsImpactEngine`.
- Interfaces end with `Provider`, `Repository`, or `Store`: `AIProvider`, `VectorStore`.
- Errors end with `Error`: `ProviderRateLimitError`.

Functions and methods:

- Use snake case.
- Prefer domain verbs: `get_company_news`, `analyze_sentiment`, `score_event_impact`.
- Avoid vague names such as `process`, `run`, or `handle` unless context is obvious.

Constants:

- Use uppercase snake case: `DEFAULT_LOOKBACK_DAYS`.

## Pydantic Usage Rules

- Use Pydantic models for all cross-module data contracts.
- Validate user inputs with request models.
- Validate AI-generated structured output before using it.
- Keep provider raw payloads out of application logic.
- Use enums for constrained values such as sentiment labels.
- Use field constraints for scores, dates, tickers, and percentages.
- Prefer explicit optional fields over loosely typed dictionaries.
- Use `model_dump()` when serializing models.
- Do not pass unvalidated LLM JSON directly into downstream engines.

## AI Prompt Management Rules

- Store reusable prompts as templates, not inline strings scattered through code.
- Keep prompts close to the AI use case or in a dedicated prompt module.
- Version prompts when output contracts change.
- Prompts must specify:
  - Task
  - Input schema
  - Output schema
  - Financial safety constraints
  - Requirement to avoid recommendations and price predictions
- AI responses that drive business logic must be parsed into Pydantic models.
- Keep deterministic settings for classification and extraction tasks where possible.
- Narrative generation may use more creative settings, but must still follow safety rules.
- Do not include API keys, tokens, or secrets in prompts.
- Do not let prompts bypass the AI provider abstraction layer.

## Logging Requirements

- Use Python `logging`, not `print()`, in application and infrastructure code.
- Log important workflow milestones:
  - request received
  - provider called
  - provider response normalized
  - event extraction completed
  - sentiment scoring completed
  - narrative generated
- Include ticker, provider name, request id, and time horizon when useful.
- Never log API keys, tokens, full credentials, or sensitive user data.
- Log provider failures with enough context to debug without exposing secrets.
- Use structured logging-friendly messages.

Example:

```python
logger.info(
    "Fetched company news",
    extra={
        "ticker": ticker,
        "provider": "finnhub",
        "article_count": len(articles),
    },
)
```

## Error Handling Standards

- Define domain and provider errors in dedicated modules.
- Convert provider-specific exceptions into project-level errors.
- Do not expose raw SDK exceptions to application use cases.
- Include provider name and operation in infrastructure errors.
- Use retries for transient provider failures when appropriate.
- Treat rate limits as explicit errors.
- Validate external data before returning it from infrastructure adapters.
- Prefer fail-fast validation for malformed user input.

Suggested error categories:

- `ThetaLensError`
- `ValidationError`
- `ProviderError`
- `ProviderAuthError`
- `ProviderRateLimitError`
- `ProviderTimeoutError`
- `AIOutputValidationError`
- `DataUnavailableError`

## Testing Requirements

- Add tests for every new domain model, engine, and use case.
- Unit tests should not call live APIs.
- Mock ports instead of mocking internal implementation details.
- Test provider adapters separately from application use cases.
- Test AI parsing with fixed sample responses.
- Test financial safety requirements for narrative output.
- Add regression tests for any bug fix.
- Keep tests deterministic.

Minimum coverage expectations by area:

- Domain models: validation and serialization tests.
- Application services: orchestration and edge cases.
- Provider adapters: response mapping and error conversion.
- AI provider layer: prompt construction and structured output parsing.
- Presentation layer: basic request/response behavior.

## AI Provider Rules

- Application code must use `AIProvider`, not `google-genai` directly.
- Gemini-specific code belongs in `thetalens/infrastructure/ai/gemini_provider.py`.
- Model choice should be configurable.
- Provider methods should return validated domain models or strings for pure narrative output.
- Event extraction, sentiment classification, and structured narrative generation should use schemas.
- The current sample script `test_gemini.py` is only a connectivity test and should not become application architecture.

## Financial Safety Rules

All agents and code must preserve these rules:

- Do not provide buy/sell/hold recommendations.
- Do not predict stock prices.
- Do not guarantee outcomes.
- Do not present options strategies as advice.
- Use language such as "research context", "risk factor", "possible interpretation", and "investors may want to examine".
- Include disclaimers in final user-facing research reports.
- Separate facts, model-generated interpretation, and uncertainty.

## Future MCP Compatibility Requirements

ThetaLens should be designed so MCP tools can wrap application use cases without refactoring core logic.

Rules:

- MCP server code belongs in `thetalens/presentation/mcp_server.py` or a dedicated presentation package.
- MCP tools must call application use cases, not providers directly.
- MCP tool inputs and outputs must use Pydantic models.
- MCP responses should be deterministic, structured, and serializable.
- Do not embed vendor-specific SDK calls in MCP tool definitions.
- Each MCP tool should map to a stable capability:
  - `market_data_tool`
  - `news_impact_tool`
  - `sentiment_tool`
  - `earnings_rag_tool`
  - `options_tool`
- MCP tools must preserve financial safety rules.

## Development Workflow For Codex

When working on this repository:

1. Read `README.md`, `ARCHITECTURE.md`, and this file before making structural changes.
2. Inspect existing files before editing.
3. Keep changes scoped to the user's request.
4. Prefer creating domain models and ports before infrastructure.
5. Add or update tests when behavior changes.
6. Do not commit secrets, `.env`, `.venv`, caches, or generated artifacts.
7. Run focused tests or at least syntax checks before reporting completion.
8. Mention any tests that could not be run.

## Repository Hygiene

- Keep `.gitignore` updated for generated files and secrets.
- Never commit API keys or tokens.
- Keep README product-focused.
- Keep ARCHITECTURE technical and structural.
- Keep AGENTS operational and development-focused.
- Avoid large unrelated refactors.
- Prefer incremental, reviewable changes.
