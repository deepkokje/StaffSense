import pytest

from app.money import (
    FxRate,
    Money,
    NegativeAmountError,
    UnsupportedCurrencyError,
)


def test_converts_inr_to_usd() -> None:
    result = Money(amount_minor=10_000, currency="INR").to_usd(FxRate(usd_rate_e6=12_000))

    assert result == Money(amount_minor=120, currency="USD")


def test_converts_jpy_without_fractional_minor_units() -> None:
    result = Money(amount_minor=1_000, currency="JPY").to_usd(FxRate(usd_rate_e6=1_500_000))

    assert result == Money(amount_minor=150_000, currency="USD")


def test_rounds_exact_half_to_even() -> None:
    result = Money(amount_minor=1, currency="USD").to_usd(FxRate(usd_rate_e6=500_000))

    assert result == Money(amount_minor=0, currency="USD")


def test_usd_at_parity_preserves_amount() -> None:
    amount = Money(amount_minor=123_456, currency="USD")

    assert amount.to_usd(FxRate(usd_rate_e6=1_000_000)) == amount


def test_rejects_negative_amount() -> None:
    with pytest.raises(NegativeAmountError):
        Money(amount_minor=-1, currency="USD")


def test_rejects_unsupported_currency() -> None:
    with pytest.raises(UnsupportedCurrencyError):
        Money(amount_minor=100, currency="CHF")
