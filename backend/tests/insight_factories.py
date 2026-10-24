from app.repositories.insight_repository import BandRow, SalaryRow


def salary_row(employee_id: int = 1, salary_minor: int = 1_000, **overrides: object) -> SalaryRow:
    return SalaryRow(
        employee_id=employee_id,
        title="Engineer",
        level=3,
        country="US",
        currency="USD",
        salary_minor=salary_minor,
        name=f"Employee {employee_id}",
        department="Engineering",
    )._replace(**overrides)


def band_row() -> BandRow:
    return BandRow(currency="USD", min_minor=800, mid_minor=1_000, max_minor=1_200)
