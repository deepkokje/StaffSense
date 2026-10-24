import type { EmployeeOut, EmployeePage } from "../api/types";

const DEFAULT_EMPLOYEE: EmployeeOut = {
  id: 1,
  name: "Ada Lovelace",
  email: "ada@example.com",
  title: "Software Engineer",
  level: 3,
  department: "Engineering",
  country: "IN",
  currency: "INR",
  salary_minor: 123_456,
  salary_usd_minor: 1_500_000,
  gender: "FEMALE",
  employment_type: "FULL_TIME",
  hire_date: "2024-01-15",
  last_raise_date: null,
  status: "ACTIVE",
  manager_id: null,
};

export function makeEmployee(overrides: Partial<EmployeeOut> = {}): EmployeeOut {
  return { ...DEFAULT_EMPLOYEE, ...overrides };
}

export function makeEmployeePage(
  employees: EmployeeOut[] = [makeEmployee()],
  page = 1,
  pageSize = 25,
): EmployeePage {
  return {
    items: employees,
    total: employees.length,
    page,
    page_size: pageSize,
    total_pages: employees.length ? 1 : 0,
  };
}
