from datetime import date
from typing import Sequence

from thetalens.domain.models import MarketSnapshot, PriceBar
from thetalens.ports.market_data_provider import MarketDataProvider


class MarketDataEngine:
    def __init__(self, provider: MarketDataProvider) -> None:
        self._provider = provider

    def get_stock_profile(self, ticker: str) -> MarketSnapshot:
        return self._provider.get_stock_profile(ticker)

    def get_price_history(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> list[PriceBar]:
        return list(self._provider.get_price_history(ticker, start_date, end_date))

