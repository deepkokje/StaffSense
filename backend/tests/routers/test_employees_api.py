from fastapi.testclient import TestClient


def test_default_params_return_employee_page_shape(api_client: TestClient) -> None:
    response = api_client.get("/employees")

    assert response.status_code == 200
    assert set(response.json()) == {"items", "total", "page", "page_size", "total_pages"}
    assert response.json()["page"] == 1
    assert response.json()["page_size"] == 25
    assert response.json()["total"] == 20
    assert response.json()["total_pages"] == 1


def test_page_size_above_max_returns_422(api_client: TestClient) -> None:
    assert api_client.get("/employees", params={"page_size": 101}).status_code == 422


def test_page_zero_returns_422(api_client: TestClient) -> None:
    assert api_client.get("/employees", params={"page": 0}).status_code == 422


def test_invalid_salary_range_returns_clear_422(api_client: TestClient) -> None:
    response = api_client.get(
        "/employees",
        params={"min_salary_usd_minor": 20_000, "max_salary_usd_minor": 10_000},
    )

    assert response.status_code == 422
    assert "min_salary_usd_minor must be less than or equal to max_salary_usd_minor" in str(
        response.json()
    )


def test_invalid_sort_field_returns_422(api_client: TestClient) -> None:
    assert api_client.get("/employees", params={"sort_by": "salary"}).status_code == 422


def test_invalid_sort_direction_and_enum_values_return_422(api_client: TestClient) -> None:
    for params in (
        {"sort_dir": "sideways"},
        {"status": "UNKNOWN"},
        {"gender": "UNKNOWN"},
    ):
        assert api_client.get("/employees", params=params).status_code == 422


def test_repeatable_filters_accept_multiple_values(api_client: TestClient) -> None:
    response = api_client.get(
        "/employees",
        params=[("country", "US"), ("country", "IN"), ("level", "2"), ("level", "3")],
    )

    assert response.status_code == 200
    assert response.json()["total"] == 8


def test_page_beyond_last_is_empty_with_matching_total(api_client: TestClient) -> None:
    response = api_client.get("/employees", params={"page": 5, "page_size": 5})
    result = response.json()

    assert response.status_code == 200
    assert result["items"] == []
    assert result["total"] == 20
    assert result["total_pages"] == 4


def test_pagination_walk_returns_each_employee_once(api_client: TestClient) -> None:
    employee_ids: list[int] = []
    for page_number in range(1, 8):
        response = api_client.get(
            "/employees",
            params={"page": page_number, "page_size": 3, "sort_by": "salary_usd_minor"},
        )
        employee_ids.extend(item["id"] for item in response.json()["items"])

    assert len(employee_ids) == 20
    assert len(set(employee_ids)) == 20


def test_money_fields_are_integer_minor_units(api_client: TestClient) -> None:
    employee = api_client.get("/employees").json()["items"][0]

    assert isinstance(employee["salary_minor"], int)
    assert isinstance(employee["salary_usd_minor"], int)
    assert isinstance(employee["currency"], str)


def test_openapi_documents_employee_query_parameters(api_client: TestClient) -> None:
    parameters = api_client.get("/openapi.json").json()["paths"]["/employees"]["get"]["parameters"]
    parameter_names = {parameter["name"] for parameter in parameters}

    assert {
        "page",
        "page_size",
        "q",
        "country",
        "department",
        "title",
        "level",
        "status",
        "gender",
        "min_salary_usd_minor",
        "max_salary_usd_minor",
        "sort_by",
        "sort_dir",
    } <= parameter_names
