from collections.abc import Iterator
from pathlib import Path
from random import Random
from tempfile import TemporaryDirectory
from time import perf_counter_ns

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import get_session
from app.main import app
from app.seeding import (
    FX_RATES,
    apply_planted_patterns,
    build_salary_bands,
    generate_employees,
    generate_salary_history,
)
from app.seeding.loader import load_seed_data

SEED = 42
EMPLOYEE_COUNT = 10_000
NANOSECONDS_PER_MILLISECOND = 1_000_000
TARGET_MILLISECONDS = 500
INSIGHT_PREFIX = "/insights/"
RAISE_PARAMETERS = {"department": "Engineering", "raise_bp": 500}


def main() -> None:
    rng = Random(SEED)
    bands = build_salary_bands()
    employees = generate_employees(EMPLOYEE_COUNT, rng, SEED, bands)
    apply_planted_patterns(employees, bands, rng)
    with TemporaryDirectory(prefix="staffsense-insights-") as directory:
        engine = create_engine(
            f"sqlite:///{Path(directory) / 'benchmark.db'}",
            connect_args={"check_same_thread": False},
        )

        def benchmark_session() -> Iterator[Session]:
            with Session(engine) as session:
                yield session

        previous_override = app.dependency_overrides.get(get_session)
        try:
            with Session(engine) as session:
                load_seed_data(
                    session, FX_RATES, bands, employees, generate_salary_history(employees)
                )
            app.dependency_overrides[get_session] = benchmark_session
            with TestClient(app) as client:
                paths = client.get("/openapi.json").json()["paths"]
                print(f"{EMPLOYEE_COUNT} employees; target < {TARGET_MILLISECONDS} ms per endpoint")
                for path, operations in paths.items():
                    if not path.startswith(INSIGHT_PREFIX) or "get" not in operations:
                        continue
                    params = RAISE_PARAMETERS if path.endswith("/what-if/raise") else {}
                    start = perf_counter_ns()
                    response = client.get(path, params=params)
                    elapsed = (perf_counter_ns() - start) // NANOSECONDS_PER_MILLISECOND
                    response.raise_for_status()
                    print(f"GET {path}: {elapsed} ms")
        finally:
            if previous_override is None:
                app.dependency_overrides.pop(get_session, None)
            else:
                app.dependency_overrides[get_session] = previous_override
            engine.dispose()


if __name__ == "__main__":
    main()
