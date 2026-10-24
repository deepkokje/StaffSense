import argparse
from random import Random
from time import perf_counter

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.config import settings
from app.seeding import (
    FX_RATES,
    apply_planted_patterns,
    build_salary_bands,
    generate_employees,
    generate_salary_history,
)
from app.seeding.loader import load_seed_data

DEFAULT_SEED = 42
DEFAULT_EMPLOYEE_COUNT = 10_000


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load deterministic StaffSense sample data.")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--count", type=int, default=DEFAULT_EMPLOYEE_COUNT)
    parser.add_argument("--db-url", default=settings.database_url)
    parser.add_argument("--reset", action="store_true")
    return parser.parse_args()


def main() -> None:
    arguments = _parse_arguments()
    if arguments.count < 0:
        raise ValueError("Employee count cannot be negative")

    start_time = perf_counter()
    rng = Random(arguments.seed)
    bands = build_salary_bands()
    employees = generate_employees(arguments.count, rng, arguments.seed, bands)
    apply_planted_patterns(employees, bands, rng)
    history = generate_salary_history(employees)
    engine = create_engine(arguments.db_url)
    try:
        with Session(engine) as session:
            load_seed_data(session, FX_RATES, bands, employees, history, reset=arguments.reset)
            row_counts = {
                "fx_rates": len(FX_RATES),
                "salary_bands": len(bands),
                "employees": len(employees),
                "salary_history": len(history),
            }
        elapsed_seconds = perf_counter() - start_time
        summary = ", ".join(f"{table}={count}" for table, count in row_counts.items())
        print(f"Seeded {summary} in {elapsed_seconds:.2f}s")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
