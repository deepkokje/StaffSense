import { getJson, sendJson } from "./client";
import type {
  EmployeeInput, EmployeeOut, EmployeePage, EmployeeQuery, SalaryHistoryResponse,
} from "./types";

const EMPLOYEES_ENDPOINT = "/employees";

export function fetchEmployees(
  query: EmployeeQuery,
  signal?: AbortSignal,
): Promise<EmployeePage> {
  return getJson<EmployeePage>(EMPLOYEES_ENDPOINT, query, signal);
}

export function createEmployee(data: EmployeeInput): Promise<EmployeeOut> {
  return sendJson<EmployeeOut>(EMPLOYEES_ENDPOINT, "POST", data);
}

export function updateEmployee(id: number, data: EmployeeInput): Promise<EmployeeOut> {
  return sendJson<EmployeeOut>(`${EMPLOYEES_ENDPOINT}/${id}`, "PUT", data);
}

export function deleteEmployee(id: number): Promise<void> {
  return sendJson<void>(`${EMPLOYEES_ENDPOINT}/${id}`, "DELETE");
}

export function fetchSalaryHistory(
  employeeId: number, signal?: AbortSignal,
): Promise<SalaryHistoryResponse> {
  return getJson<SalaryHistoryResponse>(
    `${EMPLOYEES_ENDPOINT}/${employeeId}/salary-history`, {}, signal,
  );
}
