# ThetaLens

## AI-Powered Investment Research Copilot

### Vision

ThetaLens is an AI-powered investment research platform designed to help retail investors understand:

* What happened to a company?
* Why did the stock move?
* Which events mattered most?
* What risks exist today?
* What investment opportunities may exist?
* What information is still relevant from the last 6–12 months?

The goal is **not** to predict stock prices or provide financial advice.

The goal is to transform information into explainable investment intelligence.

---

# Problem Statement

Retail investors face information overload:

* News articles
* Earnings calls
* Social media posts
* Analyst reports
* Market data
* Options activity

Most platforms show information.

Very few platforms explain:

* What actually mattered
* Why it mattered
* Whether it still matters

ThetaLens aims to solve this problem.

---

# Product Vision

When a user enters a stock ticker:

```text
NVDA
```

ThetaLens should answer:

### Company Story

What happened during the last 6 months?

### Market Story

How did the market react?

### Investor Story

Why should investors care?

### Risk Story

What could invalidate the current thesis?

---

# High-Level Architecture

```text
                  User
                    │
                    ▼
           Research Interface
                    │
                    ▼
          Investment Intelligence Layer
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
 Market Engine  News Engine  Earnings Engine
      │             │             │
      ▼             ▼             ▼
 Price Data   Event Extraction   RAG Search
      │             │             │
      └──────┬──────┴──────┬──────┘
             ▼             ▼
       Sentiment Engine  Risk Engine
             │             │
             └──────┬──────┘
                    ▼
         Investment Thesis Engine
                    │
                    ▼
           Explainability Layer
```

---

# Phase 1 – Foundation Layer

## Market Data Engine

### Purpose

Collect stock-related market information.

### Data Sources

* Yahoo Finance
* Finnhub

### Responsibilities

* Current stock price
* Historical prices
* Market capitalization
* P/E ratio
* Valuation metrics
* Options chain

### Example APIs

```python
get_stock_profile()

get_price_history()

get_options_chain()
```

---

## News Engine

### Purpose

Collect historical company news.

### Data Sources

* Finnhub
* NewsAPI

### Responsibilities

* News collection
* Historical news retrieval
* News normalization

### Example APIs

```python
get_company_news()
```

---

# Phase 2 – News Intelligence Engine

This is the core differentiator of ThetaLens.

---

## Event Extraction Engine

### Goal

Convert hundreds of headlines into meaningful business events.

Example:

#### Headlines

```text
NVIDIA launches Blackwell platform
NVIDIA Blackwell demand accelerates
Blackwell orders exceed expectations
```

#### Event

```text
Blackwell Launch
```

---

## Event Clustering Engine

### Goal

Group similar headlines into a single event.

Responsibilities:

* Deduplication
* Clustering
* Event grouping

---

## Event Impact Scoring

### Goal

Measure how much an event affected the stock.

Possible inputs:

* Event sentiment
* Price movement
* Trading volume
* Recency

Output:

```json
{
  "event": "Blackwell Launch",
  "impact_score": 9.4
}
```

---

## News Momentum Score

Provide a simple score:

```text
0 – 100
```

Examples:

```text
82 = Strong Positive Momentum

55 = Neutral

25 = Negative Momentum
```

---

# Phase 3 – Sentiment Intelligence

---

## FinBERT Sentiment Engine

Analyze:

* News headlines
* Articles
* Earnings excerpts

Output:

```json
{
  "positive": 72,
  "neutral": 18,
  "negative": 10
}
```

---

## AI Narrative Generator

Use Gemini to generate:

### Company Story

Example:

```text
The last six months have been driven primarily by AI infrastructure demand and strong enterprise spending.
```

---

## Risk Narrative Generator

Example:

```text
The biggest risks include slowing enterprise demand and increasing competition.
```

---

# Phase 4 – Investment Research Layer

---

## Company Story Engine

Answer:

```text
What happened?
```

---

## Market Story Engine

Answer:

```text
How did the market react?
```

---

## Investor Story Engine

Answer:

```text
Why should investors care?
```

---

## Risk Engine

Answer:

```text
What could go wrong?
```

---

## Opportunity Engine

Answer:

```text
Is the current valuation interesting?
```

Important:

ThetaLens provides research assistance, not buy/sell recommendations.

---

# Phase 5 – Earnings Intelligence

---

## Earnings Transcript Collector

Collect:

* Earnings call transcripts
* Prepared remarks
* Q&A sessions

---

## Embeddings Engine

Convert transcript chunks into embeddings.

Responsibilities:

* Chunking
* Embedding generation

---

## Vector Database

Recommended:

* ChromaDB

Store:

* Earnings transcripts
* Historical company knowledge

---

## Earnings RAG Engine

Example Questions:

```text
What risks did management discuss?

What changed from last quarter?

What did management say about AI demand?
```

---

# Phase 6 – Options Intelligence

This is a unique ThetaLens feature.

---

## Options Analyzer

Analyze:

* Cash Secured Puts
* Covered Calls
* LEAPS
* Bullish structures
* Risk-reward profiles

---

## Strategy Explanation Engine

Example:

```text
Bullish Trade Idea

Sell Cash Secured Put

Risk:
Assignment at $13

Potential Upside:
...
```

---

## Risk Visualization

Show:

* Max loss
* Max gain
* Break-even

---

# Phase 7 – Watchlist Intelligence

Users can track:

```text
NVDA
AMD
PLTR
NOK
```

ThetaLens monitors:

* News momentum
* Sentiment changes
* Earnings updates
* Risk changes

---

# Phase 8 – AI Agents

---

## News Agent

Monitors company news.

---

## Risk Agent

Monitors emerging risks.

---

## Earnings Agent

Monitors earnings updates.

---

## Options Agent

Identifies interesting option opportunities.

---

# Phase 9 – MCP Architecture

ThetaLens eventually becomes an MCP Server.

Exposed tools:

```text
market_data_tool

news_impact_tool

sentiment_tool

earnings_rag_tool

options_tool
```

Benefits:

* ChatGPT integration
* Claude integration
* Gemini integration
* Cursor integration
* Codex integration

---

# Phase 10 – User Experience Layer

---

## Streamlit Dashboard

### Company Research

Search stock ticker.

---

### Earnings Assistant

Ask questions about earnings calls.

---

### Watchlist Dashboard

Track monitored stocks.

---

### Options Research

View option opportunities.

---

# Technology Stack

## IDE

* VS Code

## AI Development

* Codex

## LLM

* Gemini Flash
* OpenAI (future)

## NLP

* FinBERT
* HuggingFace Transformers

## Market Data

* Yahoo Finance
* Finnhub

## News Data

* Finnhub
* NewsAPI

## Vector Database

* ChromaDB

## Backend

* FastAPI

## Frontend

* Streamlit

## MCP

* MCP Python SDK

---

# Development Priority

## MVP

1. Market Data Engine
2. News Engine
3. Event Extraction Engine
4. Event Clustering
5. Event Impact Scoring
6. News Momentum Score
7. AI Narrative Generator

---

## V2

8. Earnings Intelligence
9. RAG
10. Watchlist Intelligence

---

## V3

11. Options Intelligence

---

## V4

12. AI Agents

---

## V5

13. MCP Server

---

# Long-Term Goal

Build a production-grade Investment Research Copilot that combines:

* Financial data
* News intelligence
* Sentiment analysis
* Earnings research
* Options intelligence
* AI explainability

while simultaneously developing expertise in:

* LLM Engineering
* Prompt Engineering
* Structured Outputs
* RAG
* Embeddings
* Agents
* MCP
* AI System Design
* Financial NLP
