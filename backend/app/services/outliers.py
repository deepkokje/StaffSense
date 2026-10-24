from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from app.services.attention_rows import AttentionSalaryRow
from app.services.band_compliance import PERMILLE_SCALE
from app.services.peer_groups import (
    MIN_PEER_GROUP_SIZE,
    group_by_peer_group,
    validate_peer_currency,
)
from app.services.statistics import median, round_half_even_div

OUTLIER_THRESHOLD_PERMILLE = 200


class OutlierDirection(str, Enum):
    ABOVE = "above"
    BELOW = "below"


def deviation_permille(salary_minor: int, group_median_minor: int) -> int:
    return round_half_even_div(
        (salary_minor - group_median_minor) * PERMILLE_SCALE,
        group_median_minor,
    )


@dataclass(frozen=True)
class Outlier:
    employee_id: int
    name: str
    title: str
    level: int
    country: str
    currency: str
    salary_minor: int
    group_median_minor: int
    group_headcount: int
    deviation_permille: int
    direction: OutlierDirection


def find_outliers(rows: Iterable[AttentionSalaryRow]) -> list[Outlier]:
    outliers: list[Outlier] = []
    for group in group_by_peer_group(rows).values():
        if len(group) < MIN_PEER_GROUP_SIZE:
            continue
        validate_peer_currency(group)
        group_median = median(sorted(row.salary_minor for row in group))
        for row in group:
            deviation = deviation_permille(row.salary_minor, group_median)
            if abs(deviation) <= OUTLIER_THRESHOLD_PERMILLE:
                continue
            outliers.append(
                Outlier(
                    row.employee_id,
                    row.name,
                    row.title,
                    row.level,
                    row.country,
                    row.currency,
                    row.salary_minor,
                    group_median,
                    len(group),
                    deviation,
                    OutlierDirection.ABOVE if deviation > 0 else OutlierDirection.BELOW,
                )
            )
    return sorted(outliers, key=lambda row: (-abs(row.deviation_permille), row.employee_id))
