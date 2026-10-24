from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol


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
