from dataclasses import dataclass
from datetime import datetime

from app.services.statistics import round_half_even_div

BASIS_POINT_SCALE = 10_000


@dataclass(frozen=True)
class SalaryChange:
    old_salary_minor: int
    new_salary_minor: int
    currency: str
    changed_at: datetime
    change_minor: int
    change_bp: int | None


def describe_salary_change(
    old_minor: int, new_minor: int, currency: str, changed_at: datetime,
) -> SalaryChange:
    change_minor = new_minor - old_minor
    change_bp = (
        round_half_even_div(change_minor * BASIS_POINT_SCALE, old_minor)
        if old_minor
        else None
    )
    return SalaryChange(
        old_minor, new_minor, currency, changed_at, change_minor, change_bp,
    )


def build_salary_change(
    old_minor: int, new_minor: int, currency: str, changed_at: datetime,
) -> SalaryChange | None:
    if old_minor == new_minor:
        return None
    return describe_salary_change(old_minor, new_minor, currency, changed_at)
