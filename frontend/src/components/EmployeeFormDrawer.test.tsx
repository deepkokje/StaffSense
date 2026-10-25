import { fireEvent, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";

import { ApiError } from "../api/client";
import { createEmployee, updateEmployee } from "../api/employees";
import { makeEmployee } from "../test/factories";
import { renderWithQueryClient } from "../test/renderWithQueryClient";
import EmployeeFormDrawer from "./EmployeeFormDrawer";

vi.mock("../api/employees", () => ({
  createEmployee: vi.fn(), updateEmployee: vi.fn(),
}));
const createApi = vi.mocked(createEmployee);
const updateApi = vi.mocked(updateEmployee);
const close = vi.fn();

beforeEach(() => {
  createApi.mockReset().mockResolvedValue(makeEmployee());
  updateApi.mockReset().mockResolvedValue(makeEmployee());
  close.mockReset();
});

async function select(label: string, value: string) {
  fireEvent.mouseDown(screen.getByLabelText(label));
  fireEvent.click(await screen.findByText(value, {
    selector: ".ant-select-item-option-content",
  }));
}

async function fillCreateForm(salary = "1500.50") {
  fireEvent.change(screen.getByLabelText("Name"), { target: { value: "New Employee" } });
  fireEvent.change(screen.getByLabelText("Email"), { target: { value: "new@staff.example" } });
  await select("Title", "Software Engineer");
  await select("Department", "Engineering");
  await select("Country", "US");
  await select("Level", "3");
  fireEvent.change(screen.getByLabelText("Salary (USD)"), { target: { value: salary } });
  const hireDate = screen.getByLabelText("Hire date");
  fireEvent.change(hireDate, { target: { value: "2020-01-01" } });
  fireEvent.keyDown(hireDate, { key: "Enter", code: "Enter" });
  fireEvent.blur(hireDate);
}

test("required fields block submission", async () => {
  renderWithQueryClient(<EmployeeFormDrawer onClose={close} />);
  fireEvent.click(screen.getByText("Save employee"));
  expect((await screen.findAllByText("This field is required.")).length).toBeGreaterThan(0);
  expect(createApi).not.toHaveBeenCalled();
});

test("invalid salary shows a field error and sends no request", async () => {
  renderWithQueryClient(<EmployeeFormDrawer employee={makeEmployee()} onClose={close} />);
  fireEvent.change(screen.getByLabelText("Salary (INR)"), { target: { value: "1500.555" } });
  fireEvent.click(screen.getByText("Save employee"));
  expect(await screen.findByText("Enter a positive salary with at most 2 decimal places."))
    .toBeInTheDocument();
  expect(updateApi).not.toHaveBeenCalled();
});

test("valid create sends integer minor units and only editable fields", async () => {
  renderWithQueryClient(<EmployeeFormDrawer onClose={close} />);
  await fillCreateForm();
  fireEvent.click(screen.getByText("Save employee"));
  await waitFor(() => expect(createApi).toHaveBeenCalledWith({
    name: "New Employee", email: "new@staff.example", title: "Software Engineer",
    department: "Engineering", country: "US", currency: "USD", salary_minor: 150050,
    level: 3, gender: "UNDISCLOSED", employment_type: "FULL_TIME", status: "ACTIVE",
    hire_date: "2020-01-01", manager_id: null,
  }, expect.anything()));
  await waitFor(() => expect(close).toHaveBeenCalledOnce());
});

test("edit pre-fills every field and disables currency", () => {
  renderWithQueryClient(<EmployeeFormDrawer employee={makeEmployee({ manager_id: 42 })} onClose={close} />);
  expect(screen.getByLabelText("Name")).toHaveValue("Ada Lovelace");
  expect(screen.getByLabelText("Email")).toHaveValue("ada@example.com");
  expect(screen.getByLabelText("Salary (INR)")).toHaveValue("1234.56");
  expect(screen.getByLabelText("Hire date")).toHaveValue("2024-01-15");
  expect(screen.getByLabelText("Manager ID")).toHaveValue("42");
  expect(screen.getByLabelText("Currency")).toBeDisabled();
  expect(screen.getByText("Software Engineer")).toBeInTheDocument();
  expect(screen.getByText("Engineering")).toBeInTheDocument();
  expect(screen.getByText("IN")).toBeInTheDocument();
  expect(screen.getByText("3")).toBeInTheDocument();
  expect(screen.getByText("FEMALE")).toBeInTheDocument();
  expect(screen.getByText("FULL_TIME")).toBeInTheDocument();
  expect(screen.getByText("ACTIVE")).toBeInTheDocument();
});

test("duplicate email appears on email field and preserves the open form", async () => {
  updateApi.mockRejectedValue(new ApiError(409, "email is already used by another employee"));
  renderWithQueryClient(<EmployeeFormDrawer employee={makeEmployee()} onClose={close} />);
  fireEvent.click(screen.getByText("Save employee"));
  const error = await screen.findByText("email is already used by another employee");
  expect(error.closest(".ant-form-item")).toHaveTextContent("Email");
  expect(screen.getByLabelText("Name")).toHaveValue("Ada Lovelace");
  expect(screen.getByLabelText("Salary (INR)")).toHaveValue("1234.56");
  expect(close).not.toHaveBeenCalled();
});

test("other server validation failures show an Alert and keep values", async () => {
  updateApi.mockRejectedValue(new ApiError(422, "manager assignment would create a management cycle"));
  renderWithQueryClient(<EmployeeFormDrawer employee={makeEmployee()} onClose={close} />);
  fireEvent.click(screen.getByText("Save employee"));
  expect(await screen.findByRole("alert")).toHaveTextContent(
    "manager assignment would create a management cycle",
  );
  expect(screen.getByLabelText("Name")).toHaveValue("Ada Lovelace");
  expect(close).not.toHaveBeenCalled();
});
