from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from thetalens.domain.models import MarketSnapshot, ResearchRequest


def test_research_request_normalizes_ticker() -> None:
    request = ResearchRequest(
        ticker="nvda",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 6, 1),
    )

    assert request.ticker == "NVDA"


def test_research_request_rejects_invalid_date_range() -> None:
    with pytest.raises(ValidationError):
        ResearchRequest(
            ticker="NVDA",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 1, 1),
        )


def test_market_snapshot_requires_non_negative_price() -> None:
    with pytest.raises(ValidationError):
        MarketSnapshot(
            ticker="NVDA",
            current_price=-1,
            source="test",
            fetched_at=datetime.now(timezone.utc),
        )

