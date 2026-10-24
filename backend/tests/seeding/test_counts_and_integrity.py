from app.money import FxRate, Money
from app.seeding import FX_RATES
from app.seeding.reference_data import COUNTRY_CURRENCIES
from tests.seeding.conftest import SeedDataset


def test_generated_employees_have_valid_counts_and_references(
    seeded_dataset: SeedDataset,
) -> None:
    employees = seeded_dataset.employees
    band_keys = {
        (band["title"], band["level"], band["country"]) for band in seeded_dataset.bands
    }
    employee_ids = {employee.id for employee in employees}
    email_addresses = {employee.email for employee in employees}

    assert len(employees) == 10_000
    assert len(employee_ids) == 10_000
    assert len(email_addresses) == 10_000
    assert all(1 <= employee.level <= 6 for employee in employees)
    assert all(employee.salary_minor > 0 for employee in employees)
    assert all(
        (employee.title, employee.level, employee.country) in band_keys for employee in employees
    )
    assert all(
        employee.manager_id is None or employee.manager_id in employee_ids
        for employee in employees
    )
    assert all(
        employee.currency == COUNTRY_CURRENCIES[employee.country]
        and employee.salary_usd_minor
        == Money(employee.salary_minor, employee.currency)
        .to_usd(FxRate(FX_RATES[employee.currency]))
        .amount_minor
        for employee in employees
    )
