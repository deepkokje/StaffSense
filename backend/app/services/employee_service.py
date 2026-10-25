from app.dependencies import Clock
from app.models import Employee
from app.money import FxRate, Money
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeInput
from app.services.errors import (
    DuplicateEmail,
    EmployeeNotFound,
    HasDirectReports,
    InvalidManager,
    MissingFxRate,
    UnsupportedChange,
)
from app.services.management_chain import detect_management_cycle
from app.services.salary_history import (
    SalaryChange,
    build_salary_change,
    describe_salary_change,
)


def get_employee(repository: EmployeeRepository, employee_id: int) -> Employee:
    employee = repository.get(employee_id)
    if employee is None:
        raise EmployeeNotFound("employee not found")
    return employee


def _validate(
    repository: EmployeeRepository, data: EmployeeInput, employee_id: int | None,
) -> int:
    existing = repository.get_by_email(data.email)
    if existing is not None and existing.id != employee_id:
        raise DuplicateEmail("email is already used by another employee")
    if data.manager_id is not None:
        if repository.get(data.manager_id) is None:
            raise InvalidManager("manager must reference an existing employee")
        if detect_management_cycle(
            employee_id,
            data.manager_id,
            repository.get_manager_id,
        ):
            raise InvalidManager("manager assignment would create a management cycle")
    rate = repository.fx_rates().get(data.currency)
    if rate is None:
        raise MissingFxRate(f"missing FX rate for {data.currency}")
    return Money(data.salary_minor, data.currency).to_usd(FxRate(rate)).amount_minor


def create_employee(repository: EmployeeRepository, data: EmployeeInput) -> Employee:
    with repository.transaction():
        salary_usd_minor = _validate(repository, data, None)
        employee = Employee(
            **data.model_dump(), salary_usd_minor=salary_usd_minor, last_raise_date=None,
        )
        repository.add(employee)
    return employee


def update_employee(
    repository: EmployeeRepository, employee_id: int, data: EmployeeInput, clock: Clock,
) -> Employee:
    with repository.transaction():
        employee = get_employee(repository, employee_id)
        if data.currency != employee.currency:
            raise UnsupportedChange("changing currency is not supported")
        salary_usd_minor = _validate(repository, data, employee_id)
        change = None
        if employee.salary_minor != data.salary_minor:
            change = build_salary_change(
                employee.salary_minor, data.salary_minor, employee.currency, clock(),
            )
        for field, value in data.model_dump().items():
            setattr(employee, field, value)
        employee.salary_usd_minor = salary_usd_minor
        if change is not None:
            if change.change_minor > 0:
                employee.last_raise_date = change.changed_at.date()
            repository.salary_history.add(employee_id, change)
    return employee


def list_salary_history(
    repository: EmployeeRepository, employee_id: int,
) -> list[SalaryChange]:
    get_employee(repository, employee_id)
    return [
        describe_salary_change(
            row.old_salary_minor, row.new_salary_minor, row.currency, row.changed_at,
        )
        for row in repository.salary_history.list_for_employee(employee_id)
    ]


def delete_employee(repository: EmployeeRepository, employee_id: int) -> None:
    with repository.transaction():
        employee = get_employee(repository, employee_id)
        if repository.has_direct_reports(employee_id):
            raise HasDirectReports("employee has direct reports; reassign them first")
        repository.delete_salary_history_for(employee_id)
        repository.delete(employee)
