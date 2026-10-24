import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import make_employee


@pytest.fixture
def benchmark_client(api_client: TestClient, session: Session) -> TestClient:
    session.add_all(
        [
            make_employee(email=f"benchmark.{index}@example.com", title="Benchmark Role")
            for index in range(5)
        ]
    )
    session.commit()
    return api_client


def test_benchmarks_return_expected_shape_and_integer_stats(benchmark_client: TestClient) -> None:
    response = benchmark_client.get("/insights/benchmarks", params={"title": "Benchmark Role"})
    assert response.status_code == 200
    item = response.json()["items"][0]
    assert item["key"] == {"title": "Benchmark Role", "level": 3, "country": "US"}
    assert item["headcount"] == 5
    assert item["currency"] == "USD"
    assert item["insufficient_data"] is False
    assert set(item["stats"]) == {"min", "p25", "median", "p75", "max"}
    assert all(type(value) is int for value in item["stats"].values())
    assert type(item["key"]["level"]) is int
    assert type(item["headcount"]) is int


def test_filters_narrow_benchmark_results(benchmark_client: TestClient) -> None:
    result = benchmark_client.get(
        "/insights/benchmarks",
        params=[("country", "US"), ("title", "Benchmark Role"), ("level", "3")],
    ).json()
    assert len(result["items"]) == 1
    assert benchmark_client.get(
        "/insights/benchmarks",
        params={"country": "GB"},
    ).json() == {"items": []}


def test_include_insufficient_false_hides_small_groups(benchmark_client: TestClient) -> None:
    all_items = benchmark_client.get("/insights/benchmarks").json()["items"]
    sufficient = benchmark_client.get(
        "/insights/benchmarks",
        params={"include_insufficient": "false"},
    ).json()["items"]
    assert any(item["insufficient_data"] and item["stats"] is None for item in all_items)
    assert sufficient
    assert all(not item["insufficient_data"] for item in sufficient)


@pytest.mark.parametrize("level", [0, 7])
def test_invalid_benchmark_level_returns_422(api_client: TestClient, level: int) -> None:
    assert api_client.get("/insights/benchmarks", params={"level": level}).status_code == 422
