# StaffSense

A bare-bones salary management monorepo using FastAPI, SQLAlchemy and SQLite
for the backend, and React, TypeScript, Ant Design and TanStack React Query
for the frontend.
Includes an employee directory, peer-group salary benchmarks, and band compliance
and outlier reporting, plus read-only what-if cost estimates.

## Backend

Requires Python 3.12. From the repository root:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
cd backend
pip install -e ".[dev]"
pytest
ruff check .
uvicorn app.main:app --reload
```

The backend runs at http://127.0.0.1:8000.
`GET /health` returns `{"status": "ok"}`.

Settings are read from environment variables, with these defaults:

| Variable | Default |
| --- | --- |
| `STAFFSENSE_APP_NAME` | `StaffSense` |
| `STAFFSENSE_DATABASE_URL` | `sqlite:///./staffsense.db` |

Create tables and load synthetic employees before querying a new database:

```sh
python -m scripts.seed
```

`GET /insights/benchmarks` groups ACTIVE and ON_LEAVE employees by title, level
and country. Repeatable `country`, `title` and `level` parameters narrow the groups.
Set `include_insufficient=false` to hide groups with fewer than five employees.
Each item has a `key` (`title`, `level`, `country`), `currency`, `headcount`,
`insufficient_data` and nullable `stats` (`min`, `p25`, `median`, `p75`, `max`).
Statistics use local-currency integer minor units and integer-only interpolated
percentiles with half-even rounding. Small groups expose no salary statistics.
Every peer group must use a single currency; incompatible currencies are rejected.

### Band compliance and outliers

- `GET /insights/bands` accepts repeatable `country`, `department`, `title` and
  `level` filters, plus `status=below_min|above_max`, `page` and `page_size`.
  It returns `summary`, `items`, `total`, `page` and `page_size`. Summary counts
  cover every eligible employee matching the group/department filters, regardless
  of the status filter or pagination. Employees without a matching salary band
  count as `no_band` and are not flagged. Band boundaries are inclusive.
- `GET /insights/outliers` accepts repeatable `country`, `title` and `level`
  filters, plus `direction=above|below`, `page` and `page_size`. It returns
  `items`, `total`, `page` and `page_size`. The calculation uses full peer groups
  of at least five people, across all departments, before filtering direction.
  Rounded absolute deviations must be strictly greater than 200 per-mille.

Both endpoints include only ACTIVE and ON_LEAVE employees. Pagination starts at
one, defaults to 25 rows, and allows at most 100. Out-of-range pages return an
empty list with the correct total. Compa-ratios and signed deviations are integer
per-mille (1000 = 100%), rounded half-even using integer arithmetic. Salaries and
gaps remain local-currency integer minor units. Currency mismatches are rejected;
ratios with a zero midpoint or peer median are undefined and raise an error.

### What-if cost

- `GET /insights/what-if/bring-to-band-min` accepts repeatable `country`,
  `department`, `title` and `level` filters. It calculates the cost of raising
  eligible employees below their band's minimum to that minimum. Missing bands
  are skipped.
- `GET /insights/what-if/raise` requires `department` and integer `raise_bp`
  (1 through 5000, where 500 means 5%), with an optional single `country`.
  Unknown departments return zero employees and zero costs.

Costs are annual base salary only, for ACTIVE and ON_LEAVE employees. Nothing is
saved. Responses include `employees_affected`, `total_cost_usd_minor`, and
`by_country` rows with `country`, `currency`, `employees_affected`,
`cost_local_minor` and `cost_usd_minor`, sorted by USD cost descending then country.
Raise responses also include `current_payroll_usd_minor` and
`new_payroll_usd_minor` (current payroll plus total cost).

Each employee's raise is rounded half-even in local minor units. Costs and
current payroll are summed locally per country before each total is converted
once using stored integer FX rates, avoiding employee-level FX rounding drift.
Missing required FX rates and mixed currencies within a country raise errors.
The raise employee count includes every selected employee, even when a tiny
raise rounds to zero local minor units.

Run the non-asserting benchmark against 10,000 synthetic employees in an isolated
temporary database:

```sh
python -m scripts.benchmark_insights
```

It times all current insight GET endpoints, including equity if later present.
The target is below 500 ms per call; timing results are printed, not asserted.

## Frontend

Requires Node.js 20 or newer. In another terminal, from the repository root:

```sh
cd frontend
npm install
npm test
npm run dev
```

Open the URL printed by Vite (normally http://localhost:5173).
For a type-checked production build, run `npm run build`.

The sidebar links to `/employees`, `/insights/benchmarks`,
`/insights/attention` and `/insights/what-if`; `/` redirects to `/employees`. Benchmark filters apply
immediately, and the table paginates the returned groups locally.
Needs attention uses server pagination and offers Outside band and Outliers vs
peers tabs. The selected tab is stored in `?tab=bands|outliers`. Clicking Below
min or Above max toggles a status filter without changing the summary counts.
Filter changes reset the relevant table to page one. TanStack React Query manages
all server data; the UI only formats monetary values and per-mille integers.
The What-if page loads band-minimum cost automatically and calculates a
department raise only after a valid form submission. Percentages are parsed as
strings into integer basis points, with at most two decimal places and a range
of 0.01% through 50%. Changing draft form values does not request a new scenario.
Set `VITE_API_BASE_URL` before starting or building the UI (default
`http://localhost:8000`). Production hosts must serve `index.html` for frontend
routes so direct links and refreshes work.

## Architecture

Backend dependencies flow from routers to services to repositories to models.
Routers handle HTTP only; services contain pure business functions, and only
repositories access the database. React components contain no business logic.
Monetary values use integer minor units and a currency code, never floats.
