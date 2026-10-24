import type { BandsResponse, FlaggedEmployee, Outlier, OutliersResponse } from "../api/types";

export function makeFlaggedEmployee(overrides: Partial<FlaggedEmployee> = {}): FlaggedEmployee {
  return {
    employee_id: 1, name: "Ada Lovelace", department: "Engineering",
    title: "Software Engineer", level: 3, country: "US", currency: "USD",
    salary_minor: 70_000, band_min_minor: 80_000, band_mid_minor: 100_000,
    band_max_minor: 120_000, compa_ratio_permille: 700,
    status: "below_min", gap_to_band_minor: 10_000,
    ...overrides,
  };
}

export function makeBandsResponse(overrides: Partial<BandsResponse> = {}): BandsResponse {
  return {
    summary: { below_min: 3, within_band: 20, above_max: 2, no_band: 1 },
    items: [makeFlaggedEmployee()], total: 1, page: 1, page_size: 25,
    ...overrides,
  };
}

export function makeOutlier(overrides: Partial<Outlier> = {}): Outlier {
  return {
    employee_id: 2, name: "Grace Hopper", title: "Software Engineer",
    level: 3, country: "US", currency: "USD", salary_minor: 130_000,
    group_median_minor: 100_000, group_headcount: 7,
    deviation_permille: 300, direction: "above",
    ...overrides,
  };
}

export function makeOutliersResponse(overrides: Partial<OutliersResponse> = {}): OutliersResponse {
  return { items: [makeOutlier()], total: 1, page: 1, page_size: 25, ...overrides };
}
