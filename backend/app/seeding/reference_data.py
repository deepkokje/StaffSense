from datetime import date

SEED_REFERENCE_DATE = date(2026, 10, 1)
COUNTRY_CURRENCIES: dict[str, str] = {
    "US": "USD",
    "GB": "GBP",
    "DE": "EUR",
    "IN": "INR",
    "SG": "SGD",
    "CA": "CAD",
    "AU": "AUD",
    "JP": "JPY",
}
COUNTRIES = tuple(COUNTRY_CURRENCIES)
CURRENCIES = tuple(dict.fromkeys(COUNTRY_CURRENCIES.values()))
COUNTRY_COST_INDEX_PERMILLE: dict[str, int] = {
    "US": 1_000,
    "GB": 1_050,
    "DE": 1_020,
    "IN": 450,
    "SG": 1_150,
    "CA": 1_030,
    "AU": 1_080,
    "JP": 950,
}
COUNTRY_HEADCOUNT_WEIGHTS: dict[str, int] = {
    "US": 240,
    "GB": 120,
    "DE": 110,
    "IN": 210,
    "SG": 50,
    "CA": 100,
    "AU": 90,
    "JP": 80,
}

# These exchange rates are fixed and illustrative; they are not live market data.
FX_RATES: dict[str, int] = {
    "USD": 1_000_000,
    "GBP": 1_270_000,
    "EUR": 1_080_000,
    "INR": 12_000,
    "SGD": 740_000,
    "CAD": 740_000,
    "AUD": 660_000,
    "JPY": 6_700,
}

TITLE_DEPARTMENTS: dict[str, str] = {
    "Software Engineer": "Engineering",
    "QA Engineer": "Engineering",
    "Data Analyst": "Data",
    "Data Scientist": "Data",
    "Product Manager": "Product",
    "Designer": "Product",
    "HR Specialist": "HR",
    "Recruiter": "HR",
    "Accountant": "Finance",
    "Financial Analyst": "Finance",
    "Sales Executive": "Sales",
    "Customer Support Specialist": "Support",
}
DEPARTMENTS = tuple(dict.fromkeys(TITLE_DEPARTMENTS.values()))
TITLES = tuple(TITLE_DEPARTMENTS)
LEVELS = (1, 2, 3, 4, 5, 6)
TITLE_BASE_USD_MINOR: dict[str, int] = {
    "Software Engineer": 9_000_000,
    "QA Engineer": 6_500_000,
    "Data Analyst": 6_800_000,
    "Data Scientist": 9_500_000,
    "Product Manager": 10_000_000,
    "Designer": 7_200_000,
    "HR Specialist": 5_800_000,
    "Recruiter": 5_600_000,
    "Accountant": 6_000_000,
    "Financial Analyst": 7_500_000,
    "Sales Executive": 6_300_000,
    "Customer Support Specialist": 4_800_000,
}
LEVEL_MULTIPLIERS_PERMILLE: dict[int, int] = {
    1: 700,
    2: 850,
    3: 1_000,
    4: 1_200,
    5: 1_450,
    6: 1_750,
}
TITLE_WEIGHTS: dict[str, int] = {
    "Software Engineer": 170,
    "QA Engineer": 60,
    "Data Analyst": 100,
    "Data Scientist": 75,
    "Product Manager": 85,
    "Designer": 75,
    "HR Specialist": 65,
    "Recruiter": 60,
    "Accountant": 60,
    "Financial Analyst": 75,
    "Sales Executive": 90,
    "Customer Support Specialist": 85,
}
LEVEL_WEIGHTS: dict[int, int] = {
    1: 400,
    2: 280,
    3: 160,
    4: 90,
    5: 50,
    6: 20,
}
GENDER_GAP_TITLES = ("Software Engineer", "Data Analyst", "Sales Executive")

GENDER_WEIGHTS_BY_LEVEL: dict[int, tuple[int, int, int, int]] = {
    1: (450, 520, 20, 10),
    2: (450, 520, 20, 10),
    3: (450, 520, 20, 10),
    4: (300, 660, 25, 15),
    5: (280, 680, 25, 15),
    6: (260, 700, 25, 15),
}
GENDER_VALUES = ("FEMALE", "MALE", "OTHER", "UNDISCLOSED")
STATUS_VALUES = ("ACTIVE", "ON_LEAVE", "TERMINATED")
STATUS_WEIGHTS = (930, 40, 30)
EMPLOYMENT_TYPE_VALUES = ("FULL_TIME", "PART_TIME", "CONTRACT")
EMPLOYMENT_TYPE_WEIGHTS = (900, 70, 30)
