import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";

import { createEmployee, deleteEmployee, fetchEmployees, updateEmployee } from "../api/employees";
import { ApiError } from "../api/client";
import { renderWithQueryClient } from "../test/renderWithQueryClient";
import { makeEmployee, makeEmployeePage } from "../test/factories";
import EmployeesPage from "./EmployeesPage";

vi.mock("../api/employees", () => ({
  fetchEmployees: vi.fn(), createEmployee: vi.fn(),
  updateEmployee: vi.fn(), deleteEmployee: vi.fn(),
}));
vi.mock("../components/EmployeeFilters", () => ({ default: () => null }));
const listApi = vi.mocked(fetchEmployees);
const FULL_FORM_TEST_TIMEOUT_MS = 10_000;

beforeEach(() => {
  listApi.mockReset().mockResolvedValue(makeEmployeePage());
  vi.mocked(createEmployee).mockReset().mockResolvedValue(makeEmployee());
  vi.mocked(updateEmployee).mockReset().mockResolvedValue(makeEmployee());
  vi.mocked(deleteEmployee).mockReset().mockResolvedValue();
});

test("Add employee opens create form and successful create closes it and refreshes list", async () => {
  listApi.mockResolvedValueOnce(makeEmployeePage([]));
  renderWithQueryClient(<EmployeesPage />);
  await screen.findByText("No employees match these filters");
  fireEvent.click(screen.getByText("Add employee", { selector: "button span" }));
  const drawer = within(screen.getByRole("dialog"));
  expect(drawer.getByText("Add employee")).toBeInTheDocument();
  fireEvent.change(drawer.getByLabelText("Name"), { target: { value: "New Employee" } });
  fireEvent.change(drawer.getByLabelText("Email"), { target: { value: "new@staff.example" } });
  for (const [label, value] of [
    ["Title", "Software Engineer"], ["Department", "Engineering"],
    ["Country", "US"], ["Level", "3"],
  ]) {
    fireEvent.mouseDown(drawer.getByLabelText(label));
    fireEvent.click(await screen.findByText(value, {
      selector: ".ant-select-item-option-content",
    }));
  }
  fireEvent.change(drawer.getByLabelText("Salary (USD)"), { target: { value: "1500" } });
  const hireDate = drawer.getByLabelText("Hire date");
  fireEvent.change(hireDate, { target: { value: "2020-01-01" } });
  fireEvent.keyDown(hireDate, { key: "Enter", code: "Enter" });
  fireEvent.blur(hireDate);
  fireEvent.click(screen.getByText("Save employee"));
  await waitFor(() => expect(createEmployee).toHaveBeenCalled());
  await waitFor(() => expect(screen.queryByText("Save employee")).not.toBeInTheDocument());
  await waitFor(() => expect(listApi).toHaveBeenCalledTimes(2));
  expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();
}, FULL_FORM_TEST_TIMEOUT_MS);

test("Edit opens pre-filled employee and a successful update refreshes list", async () => {
  renderWithQueryClient(<EmployeesPage />);
  fireEvent.click(await screen.findByText("Edit"));
  expect(screen.getByRole("dialog")).toHaveTextContent("Edit employee");
  expect(screen.getByLabelText("Name")).toHaveValue("Ada Lovelace");
  fireEvent.change(screen.getByLabelText("Name"), { target: { value: "Edited Ada" } });
  fireEvent.click(screen.getByText("Save employee"));
  await waitFor(() => expect(updateEmployee).toHaveBeenCalledWith(
    1, expect.objectContaining({ name: "Edited Ada", salary_minor: 123456 }),
  ));
  await waitFor(() => expect(listApi).toHaveBeenCalledTimes(2));
  await waitFor(() => expect(screen.queryByText("Save employee")).not.toBeInTheDocument());
});

test("Delete requires confirmation, does nothing on cancel, and refreshes on confirmation", async () => {
  renderWithQueryClient(<EmployeesPage />);
  fireEvent.click(await screen.findByText("Delete"));
  expect(await screen.findByText("Delete this employee?")).toBeInTheDocument();
  expect(deleteEmployee).not.toHaveBeenCalled();
  fireEvent.click(screen.getByText("Cancel"));
  expect(deleteEmployee).not.toHaveBeenCalled();
  fireEvent.click(screen.getByText("Delete", { selector: ".ant-table-cell button span" }));
  fireEvent.click(await screen.findByText("Delete", { selector: ".ant-popconfirm-buttons button span" }));
  await waitFor(() => expect(deleteEmployee).toHaveBeenCalledWith(1, expect.anything()));
  await waitFor(() => expect(listApi).toHaveBeenCalledTimes(2));
});

test("Delete conflict shows API message and retains the employee row", async () => {
  vi.mocked(deleteEmployee).mockRejectedValue(
    new ApiError(409, "employee has direct reports; reassign them first"),
  );
  renderWithQueryClient(<EmployeesPage />);
  fireEvent.click(await screen.findByText("Delete"));
  fireEvent.click(await screen.findByText("Delete", { selector: ".ant-popconfirm-buttons button span" }));
  expect(await screen.findByText("employee has direct reports; reassign them first"))
    .toBeInTheDocument();
  expect(screen.getByText("Ada Lovelace")).toBeInTheDocument();
  expect(listApi).toHaveBeenCalledTimes(1);
});
