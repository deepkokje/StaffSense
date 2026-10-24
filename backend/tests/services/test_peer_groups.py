from app.repositories.insight_repository import SalaryRow
from app.services.peer_groups import PeerGroupKey, group_by_peer_group


def test_grouping_uses_title_level_and_country() -> None:
    rows = [
        SalaryRow(1, "Engineer", 2, "US", "USD", 10, "One", "Engineering"),
        SalaryRow(2, "Engineer", 2, "US", "USD", 20, "Two", "Engineering"),
        SalaryRow(3, "Engineer", 2, "JP", "JPY", 30, "Three", "Engineering"),
        SalaryRow(4, "Engineer", 3, "US", "USD", 40, "Four", "Engineering"),
        SalaryRow(5, "Designer", 2, "US", "USD", 50, "Five", "Product"),
    ]
    groups = group_by_peer_group(rows)
    assert len(groups) == 4
    assert groups[PeerGroupKey("Engineer", 2, "US")] == rows[:2]
    assert groups[PeerGroupKey("Engineer", 2, "JP")] == [rows[2]]
