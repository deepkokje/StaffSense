from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from app.services.attention_rows import AttentionSalaryRow
from app.services.peer_groups import PeerGroupKey
from app.services.statistics import round_half_even_div

PERMILLE_SCALE = 1_000


class BandValues(Protocol):
    @property
    def currency(self) -> str: ...

    @property
    def min_minor(self) -> int: ...

    @property
    def mid_minor(self) -> int: ...

    @property
    def max_minor(self) -> int: ...


class BandStatus(str, Enum):
    BELOW_MIN = "below_min"
    WITHIN_BAND = "within_band"
    ABOVE_MAX = "above_max"


def compa_ratio_permille(salary_minor: int, band_mid_minor: int) -> int:
    return round_half_even_div(salary_minor * PERMILLE_SCALE, band_mid_minor)


def classify(salary_minor: int, band_min_minor: int, band_max_minor: int) -> BandStatus:
    if salary_minor < band_min_minor:
        return BandStatus.BELOW_MIN
    if salary_minor > band_max_minor:
        return BandStatus.ABOVE_MAX
    return BandStatus.WITHIN_BAND


@dataclass(frozen=True)
class FlaggedEmployee:
    employee_id: int
    name: str
    department: str
    title: str
    level: int
    country: str
    currency: str
    salary_minor: int
    band_min_minor: int
    band_mid_minor: int
    band_max_minor: int
    compa_ratio_permille: int
    status: BandStatus
    gap_to_band_minor: int


@dataclass(frozen=True)
class BandSummary:
    below_min: int
    within_band: int
    above_max: int
    no_band: int


@dataclass(frozen=True)
class BandReport:
    summary: BandSummary
    flagged: list[FlaggedEmployee]


def evaluate_bands(
    rows: Iterable[AttentionSalaryRow],
    bands_by_key: Mapping[PeerGroupKey, BandValues],
) -> BandReport:
    counts = dict.fromkeys(BandStatus, 0)
    no_band = 0
    flagged: list[FlaggedEmployee] = []
    for row in rows:
        band = bands_by_key.get(PeerGroupKey(row.title, row.level, row.country))
        if band is None:
            no_band += 1
            continue
        if band.currency != row.currency:
            raise ValueError(f"Band currency does not match employee {row.employee_id} currency.")
        status = classify(row.salary_minor, band.min_minor, band.max_minor)
        counts[status] += 1
        if status == BandStatus.WITHIN_BAND:
            continue
        gap = max(band.min_minor - row.salary_minor, row.salary_minor - band.max_minor)
        flagged.append(
            FlaggedEmployee(
                row.employee_id,
                row.name,
                row.department,
                row.title,
                row.level,
                row.country,
                row.currency,
                row.salary_minor,
                band.min_minor,
                band.mid_minor,
                band.max_minor,
                compa_ratio_permille(row.salary_minor, band.mid_minor),
                status,
                gap,
            )
        )
    flagged.sort(key=lambda employee: (-employee.gap_to_band_minor, employee.employee_id))
    return BandReport(
        BandSummary(
            counts[BandStatus.BELOW_MIN],
            counts[BandStatus.WITHIN_BAND],
            counts[BandStatus.ABOVE_MAX],
            no_band,
        ),
        flagged,
    )
