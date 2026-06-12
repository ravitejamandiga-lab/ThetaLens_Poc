from abc import ABC, abstractmethod
from datetime import date
from typing import Sequence

from thetalens.domain.models import MarketSnapshot, PriceBar


class MarketDataProvider(ABC):
    @abstractmethod
    def get_stock_profile(self, ticker: str) -> MarketSnapshot:
        """Return current profile and valuation data for a ticker."""

    @abstractmethod
    def get_price_history(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Sequence[PriceBar]:
        """Return historical price bars for a ticker."""

