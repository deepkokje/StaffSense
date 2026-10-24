import random
from time import perf_counter_ns

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Base
from app.repositories.employee_repository import EmployeeRepository
from app.seeding import (
    FX_RATES,
    apply_planted_patterns,
    build_salary_bands,
    generate_employees,
    generate_salary_history,
)
from app.seeding.loader import load_seed_data
from app.services.employee_query import EmployeeFilters, SortDirection, SortField, list_employees

SEED = 42
EMPLOYEE_COUNT = 10_000
BENCHMARK_PAGE_SIZE = 25
LARGE_PAGE_NUMBER = 100
MILLISECONDS_PER_SECOND = 1_000_000


def _benchmark_call(
    repository: EmployeeRepository,
    label: str,
    filters: EmployeeFilters,
    page: int = 1,
) -> None:
    start_time = perf_counter_ns()
    list_employees(repository, filters, page=page, page_size=BENCHMARK_PAGE_SIZE)
    elapsed_milliseconds = (
        perf_counter_ns() - start_time
    ) // MILLISECONDS_PER_SECOND
    print(f"{label}: {elapsed_milliseconds} ms")


def main() -> None:
    rng = random.Random(SEED)
    bands = build_salary_bands()
    employees = generate_employees(EMPLOYEE_COUNT, rng, SEED, bands)
    apply_planted_patterns(employees, bands, rng)
    history = generate_salary_history(employees)

    engine = create_engine("sqlite://")
    try:
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            load_seed_data(session, FX_RATES, bands, employees, history)
            repository = EmployeeRepository(session)
            _benchmark_call(repository, "no filters", EmployeeFilters())
            _benchmark_call(
                repository,
                "country filter",
                EmployeeFilters(country=("IN",)),
            )
            _benchmark_call(
                repository,
                "salary range and sort",
                EmployeeFilters(
                    min_salary_usd_minor=5_000_000,
                    max_salary_usd_minor=15_000_000,
                    sort_by=SortField.SALARY_USD_MINOR,
                    sort_dir=SortDirection.DESC,
                ),
            )
            _benchmark_call(
                repository,
                "search",
                EmployeeFilters(q="alex"),
            )
            _benchmark_call(
                repository,
                f"page {LARGE_PAGE_NUMBER}",
                EmployeeFilters(),
                page=LARGE_PAGE_NUMBER,
            )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
