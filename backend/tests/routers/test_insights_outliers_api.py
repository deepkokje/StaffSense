import pytest
from fastapi.testclient import TestClient

from tests.conftest import ATTENTION_TITLE

ENDPOINT = "/insights/outliers"


def test_outlier_response_has_integer_fields_and_full_peer_headcounts(
    attention_client: TestClient,
) -> None:
    response = attention_client.get(ENDPOINT, params={"title": ATTENTION_TITLE})
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"items", "total", "page", "page_size"}
    assert data["total"] == 3
    assert [row["deviation_permille"] for row in data["items"]] == [450, -300, 300]
    assert all(row["group_headcount"] == 7 for row in data["items"])
    for row in data["items"]:
        for key in (
            "employee_id",
            "level",
            "salary_minor",
            "group_median_minor",
            "group_headcount",
            "deviation_permille",
        ):
            assert type(row[key]) is int


@pytest.mark.parametrize("direction, expected", [("above", 2), ("below", 1)])
def test_outlier_direction_filter_uses_full_group_median(
    attention_client: TestClient,
    direction: str,
    expected: int,
) -> None:
    data = attention_client.get(
        ENDPOINT,
        params={
            "title": ATTENTION_TITLE,
            "country": "US",
            "level": 3,
            "direction": direction,
        },
    ).json()
    assert data["total"] == expected
    assert all(
        row["direction"] == direction and row["group_median_minor"] == 1_000
        for row in data["items"]
    )
    assert (
        attention_client.get(
            ENDPOINT,
            params={
                "title": ATTENTION_TITLE,
                "country": "GB",
            },
        ).json()["items"]
        == []
    )


def test_walking_outlier_pages_returns_every_item_once(attention_client: TestClient) -> None:
    ids = []
    for page in range(1, 5):
        data = attention_client.get(
            ENDPOINT,
            params={
                "title": ATTENTION_TITLE,
                "page": page,
                "page_size": 1,
            },
        ).json()
        assert data["total"] == 3
        if page == 4:
            assert data["items"] == []
        ids.extend(row["employee_id"] for row in data["items"])
    assert len(ids) == len(set(ids)) == 3


@pytest.mark.parametrize(
    "params",
    [
        {"direction": "invalid"},
        {"level": 0},
        {"page": 0},
        {"page_size": 101},
    ],
)
def test_invalid_outlier_parameters_return_422(
    api_client: TestClient, params: dict[str, object]
) -> None:
    assert api_client.get(ENDPOINT, params=params).status_code == 422
