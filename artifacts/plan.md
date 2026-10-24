# Salary Management Software: Plan
**Author:** @Deep Kokje · **Reviewer:** Incubyte team · **Last updated:** 24 Oct 2026

## Overview
ACME's HR team manages salaries for 10,000 employees across countries in Excel. This design replaces that with a web app whose first screen answers five questions: is there a gender pay gap, who is paid outside their band, who deviates from their peers, what is the going rate for a role, and what would it cost to fix it.

The backend is FastAPI with SQLite and the UI is React with Ant Design. Insight logic is pure functions over peer groups (title + level + country), so each one is unit-testable without a database.

A deterministic seed script creates 10,000 employees with planted patterns, so the demo shows real findings instead of an empty dashboard.

## Context
Excel cannot answer "how do we pay people?" reliably at this size. Salaries sit in many currencies, peers must be grouped by title, level and country, and bands and gender live in separate sheets. Each question means rebuilding pivot tables by hand, and two people get two answers. This project is the first step to one trusted source of pay data. The Requirements tab has the scope; this tab covers how to build it.

## Goals and Non-Goals
**Goals**

- Directory loads in under 300 ms and each insight in under 500 ms at 10,000 rows, checked with query timing logs.
- All five headline insights return correct results and are covered by unit tests, including small and empty groups.
- The seeded demo shows an equity gap, out-of-band people and a non-zero what-if cost.
**Non-goals:** auth and RBAC, payroll, tax, bonuses and equity, live FX rates, Excel import, and approval workflows. The Requirements tab gives the reason for each.

## How we plan to solve it
**Stack:** FastAPI + SQLAlchemy + SQLite, React + TypeScript (Vite) + Ant Design, pytest, Vitest. SQLite keeps setup trivial, and the repository layer lets you swap in Postgres later.

The browser talks to FastAPI routers. Routers call services, where all insight logic lives as pure functions. Services read through repositories, which are the only code that touches SQLite. The seed script writes the same tables.

[embed: node/1f24e5b3-ebb0]
Only repositories touch SQLite, so services stay pure and testable. The seed script writes the same tables.

In use, the HR manager opens the dashboard and sees the raw and adjusted gap side by side, clicks into the peer groups driving it, opens the outlier list, and runs the what-if cost to see what fixing it would take.


### How we will compute each insight

| Insight | Method |
| --- | --- |
| Pay equity | Raw gap = (median male − median female) ÷ median male. Adjusted gap = average of the same gap inside each peer group with both genders and at least 5 people, weighted by group size. |
| Band compliance | Compa-ratio = salary ÷ band midpoint. Below min or above max is flagged. |
| Outliers | % deviation from peer-group median; flag beyond ±20%. |
| Benchmarks | min, p25, median, p75, max per peer group. SQLite has no median, so group salaries in SQL and compute percentiles in Python (fast at 10k rows). |
| What-if cost | Sum of (band min − salary) for everyone below min, in USD; or X% × payroll for a chosen department. |
| Compression, progression, geo | Tenure vs. pay in a peer group; months since last raise; median per title and level indexed to a base country. |

## Testing approach
**Tests worth writing:**

- Percentiles and median: empty, single-value, even-count groups.
- Equity: no gap, planted gap, group with one gender only, group under 5.
- Bands: below min, above max, exactly on the boundary.
- Outliers: threshold edges and groups under 5.
- What-if: zero cost when everyone is in band; correct currency conversion.
- FX normalization and rounding.
- CRUD validation (negative salary, unknown currency, duplicate email) and salary-history creation on update.
- Filter and pagination combinations; seed determinism (same seed, 10,000 rows).
