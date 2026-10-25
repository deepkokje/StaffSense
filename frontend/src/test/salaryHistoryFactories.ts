import type { SalaryHistoryEntry, SalaryHistoryResponse } from "../api/types";

export function makeSalaryHistoryEntry(
  overrides: Partial<SalaryHistoryEntry> = {},
): SalaryHistoryEntry {
  return {
    old_salary_minor: 100000, new_salary_minor: 110000,
    currency: "USD", changed_at: "2026-10-25T09:30:00",
    change_minor: 10000, change_bp: 1000,
    ...overrides,
  };
}

export function makeSalaryHistoryResponse(
  items: SalaryHistoryEntry[] = [makeSalaryHistoryEntry()],
): SalaryHistoryResponse {
  return { items };
}
