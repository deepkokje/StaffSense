import { getJson } from "./client";
import type { EmployeePage, EmployeeQuery } from "./types";

const EMPLOYEES_ENDPOINT = "/employees";

export function fetchEmployees(
  query: EmployeeQuery,
  signal?: AbortSignal,
): Promise<EmployeePage> {
  return getJson<EmployeePage>(EMPLOYEES_ENDPOINT, query, signal);
}
