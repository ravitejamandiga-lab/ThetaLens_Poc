from abc import ABC, abstractmethod
from datetime import date
from typing import Sequence

from thetalens.domain.models import NewsArticle


class NewsProvider(ABC):
    @abstractmethod
    def get_company_news(
        self,
        ticker: str,
        start_date: date,
        end_date: date,
    ) -> Sequence[NewsArticle]:
        """Return normalized company news for a ticker."""

