from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

MIN_PEER_GROUP_SIZE = 5


class CurrencyRow(Protocol):
    @property
    def currency(self) -> str: ...


def validate_peer_currency(rows: Iterable[CurrencyRow]) -> None:
    if len({row.currency for row in rows}) != 1:
        raise ValueError("A peer group must have exactly one currency.")


class PeerGroupRow(Protocol):
    @property
    def title(self) -> str: ...

    @property
    def level(self) -> int: ...

    @property
    def country(self) -> str: ...


@dataclass(frozen=True)
class PeerGroupKey:
    title: str
    level: int
    country: str


def group_by_peer_group[T: PeerGroupRow](rows: Iterable[T]) -> dict[PeerGroupKey, list[T]]:
    groups: dict[PeerGroupKey, list[T]] = {}
    for row in rows:
        key = PeerGroupKey(row.title, row.level, row.country)
        groups.setdefault(key, []).append(row)
    return groups
