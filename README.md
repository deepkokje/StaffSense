# StaffSense

A bare-bones salary management monorepo using FastAPI, SQLAlchemy and SQLite
for the backend, and React, TypeScript, Ant Design and TanStack React Query
for the frontend.
No salary features or database tables are implemented yet.

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

The database engine and session factory are configured, but no tables are created.

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

TanStack React Query is available throughout the app through `AppProviders`,
which keeps one query client per mounted application using the library defaults.
Future API hooks can use `useQuery` and `useMutation` for server-state management.
No API calls or queries are implemented yet.

## Architecture

Backend dependencies flow from routers to services to repositories to models.
Routers handle HTTP only; services contain pure business functions, and only
repositories access the database. React components contain no business logic.
Future monetary values must use integer minor units and a currency code, never floats.
