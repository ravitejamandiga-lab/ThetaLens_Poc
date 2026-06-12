class ThetaLensError(Exception):
    """Base exception for ThetaLens errors."""


class ProviderError(ThetaLensError):
    """Base exception for external provider failures."""


class ProviderAuthError(ProviderError):
    """Raised when a provider rejects credentials."""


class ProviderRateLimitError(ProviderError):
    """Raised when a provider rate limit is reached."""


class ProviderTimeoutError(ProviderError):
    """Raised when a provider request times out."""


class AIOutputValidationError(ThetaLensError):
    """Raised when AI output cannot be validated into expected models."""


class DataUnavailableError(ThetaLensError):
    """Raised when required research data is unavailable."""

