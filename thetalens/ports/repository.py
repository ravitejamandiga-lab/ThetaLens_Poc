from abc import ABC, abstractmethod

from thetalens.domain.models import ResearchReport


class ResearchReportRepository(ABC):
    @abstractmethod
    def save(self, report: ResearchReport) -> None:
        """Persist a generated research report."""

