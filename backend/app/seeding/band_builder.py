from typing import TypedDict

from app.money import CURRENCY_EXPONENTS, FX_RATE_SCALE, USD_EXPONENT
from app.seeding.reference_data import (
    COUNTRY_COST_INDEX_PERMILLE,
    COUNTRY_CURRENCIES,
    FX_RATES,
    LEVEL_MULTIPLIERS_PERMILLE,
    LEVELS,
    TITLE_BASE_USD_MINOR,
    TITLES,
)

BAND_MIN_PERMILLE = 800
BAND_MAX_PERMILLE = 1_200
PERMILLE_SCALE = 1_000


class SalaryBandData(TypedDict):
    title: str
    level: int
    country: str
    currency: str
    min_minor: int
    mid_minor: int
    max_minor: int


def _round_ratio_half_even(numerator: int, denominator: int) -> int:
    quotient, remainder = divmod(numerator, denominator)
    doubled_remainder = remainder * 2
    if doubled_remainder > denominator or (
        doubled_remainder == denominator and quotient % 2 == 1
    ):
        return quotient + 1
    return quotient


def _usd_minor_to_local_minor(usd_minor: int, currency: str, usd_rate_e6: int) -> int:
    local_exponent = CURRENCY_EXPONENTS[currency]
    numerator = usd_minor * FX_RATE_SCALE * (10**local_exponent)
    denominator = usd_rate_e6 * (10**USD_EXPONENT)
    return _round_ratio_half_even(numerator, denominator)


def build_salary_bands() -> list[SalaryBandData]:
    bands: list[SalaryBandData] = []
    for title in TITLES:
        for level in LEVELS:
            for country, currency in COUNTRY_CURRENCIES.items():
                usd_mid_minor = (
                    TITLE_BASE_USD_MINOR[title]
                    * LEVEL_MULTIPLIERS_PERMILLE[level]
                    * COUNTRY_COST_INDEX_PERMILLE[country]
                    // (PERMILLE_SCALE * PERMILLE_SCALE)
                )
                mid_minor = _usd_minor_to_local_minor(
                    usd_mid_minor,
                    currency,
                    FX_RATES[currency],
                )
                bands.append(
                    {
                        "title": title,
                        "level": level,
                        "country": country,
                        "currency": currency,
                        "min_minor": mid_minor * BAND_MIN_PERMILLE // PERMILLE_SCALE,
                        "mid_minor": mid_minor,
                        "max_minor": mid_minor * BAND_MAX_PERMILLE // PERMILLE_SCALE,
                    }
                )
    return bands
