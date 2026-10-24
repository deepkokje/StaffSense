# Salary Management Software: Requirements
24 Oct 2026 · @Deep Kokje

**Goal:** Replace ACME's Excel salary files with one web app that lets the HR manager answer three questions in seconds: are we paying fairly, are we paying consistently, and what would it cost to fix it?

**Persona:** One HR manager, 10,000 employees across multiple countries. Needs trusted numbers, fast answers, and no spreadsheet wrangling.

## Scope and features
The first screen is a dashboard of five headline insights. Each one names the action it drives.

| Priority | Feature | Question the HR manager asks | Action it drives |
| --- | --- | --- | --- |
| Headline | Pay equity | Is there a gender pay gap? Raw gap, and adjusted gap within the same title, level and country. | Remediation, compliance |
| Headline | Band compliance | Who is paid outside their salary band? Compa-ratio = salary ÷ band midpoint. | Fix under- and over-paid people |
| Headline | Outliers vs peers | Who deviates more than 20% from their peer-group median? | Review list |
| Headline | Pay benchmarks | What is the going rate for a title, level and country (min, p25, median, p75, max)? | Offers and reviews |
| Headline | What-if cost | What does it cost to lift everyone to band minimum, or give X% to a department? | Budget request |
| Core | Pay snapshot | What is our headcount, payroll and distribution by country, department and level? | Budget baseline |
| Core | Employee directory | Find, add, edit and delete employees; export the filtered view to CSV. | Replace Excel day to day |
| Stretch | Compression and inversion | Are new hires out-earning tenured peers, or reports out-earning managers? | Retention risk |
| Stretch | Pay progression | Who has gone longest without a raise? | Raise cycle planning |
| Stretch | Geo comparison | How does the same role pay across countries? | Location strategy |

**Foundations:**

- Salaries are stored in local currency and normalized to USD with a fixed rate table for cross-country views.
- Peer group = title + level + country. Groups under 5 people show "insufficient data", so stats stay meaningful and individuals stay unidentifiable.
- Each salary change records old value, new value and date.
- A deterministic seed script creates 10,000 employees with realistic patterns: a small planted gender gap, some out-of-band people, a few compression cases.

## Deliberately left out

- **Auth and RBAC:** one persona, and it adds time without showing core judgment. First thing to add for production, since salary data is sensitive.
- **Payroll, tax, bonuses, equity:** a different problem domain. Base salary only.
- **Live FX rates:** non-deterministic, and the insights don't need that precision. Rates are a configurable static table.
- **Excel import:** a one-time migration, so the seed script is enough here.
- **Approval workflows and full audit trail:** premature for v1. Salary history is enough.a

## Success criteria

- Directory loads in under 300 ms and each insight in under 500 ms at 10,000 rows.
- Every headline insight has unit tests, including empty, single-value and small-group cases.
- The seeded demo shows a visible pay gap, out-of-band people and a non-zero what-if cost.