from thetalens.infrastructure.ai.gemini_provider import GeminiProvider
from thetalens.infrastructure.config import load_settings


def main() -> None:
    settings = load_settings()
    provider = GeminiProvider(
        api_key=settings.gemini_api_key,
        model=settings.gemini_model,
    )

    ticker = "INFQ"
    response = provider.generate_text(
        f"""
You are ThetaLens, an investment research assistant.

Ticker: {ticker}

Explain what research questions ThetaLens should answer for this ticker.
Do not provide buy/sell recommendations.
Do not predict stock prices.
Keep it concise.
"""
    )

    print(response)


if __name__ == "__main__":
    main()
