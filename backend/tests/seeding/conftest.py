import random
from dataclasses import dataclass

import pytest

from app.seeding import (
    EmployeeSeed,
    SalaryHistorySeed,
    apply_planted_patterns,
    build_salary_bands,
    generate_employees,
    generate_salary_history,
)
from app.seeding.band_builder import SalaryBandData


@dataclass
class SeedDataset:
    bands: list[SalaryBandData]
    employees: list[EmployeeSeed]
    history: list[SalaryHistorySeed]


def generate_dataset(seed: int, count: int) -> SeedDataset:
    rng = random.Random(seed)
    bands = build_salary_bands()
    employees = generate_employees(count, rng, seed, bands)
    apply_planted_patterns(employees, bands, rng)
    history = generate_salary_history(employees)
    return SeedDataset(bands, employees, history)


@pytest.fixture(scope="module")
def seeded_dataset() -> SeedDataset:
    return generate_dataset(seed=42, count=10_000)
