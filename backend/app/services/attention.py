from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from app.services.attention_rows import AttentionSalaryRow
from app.services.band_compliance import (
    BandSummary,
    BandValues,
    FlaggedEmployee,
    evaluate_bands,
)
from app.services.outliers import Outlier, OutlierDirection, find_outliers
from app.services.pagination import paginate
from app.services.peer_groups import PeerGroupKey


class BandStatusFilter(str, Enum):
    BELOW_MIN = "below_min"
    ABOVE_MAX = "above_max"


class AttentionRepository(Protocol):
    def active_salary_rows(
        self,
        countries: Sequence[str] | None = None,
        titles: Sequence[str] | None = None,
        levels: Sequence[int] | None = None,
        departments: Sequence[str] | None = None,
    ) -> Sequence[AttentionSalaryRow]: ...

    def salary_bands(self) -> Mapping[PeerGroupKey, BandValues]: ...


@dataclass(frozen=True)
class BandsPage:
    summary: BandSummary
    items: list[FlaggedEmployee]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True)
class OutliersPage:
    items: list[Outlier]
    total: int
    page: int
    page_size: int


def list_band_compliance(
    repository: AttentionRepository,
    *,
    countries: Sequence[str] | None = None,
    departments: Sequence[str] | None = None,
    titles: Sequence[str] | None = None,
    levels: Sequence[int] | None = None,
    status: BandStatusFilter | None = None,
    page: int,
    page_size: int,
) -> BandsPage:
    rows = repository.active_salary_rows(countries, titles, levels, departments)
    report = evaluate_bands(rows, repository.salary_bands())
    flagged = [row for row in report.flagged if status is None or row.status.value == status.value]
    items, total = paginate(flagged, page, page_size)
    return BandsPage(report.summary, items, total, page, page_size)


def list_outliers(
    repository: AttentionRepository,
    *,
    countries: Sequence[str] | None = None,
    titles: Sequence[str] | None = None,
    levels: Sequence[int] | None = None,
    direction: OutlierDirection | None = None,
    page: int,
    page_size: int,
) -> OutliersPage:
    rows = repository.active_salary_rows(countries, titles, levels)
    flagged = [
        row for row in find_outliers(rows) if direction is None or row.direction == direction
    ]
    items, total = paginate(flagged, page, page_size)
    return OutliersPage(items, total, page, page_size)
