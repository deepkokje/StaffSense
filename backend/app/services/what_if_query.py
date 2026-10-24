from collections.abc import Mapping, Sequence
from typing import Protocol

from app.services.attention import AttentionRepository
from app.services.what_if import (
    BandMinCostReport,
    RaiseCostReport,
    cost_of_raise,
    cost_to_reach_band_min,
)


class WhatIfRepository(AttentionRepository, Protocol):
    def fx_rates(self) -> Mapping[str, int]: ...


def bring_to_band_min(
    repository: WhatIfRepository,
    *,
    countries: Sequence[str] | None = None,
    departments: Sequence[str] | None = None,
    titles: Sequence[str] | None = None,
    levels: Sequence[int] | None = None,
) -> BandMinCostReport:
    rows = repository.active_salary_rows(countries, titles, levels, departments)
    return cost_to_reach_band_min(rows, repository.salary_bands(), repository.fx_rates())


def department_raise(
    repository: WhatIfRepository,
    *,
    department: str,
    raise_bp: int,
    country: str | None = None,
) -> RaiseCostReport:
    rows = repository.active_salary_rows(
        countries=[country] if country is not None else None,
        departments=[department],
    )
    return cost_of_raise(rows, raise_bp, repository.fx_rates())
