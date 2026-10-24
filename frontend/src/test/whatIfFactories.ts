import type { BandMinCostReport, RaiseCostReport } from "../api/types";

export function makeBandMinCost(
  overrides: Partial<BandMinCostReport> = {},
): BandMinCostReport {
  return {
    total_cost_usd_minor: 123_456,
    employees_affected: 3,
    by_country: [{
      country: "IN", currency: "INR", employees_affected: 3,
      cost_local_minor: 10_288_000, cost_usd_minor: 123_456,
    }],
    ...overrides,
  };
}

export function makeRaiseCost(overrides: Partial<RaiseCostReport> = {}): RaiseCostReport {
  return {
    employees_affected: 4, total_cost_usd_minor: 15_000,
    current_payroll_usd_minor: 300_000, new_payroll_usd_minor: 315_000,
    by_country: [{
      country: "US", currency: "USD", employees_affected: 4,
      cost_local_minor: 15_000, cost_usd_minor: 15_000,
    }],
    ...overrides,
  };
}
