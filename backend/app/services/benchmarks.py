from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import Protocol

from app.services.peer_groups import PeerGroupKey, PeerGroupRow, group_by_peer_group
from app.services.statistics import (
    LOWER_QUARTILE_PERCENT,
    UPPER_QUARTILE_PERCENT,
    median,
    percentile,
)

MIN_PEER_GROUP_SIZE = 5


class BenchmarkSalaryRow(PeerGroupRow, Protocol):
    @property
    def currency(self) -> str: ...

    @property
    def salary_minor(self) -> int: ...


class BenchmarkRepository(Protocol):
    def active_salary_rows(
        self,
        countries: Sequence[str] | None = None,
        titles: Sequence[str] | None = None,
        levels: Sequence[int] | None = None,
    ) -> Sequence[BenchmarkSalaryRow]: ...


@dataclass(frozen=True)
class BenchmarkStats:
    min: int
    p25: int
    median: int
    p75: int
    max: int


@dataclass(frozen=True)
class PeerGroupBenchmark:
    key: PeerGroupKey
    currency: str
    headcount: int
    stats: BenchmarkStats | None
    insufficient_data: bool


def compute_benchmarks(rows: Iterable[BenchmarkSalaryRow]) -> list[PeerGroupBenchmark]:
    benchmarks: list[PeerGroupBenchmark] = []
    groups = group_by_peer_group(rows)
    for key in sorted(groups, key=lambda key: (key.country, key.title, key.level)):
        group = groups[key]
        currencies = {row.currency for row in group}
        if len(currencies) != 1:
            raise ValueError(f"Peer group {key} must have exactly one currency.")
        insufficient_data = len(group) < MIN_PEER_GROUP_SIZE
        stats = None
        if not insufficient_data:
            salaries = sorted(row.salary_minor for row in group)
            stats = BenchmarkStats(
                min=salaries[0],
                p25=percentile(salaries, LOWER_QUARTILE_PERCENT),
                median=median(salaries),
                p75=percentile(salaries, UPPER_QUARTILE_PERCENT),
                max=salaries[-1],
            )
        benchmarks.append(
            PeerGroupBenchmark(
                key=key,
                currency=group[0].currency,
                headcount=len(group),
                stats=stats,
                insufficient_data=insufficient_data,
            )
        )
    return benchmarks


def list_benchmarks(
    repository: BenchmarkRepository,
    countries: Sequence[str] | None = None,
    titles: Sequence[str] | None = None,
    levels: Sequence[int] | None = None,
    include_insufficient: bool = True,
) -> list[PeerGroupBenchmark]:
    benchmarks = compute_benchmarks(repository.active_salary_rows(countries, titles, levels))
    return [
        benchmark
        for benchmark in benchmarks
        if include_insufficient or not benchmark.insufficient_data
    ]
