import pytest

from app.repositories.insight_repository import SalaryRow
from app.services.benchmarks import BenchmarkStats, compute_benchmarks


def make_rows(count: int = 5, country: str = "US") -> list[SalaryRow]:
    return [
        SalaryRow(
            index, "Engineer", 2, country, "USD", index * 10, f"Employee {index}", "Engineering"
        )
        for index in range(1, count + 1)
    ]


def test_exactly_five_people_have_stats_and_correct_headcount() -> None:
    result = compute_benchmarks(make_rows())[0]
    # Five ranks are 0,1,2,3,4: quartiles land exactly on 20,30,40.
    assert result.stats == BenchmarkStats(min=10, p25=20, median=30, p75=40, max=50)
    assert result.headcount == 5
    assert result.currency == "USD"
    assert not result.insufficient_data


def test_four_people_have_no_stats() -> None:
    result = compute_benchmarks(make_rows(4))[0]
    assert result.headcount == 4
    assert result.stats is None
    assert result.insufficient_data


def test_benchmarks_are_sorted_by_country_title_and_level() -> None:
    rows = [
        SalaryRow(1, "Engineer", 3, "US", "USD", 10, "One", "Engineering"),
        SalaryRow(2, "Engineer", 2, "US", "USD", 20, "Two", "Engineering"),
        SalaryRow(3, "Designer", 2, "US", "USD", 30, "Three", "Product"),
        SalaryRow(4, "Engineer", 2, "JP", "JPY", 40, "Four", "Engineering"),
    ]
    forward = compute_benchmarks(rows)
    assert forward == compute_benchmarks(list(reversed(rows)))
    assert [(item.key.country, item.key.title, item.key.level) for item in forward] == [
        ("JP", "Engineer", 2),
        ("US", "Designer", 2),
        ("US", "Engineer", 2),
        ("US", "Engineer", 3),
    ]


def test_empty_input_has_no_benchmarks() -> None:
    assert compute_benchmarks([]) == []


def test_mixed_currencies_in_one_peer_group_are_rejected() -> None:
    rows = make_rows()
    rows.append(SalaryRow(6, "Engineer", 2, "US", "EUR", 60, "Six", "Engineering"))
    with pytest.raises(ValueError, match="currency"):
        compute_benchmarks(rows)
