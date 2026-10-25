# Code-generation prompt log

Starting with future requests, record each prompt I provide that asks you to create or modify code in this file. Keep my prompt wording verbatim and append each prompt as a new dated entry. Do not add unrelated questions or requests.

## Prompts

### 2026-10-24

```text
You are creaton a monorepo for a salary management app. Build ONLY the bare-bones structure described below. Do not add features, models, or business logic yet.

Stack:
- Backend: Python 3.12, FastAPI, SQLAlchemy 2.x, SQLite, pytest, ruff
- Frontend: Vite, React, TypeScript, Ant Design, Vitest

Folder structure to create:
.
├── CLAUDE.md                  (leave empty for now)
├── README.md                  (short: what it is, how to run backend and frontend)
├── .gitignore                 (Python, Node, SQLite files, .env, IDE folders)
├── docs/
│   ├── REQUIREMENTS.md        (empty placeholder)
│   ├── PLAN.md                (empty placeholder)
│   ├── ARCHITECTURE.md        (empty placeholder)
│   └── AI_NOTES.md            (empty placeholder)
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            (creates the FastAPI app, includes routers)
│   │   ├── config.py          (settings read from env, with defaults)
│   │   ├── db.py              (SQLAlchemy engine and session setup only)
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── health.py      (GET /health -> {"status": "ok"})
│   │   ├── services/__init__.py       (empty, business logic goes here later)
│   │   ├── repositories/__init__.py   (empty, DB access goes here later)
│   │   ├── models/__init__.py         (empty, SQLAlchemy models go here later)
│   │   └── schemas/__init__.py        (empty, Pydantic schemas go here later)
│   ├── scripts/__init__.py    (seed script goes here later)
│   └── tests/
│       ├── __init__.py
│       └── test_health.py     (one test using FastAPI TestClient)
└── frontend/
    ├── package.json
    ├── tsconfig.json
    ├── vite.config.ts         (include Vitest config)
    ├── index.html
    └── src/
        ├── main.tsx
        ├── App.tsx            (Ant Design layout with a placeholder page)
        ├── api/               (empty, API client goes here later)
        ├── components/        (empty)
        ├── pages/
        │   └── Dashboard.tsx  (placeholder: title and "Coming soon")
        └── App.test.tsx       (one test: App renders the placeholder title)

Architecture rules (follow these in all code)
1. Backend layering is routers -> services -> repositories -> models. Routers only handle HTTP. Services hold business logic as pure functions. Repositories are the only code that touches the database.
2. Never use floats for money. Salaries are integer minor units plus a currency code.
3. No business logic in routers or React components.
4. Keep each file small and single-purpose.

Code quality rules
- Type hints on every Python function. Strict mode on in tsconfig.
- Short docstrings or comments only where the intent is not obvious. Explain why, not what.
- Clear, descriptive names. No abbreviations, no magic numbers (use named constants).
- No unused imports, dead code or commented-out code.
- Configure ruff (line length 100, rules: E, F, I, B, UP) and keep the code passing it.
- Pin dependency versions in pyproject.toml and package.json.

## Do NOT
- Do not add GitHub Actions or Docker yet.
- Do not add database models, tables, seed data or any insight logic yet.
- Do not add auth.

## Done when
- `cd backend && pip install -e ".[dev]" && pytest && ruff check .` all pass
- `cd backend && uvicorn app.main:app --reload` serves GET /health
- `cd frontend && npm install && npm test && npm run dev` all work
- README explains these commands

When finished, list every file you created and the exact commands to run both test suites.
```

### 2026-10-24

```text
add react query  integration as well for better server side state data managment
```

### 2026-10-24

```text
You are working in an existing monorepo (FastAPI + SQLAlchemy 2.x + SQLite backend, already scaffolded). Implement ONLY the data foundation: the money type, the SQLAlchemy models, and salary bands. No routers, services, repositories, seed data or insight logic yet.

## Architecture rules (follow strictly)
1. Layering is routers -> services -> repositories -> models. This step only touches models, db setup, and a pure money module.
2. NEVER use floats for money. Salaries are integer minor units (e.g. cents, paise) plus a 3-letter currency code.
3. FX rates are also stored as integers (no floats, no SQLite Numeric/Decimal columns). Use Python's Decimal only inside the money module for arithmetic.
4. Small single-purpose files, type hints everywhere, named constants instead of magic numbers, comments only where the "why" is not obvious.

## 1. Money module: backend/app/money.py (pure Python, no DB imports)
- A table of supported currencies with their minor-unit exponent: USD, EUR, GBP, INR, JPY (exponent 0), CAD, AUD, SGD. Others raise UnsupportedCurrencyError.
- A frozen dataclass `Money(amount_minor: int, currency: str)`:
  - rejects negative amounts and unsupported currencies (ValueError subclasses defined in this module)
  - `to_usd(rate: FxRate) -> Money` converts to USD minor units using Decimal arithmetic and ROUND_HALF_EVEN
- FX rate representation: `usd_rate_e6: int` = USD value of 1 major unit of the currency, multiplied by 1,000,000 (constant `FX_RATE_SCALE = 1_000_000`). Example: 1 INR = 0.012 USD -> 12000.
- Conversion must respect each currency's exponent (JPY has none, USD has 2).
- USD to USD with rate scale 1.0 returns the same amount.

## 2. SQLAlchemy models: backend/app/models/ (one file per model)
Use SQLAlchemy 2.x typed style (DeclarativeBase, Mapped, mapped_column). Put the shared Base in models/base.py and export everything from models/__init__.py.

### Employee (employees)
id (PK), name, email (unique), title, level (int, 1-6), department, country (ISO alpha-2), currency (3 letters), salary_minor (int, >= 0), salary_usd_minor (int, >= 0, denormalized for fast queries), gender (enum: FEMALE, MALE, OTHER, UNDISCLOSED), manager_id (nullable self FK), employment_type (enum: FULL_TIME, PART_TIME, CONTRACT), hire_date (date), last_raise_date (nullable date), status (enum: ACTIVE, ON_LEAVE, TERMINATED).
- CheckConstraints: salary_minor >= 0, level between 1 and 6.
- Indexes: country, department, title, level, salary_usd_minor, and a composite (title, level, country).

### SalaryBand (salary_bands)
id (PK), title, level, country, currency, min_minor, mid_minor, max_minor (all int, in local currency minor units).
- Unique on (title, level, country).
- CheckConstraint: 0 <= min_minor <= mid_minor <= max_minor.

### SalaryHistory (salary_history)
id (PK), employee_id (FK -> employees.id, indexed), old_salary_minor, new_salary_minor, currency, changed_at (datetime).

### FxRate (fx_rates)
currency (PK, 3 letters), usd_rate_e6 (int, > 0).

Define the enums in models/enums.py as str-based Enums. Store them as strings in the DB.

## 3. DB setup: backend/app/db.py
Keep the existing engine/session setup. Add:
- `create_all_tables(engine)` that calls Base.metadata.create_all
- a `get_session` FastAPI dependency (already exists? keep one version only)
Do not add Alembic yet.

## 4. Tests (pytest, fast, deterministic, no network, no randomness)
backend/tests/test_money.py:
- converts INR to USD correctly with a known rate
- JPY (exponent 0) converts correctly
- uses banker's rounding (ROUND_HALF_EVEN) on an exact .5 case
- USD with a 1.0 rate returns the same amount
- rejects negative amounts
- rejects unsupported currency
backend/tests/conftest.py: an in-memory SQLite engine fixture and a session fixture, creating tables fresh for each test.
backend/tests/test_models.py:
- can insert and read back an Employee
- duplicate email raises IntegrityError
- negative salary raises IntegrityError
- level 0 and level 7 are rejected
- SalaryBand rejects min > mid and mid > max
- SalaryBand rejects a duplicate (title, level, country)
- SalaryHistory requires a valid employee_id (enable SQLite foreign keys via PRAGMA in the engine fixture)
- manager_id can reference another employee
Name each test for the behavior it checks. Use small helper functions or factories in conftest for building valid objects, so tests stay short.

## Do NOT
- Do not add routers, services, repositories, seed scripts or any insight logic.
- Do not add GitHub Actions or Docker.
- Do not use float for any money or rate value anywhere.

## Done when
- `cd backend && pytest && ruff check .` pass
- All files are small and each has one clear purpose
- Finish by listing every file you added or changed and any assumption you made.
```

### 2026-10-24

```text
1. NEVER use floats for money or FX rates. Salaries are integer minor units. Use integer per-mille factors (e.g. 930 = 93.0%) and integer arithmetic (`amount * permille // 1000`). Floats are allowed ONLY for sampling (e.g. random.gauss) and must be converted to an int per-mille factor before touching money.
2. Use the existing money module (Money, to_usd, FX_RATE_SCALE) for USD conversion. Do not reimplement conversion.
3. Fully deterministic: use ONE `random.Random(seed)` instance passed down explicitly. Never use the global `random`, `datetime.now()` or `date.today()`. Use a constant `SEED_REFERENCE_DATE = date(2026, 10, 1)`.
4. Generation is pure (returns dataclasses, no DB). Exactly one file (loader) touches the database.
5. Small single-purpose files, type hints everywhere, named constants (no magic numbers), comments only for the "why".

## Files to create
backend/app/seeding/
- __init__.py
- reference_data.py   constants: countries, currencies, titles, departments, levels, FX rates, weights
- band_builder.py     builds SalaryBand rows for every (title, level, country)
- employee_generator.py   generates base employees (no patterns yet)
- planted_patterns.py     applies each planted pattern as a separate, named function
- loader.py           the only DB-touching file: bulk inserts in ONE transaction
backend/scripts/seed.py   thin CLI entry point

## Reference data (reference_data.py)
- 8 countries: US (USD), GB (GBP), DE (EUR), IN (INR), SG (SGD), CA (CAD), AU (AUD), JP (JPY).
- FX rates as integers: usd_rate_e6 per currency. Use illustrative rates and add a comment saying they are fixed and illustrative.
- Country cost index (per-mille of the US level), country headcount weights (US and IN largest, SG smallest).
- 12 titles, each mapped to one department: Software Engineer, QA Engineer (Engineering); Data Analyst, Data Scientist (Data); Product Manager, Designer (Product); HR Specialist, Recruiter (HR); Accountant, Financial Analyst (Finance); Sales Executive (Sales); Customer Support Specialist (Support).
- A base USD salary (in minor units) per title, and a level multiplier per-mille for levels 1-6.
- Title weights and level weights, skewed (fewer people at levels 5-6) so peer-group sizes vary and some combos end up with fewer than 5 people.

## Bands (band_builder.py)
- For every (title, level, country): midpoint = base_usd × level multiplier × country index, converted to local currency using the FX rate (integer math). min = 80% of mid, max = 120% of mid (per-mille constants BAND_MIN_PERMILLE = 800, BAND_MAX_PERMILLE = 1200).
- Return SalaryBand-ready dicts. Currency = the country's currency.

## Base generation (employee_generator.py)
- Generate exactly `count` employees with ids 1..count.
- Pick country, title, level by weight. Salary = band mid × a per-mille factor sampled around 1000 (gauss, sigma about 70, clipped to 850-1150), as an int.
- Gender mix about 45% FEMALE, 52% MALE, 2% OTHER, 1% UNDISCLOSED. Fewer women at levels 4-6 (to make the raw gap larger than the adjusted gap).
- Status: about 93% ACTIVE, 4% ON_LEAVE, 3% TERMINATED. employment_type: about 90% FULL_TIME.
- hire_date: between 0 and 10 years before SEED_REFERENCE_DATE. last_raise_date: usually within the last 12 months; null if hired under 12 months ago.
- Names via Faker seeded from the same seed. Email = unique, like `first.last.<id>@acme.example`.
- manager_id: choose an employee in the same department and country with a higher level (1-2 levels up), else null. Level 6 has no manager.
- Compute salary_usd_minor with the money module.

## Planted patterns (planted_patterns.py), each its own function with a docstring saying which insight it feeds. Expose the tuning values as named constants at the top.
1. GENDER_GAP: in 3 chosen titles, multiply FEMALE salaries by 930 per-mille (about 7% lower).
2. BELOW_BAND: about 3% of employees get a salary of 900-980 per-mille of their band min.
3. ABOVE_BAND: about 2% get 1020-1150 per-mille of their band max.
4. OUTLIERS: about 1% get 700 or 1300 per-mille of their peer-group median.
5. COMPRESSION: in 2 peer groups with at least 8 people, set the 2 most recently hired to 1120 per-mille of the group median.
6. INVERSION: for about 1% of employees with a manager, set salary above the manager's salary (same currency only).
7. STALE_RAISES: about 8% get a last_raise_date more than 24 months before SEED_REFERENCE_DATE.
8. Small groups need no code: the skewed weights must leave some (title, level, country) groups with 1-4 people.
Apply patterns in a fixed order. Recompute salary_usd_minor after any salary change. Pattern selection must use the passed-in Random, never global state.

## Salary history
For each employee with a last_raise_date, create one SalaryHistory row: new = current salary, old = about 92% of it (integer per-mille), changed_at = last_raise_date.

## Loader (loader.py)
- `load_seed_data(session, fx_rates, bands, employees, history)` inserts using `session.execute(insert(Model), list_of_dicts)` in chunks of 1,000, all inside ONE transaction. Order: fx_rates, salary_bands, employees (managers must exist before reports, so insert in id order and disable the self-FK problem by inserting employees with manager_id set after, or sort so managers come first), salary_history.
- Refuse to run if the employees table already has rows, unless reset=True (drops and recreates all tables).

## CLI (scripts/seed.py)
`python -m scripts.seed --seed 42 --count 10000 --db-url sqlite:///./salary.db --reset`
Defaults: seed 42, count 10000, db-url from app config. Print a short summary at the end: row counts per table and elapsed time. It should finish in a few seconds.

## Tests (pytest, fast, deterministic, no network)
backend/tests/seeding/
- test_determinism: same seed gives identical output twice; different seeds differ.
- test_counts_and_integrity: exactly 10,000 employees; unique emails and ids; levels 1-6; all salaries > 0; every employee's (title, level, country) has a band; salary_usd_minor equals the money-module conversion; every manager_id points to an existing employee.
- test_bands: min <= mid <= max for all bands; one band per (title, level, country).
- test_planted_patterns (generate 10,000 in memory, no DB):
  - adjusted gap in the 3 planted titles is between 5% and 9%; raw gap overall is larger than the adjusted gap
  - share below band min is between 2% and 4%; share above band max between 1% and 3%
  - at least 10 employees paid more than their manager
  - at least 2 peer groups show compression
  - at least 5 peer groups have fewer than 5 people
  - share with last raise over 24 months ago is between 6% and 10%
- test_loader: load 500 employees into an in-memory SQLite (use the existing conftest fixtures, foreign keys ON); row counts match; running again without reset raises; with reset succeeds.
Use small helper functions in the tests so each test is a few lines. Name tests for the behavior they check.

## Do NOT
- Do not add routers, services, repositories, Docker or GitHub Actions.
- Do not use float for money or FX anywhere in stored or computed amounts.
- Do not use global random or the current date.

## Done when
- `cd backend && pytest && ruff check .` pass
- `python -m scripts.seed --reset` creates the DB in a few seconds
- Finish by listing every file added or changed and any assumption you made.
```

### 2026-10-24

```text
create wreuirments file for python so iuser can esaily now or installl apckges
```

### 2026-10-24

```text
## Architecture rules (follow strictly)
1. Layering is routers -> services -> repositories -> models. Routers handle HTTP only. The service holds the logic that turns request params into a filter object and a page result. The repository is the ONLY code that builds SQL or touches the session.
2. NEVER use floats for money. Responses return integer minor units plus the currency code. Salary filters use integer USD minor units.
3. Small single-purpose files, type hints everywhere, named constants (no magic numbers), comments only where the "why" is not obvious.
4. Never build SQL by string concatenation. Use SQLAlchemy expressions only.

## Files to create or change
backend/app/schemas/employee.py
  - EmployeeOut: id, name, email, title, level, department, country, currency, salary_minor, salary_usd_minor, gender, employment_type, hire_date, last_raise_date, status, manager_id
  - EmployeePage: items (list[EmployeeOut]), total (int), page (int), page_size (int), total_pages (int)
backend/app/services/employee_query.py   (pure Python, no DB imports)
  - EmployeeFilters: frozen dataclass holding all filters and sort settings (see below)
  - SortField enum and SortDirection enum
  - build_page_info(total, page, page_size) -> total_pages calculation (total_pages is 0 when total is 0)
  - list_employees(repository, filters, page, page_size) -> EmployeePage
backend/app/repositories/employee_repository.py
  - EmployeeRepository(session) with:
    - search(filters, offset, limit) -> list[Employee]
    - count(filters) -> int
  - A private function that applies filters to a select statement so search() and count() share it.
backend/app/routers/employees.py
  - GET /employees
backend/app/main.py: include the router. Add CORS middleware allowing http://localhost:5173 (origins come from config, not hard-coded in main.py).
backend/app/config.py: add CORS_ORIGINS, DEFAULT_PAGE_SIZE = 25, MAX_PAGE_SIZE = 100.

## Query parameters for GET /employees
- page (int, default 1, >= 1)
- page_size (int, default 25, 1 to 100)
- q: text search, case-insensitive match on name OR email. Escape %, _ and \ so user input is treated literally.
- country, department, title: repeatable params (e.g. ?country=IN&country=US) matched with IN (...)
- level: repeatable ints (1-6)
- status, gender: repeatable enum values
- min_salary_usd_minor, max_salary_usd_minor: optional ints >= 0. If both are given and min > max, return 422 with a clear message.
- sort_by: one of name, title, department, country, level, salary_usd_minor, hire_date (default name)
- sort_dir: asc or desc (default asc)
Unknown sort_by, sort_dir or enum values must return 422 (use enums in the FastAPI signature).

## Behavior details
- Always add `id` as the final tie-breaker in ORDER BY so pagination is stable.
- A page beyond the last page returns an empty items list with the correct total (not a 404).
- total counts all rows matching the filters (before pagination).
- The session comes from the existing get_session dependency.
- Filters combine with AND; values inside one repeatable filter combine with OR.

## Tests (pytest, fast, deterministic, no network)
backend/tests/conftest.py: add an `api_client` fixture that uses TestClient with get_session overridden to an in-memory SQLite session, and a helper `make_employee(**overrides)` that builds a valid Employee. Reuse the existing fixtures where they exist.
backend/tests/services/test_employee_query.py (pure unit tests, no DB):
- total_pages for 0, exact multiple, and remainder cases
- list_employees passes the right offset and limit to a fake repository (page 3, size 10 -> offset 20, limit 10)
backend/tests/repositories/test_employee_repository.py (small in-memory dataset of about 20 hand-made employees):
- no filters returns all
- each filter alone: country, department, title, level, status, gender
- repeatable filter uses OR (country IN, level IN)
- different filters combine with AND
- salary range: inclusive on both ends
- search matches name and email, case-insensitive
- search treats % and _ literally (a query of "%" does not match everything)
- sorting asc and desc for at least salary_usd_minor and name
- ties on the sort field are ordered by id
- count() equals the number of matching rows, ignoring pagination
backend/tests/routers/test_employees_api.py:
- 200 with default params returns the page shape (items, total, page, page_size, total_pages)
- page_size above the max returns 422
- page 0 returns 422
- min_salary_usd_minor > max_salary_usd_minor returns 422
- invalid sort_by returns 422
- page beyond the last returns empty items and the correct total
- walking all pages returns every employee exactly once with no duplicates
- money fields are integers in the JSON response
Name each test for the behavior it checks. Keep tests short using helper functions.

## Performance check (a script, not a pytest test)
backend/scripts/benchmark_list.py: seeds an in-memory or temp DB with the existing seed generator at 10,000 employees, then times 5 representative calls (no filters, country filter, salary range + sort, search, page 100) and prints the elapsed milliseconds. Target is under 300 ms each. Do not assert in CI; just print.

## Do NOT
- Do not add create/update/delete endpoints, insight endpoints, auth, Docker or GitHub Actions.
- Do not use float for money anywhere.
- Do not put SQL or session code in routers or services.

## Done when
- `cd backend && pytest && ruff check .` pass
- `uvicorn app.main:app --reload` serves GET /employees and the OpenAPI docs at /docs show all params
- Finish by listing every file added or changed and any assumption you made.
```

### 2026-10-24

```text
You are working in an existing monorepo. Backend (FastAPI) already serves GET /employees with pagination, filters, search and sorting. Frontend is scaffolded: Vite + React + TypeScript (strict) + Ant Design + Vitest. Implement ONLY an employee table page that renders data from that endpoint, using TanStack Query (React Query v5) for data fetching. No create/edit/delete, no charts, no dashboard, no backend changes.

## Architecture rules (follow strictly)
1. Separate concerns: `api/` = HTTP calls and types, `hooks/` = state and React Query hooks, `components/` = presentational pieces, `pages/` = composition. No fetch calls inside components.
2. NEVER do money math in the UI. The API returns integer minor units plus a currency code. The UI only formats them for display.
3. Strict TypeScript, no `any`. Small single-purpose files, descriptive names, named constants instead of magic numbers, comments only for the "why".
4. The API base URL comes from `import.meta.env.VITE_API_BASE_URL` (default http://localhost:8000). Add a `.env.example`.
5. All server data goes through React Query. Do not store fetched data in useState or useEffect.

## Dependencies
Add @tanstack/react-query. Dev: @testing-library/react, @testing-library/user-event, @testing-library/jest-dom, jsdom. Configure Vitest with jsdom. Pin versions. (already installed )

## Files to create
frontend/src/api/
- client.ts        `getJson<T>(path, params, signal?)`: builds the query string (repeatable params as repeated keys, skips undefined), throws a typed ApiError (with status) on non-2xx, supports AbortSignal
- employees.ts     `fetchEmployees(query: EmployeeQuery, signal?: AbortSignal): Promise<EmployeePage>`
- types.ts         EmployeeOut, EmployeePage, EmployeeQuery and the enums (Gender, EmploymentType, EmployeeStatus, SortField, SortDirection) matching the backend exactly
frontend/src/lib/
- queryClient.ts   creates the QueryClient with defaults: staleTime 30s, retry 1, refetchOnWindowFocus false (named constants)
- formatMoney.ts   `formatMinorUnits(amountMinor, currency)` using Intl.NumberFormat; read the currency's minor digits from Intl (JPY 0, USD 2); readable fallback for an unknown currency
- formatDate.ts    ISO date to a readable date
frontend/src/hooks/
- useDebouncedValue.ts       generic debounce hook (300 ms constant)
- useEmployeeTableState.ts   owns ONLY UI state: page, pageSize, search, filters, sort. Resets page to 1 when search, filters or sort change. Exposes the state, setters and a `clearFilters`.
- useEmployeesQuery.ts       wraps useQuery: queryKey ['employees', query], queryFn passes the abort signal to fetchEmployees, placeholderData: keepPreviousData. Takes the debounced search value, not the raw input. Returns the query result.
frontend/src/components/
- EmployeeFilters.tsx   search input, multi-selects for country, department, level and status, a gender select, and a "Clear filters" button. Controlled component.
- EmployeeTable.tsx     Ant Design Table with server-side pagination and sorting, columns: Name, Title, Department, Country, Level, Salary (local), Salary (USD), Hire date, Status. Salary columns use formatMinorUnits, right-aligned. Sortable: name, title, department, country, level, salary_usd_minor, hire_date. Shows the total count. Page size options 25, 50, 100. Takes `loading` and `isPlaceholderData` as props so rows can look dimmed while the next page loads.
- ErrorBanner.tsx      Ant Design Alert with a Retry button
frontend/src/pages/EmployeesPage.tsx   composes the state hook, query hook, filters, table and error banner
frontend/src/main.tsx  wrap the app in QueryClientProvider using the shared queryClient
frontend/src/App.tsx   Ant Design Layout: header with the app name, content renders EmployeesPage. Remove the old placeholder dashboard page.
frontend/src/constants/filterOptions.ts   fixed options for country (US, GB, DE, IN, SG, CA, AU, JP), department, level 1-6, status, gender. Comment: these will come from the API later.

## Behavior details
- Initial load: page 1, 25 rows, sorted by name ascending.
- Search is debounced; filters apply immediately.
- While a new page loads, keep showing the previous rows (keepPreviousData) with a loading indicator.
- Empty state: a clear "No employees match these filters" message with a clear-filters action.
- Error state: ErrorBanner with the message and a Retry button that calls the query's refetch; the table keeps the last good data.
- Map Ant Design's sorter events to the API's sort_by and sort_dir. Clearing the sort returns to the default.

## Tests (Vitest + Testing Library, fast, deterministic, no real network)
Create a test helper `renderWithQueryClient(ui)` that wraps in a fresh QueryClientProvider with retry: false.
- lib/formatMoney.test.ts: USD 2 digits, JPY 0 digits, INR formatting, unknown currency fallback, zero amount.
- api/client.test.ts (mock global fetch): repeatable params become repeated keys, undefined values are omitted, a 500 throws ApiError with the status.
- hooks/useEmployeeTableState.test.ts: changing search, a filter or the sort resets page to 1; clearFilters restores defaults.
- hooks/useEmployeesQuery.test.tsx (mock fetchEmployees): requests with the initial params; a changed query triggers a new request; an error surfaces in the result.
- components/EmployeeTable.test.tsx: renders rows from props; shows formatted local and USD salary; the empty state message; clicking a sortable header calls onSortChange with the right field and direction.
- pages/EmployeesPage.test.tsx (mock the api module): renders the first page of rows; typing in search sends ONE debounced request (use fake timers); clicking Retry after an error calls the API again and shows the rows.
Name each test for the behavior it checks. Use small factories for fake employees.

## Do NOT
- Do not add routing, Redux or any other state library, charts, forms, auth, Docker or GitHub Actions.
- Do not do arithmetic on money values.
- Do not use `any` or disable lint rules to get things passing.
- Do not use useEffect for data fetching.

## Done when
- `cd frontend && npm test && npm run build` pass, plus the project's lint/type check
- With the backend seeded and running, `npm run dev` shows the real employee table at http://localhost:5173 with working pagination, search, filters and sorting
- Finish by listing every file added or changed and any assumption you made.
```

### 2026-10-24

```text
No such table found error is encountered.
 Plese create tables and run the scripts for inserting teh dtaa
```

### 2026-10-24 - Prompt history

```text
in which file my pr,pts are presernt
```

````text
but last prmot in this file is ```text
add react query  integration as well for better server side state data managment
```
````

```text
add later prompts as well, please
```

### 2026-10-24 - Deployment

```text
how to deploy this app?
```

```text
but on what can i deploy backedn
```

```text
ok so give me plan to deploy UI and backend use rnede rfot abckedn
```

### 2026-10-24 - Peer-group benchmarks

```text
You are working in an existing monorepo: FastAPI + SQLAlchemy 2.x + SQLite backend, and a Vite + React + TypeScript (strict) + Ant Design + React Query + Vitest frontend. Models, the money module, the seed script, GET /employees and an employee table page already exist. Implement ONE feature end to end: peer-group benchmarks (the going rate for a role). Backend first, tests first, then the UI. Do not add anything outside this scope.

## What the feature does
For each peer group (title + level + country) show headcount and the salary distribution: min, p25, median, p75, max, in the group's local currency. Groups with fewer than 5 people are reported as "insufficient data" and show no stats.

## Backend rules (follow strictly)
1. Layering: routers -> services -> repositories -> models. Services are pure functions with NO database or FastAPI imports. The repository is the only code that builds SQL. The router only parses HTTP params and returns schemas.
2. NEVER use floats for money. Salaries are integer minor units. Percentiles use integer arithmetic only; rounding is half-even (banker's rounding) in one helper.
3. Only employees with status ACTIVE or ON_LEAVE count. TERMINATED is excluded.
4. MIN_PEER_GROUP_SIZE = 5 as a named constant.
5. Write the tests BEFORE the implementation, with expected values computed by hand (show the arithmetic in comments). Tests are fast, deterministic, no network, no randomness.
6. Small single-purpose files, type hints everywhere, named constants, descriptive names, comments only for the "why". The repository returns lightweight rows (NamedTuple), not ORM objects.

## Backend: files
backend/app/services/statistics.py (pure)
  - round_half_even_div(numerator: int, denominator: int) -> int
  - percentile(sorted_values: list[int], percent: int) -> int
    Method: linear interpolation between closest ranks. With n values: numerator = percent * (n - 1); index = numerator // 100; remainder = numerator % 100; result = round_half_even_div(lower * 100 + (upper - lower) * remainder, 100), where lower = values[index] and upper = values[min(index + 1, n - 1)]. Raise ValueError on an empty list or percent outside 0..100.
  - median(sorted_values) -> int (percentile 50)
backend/app/services/peer_groups.py (pure)
  - PeerGroupKey: frozen dataclass (title, level, country)
  - group_by_peer_group(rows) -> dict[PeerGroupKey, list]
backend/app/services/benchmarks.py (pure)
  - BenchmarkStats: min, p25, median, p75, max (ints, local minor units)
  - PeerGroupBenchmark: key, currency, headcount, stats (None when insufficient), insufficient_data (bool)
  - compute_benchmarks(rows) -> list[PeerGroupBenchmark], sorted by country, title, level (stable)
backend/app/repositories/insight_repository.py
  - SalaryRow NamedTuple with only the columns needed now: employee_id, title, level, country, currency, salary_minor
  - InsightRepository(session).active_salary_rows(countries=None, titles=None, levels=None) -> list[SalaryRow]. Select only those columns; filter status IN (ACTIVE, ON_LEAVE); optional IN filters. Never build SQL from strings.
backend/app/schemas/insights.py: BenchmarkStatsOut, PeerGroupBenchmarkOut, BenchmarksResponse (items list)
backend/app/routers/insights.py: GET /insights/benchmarks
  - repeatable optional params: country, title, level (1-6)
  - include_insufficient: bool, default true
  - response: { items: [...] } with integers only in the JSON
Include the router in main.py.

## Backend: tests (write first)
tests/services/test_statistics.py (hand-computed):
  - [10, 20, 30, 40]: p0=10, p25=18 (17.5 rounds half-even to 18), p50=25, p75=32 (32.5 rounds half-even to 32), p100=40
  - a single value returns that value for every percentile
  - odd count: median is the middle value; even count: rounded average of the middle two
  - duplicate values handled
  - empty list raises ValueError; percent -1 and 101 raise ValueError
tests/services/test_peer_groups.py: grouping by the three-part key; same title and level in two countries are separate groups.
tests/services/test_benchmarks.py: stats for a hand-made group of exactly 5 people; a group of 4 is insufficient with stats None; output ordering is stable; headcount is correct.
tests/repositories/test_insight_repository.py: TERMINATED excluded; ON_LEAVE included; country, title and level filters each work and combine with AND.
tests/routers/test_insights_benchmarks_api.py: 200 and response shape; filters narrow the results; include_insufficient=false hides small groups; invalid level returns 422; all numbers in the JSON are integers.
tests/test_seed_integration.py: generate 2,000 seeded employees in memory and assert there is at least one sufficient group and at least one insufficient group.

## Frontend rules (follow strictly)
1. Keep the existing structure: api/ (HTTP and types), hooks/ (React Query hooks), components/ (presentational), pages/ (composition), lib/ (formatting), constants/. All server data goes through React Query. No fetch in components, no useEffect for fetching.
2. NEVER do money math in the UI. Only format integers for display with the existing formatMinorUnits(amountMinor, currency).
3. Ant Design components only. No new chart library. Strict TypeScript, no `any`. Named constants. Mirror the backend response types exactly.
4. Handle loading, empty and error states (reuse the existing ErrorBanner with Retry).
5. Tests: Vitest + Testing Library with the existing renderWithQueryClient helper, mocked api module, fake timers where needed, no real network.

## Frontend: files
- Add react-router-dom (pin the version). Routes: /employees, /insights/benchmarks, and "/" redirects to /employees.
- src/constants/navigation.ts: ONE array of menu items (label, path), currently Employees and Benchmarks. Later commits will add more.
- src/App.tsx: Ant Design Layout with a left Sider Menu built from that array; the active item follows the current route. Content area renders the routed page. Keep the existing header with the app name.
- src/api/types.ts: add BenchmarkStats, PeerGroupBenchmark, BenchmarksResponse and BenchmarksQuery.
- src/api/insights.ts: fetchBenchmarks(query, signal) using the existing getJson (repeatable params as repeated keys).
- src/hooks/useBenchmarksQuery.ts: useQuery with queryKey ['benchmarks', query] and keepPreviousData.
- src/pages/BenchmarksPage.tsx:
  - filters: multi-selects for country, title and level (reuse constants/filterOptions.ts; add a title options list there), and a "Show small groups" Switch (default on) that sets include_insufficient.
  - Ant Design Table with columns Country, Title, Level, Headcount, Min, P25, Median, P75, Max. Stats are formatted with the group's own currency and right-aligned.
  - insufficient groups show a Tag "Insufficient data (n < 5)" and dashes in the stat columns.
  - the endpoint returns all groups, so use client-side pagination, page size 25, default order as returned.
  - empty state: "No peer groups match these filters".

## Frontend: tests
- BenchmarksPage: renders rows with local-currency formatting (a USD group and a JPY group); an insufficient group shows the Tag and dashes; toggling the switch changes the request param; changing a filter changes the request; empty state; error state with Retry.
- App/navigation: menu is built from the navigation array; clicking Benchmarks shows the Benchmarks page; "/" redirects to the Employees page.
Name every test for the behavior it checks. Use small factories for fake benchmark rows.

## Do NOT
- Do not add auth, Docker, GitHub Actions, charts, forms, or any other insight.
- Do not use float for money or percentiles anywhere. Do not do money math in the UI.
- Do not disable lint rules or use `any` to get things passing.

## Done when
- `cd backend && pytest && ruff check .` pass
- `cd frontend && npm test && npm run build` and the lint/type check pass
- With the DB seeded and the backend running, the Benchmarks page shows real groups with correct stats
- Finish by listing every file added or changed and any assumption you made.
```

### 2026-10-24 - Updating the prompt log

```text
add latest prmots in prompt.md
```


## Prompt history continuation - 24-25 Oct 2026

Original user wording is preserved below. Pasted requests are reproduced from their read-only attachment snapshots. Times are IST (UTC+05:30).

### 2026-10-24 16:49 IST - Band compliance and peer outliers

Source: user attachment "Pasted text #1".

```text
You are working in an existing monorepo: FastAPI + SQLAlchemy 2.x + SQLite backend, and a Vite + React + TypeScript (strict) + Ant Design + React Query + react-router-dom + Vitest frontend. Already built: models, money module, seed script, GET /employees with an employee table page, and peer-group benchmarks (services/statistics.py, services/peer_groups.py, services/benchmarks.py, repositories/insight_repository.py with SalaryRow and active_salary_rows, routers/insights.py, navigation array, BenchmarksPage). Implement ONE feature end to end: band compliance and outliers. Backend first, tests first, then the UI. Reuse existing code; do not duplicate it. Do not add anything outside this scope.

## What the feature does
1. Band compliance: for each active employee, compare salary to the salary band for their (title, level, country). Report who is below the band minimum or above the maximum, with a compa-ratio.
2. Outliers: flag employees whose salary deviates more than 20% from the median of their peer group (title + level + country).

## Backend rules (follow strictly)
1. Layering: routers -> services -> repositories -> models. Services are pure functions with NO database or FastAPI imports. The repository is the only code that builds SQL. Routers only parse HTTP params and return schemas.
2. NEVER use floats for money, ratios or percentages. Salaries are integer minor units. Ratios and deviations are integer per-mille (1000 = 100%). Rounding is half-even (banker's) using the existing round_half_even_div helper.
3. Only ACTIVE and ON_LEAVE employees count. TERMINATED is excluded.
4. Reuse MIN_PEER_GROUP_SIZE = 5 and PeerGroupKey from peer_groups.py.
5. Write the tests BEFORE the implementation, with expected values computed by hand (show the arithmetic in comments). Tests are fast, deterministic, no network, no randomness.
6. Small single-purpose files, type hints everywhere, named constants, descriptive names, comments only for the "why". Repositories return lightweight rows (NamedTuple), not ORM objects.

## Backend: changes to existing code
- Extend SalaryRow in repositories/insight_repository.py with: name, department (keep existing fields). Update the existing benchmark tests and factories so they still pass.
- Add InsightRepository.salary_bands() -> dict[PeerGroupKey, BandRow], where BandRow is a NamedTuple (currency, min_minor, mid_minor, max_minor).
- active_salary_rows should also accept an optional departments filter.

## Backend: files
backend/app/services/pagination.py (pure): paginate(items, page, page_size) -> (slice, total). A page beyond the last returns an empty list with the correct total.
backend/app/services/band_compliance.py (pure)
  - compa_ratio_permille(salary_minor, band_mid_minor) -> int
  - BandStatus enum: BELOW_MIN, WITHIN_BAND, ABOVE_MAX. A salary exactly equal to the min or the max is WITHIN_BAND.
  - classify(salary_minor, band_min_minor, band_max_minor) -> BandStatus
  - FlaggedEmployee dataclass: employee_id, name, department, title, level, country, currency, salary_minor, band_min_minor, band_mid_minor, band_max_minor, compa_ratio_permille, status, gap_to_band_minor (positive integer: distance outside the band)
  - BandSummary dataclass: below_min, within_band, above_max, no_band (counts)
  - evaluate_bands(rows, bands_by_key) -> BandReport(summary, flagged sorted by gap_to_band_minor descending then employee_id ascending). Employees with no band count as no_band and are not flagged.
backend/app/services/outliers.py (pure)
  - OUTLIER_THRESHOLD_PERMILLE = 200
  - deviation_permille(salary_minor, group_median_minor) -> int (signed, half-even; raise ValueError if the median is 0)
  - OutlierDirection enum: ABOVE, BELOW
  - Outlier dataclass: employee_id, name, title, level, country, currency, salary_minor, group_median_minor, group_headcount, deviation_permille, direction
  - find_outliers(rows) -> list[Outlier]: only peer groups with at least MIN_PEER_GROUP_SIZE people; flag when abs(deviation) is STRICTLY greater than the threshold; sorted by absolute deviation descending then employee_id ascending.
backend/app/schemas/insights.py: add schemas for both responses.
backend/app/routers/insights.py: add
  - GET /insights/bands: optional repeatable country, department, title, level; optional status (below_min or above_max); page (>=1, default 1), page_size (1-100, default 25). Response: summary (counts over ALL employees matching the country/department/title/level filters, NOT affected by status or paging), items (the flagged page, filtered by status if given), total (flagged count after the status filter), page, page_size.
  - GET /insights/outliers: optional repeatable country, title, level; optional direction (above or below); page, page_size as above. Response: items, total, page, page_size. Outliers use the full peer group of every matching group; there is no department filter here because department is not part of the peer-group key.
Unknown enum values return 422.

## Backend: tests (write first)
tests/services/test_pagination.py: first page, last partial page, page beyond the end returns empty with correct total.
tests/services/test_band_compliance.py (hand-computed):
  - compa-ratio: salary 900, mid 1000 -> 900; salary 1000, mid 1000 -> 1000; salary 1234, mid 1000 -> 1234
  - classify: below min, above max, exactly on min (WITHIN_BAND), exactly on max (WITHIN_BAND)
  - gap_to_band: below by 100 -> 100; above by 250 -> 250
  - an employee with no band is counted in no_band and not flagged
  - flagged ordering: larger gap first; ties by employee_id
  - summary counts are correct for a small mixed set
tests/services/test_outliers.py (hand-computed):
  - a group of 4 produces no outliers; a group of 5 can
  - median 1000: salary 1200 -> deviation 200, NOT flagged; salary 1201 -> 201, flagged ABOVE; salary 799 -> -201, flagged BELOW
  - even-count group median uses the rounded average of the middle two
  - sorting by absolute deviation descending
  - median 0 raises ValueError in deviation_permille
tests/repositories/test_insight_repository.py: salary_bands keyed correctly; terminated excluded; the department filter works; the new SalaryRow fields are populated.
tests/routers/test_insights_bands_api.py and test_insights_outliers_api.py: response shape; filters narrow the data; summary ignores the status filter and paging; walking all pages returns every flagged item exactly once; status and direction filters work; invalid enum returns 422; all numbers are integers.
tests/test_seed_integration.py: generate 3,000 seeded employees in memory; assert below_min > 0, above_max > 0 and the outlier count > 0.

## Frontend rules (follow strictly)
1. Keep the existing structure: api/ (HTTP and types), hooks/ (React Query hooks), components/ (presentational), pages/ (composition), lib/ (formatting), constants/. All server data goes through React Query. No fetch in components, no useEffect for fetching.
2. NEVER do money or ratio math in the UI. Only format integers for display: formatMinorUnits (exists) and a new formatPermille.
3. Ant Design components only (Tabs, Statistic, Card, Table, Tag, Segmented, Select, Empty, Skeleton). No new chart library. Strict TypeScript, no `any`. Named constants. Mirror the backend response types exactly.
4. Handle loading, empty and error states (reuse ErrorBanner with Retry).
5. Tests: Vitest + Testing Library with the existing renderWithQueryClient helper, mocked api module, no real network.

## Frontend: files
- src/lib/formatPermille.ts (+ tests): integer per-mille to a string using integer/string operations only, no floats: 1000 -> "100.0%", 934 -> "93.4%", 5 -> "0.5%", -201 -> "-20.1%", 0 -> "0.0%".
- src/constants/navigation.ts: add "Needs attention" at /insights/attention. Add the route in App.tsx.
- src/api/types.ts: add types for both responses (mirror the backend). src/api/insights.ts: fetchBands, fetchOutliers.
- src/hooks/useBandsQuery.ts, useOutliersQuery.ts (React Query, keepPreviousData).
- src/pages/AttentionPage.tsx using Ant Design Tabs, with the active tab stored in the URL query string (?tab=bands or ?tab=outliers, default bands) via useSearchParams, so it survives a refresh.
  - Tab "Outside band":
    - Four Statistic cards from the summary: Below min, Within band, Above max, No band.
    - Clicking the Below min or Above max card sets the status filter; clicking it again clears it.
    - Filters: country, department, title, level (multi-selects, reuse constants/filterOptions.ts).
    - Server-paginated Table (page sizes 25, 50, 100): Name, Title, Level, Country, Salary (local), Band min / mid / max (local), Compa-ratio (formatPermille), Gap to band (local currency), Status Tag (red for below, orange for above).
  - Tab "Outliers vs peers":
    - Segmented control: All, Above, Below (direction).
    - Filters: country, title, level.
    - Server-paginated Table: Name, Title, Level, Country, Salary (local), Peer median (local), Deviation (signed formatPermille shown in a Tag, red for below, orange for above), Peer group size.
  - Empty state for each tab: "Nobody matches these filters".
  - Changing any filter or the status or direction resets the page to 1.

## Frontend: tests
- lib/formatPermille.test.ts: all the examples above plus a negative value and a single-digit value.
- AttentionPage, bands tab: summary cards render the counts; clicking Below min sends status=below_min and clicking again clears it; compa-ratio and gap render formatted; changing a filter resets the page; pagination sends the page param; empty and error states.
- AttentionPage, outliers tab: direction control changes the request; deviation shows with its sign; pagination works.
- The tab is read from the URL on load (?tab=outliers opens the outliers tab) and clicking a tab updates the URL.
Name each test for the behavior it checks. Use small factories for fake rows.

## Do NOT
- Do not add auth, Docker, GitHub Actions, charts, forms, links to employee pages, or any other insight.
- Do not use float for money, ratios or percentages anywhere. Do not do math in the UI.
- Do not disable lint rules or use `any` to get things passing.
- Do not duplicate the median or grouping code; import it.

## Done when
- `cd backend && pytest && ruff check .` pass
- `cd frontend && npm test && npm run build` and the lint/type check pass
- With the DB seeded and the backend running, the Needs attention page shows real flagged people and outliers
- Finish by listing every file added or changed and any assumption you made.
```

### 2026-10-24 17:08 IST - What-if cost calculator

```text
You are working in an existing monorepo: FastAPI + SQLAlchemy 2.x + SQLite backend, and a Vite + React + TypeScript (strict) + Ant Design + React Query + react-router-dom + Vitest frontend. Already built: models, money module (app/money.py with Money, to_usd, FX_RATE_SCALE), seed script, employee list and table, peer-group benchmarks, band compliance and outliers (services/band_compliance.py with BandStatus and classify, services/peer_groups.py with PeerGroupKey, repositories/insight_repository.py with SalaryRow, active_salary_rows and salary_bands, routers/insights.py, AttentionPage). Implement ONE feature end to end: what-if cost. Backend first, tests first, then the UI. Reuse existing code; do not duplicate it. Do not add anything outside this scope.

## What the feature does
Read-only cost calculator. Nothing is written to the database. Costs are annual, base salary only, in USD minor units.
1. Bring to band minimum: the cost of raising every active employee paid below their band minimum up to that minimum.
2. Department raise: the cost of giving every active employee in a department a percentage raise.

## Backend rules (follow strictly)
1. Layering: routers -> services -> repositories -> models. Services are pure functions with NO database or FastAPI imports. The repository is the only code that builds SQL. Routers only parse HTTP params and return schemas.
2. NEVER use floats for money, rates or percentages. Salaries are integer minor units; FX rates are integer usd_rate_e6; raises are integer basis points (500 = 5%). Rounding is half-even using the existing round_half_even_div helper. Convert to USD with the existing money module only; do not reimplement conversion.
3. Only ACTIVE and ON_LEAVE employees count. TERMINATED is excluded.
4. Sum costs in LOCAL minor units per country first, then convert each country's total to USD ONCE (comment why: avoids rounding drift). The grand total is the sum of the per-country USD totals.
5. Write the tests BEFORE the implementation, with expected values computed by hand (show the arithmetic in comments). Fast, deterministic, no network, no randomness.
6. Small single-purpose files, type hints everywhere, named constants, descriptive names, comments only for the "why".

## Backend: changes to existing code
- Add InsightRepository.fx_rates() -> dict[str, int] (currency -> usd_rate_e6).
- active_salary_rows must support optional departments, countries, titles and levels filters (extend only if any are missing).

## Backend: files
backend/app/services/what_if.py (pure)
  - MIN_RAISE_BP = 1, MAX_RAISE_BP = 5000
  - CountryCost dataclass: country, currency, employees_affected, cost_local_minor, cost_usd_minor
  - BandMinCostReport: total_cost_usd_minor, employees_affected, by_country (sorted by cost_usd_minor descending, then country)
  - RaiseCostReport: employees_affected, total_cost_usd_minor, current_payroll_usd_minor, new_payroll_usd_minor, by_country (same sorting)
  - cost_to_reach_band_min(rows, bands_by_key, fx_rates) -> BandMinCostReport. Per employee, if BELOW_MIN (use classify from band_compliance), cost = band_min - salary. Employees with no band are skipped without error.
  - cost_of_raise(rows, raise_bp, fx_rates) -> RaiseCostReport. Per employee cost = round_half_even_div(salary * raise_bp, 10000). current_payroll_usd_minor is the sum of per-country current payroll converted once per country; new_payroll = current + total cost.
  - Raise ValueError for a missing FX rate and for raise_bp outside the range.
backend/app/schemas/insights.py: schemas for both responses.
backend/app/routers/insights.py: add
  - GET /insights/what-if/bring-to-band-min: optional repeatable country, department, title, level.
  - GET /insights/what-if/raise: department (required, string), raise_bp (required int, 1..5000), optional country. Missing department or raise_bp outside the range returns 422. An unknown department returns 200 with zero employees and zero costs.

## Backend: tests (write first)
tests/services/test_what_if.py (hand-computed):
  - everyone in band: cost 0, employees_affected 0
  - one USD employee 100 below band min: cost 100
  - an employee exactly on band min costs 0
  - an employee with no band is skipped
  - INR country: local cost 10000 minor (INR 100) with usd_rate_e6 = 12000 converts to 120 USD minor (INR 100 x 0.012 = USD 1.20); show this arithmetic in a comment
  - JPY country (exponent 0): local cost 1000 with usd_rate_e6 = 6500 converts to 650 USD minor (JPY 1000 x 0.0065 = USD 6.50)
  - two employees in the same country are summed in local units first, then converted once (build a case where converting each separately would differ by rounding)
  - raise: salaries 1000 and 2001 at 500 bp cost 50 and 100 (100.05 rounds half-even to 100), total 150
  - new_payroll = current_payroll + total cost
  - missing FX rate raises ValueError; raise_bp 0 and 5001 raise ValueError
  - by_country sorting
tests/repositories/test_insight_repository.py: fx_rates returns the right mapping; terminated excluded; filters work.
tests/routers/test_insights_what_if_api.py: both endpoints return the right shape; raise_bp 0 and 5001 return 422; missing department returns 422; unknown department returns 200 with zeros; filters narrow the result; all numbers are integers.
tests/test_seed_integration.py: with 3,000 seeded employees, bring-to-band-min cost > 0 and employees_affected is between 1% and 6% of employees.

Also add backend/scripts/benchmark_insights.py: seeds 10,000 employees in a temp DB and times every insight endpoint (benchmarks, bands, outliers, equity if present, both what-if endpoints), printing milliseconds. Target is under 500 ms each. Do not assert in CI.

## Frontend rules (follow strictly)
1. Keep the existing structure: api/, hooks/, components/, pages/, lib/, constants/. All server data goes through React Query. No fetch in components, no useEffect for fetching.
2. NEVER do money or percentage math in the UI. Only format integers for display (formatMinorUnits exists). The raise percent the user types is converted to integer basis points by STRING parsing only.
3. Ant Design components only (Card, Statistic, Table, Form, Input, Select, Button, Empty, Alert, Skeleton). No new chart library. Strict TypeScript, no `any`. Named constants. Mirror the backend response types exactly.
4. Handle loading, empty and error states (reuse ErrorBanner with Retry).
5. Tests: Vitest + Testing Library with the existing renderWithQueryClient helper, mocked api module, no real network.

## Frontend: files
- src/lib/percentToBasisPoints.ts (+ tests): parse a user-typed percent string with no floats. "5" -> 500, "2.5" -> 250, "0.05" -> 5, " 5 " -> 500. Max 2 decimal places. Return { ok: true, basisPoints } or { ok: false, reason }. Invalid: "", "abc", "-1", "7.255", "5%", below 0.01 or above 50. Export MIN and MAX as named constants matching the backend (1 and 5000).
- src/constants/navigation.ts: add "What-if" at /insights/what-if. Add the route in App.tsx.
- src/api/types.ts and src/api/insights.ts: fetchBringToBandMin(query, signal), fetchRaiseCost(query, signal). Types mirror the backend.
- src/hooks/useBringToBandMinQuery.ts and useRaiseCostQuery.ts. The raise query takes an `enabled` flag; do not fetch until the user submits.
- src/pages/WhatIfPage.tsx with two Cards:
  1. "Bring everyone to band minimum": loads automatically; optional country filter. Statistic cards for total cost (USD) and employees affected; a Table by country: Country, Employees affected, Cost (local currency), Cost (USD). When cost is 0 show "Everyone is within band".
  2. "Give a department a raise": a Form with Department (Select, reuse filterOptions), Percent (text Input), optional Country, and a Calculate button. Validate with percentToBasisPoints and show the inline error; an invalid value does not send a request. The submitted values live in state and drive the query's `enabled`. Results: employees affected, cost (USD), current payroll -> new payroll (USD), and a by-country Table. When no employees match show "No employees in this selection".

## Frontend: tests
- lib/percentToBasisPoints.test.ts: all the valid and invalid examples above.
- WhatIfPage, card 1: renders cost and counts formatted in USD; the zero state message; country filter changes the request; error state with Retry.
- WhatIfPage, card 2: invalid percent shows the error and sends no request; valid input sends raise_bp as an integer; results render formatted USD; empty-selection message.
Name each test for the behavior it checks. Use small factories for fake responses.

## Do NOT
- Do not add auth, Docker, GitHub Actions, charts, saving of scenarios, or any other insight.
- Do not use float for money, rates or percentages anywhere. Do not do math in the UI.
- Do not disable lint rules or use `any` to get things passing.

## Done when
- `cd backend && pytest && ruff check .` pass
- `cd frontend && npm test && npm run build` and the lint/type check pass
- With the DB seeded and both apps running, the What-if page shows a real cost for scenario 1 and a result for scenario 2
- Finish by listing every file added or changed and any assumption you made.
```

### 2026-10-24 17:19 IST - Dashboard home page

```text
You are working in an existing monorepo with a Vite + React + TypeScript (strict) + Ant Design + React Query + react-router-dom + Vitest frontend. Backend endpoints already exist: /insights/equity, /insights/bands, /insights/outliers and /insights/what-if/bring-to-band-min, with React Query hooks (useEquityQuery, useBandsQuery, useOutliersQuery, useBringToBandMinQuery), formatters (formatMinorUnits, formatBasisPoints with describeGap) and pages for each. Implement ONLY a dashboard home page. No backend changes and no new endpoints.

## What it does
A home page at "/" titled "How we pay people" with five headline cards, each showing one number and linking to the page with the detail.

## Rules (follow strictly)
1. Keep the existing structure: hooks/, components/, pages/, lib/, constants/. All server data goes through the EXISTING React Query hooks. Do not fetch in components and do not use useEffect for fetching. Do not duplicate API calls or types.
2. NEVER do money, ratio or percentage math in the UI. Only format integers for display with the existing helpers. Do not add or subtract numbers from the API.
3. Ant Design components only (Row, Col, Card, Statistic, Skeleton, Alert, Typography, Tag, Empty). No chart library. Strict TypeScript, no `any`. Named constants.
4. Each card has its OWN loading, error (message plus a Retry button calling that query's refetch) and empty state. One failing query must never blank the other cards.
5. Tests: Vitest + Testing Library with the existing renderWithQueryClient helper, mocked hooks or api module, no real network.

## Files
- src/hooks/useDashboardData.ts: a small hook that calls the existing hooks with summary-sized requests and returns one object per card ({ data, isLoading, isError, refetch }). Requests: equity with no filters; bands with page_size=1 and no filters (read the summary counts); outliers with page_size=1 (read total); bring-to-band-min with no filters. Keep the raw responses; do no arithmetic.
- src/components/dashboard/HeadlineCard.tsx: a presentational card taking title, value (ReactNode), caption, link path, and loading, error and onRetry props. The whole card title links to the route using react-router Link.
- src/pages/DashboardPage.tsx: a responsive grid (Row and Col) of five cards:
  1. Pay equity: the adjusted gap (formatBasisPoints), with the raw gap beneath as a caption and describeGap text. Null gap shows "Not enough data". Links to /insights/equity.
  2. Below band: summary.below_min count. Caption: "paid under their band minimum". Links to /insights/attention?tab=bands&status=below_min if the Attention page reads that param, otherwise /insights/attention?tab=bands.
  3. Above band: summary.above_max count. Caption: "paid over their band maximum". Links to the bands tab.
  4. Outliers: total count. Caption: "more than 20% from their peer-group median". Links to /insights/attention?tab=outliers.
  5. Cost to reach band minimum: total_cost_usd_minor with formatMinorUnits in USD. Caption: "{employees_affected} employees affected, per year". When the cost is 0 show "Everyone is within band". Links to /insights/what-if.
- src/constants/navigation.ts: add "Dashboard" as the FIRST item at "/". Update App.tsx routes so "/" renders DashboardPage (it no longer redirects to /employees) and the menu highlights correctly.
- If AttentionPage does not yet read a `status` query param on the bands tab, do not change it; link to the tab only.

## Tests
- DashboardPage: each card renders its number from mocked data; the equity card shows "Not enough data" for null gaps; the cost card shows "Everyone is within band" at zero; each card links to the right route; one failed query shows an error with Retry in that card only while the other four still render; clicking Retry calls that query's refetch; loading shows skeletons.
- App/navigation: the menu lists Dashboard first; "/" renders the dashboard; the active item highlights correctly.
Name each test for the behavior it checks. Use small factories for fake responses.

## Do NOT
- Do not add backend code, new endpoints, charts, auth, Docker or GitHub Actions.
- Do not do any arithmetic on API numbers in the UI.
- Do not disable lint rules or use `any`.

## Done when
- `cd frontend && npm test && npm run build` and the lint/type check pass
- With the DB seeded and both apps running, "/" shows five cards with real numbers and each link goes to the right page
- Finish by listing every file added or changed and any assumption you made.
```

### 2026-10-24 17:31 IST - Dashboard graphs

```text
shopw graphs insytead of numbers in dashbaord
```

### 2026-10-24 17:34 IST - Band-minimum cost pie chart

```text
[Cost to reach band minimum](http://localhost:5173/insights/what-if) show pie chatt in it
```

### 2026-10-24 17:36 IST - Chart library request

```text
use r chrtjs library and do it again
```

### 2026-10-24 17:40 IST - Removing the pay equity card

```text
remove Pay equity card
```

### 2026-10-24 17:43 IST - Salary history - initial prerequisite check

```text
You are working in an existing monorepo: FastAPI + SQLAlchemy 2.x + SQLite backend, and a Vite + React + TypeScript (strict) + Ant Design + React Query + react-router-dom + Vitest frontend. Already built: models (including the SalaryHistory model and table, and last_raise_date on Employee), money module, seed script (which already inserts one SalaryHistory row per employee with a raise), employee list and table, insights, and employee create/edit/delete (commit 11). Implement ONE feature end to end: salary history. Backend first, tests first, then the UI. Reuse existing code; do not duplicate it.

FIRST CHECK: confirm an employee update endpoint (PUT or PATCH /employees/{id}) and its service already exist. If they do not, STOP and tell me that commit 11 must be done first. Do not build employee editing in this commit.

## What the feature does
1. Every time an employee's salary changes through the update endpoint, record one history row: old salary, new salary, currency, and when it changed.
2. Show an employee's salary history (newest first) in the UI, with the size of each change.

## Backend rules (follow strictly)
1. Layering: routers -> services -> repositories -> models. Services are pure where possible, with NO FastAPI imports. The repository is the only code that builds SQL. Routers only parse HTTP params and return schemas.
2. NEVER use floats for money or percentages. Salaries are integer minor units. Percentage change is integer basis points (10000 = 100%), rounded half-even with the existing round_half_even_div helper.
3. No datetime.now() or date.today() inside services or repositories. Inject a clock: a `Clock` callable returning datetime, provided through a FastAPI dependency (default: current UTC time) so tests can pass a fixed time.
4. The employee update and the history insert happen in ONE transaction. If the history insert fails, the salary change must roll back too.
5. Write the tests BEFORE the implementation, with expected values computed by hand (show the arithmetic in comments). Fast, deterministic, no network, no randomness.
6. Small single-purpose files, type hints everywhere, named constants, descriptive names, comments only for the "why".

## Backend: behavior
- History is recorded only when salary_minor actually changes. Updating other fields (name, title, department, and so on) writes no history row. Saving the same salary again writes no row.
- Currency changes are NOT supported in this feature: if an update changes the currency, the endpoint returns 422 with a clear message ("changing currency is not supported"). If the existing update already allows it, change it to reject.
- When the salary goes UP, set the employee's last_raise_date to the change date. When it goes down, leave last_raise_date unchanged.
- salary_usd_minor must be recomputed with the money module on every salary change (confirm commit 11 does this; fix it if not).
- Creating an employee writes no history row (the first salary is the starting point). Deleting an employee leaves its history in place only if the delete is a soft delete; if the existing delete is a hard delete, also delete that employee's history rows in the same transaction.

## Backend: files
backend/app/services/salary_history.py (pure)
  - SalaryChange dataclass: old_salary_minor, new_salary_minor, currency, changed_at, change_minor (new - old, signed), change_bp (int or None)
  - build_salary_change(old_minor, new_minor, currency, changed_at) -> SalaryChange | None. Returns None when old == new. change_bp = round_half_even_div(change_minor * 10000, old_minor), and None when old_minor is 0.
backend/app/repositories/salary_history_repository.py
  - SalaryHistoryRepository(session): add(employee_id, change) and list_for_employee(employee_id) -> list of rows ordered by changed_at descending, then id descending (stable).
Existing employee update service: after validating, call build_salary_change; if it returns a change, add the history row and apply the last_raise_date rule, all in the same transaction as the employee update.
backend/app/schemas/salary_history.py: SalaryHistoryEntryOut (old_salary_minor, new_salary_minor, currency, changed_at, change_minor, change_bp) and SalaryHistoryResponse (items).
backend/app/routers/employees.py (or a new router file included in main.py): GET /employees/{employee_id}/salary-history -> { items: [...] } with change_minor and change_bp computed per row. For rows that were seeded, compute them the same way from old and new. An unknown employee returns 404; an employee with no history returns 200 with an empty list.
Add the Clock dependency in backend/app/dependencies.py (or the existing equivalent).

## Backend: tests (write first)
tests/services/test_salary_history.py (hand-computed):
  - old 1000 -> new 1100: change_minor 100, change_bp 1000
  - old 1000 -> new 900: change_minor -100, change_bp -1000
  - old 3 -> new 4: 3333.33 bp rounds to 3333
  - old 32 -> new 33: 312.5 bp rounds half-even to 312
  - old 2 -> new 3: 5000
  - old 0 -> new 500: change_bp is None
  - old == new returns None
tests/repositories/test_salary_history_repository.py: add then list returns newest first; ties on changed_at are ordered by id descending; histories of two employees do not mix.
tests/services/test_employee_update_history.py (in-memory DB, fixed clock):
  - changing salary writes exactly one history row with the right old, new, currency and changed_at
  - changing only the name writes none
  - saving an identical salary writes none
  - a raise sets last_raise_date to the fixed date; a cut leaves it unchanged
  - salary_usd_minor is recomputed after a change
  - a currency change is rejected and nothing is written
  - if the history insert is forced to fail (use a fake repository that raises), the employee's salary is unchanged afterwards (transaction rolled back)
tests/routers/test_salary_history_api.py: 200 and response shape; newest first; unknown employee returns 404; no history returns an empty list; after a PUT that changes the salary, the endpoint shows the new row; all numbers in the JSON are integers.
tests/test_seed_integration.py: pick a seeded employee with a raise and assert the endpoint returns one entry whose change_bp is positive.

## Frontend rules (follow strictly)
1. Keep the existing structure: api/, hooks/, components/, pages/, lib/, constants/. All server data goes through React Query. No fetch in components, no useEffect for fetching.
2. NEVER do money or percentage math in the UI. Format only: formatMinorUnits (exists), formatBasisPoints (reuse if it exists from the pay equity commit; otherwise create it with tests: 1000 -> "10.00%", -150 -> "-1.50%", 0 -> "0.00%", integer/string operations only). For a signed money change, format the absolute value with formatMinorUnits and add the sign from the sign of change_minor.
3. Ant Design components only (Drawer, Table or Timeline, Tag, Empty, Skeleton, Button, Tooltip). Strict TypeScript, no `any`. Named constants. Mirror the backend response types exactly.
4. Handle loading, empty and error states (reuse ErrorBanner with Retry).
5. Tests: Vitest + Testing Library with the existing renderWithQueryClient helper, mocked api module, no real network.

## Frontend: files
- src/api/types.ts and src/api/employees.ts: SalaryHistoryEntry, SalaryHistoryResponse, fetchSalaryHistory(employeeId, signal).
- src/hooks/useSalaryHistoryQuery.ts: useQuery keyed ['salary-history', employeeId], enabled only when an employeeId is provided.
- src/components/SalaryHistoryDrawer.tsx: an Ant Design Drawer titled "Salary history - {employee name}". Body: a Table with columns Date (formatDate), Old salary, New salary (both in the employee's currency), Change (a Tag: green with "+", red with "-", showing the signed amount and the formatBasisPoints percentage; "n/a" for the percentage when change_bp is null). Newest first. Empty state: "No salary changes recorded". Loading skeleton and error banner with Retry.
- src/components/EmployeeTable.tsx: add an actions column with a "History" button (use the existing actions column from commit 11 if present). It calls an onViewHistory(employee) prop.
- src/pages/EmployeesPage.tsx: holds the selected employee for the drawer in state and renders SalaryHistoryDrawer.
- After a successful employee edit (commit 11 mutation), invalidate the ['salary-history', id] query and the employees list query so the history and table refresh.

## Frontend: tests
- SalaryHistoryDrawer: renders rows newest first with formatted old, new and change; a raise shows a green "+" tag and a cut shows a red "-" tag; a null percentage shows "n/a"; the empty state; the error state with Retry.
- EmployeesPage: clicking History opens the drawer for that employee and requests that employee's id; closing the drawer works.
- After a successful edit that changes the salary, the history query is invalidated (assert it is refetched).
- lib/formatBasisPoints tests if you create it.
Name each test for the behavior it checks. Use small factories for fake entries.

## Do NOT
- Do not build employee create/edit/delete here, add auth, Docker, GitHub Actions, charts, or any other insight.
- Do not use float for money or percentages anywhere. Do not do math in the UI.
- Do not use datetime.now() or date.today() outside the Clock dependency.
- Do not disable lint rules or use `any`.

## Done when
- `cd backend && pytest && ruff check .` pass
- `cd frontend && npm test && npm run build` and the lint/type check pass
- With the DB seeded and both apps running: editing an employee's salary adds a row in their history drawer immediately, editing only their name does not, and a seeded employee's drawer shows their seeded raise
- Finish by listing every file added or changed and any assumption you made.
```

### 2026-10-24 17:45 IST - Employee create, edit and delete - truncated request

This message was truncated; the next entry contains the complete request supplied as an attachment.

```text
You are working in an existing monorepo: FastAPI + SQLAlchemy 2.x + SQLite backend, and a Vite + React + TypeScript (strict) + Ant Design + React Query + react-router-dom + Vitest frontend. Already built: models (Employee, SalaryBand, SalaryHistory, FxRate), the money module (app/money.py: Money, to_usd, supported currencies and exponents, FX_RATE_SCALE), seed script, GET /employees with an employee table page, insights (benchmarks, bands, outliers, what-if, equity), and the dashboard. Implement ONE feature end to end: create, edit and delete employees. Backend first, tests first, then the UI. Reuse existing code; do not duplicate it. Do not add anything outside this scope.

## What the feature does
The HR manager can add an employee, edit one, and delete one from the employee table. After any change, the table and all insight pages show fresh numbers.

## Backend rules (follow strictly)
1. Layering: routers -> services -> repositories -> models. Services hold validation and business rules and receive the repository as an argument; they import NO FastAPI or SQLAlchemy session code. The repository is the only code that builds SQL. Routers only parse HTTP and return schemas.
2. NEVER use floats for money. The API accepts and returns salary_minor as an integer in the employee's currency minor units. salary_usd_minor is NEVER accepted from the client: the server computes it with the existing money module and the fx_rates table (an FX rate must exist for the currency, otherwise return 422 with a clear message).
3. Each write endpoint is ONE transaction: everything commits together or rolls back together. Follow the existing session pattern.
4. Keep the update logic in ONE service function, update_employee(repository, employee_id, data), so a later commit can extend it. Do not spread it across the router.
5. Write the tests BEFORE the implementation. Tests are fast, deterministic, no network, no randomness.
6. Small single-purpose files, type hints everywhere, named constants, descriptive names, comments only for the "why".

## Backend: API design
- GET /employees/{id} -> EmployeeOut (404 if unknown).
- POST /employees -> 201 with EmployeeOut.
- PUT /employees/{id} -> 200 with EmployeeOut (full replacement of the editable fields; 404 if unknown).
- DELETE /employees/{id} -> 204 (404 if unknown).

## Backend: input schema (EmployeeInput in schemas/employee.py; used for both POST and PUT)
name (1-200 chars after trimming, not blank), email (trimmed, lower-cased, simple pattern check: one "@", something on both sides, a dot in the domain; do NOT use Pydantic EmailStr, because seeded emails use the reserved .example domain and would be rejected), title, department, country (2 uppercase letters), currency (3 uppercase letters, must be a supported currency), salary_minor (int, > 0), level (1-6), gender, employment_type, status (use the existing enums), hire_date (date), manager_id (optional int).
NOT in the input: id, salary_usd_minor, last_raise_date. last_raise_date is untouched by create (null) and update (preserved).
Unknown or extra fields are rejected (extra = "forbid").

## Backend: business rules (services/employee_service.py)
- Email must be unique (case-insensitive): a duplicate on create, or on update to another employee's email, returns 409 with a clear message. Updating an employee while keeping their own email is fine.
- manager_id, if given, must reference an existing employee (422 otherwise), must not be the employee themselves (422), and must not create a management cycle (422). Implement the cycle check as a pure function detect_management_cycle(employee_id, new_manager_id, get_manager_id) that walks up the chain.
- Currency cannot be changed on update (422 with "changing currency is not supported"). On create any supported currency is allowed.
- Delete: if the employee is the manager of other employees, return 409 with the message "employee has direct reports; reassign them first". Otherwise delete the employee AND their salary_history rows in the same transaction (the foreign key requires it).
- Create and update recompute salary_usd_minor with the money module. Update changes nothing else automatically.
- Add small domain errors (EmployeeNotFound, DuplicateEmail, InvalidManager, UnsupportedChange, HasDirectReports, MissingFxRate) in services/errors.py and map them to HTTP status codes in ONE place (an exception handler or a small mapping in the router module), not scattered try/except blocks.

## Backend: files
backend/app/schemas/employee.py: add EmployeeInput (EmployeeOut exists).
backend/app/services/errors.py
backend/app/services/management_chain.py (pure): detect_management_cycle
backend/app/services/employee_service.py: create_employee, update_employee, delete_employee, get_employee
backend/app/repositories/employee_repository.py: add get(id), get_by_email(email) (case-insensitive), add(employee), delete(employee), has_direct_reports(id), get_manager_id(id), delete_salary_history_for(id), and fx_rates() if not already present.
backend/app/routers/employees.py: the four endpoints above, using the shared error mapping.

## Backend: tests (write first)
tests/services/test_management_chain.py (pure): no manager is fine; a simple valid chain; self as manager is a cycle; A->B->C then making C the manager of A is a cycle; unrelated manager is fine.
tests/services/test_employee_service.py (in-memory DB, fixtures from conftest):
  - create computes salary_usd_minor correctly (INR example with a known rate and arithmetic in a comment)
  - create with a duplicate email in a different letter case raises DuplicateEmail
  - create with a currency that has no FX rate raises MissingFxRate
  - create with an unknown manager_id raises InvalidManager
  - update changes fields and recomputes salary_usd_minor when salary changes
  - update keeping the same email succeeds; changing to another employee's email raises DuplicateEmail
  - update with a different currency raises UnsupportedChange
  - update preserves last_raise_date
  - update that creates a management cycle raises InvalidManager
  - delete removes the employee and their salary_history rows
  - delete of someone with direct reports raises HasDirectReports and deletes nothing
  - unknown id raises EmployeeNotFound for get, update and delete
tests/routers/test_employees_write_api.py: POST returns 201 and the new employee appears in GET /employees; POST with blank name, level 0, level 7, salary 0, an invalid email, an unsupported currency and an extra field each return 422; duplicate email returns 409; PUT returns 200 and the change is visible; PUT or DELETE of an unknown id returns 404; DELETE returns 204 and the employee is gone; DELETE with direct reports returns 409; all money fields in responses are integers.
tests/test_insights_refresh.py: after creating a below-band employee through the API, the bands summary below_min count increases by one (shows the insights
```

### 2026-10-24 17:46 IST - Employee create, edit and delete - complete pasted request

Source: user attachment "Pasted text #1".

```text
You are working in an existing monorepo: FastAPI + SQLAlchemy 2.x + SQLite backend, and a Vite + React + TypeScript (strict) + Ant Design + React Query + react-router-dom + Vitest frontend. Already built: models (Employee, SalaryBand, SalaryHistory, FxRate), the money module (app/money.py: Money, to_usd, supported currencies and exponents, FX_RATE_SCALE), seed script, GET /employees with an employee table page, insights (benchmarks, bands, outliers, what-if, equity), and the dashboard. Implement ONE feature end to end: create, edit and delete employees. Backend first, tests first, then the UI. Reuse existing code; do not duplicate it. Do not add anything outside this scope.

## What the feature does
The HR manager can add an employee, edit one, and delete one from the employee table. After any change, the table and all insight pages show fresh numbers.

## Backend rules (follow strictly)
1. Layering: routers -> services -> repositories -> models. Services hold validation and business rules and receive the repository as an argument; they import NO FastAPI or SQLAlchemy session code. The repository is the only code that builds SQL. Routers only parse HTTP and return schemas.
2. NEVER use floats for money. The API accepts and returns salary_minor as an integer in the employee's currency minor units. salary_usd_minor is NEVER accepted from the client: the server computes it with the existing money module and the fx_rates table (an FX rate must exist for the currency, otherwise return 422 with a clear message).
3. Each write endpoint is ONE transaction: everything commits together or rolls back together. Follow the existing session pattern.
4. Keep the update logic in ONE service function, update_employee(repository, employee_id, data), so a later commit can extend it. Do not spread it across the router.
5. Write the tests BEFORE the implementation. Tests are fast, deterministic, no network, no randomness.
6. Small single-purpose files, type hints everywhere, named constants, descriptive names, comments only for the "why".

## Backend: API design
- GET /employees/{id} -> EmployeeOut (404 if unknown).
- POST /employees -> 201 with EmployeeOut.
- PUT /employees/{id} -> 200 with EmployeeOut (full replacement of the editable fields; 404 if unknown).
- DELETE /employees/{id} -> 204 (404 if unknown).

## Backend: input schema (EmployeeInput in schemas/employee.py; used for both POST and PUT)
name (1-200 chars after trimming, not blank), email (trimmed, lower-cased, simple pattern check: one "@", something on both sides, a dot in the domain; do NOT use Pydantic EmailStr, because seeded emails use the reserved .example domain and would be rejected), title, department, country (2 uppercase letters), currency (3 uppercase letters, must be a supported currency), salary_minor (int, > 0), level (1-6), gender, employment_type, status (use the existing enums), hire_date (date), manager_id (optional int).
NOT in the input: id, salary_usd_minor, last_raise_date. last_raise_date is untouched by create (null) and update (preserved).
Unknown or extra fields are rejected (extra = "forbid").

## Backend: business rules (services/employee_service.py)
- Email must be unique (case-insensitive): a duplicate on create, or on update to another employee's email, returns 409 with a clear message. Updating an employee while keeping their own email is fine.
- manager_id, if given, must reference an existing employee (422 otherwise), must not be the employee themselves (422), and must not create a management cycle (422). Implement the cycle check as a pure function detect_management_cycle(employee_id, new_manager_id, get_manager_id) that walks up the chain.
- Currency cannot be changed on update (422 with "changing currency is not supported"). On create any supported currency is allowed.
- Delete: if the employee is the manager of other employees, return 409 with the message "employee has direct reports; reassign them first". Otherwise delete the employee AND their salary_history rows in the same transaction (the foreign key requires it).
- Create and update recompute salary_usd_minor with the money module. Update changes nothing else automatically.
- Add small domain errors (EmployeeNotFound, DuplicateEmail, InvalidManager, UnsupportedChange, HasDirectReports, MissingFxRate) in services/errors.py and map them to HTTP status codes in ONE place (an exception handler or a small mapping in the router module), not scattered try/except blocks.

## Backend: files
backend/app/schemas/employee.py: add EmployeeInput (EmployeeOut exists).
backend/app/services/errors.py
backend/app/services/management_chain.py (pure): detect_management_cycle
backend/app/services/employee_service.py: create_employee, update_employee, delete_employee, get_employee
backend/app/repositories/employee_repository.py: add get(id), get_by_email(email) (case-insensitive), add(employee), delete(employee), has_direct_reports(id), get_manager_id(id), delete_salary_history_for(id), and fx_rates() if not already present.
backend/app/routers/employees.py: the four endpoints above, using the shared error mapping.

## Backend: tests (write first)
tests/services/test_management_chain.py (pure): no manager is fine; a simple valid chain; self as manager is a cycle; A->B->C then making C the manager of A is a cycle; unrelated manager is fine.
tests/services/test_employee_service.py (in-memory DB, fixtures from conftest):
  - create computes salary_usd_minor correctly (INR example with a known rate and arithmetic in a comment)
  - create with a duplicate email in a different letter case raises DuplicateEmail
  - create with a currency that has no FX rate raises MissingFxRate
  - create with an unknown manager_id raises InvalidManager
  - update changes fields and recomputes salary_usd_minor when salary changes
  - update keeping the same email succeeds; changing to another employee's email raises DuplicateEmail
  - update with a different currency raises UnsupportedChange
  - update preserves last_raise_date
  - update that creates a management cycle raises InvalidManager
  - delete removes the employee and their salary_history rows
  - delete of someone with direct reports raises HasDirectReports and deletes nothing
  - unknown id raises EmployeeNotFound for get, update and delete
tests/routers/test_employees_write_api.py: POST returns 201 and the new employee appears in GET /employees; POST with blank name, level 0, level 7, salary 0, an invalid email, an unsupported currency and an extra field each return 422; duplicate email returns 409; PUT returns 200 and the change is visible; PUT or DELETE of an unknown id returns 404; DELETE returns 204 and the employee is gone; DELETE with direct reports returns 409; all money fields in responses are integers.
tests/test_insights_refresh.py: after creating a below-band employee through the API, the bands summary below_min count increases by one (shows the insights read live data).

## Frontend rules (follow strictly)
1. Keep the existing structure: api/, hooks/, components/, pages/, lib/, constants/. Server data goes through React Query (useQuery for reads, useMutation for writes). No fetch in components, no useEffect for fetching.
2. NEVER do money math with floats in the UI. The salary the user types is converted to integer minor units by STRING parsing only, using the currency's minor-unit exponent (read the exponent the same way formatMoney does: JPY 0, USD 2, and so on).
3. Ant Design components only (Drawer, Form, Input, InputNumber, Select, DatePicker, Button, Popconfirm, message, Tooltip). Strict TypeScript, no `any`. Named constants. Mirror the backend types exactly.
4. Handle loading, error and validation states. Server errors map to the form: a 409 duplicate-email error shows under the email field; other 422 messages show in an Alert at the top of the form; the form stays open and keeps its values.
5. Tests: Vitest + Testing Library with the existing renderWithQueryClient helper, mocked api module, no real network.

## Frontend: files
- src/lib/parseMoneyInput.ts (+ tests): parseMoneyInput(text, currency) -> { ok: true, amountMinor } | { ok: false, reason }. Trim spaces; allow an optional thousands separator "," (e.g. "1,00,000" and "100,000" both work); decimal places allowed only up to the currency exponent. Examples: ("1500.50", USD) -> 150050; ("1500", USD) -> 150000; ("1500.5", USD) -> 150050; ("1500.555", USD) -> invalid; ("1500", JPY) -> 1500; ("1500.5", JPY) -> invalid; ("", USD), ("abc", USD), ("-5", USD), ("0", USD) -> invalid; unknown currency -> invalid. Max 12 digits.
- src/lib/queryKeys.ts: central query key constants for employees, benchmarks, bands, outliers, equity, what-if and salary-history, so keys are not hard-coded as strings in many places. Update the existing hooks to use them.
- src/lib/invalidateEmployeeData.ts: invalidates the employees list and ALL insight queries (benchmarks, bands, outliers, equity, what-if, dashboard data) and salary-history, because any employee change can affect all of them.
- src/api/types.ts and src/api/employees.ts: EmployeeInput type; createEmployee, updateEmployee, deleteEmployee. Extend the existing ApiError to carry the parsed `detail` from the response body so the UI can read the message.
- src/hooks/useEmployeeMutations.ts: useCreateEmployee, useUpdateEmployee, useDeleteEmployee (useMutation). On success call invalidateEmployeeData and show a success toast via Ant Design message.
- src/components/EmployeeFormDrawer.tsx: a Drawer with an Ant Design Form for create and edit modes. Fields: Name, Email, Title (Select), Department (Select), Country (Select), Currency (Select; DISABLED in edit mode with a Tooltip "Currency cannot be changed"), Salary (text input, shown in the selected currency, e.g. "1,50,000.00"), Level (1-6), Gender, Employment type, Status, Hire date (DatePicker; send "YYYY-MM-DD"), Manager ID (optional InputNumber). Required-field validation on the client. On submit convert the salary text with parseMoneyInput; if invalid show the field error and send no request. In edit mode pre-fill every field, converting salary_minor to the display text with a helper that uses integer/string operations only (add formatMinorUnitsPlain(amountMinor, currency) in lib/ with tests, no grouping separators, e.g. 150050 USD -> "1500.50").
- src/components/EmployeeTable.tsx: add an Actions column with Edit (opens the drawer in edit mode), History (keep a prop slot for the next commit, but do NOT render it yet) and Delete (Popconfirm "Delete this employee?"). Show a clear error toast for a 409 on delete (the message from the API).
- src/pages/EmployeesPage.tsx: an "Add employee" primary button above the table; holds the drawer state (closed, create, edit with the employee).
- src/constants/filterOptions.ts: reuse the existing option lists for the form selects.

## Frontend: tests
- lib/parseMoneyInput.test.ts: every example above.
- lib/formatMinorUnitsPlain.test.ts: USD, JPY, a value with a trailing zero, zero cents.
- lib/invalidateEmployeeData.test.ts: calling it invalidates the employees key and every insight key.
- EmployeeFormDrawer: required fields block submit; an invalid salary shows the error and sends no request; a valid create sends salary_minor as an integer and the right payload; edit mode pre-fills fields and disables currency; a 409 duplicate-email response shows the error under the email field and keeps the drawer open with values intact; other 422 messages show in the Alert.
- EmployeesPage: clicking "Add employee" opens the create drawer; a successful create closes the drawer and refetches the list; clicking Edit opens the drawer with that employee; Delete asks for confirmation, calls the API on confirm and does nothing on cancel; a 409 on delete shows the API message and the row stays.
Name each test for the behavior it checks. Use small factories for fake employees.

## Do NOT
- Do not add salary history, auth, soft delete, bulk edit, CSV import or export, Docker or GitHub Actions.
- Do not accept salary_usd_minor or last_raise_date from the client.
- Do not use float for money anywhere. Do not use Pydantic EmailStr.
- Do not use datetime.now() or date.today() (no future-date checks yet).
- Do not disable lint rules or use `any`.

## Done when
- `cd backend && pytest && ruff check .` pass
- `cd frontend && npm test && npm run build` and the lint/type check pass
- With the DB seeded and both apps running: you can add an employee, edit them, and delete them; a deliberately underpaid new employee shows up on the Needs attention page and the dashboard counts change; the duplicate-email error appears on the field
- Finish by listing every file added or changed and any assumption you made.
```

### 2026-10-25 08:30 IST - Salary history - implementation request

```text
You are working in an existing monorepo: FastAPI + SQLAlchemy 2.x + SQLite backend, and a Vite + React + TypeScript (strict) + Ant Design + React Query + react-router-dom + Vitest frontend. Already built: models (including the SalaryHistory model and table, and last_raise_date on Employee), money module, seed script (which already inserts one SalaryHistory row per employee with a raise), employee list and table, insights, and employee create/edit/delete (commit 11). Implement ONE feature end to end: salary history. Backend first, tests first, then the UI. Reuse existing code; do not duplicate it.

FIRST CHECK: confirm an employee update endpoint (PUT or PATCH /employees/{id}) and its service already exist. If they do not, STOP and tell me that commit 11 must be done first. Do not build employee editing in this commit.

## What the feature does
1. Every time an employee's salary changes through the update endpoint, record one history row: old salary, new salary, currency, and when it changed.
2. Show an employee's salary history (newest first) in the UI, with the size of each change.

## Backend rules (follow strictly)
1. Layering: routers -> services -> repositories -> models. Services are pure where possible, with NO FastAPI imports. The repository is the only code that builds SQL. Routers only parse HTTP params and return schemas.
2. NEVER use floats for money or percentages. Salaries are integer minor units. Percentage change is integer basis points (10000 = 100%), rounded half-even with the existing round_half_even_div helper.
3. No datetime.now() or date.today() inside services or repositories. Inject a clock: a `Clock` callable returning datetime, provided through a FastAPI dependency (default: current UTC time) so tests can pass a fixed time.
4. The employee update and the history insert happen in ONE transaction. If the history insert fails, the salary change must roll back too.
5. Write the tests BEFORE the implementation, with expected values computed by hand (show the arithmetic in comments). Fast, deterministic, no network, no randomness.
6. Small single-purpose files, type hints everywhere, named constants, descriptive names, comments only for the "why".

## Backend: behavior
- History is recorded only when salary_minor actually changes. Updating other fields (name, title, department, and so on) writes no history row. Saving the same salary again writes no row.
- Currency changes are NOT supported in this feature: if an update changes the currency, the endpoint returns 422 with a clear message ("changing currency is not supported"). If the existing update already allows it, change it to reject.
- When the salary goes UP, set the employee's last_raise_date to the change date. When it goes down, leave last_raise_date unchanged.
- salary_usd_minor must be recomputed with the money module on every salary change (confirm commit 11 does this; fix it if not).
- Creating an employee writes no history row (the first salary is the starting point). Deleting an employee leaves its history in place only if the delete is a soft delete; if the existing delete is a hard delete, also delete that employee's history rows in the same transaction.

## Backend: files
backend/app/services/salary_history.py (pure)
  - SalaryChange dataclass: old_salary_minor, new_salary_minor, currency, changed_at, change_minor (new - old, signed), change_bp (int or None)
  - build_salary_change(old_minor, new_minor, currency, changed_at) -> SalaryChange | None. Returns None when old == new. change_bp = round_half_even_div(change_minor * 10000, old_minor), and None when old_minor is 0.
backend/app/repositories/salary_history_repository.py
  - SalaryHistoryRepository(session): add(employee_id, change) and list_for_employee(employee_id) -> list of rows ordered by changed_at descending, then id descending (stable).
Existing employee update service: after validating, call build_salary_change; if it returns a change, add the history row and apply the last_raise_date rule, all in the same transaction as the employee update.
backend/app/schemas/salary_history.py: SalaryHistoryEntryOut (old_salary_minor, new_salary_minor, currency, changed_at, change_minor, change_bp) and SalaryHistoryResponse (items).
backend/app/routers/employees.py (or a new router file included in main.py): GET /employees/{employee_id}/salary-history -> { items: [...] } with change_minor and change_bp computed per row. For rows that were seeded, compute them the same way from old and new. An unknown employee returns 404; an employee with no history returns 200 with an empty list.
Add the Clock dependency in backend/app/dependencies.py (or the existing equivalent).

## Backend: tests (write first)
tests/services/test_salary_history.py (hand-computed):
  - old 1000 -> new 1100: change_minor 100, change_bp 1000
  - old 1000 -> new 900: change_minor -100, change_bp -1000
  - old 3 -> new 4: 3333.33 bp rounds to 3333
  - old 32 -> new 33: 312.5 bp rounds half-even to 312
  - old 2 -> new 3: 5000
  - old 0 -> new 500: change_bp is None
  - old == new returns None
tests/repositories/test_salary_history_repository.py: add then list returns newest first; ties on changed_at are ordered by id descending; histories of two employees do not mix.
tests/services/test_employee_update_history.py (in-memory DB, fixed clock):
  - changing salary writes exactly one history row with the right old, new, currency and changed_at
  - changing only the name writes none
  - saving an identical salary writes none
  - a raise sets last_raise_date to the fixed date; a cut leaves it unchanged
  - salary_usd_minor is recomputed after a change
  - a currency change is rejected and nothing is written
  - if the history insert is forced to fail (use a fake repository that raises), the employee's salary is unchanged afterwards (transaction rolled back)
tests/routers/test_salary_history_api.py: 200 and response shape; newest first; unknown employee returns 404; no history returns an empty list; after a PUT that changes the salary, the endpoint shows the new row; all numbers in the JSON are integers.
tests/test_seed_integration.py: pick a seeded employee with a raise and assert the endpoint returns one entry whose change_bp is positive.

## Frontend rules (follow strictly)
1. Keep the existing structure: api/, hooks/, components/, pages/, lib/, constants/. All server data goes through React Query. No fetch in components, no useEffect for fetching.
2. NEVER do money or percentage math in the UI. Format only: formatMinorUnits (exists), formatBasisPoints (reuse if it exists from the pay equity commit; otherwise create it with tests: 1000 -> "10.00%", -150 -> "-1.50%", 0 -> "0.00%", integer/string operations only). For a signed money change, format the absolute value with formatMinorUnits and add the sign from the sign of change_minor.
3. Ant Design components only (Drawer, Table or Timeline, Tag, Empty, Skeleton, Button, Tooltip). Strict TypeScript, no `any`. Named constants. Mirror the backend response types exactly.
4. Handle loading, empty and error states (reuse ErrorBanner with Retry).
5. Tests: Vitest + Testing Library with the existing renderWithQueryClient helper, mocked api module, no real network.

## Frontend: files
- src/api/types.ts and src/api/employees.ts: SalaryHistoryEntry, SalaryHistoryResponse, fetchSalaryHistory(employeeId, signal).
- src/hooks/useSalaryHistoryQuery.ts: useQuery keyed ['salary-history', employeeId], enabled only when an employeeId is provided.
- src/components/SalaryHistoryDrawer.tsx: an Ant Design Drawer titled "Salary history - {employee name}". Body: a Table with columns Date (formatDate), Old salary, New salary (both in the employee's currency), Change (a Tag: green with "+", red with "-", showing the signed amount and the formatBasisPoints percentage; "n/a" for the percentage when change_bp is null). Newest first. Empty state: "No salary changes recorded". Loading skeleton and error banner with Retry.
- src/components/EmployeeTable.tsx: add an actions column with a "History" button (use the existing actions column from commit 11 if present). It calls an onViewHistory(employee) prop.
- src/pages/EmployeesPage.tsx: holds the selected employee for the drawer in state and renders SalaryHistoryDrawer.
- After a successful employee edit (commit 11 mutation), invalidate the ['salary-history', id] query and the employees list query so the history and table refresh.

## Frontend: tests
- SalaryHistoryDrawer: renders rows newest first with formatted old, new and change; a raise shows a green "+" tag and a cut shows a red "-" tag; a null percentage shows "n/a"; the empty state; the error state with Retry.
- EmployeesPage: clicking History opens the drawer for that employee and requests that employee's id; closing the drawer works.
- After a successful edit that changes the salary, the history query is invalidated (assert it is refetched).
- lib/formatBasisPoints tests if you create it.
Name each test for the behavior it checks. Use small factories for fake entries.

## Do NOT
- Do not build employee create/edit/delete here, add auth, Docker, GitHub Actions, charts, or any other insight.
- Do not use float for money or percentages anywhere. Do not do math in the UI.
- Do not use datetime.now() or date.today() outside the Clock dependency.
- Do not disable lint rules or use `any`.

## Done when
- `cd backend && pytest && ruff check .` pass
- `cd frontend && npm test && npm run build` and the lint/type check pass
- With the DB seeded and both apps running: editing an employee's salary adds a row in their history drawer immediately, editing only their name does not, and a seeded employee's drawer shows their seeded raise
- Finish by listing every file added or changed and any assumption you made.
```

### 2026-10-25 08:58 IST - Keeping artifact documentation aligned with implemented features

Selected folder: `/Users/deepkokje/Projects/StaffSense/artifacts`.

```text
for this folder, onlt keep current features whihc we implemented remove other stuff
```

### 2026-10-25 09:06 IST - Checking the prompt log

```text
is prompt.md updated?
```

### 2026-10-25 09:06 IST - Updating the prompt log

```text
add those prompts as well
```

### 2026-10-25 09:16 IST - Preparing demo API hosting

```text
we can go with option 1. start with apin hosting
```

### 2026-10-25 09:52 IST - Preparing demo UI hosting

```text
now ui deployment
```
