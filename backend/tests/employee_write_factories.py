from app.schemas.employee import EmployeeInput


def employee_input(**overrides: object) -> EmployeeInput:
    values: dict[str, object] = {
        "name": "New Employee",
        "email": "new@staff.example",
        "title": "Engineer",
        "department": "Engineering",
        "country": "US",
        "currency": "USD",
        "salary_minor": 10000,
        "level": 3,
        "gender": "UNDISCLOSED",
        "employment_type": "FULL_TIME",
        "status": "ACTIVE",
        "hire_date": "2020-01-01",
        "manager_id": None,
    }
    values.update(overrides)
    return EmployeeInput.model_validate(values)
