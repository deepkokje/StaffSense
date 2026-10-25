# StaffSense: Implemented Requirements

**Author:** @Deep Kokje  
**Last updated:** 25 Oct 2026

## Goal

Give one HR manager a searchable employee directory, salary comparisons and
read-only cost estimates for a multi-country workforce.

## Current features

| Feature | Implemented behavior |
| --- | --- |
| Dashboard | Home page titled "How we pay people" with four cards: Below band, Above band, Outliers and Cost to reach band minimum. Band and outlier cards use bar graphs; cost uses a Recharts country-cost pie. Each card links to its detail page and handles loading and errors independently. |
| Employee directory | Search name or email, filter employees, sort and paginate on the server. Display local salary and USD salary. |
| Employee management | Add, edit and permanently delete employees. Validate unique email, manager existence and management cycles. Reject currency changes and deletion of managers with direct reports. |
| Salary history | Record actual salary changes atomically with employee updates. Show newest-first history with old/new salary, signed change and percentage. Raises update the last raise date; cuts preserve it. |
| Peer benchmarks | Show minimum, p25, median, p75 and maximum salary by title, level and country. Groups with fewer than five employees show insufficient data. |
| Band compliance | Show below-minimum, within-band, above-maximum and missing-band counts, with a filtered and paginated attention list. |
| Peer outliers | Flag eligible employees more than 20% from their peer-group median. Support filters, direction and pagination. |
| What-if cost | Estimate the annual cost of reaching band minimum or giving a department a percentage raise. Scenarios are read-only. |

## Data and business rules

- Salaries are integer minor units plus a supported currency code. Supported
  currencies are USD, EUR, GBP, INR, JPY, CAD, AUD and SGD; JPY has no fractional
  minor units, and the others have two.
- FX rates are positive integers scaled by 1,000,000. The money module performs
  conversion with Decimal and half-even rounding.
- The server computes USD salary using stored FX rates; clients cannot supply
  USD salary or the last raise date.
- Employee writes require a positive salary, level 1 through 6 and valid input
  fields. Emails are trimmed, lower-cased and checked case-insensitively for
  uniqueness. Extra input fields are rejected.
- Insight calculations include ACTIVE and ON_LEAVE employees, not TERMINATED.
- Peer group means title + level + country. Local salary comparisons require
  compatible currencies.
- Band boundaries are inclusive. Employees without a band are counted separately
  and skipped by the band-minimum cost calculation.
- What-if raises use integer basis points from 1 through 5000. Per-employee raises
  round half-even locally; country totals are converted to USD once per country
  to avoid FX rounding drift.
- Salary history stores old salary, new salary, currency and change timestamp.
  Percentage changes use integer basis points and half-even rounding; a change
  from zero has no defined percentage.
- Creating an employee records no history. Saving the same salary or changing
  only other fields records no history. Hard deletion removes history in the
  same transaction as the employee.
- Successful employee writes invalidate employee, insight and history query
  caches so affected views reload current data.

## Demo data and validation

- Deterministic seeding supports a 10,000-employee demo with salary bands, fixed
  FX rates and existing salary-history entries.
- Backend tests cover money, statistics, validation, repositories, endpoints,
  salary-history transactions and seeded-data integration.
- Frontend tests cover formatting, parsing, forms, navigation, query refresh,
  history and loading/error/empty states.
- An isolated benchmark script times the implemented insight endpoints with
  10,000 employees. The target is below 500 ms per endpoint; timing is not a CI
  assertion.
