from enum import Enum


class SentimentLabel(str, Enum):
    """Supported sentiment labels for financial text."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

