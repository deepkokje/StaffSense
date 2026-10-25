# StaffSense: Delivered Feature Summary

**Author:** @Deep Kokje  
**Last updated:** 25 Oct 2026

This document records completed work only. Current requirements are in
[REQUIREMENTS.md](./REQUIREMENTS.md); implementation boundaries are in
[arch.md](./arch.md).

## Delivered foundation

- Integer-minor-unit money with supported currency exponents, integer fixed FX
  rates and half-even conversion.
- Typed SQLAlchemy Employee, SalaryBand, SalaryHistory and FxRate models, shared
  metadata, engine and session dependency.
- Deterministic demo generation and loading for 10,000 employees, including
  salary bands, FX rates and historical raises.

## Delivered backend

| Feature | Result |
| --- | --- |
| Employee directory | Search, filters, server sorting and pagination, plus individual employee retrieval. |
| Employee writes | Create, full editable-field replacement and hard delete with shared domain-error mapping and atomic transactions. |
| Validation | Case-insensitive email uniqueness, supported currency and FX lookup, manager existence, cycle prevention, currency-change rejection and direct-report deletion protection. |
| Salary history | Actual salary changes recorded with an injected clock in the employee transaction; raise-date rules, signed integer changes, half-even basis points and newest-first retrieval. |
| Benchmarks | Shared peer grouping, interpolated percentiles and insufficient-data handling. |
| Band compliance | Summary counts, boundary classification, ratios, filtering and pagination. |
| Peer outliers | Median-based deviation, minimum group size, direction filtering and pagination. |
| What-if | Read-only band-minimum and department-raise cost reports, local aggregation and country-level USD conversion. |
| Performance check | Script that seeds an isolated temporary database and times the current insight endpoints. |

## Delivered frontend

- Dashboard at `/` with four cards: Below band, Above band, Outliers and Cost to
  reach band minimum. Accessible bar graphs and a Recharts cost pie retain exact
  value labels and link to detail pages.
- Employee directory with search, filters, sorting and pagination.
- Add/edit form drawer with currency-aware integer salary parsing, date selection,
  preserved values on failure and field-level duplicate-email errors.
- Confirmed deletion with clear conflict messages.
- Salary-history drawer with dated old/new salaries, signed amounts, green raise
  and red cut tags, percentages and an undefined-percentage label for zero bases.
- Benchmark page, Needs attention tabs and What-if calculators.
- Shared React Query keys and mutation invalidation for current employee,
  insight and salary-history data. Dashboard cards reuse insight queries.
- Loading, empty, error and retry states for data views.

## Verification completed

- Backend tests cover money conversion, half-even statistics, model constraints,
  repository filters, CRUD validation, management cycles, history ordering,
  atomic rollback, API responses and seeded-data integration.
- Frontend tests cover integer parsing and formatting, navigation, insight
  rendering, forms, confirmed deletion, salary-history states and refresh after
  employee edits.
- pytest and Ruff pass; Vitest and the strict TypeScript production build pass.
- Seeded-browser checks confirmed employee create/edit/delete, duplicate-email
  feedback and refreshed attention/dashboard counts.
- Seeded-browser checks confirmed an existing historical raise, a newly recorded
  salary change and no additional history from a name-only edit.

## Current behavior to preserve

- No floating-point monetary or percentage business calculations.
- Application layering remains routers -> services -> repositories -> models.
- Pure calculation functions remain independent of database and HTTP code.
- Employee updates and their salary-history inserts commit or roll back together.
- Eligible insight data includes ACTIVE and ON_LEAVE employees only.
- What-if scenarios do not modify employee salaries.
