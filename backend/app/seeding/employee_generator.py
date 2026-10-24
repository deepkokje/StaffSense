import random
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from faker import Faker

from app.money import FxRate, Money
from app.seeding.band_builder import SalaryBandData
from app.seeding.reference_data import (
    COUNTRY_CURRENCIES,
    COUNTRY_HEADCOUNT_WEIGHTS,
    EMPLOYMENT_TYPE_VALUES,
    EMPLOYMENT_TYPE_WEIGHTS,
    FX_RATES,
    GENDER_VALUES,
    GENDER_WEIGHTS_BY_LEVEL,
    LEVEL_WEIGHTS,
    LEVELS,
    SEED_REFERENCE_DATE,
    STATUS_VALUES,
    STATUS_WEIGHTS,
    TITLE_DEPARTMENTS,
    TITLE_WEIGHTS,
    TITLES,
)

SALARY_FACTOR_MEAN_PERMILLE = 1_000
SALARY_FACTOR_SIGMA_PERMILLE = 70
SALARY_FACTOR_MIN_PERMILLE = 850
SALARY_FACTOR_MAX_PERMILLE = 1_150
PERMILLE_SCALE = 1_000
MAX_TENURE_DAYS = 3_652
DAYS_PER_YEAR = 365
LAST_RAISE_RECENT_DAYS = 365
LAST_RAISE_PROBABILITY_PERMILLE = 900


@dataclass
class EmployeeSeed:
    id: int
    name: str
    email: str
    title: str
    level: int
    department: str
    country: str
    currency: str
    salary_minor: int
    salary_usd_minor: int
    gender: str
    manager_id: int | None
    employment_type: str
    hire_date: date
    last_raise_date: date | None
    status: str


@dataclass(frozen=True)
class SalaryHistorySeed:
    employee_id: int
    old_salary_minor: int
    new_salary_minor: int
    currency: str
    changed_at: datetime


def _clean_name_part(name_part: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name_part.lower())


def _sample_date(rng: random.Random, first_day: date, last_day: date) -> date:
    date_span = (last_day - first_day).days
    return first_day + timedelta(days=rng.randint(0, date_span))


def _to_usd_minor(amount_minor: int, currency: str) -> int:
    return Money(amount_minor, currency).to_usd(FxRate(FX_RATES[currency])).amount_minor


def generate_employees(
    count: int,
    rng: random.Random,
    seed: int,
    bands: list[SalaryBandData],
) -> list[EmployeeSeed]:
    faker = Faker()
    faker.seed_instance(seed)
    bands_by_key = {
        (band["title"], band["level"], band["country"]): band for band in bands
    }

    employees: list[EmployeeSeed] = []
    for employee_id in range(1, count + 1):
        country = rng.choices(
            list(COUNTRY_CURRENCIES),
            weights=[COUNTRY_HEADCOUNT_WEIGHTS[item] for item in COUNTRY_CURRENCIES],
            k=1,
        )[0]
        title = rng.choices(
            TITLES,
            weights=[TITLE_WEIGHTS[item] for item in TITLES],
            k=1,
        )[0]
        level = rng.choices(
            LEVELS,
            weights=[LEVEL_WEIGHTS[item] for item in LEVELS],
            k=1,
        )[0]
        band = bands_by_key[(title, level, country)]
        sampled_salary_factor = int(
            round(rng.gauss(SALARY_FACTOR_MEAN_PERMILLE, SALARY_FACTOR_SIGMA_PERMILLE))
        )
        salary_factor = max(
            SALARY_FACTOR_MIN_PERMILLE,
            min(SALARY_FACTOR_MAX_PERMILLE, sampled_salary_factor),
        )
        salary_minor = band["mid_minor"] * salary_factor // PERMILLE_SCALE
        first_name = faker.first_name()
        last_name = faker.last_name()
        email = (
            f"{_clean_name_part(first_name)}.{_clean_name_part(last_name)}."
            f"{employee_id}@acme.example"
        )
        hire_date = _sample_date(
            rng,
            SEED_REFERENCE_DATE - timedelta(days=MAX_TENURE_DAYS),
            SEED_REFERENCE_DATE,
        )
        last_raise_date = None
        tenure_days = (SEED_REFERENCE_DATE - hire_date).days
        if (
            tenure_days >= LAST_RAISE_RECENT_DAYS
            and rng.randrange(PERMILLE_SCALE) < LAST_RAISE_PROBABILITY_PERMILLE
        ):
            raise_start = max(
                hire_date,
                SEED_REFERENCE_DATE - timedelta(days=LAST_RAISE_RECENT_DAYS),
            )
            last_raise_date = _sample_date(rng, raise_start, SEED_REFERENCE_DATE)

        employees.append(
            EmployeeSeed(
                id=employee_id,
                name=f"{first_name} {last_name}",
                email=email,
                title=title,
                level=level,
                department=TITLE_DEPARTMENTS[title],
                country=country,
                currency=COUNTRY_CURRENCIES[country],
                salary_minor=salary_minor,
                salary_usd_minor=_to_usd_minor(salary_minor, COUNTRY_CURRENCIES[country]),
                gender=rng.choices(
                    GENDER_VALUES,
                    weights=GENDER_WEIGHTS_BY_LEVEL[level],
                    k=1,
                )[0],
                manager_id=None,
                employment_type=rng.choices(
                    EMPLOYMENT_TYPE_VALUES,
                    weights=EMPLOYMENT_TYPE_WEIGHTS,
                    k=1,
                )[0],
                hire_date=hire_date,
                last_raise_date=last_raise_date,
                status=rng.choices(STATUS_VALUES, weights=STATUS_WEIGHTS, k=1)[0],
            )
        )

    candidates_by_group: dict[tuple[str, str, int], list[EmployeeSeed]] = {}
    for employee in employees:
        candidates_by_group.setdefault(
            (employee.department, employee.country, employee.level),
            [],
        ).append(employee)

    for employee in employees:
        if employee.level == max(LEVELS):
            continue
        manager_candidates: list[EmployeeSeed] = []
        for manager_level in range(employee.level + 1, min(employee.level + 2, max(LEVELS)) + 1):
            manager_candidates.extend(
                candidates_by_group.get(
                    (employee.department, employee.country, manager_level),
                    [],
                )
            )
        if manager_candidates:
            employee.manager_id = rng.choice(manager_candidates).id

    return employees


def generate_salary_history(employees: list[EmployeeSeed]) -> list[SalaryHistorySeed]:
    history: list[SalaryHistorySeed] = []
    for employee in employees:
        if employee.last_raise_date is None:
            continue
        history.append(
            SalaryHistorySeed(
                employee_id=employee.id,
                old_salary_minor=employee.salary_minor * 920 // PERMILLE_SCALE,
                new_salary_minor=employee.salary_minor,
                currency=employee.currency,
                changed_at=datetime.combine(employee.last_raise_date, datetime.min.time()),
            )
        )
    return history
