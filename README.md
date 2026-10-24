# StaffSense

A bare-bones salary management monorepo using FastAPI, SQLAlchemy and SQLite
for the backend, and React, TypeScript, Ant Design and TanStack React Query
for the frontend.
Includes an employee directory and peer-group salary benchmarks.

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

The sidebar links to `/employees` and `/insights/benchmarks`; `/` redirects to
`/employees`. Benchmark filters apply immediately, and the table paginates the
returned groups locally. TanStack React Query manages all server data.
Set `VITE_API_BASE_URL` before starting or building the UI (default
`http://localhost:8000`). Production hosts must serve `index.html` for frontend
routes so direct links and refreshes work.

## Architecture

Backend dependencies flow from routers to services to repositories to models.
Routers handle HTTP only; services contain pure business functions, and only
repositories access the database. React components contain no business logic.
Monetary values use integer minor units and a currency code, never floats.
