from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal

CURRENCY_EXPONENTS: dict[str, int] = {
    "USD": 2,
    "EUR": 2,
    "GBP": 2,
    "INR": 2,
    "JPY": 0,
    "CAD": 2,
    "AUD": 2,
    "SGD": 2,
}
FX_RATE_SCALE = 1_000_000
USD_CURRENCY = "USD"
USD_EXPONENT = CURRENCY_EXPONENTS[USD_CURRENCY]
ROUNDING_QUANTUM = Decimal("1")


class UnsupportedCurrencyError(ValueError):
    pass


class NegativeAmountError(ValueError):
    pass


class InvalidMoneyAmountError(ValueError):
    pass


class InvalidFxRateError(ValueError):
    pass


@dataclass(frozen=True)
class FxRate:
    usd_rate_e6: int

    def __post_init__(self) -> None:
        if not isinstance(self.usd_rate_e6, int) or isinstance(self.usd_rate_e6, bool):
            raise InvalidFxRateError("FX rate must be an integer")
        if self.usd_rate_e6 <= 0:
            raise InvalidFxRateError("FX rate must be greater than zero")


@dataclass(frozen=True)
class Money:
    amount_minor: int
    currency: str

    def __post_init__(self) -> None:
        if not isinstance(self.amount_minor, int) or isinstance(self.amount_minor, bool):
            raise InvalidMoneyAmountError("Money amount must be an integer")
        if self.amount_minor < 0:
            raise NegativeAmountError("Money amount cannot be negative")
        if self.currency not in CURRENCY_EXPONENTS:
            raise UnsupportedCurrencyError(f"Unsupported currency: {self.currency}")

    def to_usd(self, rate: FxRate) -> Money:
        source_exponent = CURRENCY_EXPONENTS[self.currency]
        conversion = (
            Decimal(self.amount_minor)
            * Decimal(rate.usd_rate_e6)
            * Decimal(10**USD_EXPONENT)
            / Decimal(FX_RATE_SCALE)
            / Decimal(10**source_exponent)
        )
        usd_minor = int(conversion.quantize(ROUNDING_QUANTUM, rounding=ROUND_HALF_EVEN))
        return Money(amount_minor=usd_minor, currency=USD_CURRENCY)
