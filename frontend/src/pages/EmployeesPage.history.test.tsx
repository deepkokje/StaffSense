import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";

import { fetchEmployees, fetchSalaryHistory, updateEmployee } from "../api/employees";
import { makeEmployee, makeEmployeePage } from "../test/factories";
import { renderWithQueryClient } from "../test/renderWithQueryClient";
import { makeSalaryHistoryEntry, makeSalaryHistoryResponse } from "../test/salaryHistoryFactories";
import EmployeesPage from "./EmployeesPage";

vi.mock("../api/employees", () => ({
  fetchEmployees: vi.fn(), fetchSalaryHistory: vi.fn(), updateEmployee: vi.fn(),
  createEmployee: vi.fn(), deleteEmployee: vi.fn(),
}));
vi.mock("../components/EmployeeFilters", () => ({ default: () => null }));

beforeEach(() => {
  vi.mocked(fetchEmployees).mockReset().mockResolvedValue(makeEmployeePage([
    makeEmployee({ id: 42, currency: "USD" }),
  ]));
  vi.mocked(fetchSalaryHistory).mockReset().mockResolvedValue(makeSalaryHistoryResponse());
  vi.mocked(updateEmployee).mockReset().mockResolvedValue(makeEmployee({ id: 42, currency: "USD" }));
});

test("History opens for the selected employee and closes without another request", async () => {
  renderWithQueryClient(<EmployeesPage />);
  expect(fetchSalaryHistory).not.toHaveBeenCalled();
  fireEvent.click(await screen.findByText("History"));
  expect(await screen.findByText("Salary history - Ada Lovelace")).toBeInTheDocument();
  expect(await screen.findByText("+$100.00 (10.00%)")).toBeInTheDocument();
  expect(fetchSalaryHistory).toHaveBeenCalledWith(42, expect.any(AbortSignal));
  fireEvent.click(screen.getByLabelText("Close"));
  await waitFor(() => expect(screen.queryByText("Salary history - Ada Lovelace"))
    .not.toBeInTheDocument());
  expect(fetchSalaryHistory).toHaveBeenCalledTimes(1);
});

test("successful salary edit invalidates history and employee list and displays the refreshed row", async () => {
  vi.mocked(fetchSalaryHistory).mockResolvedValueOnce(makeSalaryHistoryResponse([]))
    .mockResolvedValue(makeSalaryHistoryResponse([makeSalaryHistoryEntry()]));
  renderWithQueryClient(<EmployeesPage />);
  fireEvent.click(await screen.findByText("History"));
  await screen.findByText("No salary changes recorded");
  fireEvent.click(screen.getByLabelText("Close"));
  fireEvent.click(screen.getByText("Edit"));
  fireEvent.change(screen.getByLabelText("Salary (USD)", { selector: "input" }), {
    target: { value: "1100.00" },
  });
  fireEvent.click(screen.getByText("Save employee"));
  await waitFor(() => expect(updateEmployee).toHaveBeenCalledWith(
    42, expect.objectContaining({ salary_minor: 110000 }),
  ));
  await waitFor(() => expect(fetchEmployees).toHaveBeenCalledTimes(2));
  await waitFor(() => expect(screen.queryByText("Save employee")).not.toBeInTheDocument());
  fireEvent.click(screen.getByText("History"));
  expect(await screen.findByText("+$100.00 (10.00%)")).toBeInTheDocument();
  expect(fetchSalaryHistory).toHaveBeenCalledTimes(2);
});
