import pytest
from fastapi.testclient import TestClient

from tests.conftest import ATTENTION_TITLE

ENDPOINT = "/insights/bands"


def test_band_response_has_integer_summary_and_formatted_row_fields(
    attention_client: TestClient,
) -> None:
    response = attention_client.get(ENDPOINT, params={"title": ATTENTION_TITLE})
    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"summary", "items", "total", "page", "page_size"}
    assert data["summary"] == {"below_min": 1, "within_band": 4, "above_max": 2, "no_band": 1}
    assert data["total"] == 3
    row = data["items"][0]
    assert row["salary_minor"] == 1_450
    assert row["gap_to_band_minor"] == 250
    assert row["status"] == "above_max"
    assert row["name"] == "Attention 6"
    assert all(type(value) is int for value in data["summary"].values())
    for key in (
        "employee_id",
        "level",
        "salary_minor",
        "band_min_minor",
        "band_mid_minor",
        "band_max_minor",
        "compa_ratio_permille",
        "gap_to_band_minor",
    ):
        assert type(row[key]) is int


def test_band_summary_ignores_status_and_paging(attention_client: TestClient) -> None:
    data = attention_client.get(
        ENDPOINT,
        params={
            "title": ATTENTION_TITLE,
            "status": "below_min",
            "page": 2,
            "page_size": 1,
        },
    ).json()
    assert data["summary"] == {"below_min": 1, "within_band": 4, "above_max": 2, "no_band": 1}
    assert data["total"] == 1
    assert data["items"] == []


def test_band_filters_combine_and_status_limits_flagged_only(attention_client: TestClient) -> None:
    data = attention_client.get(
        ENDPOINT,
        params={
            "title": ATTENTION_TITLE,
            "country": "US",
            "department": "Data",
            "level": 3,
            "status": "above_max",
        },
    ).json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Attention 7"
    assert data["summary"] == {"below_min": 0, "within_band": 0, "above_max": 1, "no_band": 0}


def test_walking_band_pages_returns_each_flag_once(attention_client: TestClient) -> None:
    ids = []
    for page in range(1, 4):
        data = attention_client.get(
            ENDPOINT,
            params={
                "title": ATTENTION_TITLE,
                "page": page,
                "page_size": 1,
            },
        ).json()
        assert data["total"] == 3
        ids.extend(item["employee_id"] for item in data["items"])
    assert len(ids) == len(set(ids)) == 3


@pytest.mark.parametrize(
    "params",
    [
        {"status": "within_band"},
        {"status": "invalid"},
        {"level": 0},
        {"level": 7},
        {"page": 0},
        {"page_size": 101},
    ],
)
def test_invalid_band_parameters_return_422(
    api_client: TestClient, params: dict[str, object]
) -> None:
    assert api_client.get(ENDPOINT, params=params).status_code == 422
