import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";

import { fetchSalaryHistory } from "../api/employees";
import { makeEmployee } from "../test/factories";
import { renderWithQueryClient } from "../test/renderWithQueryClient";
import { makeSalaryHistoryEntry, makeSalaryHistoryResponse } from "../test/salaryHistoryFactories";
import SalaryHistoryDrawer from "./SalaryHistoryDrawer";

vi.mock("../api/employees", () => ({ fetchSalaryHistory: vi.fn() }));
const historyApi = vi.mocked(fetchSalaryHistory);
const close = vi.fn();

beforeEach(() => {
  historyApi.mockReset().mockResolvedValue(makeSalaryHistoryResponse());
  close.mockReset();
});

test("renders newest-first rows with signed USD changes and green raise and red cut tags", async () => {
  historyApi.mockResolvedValue(makeSalaryHistoryResponse([
    makeSalaryHistoryEntry(),
    makeSalaryHistoryEntry({
      old_salary_minor: 110000, new_salary_minor: 100000,
      changed_at: "2026-09-01T12:00:00", change_minor: -10000, change_bp: -909,
    }),
  ]));
  renderWithQueryClient(<SalaryHistoryDrawer employee={makeEmployee({ currency: "USD" })} onClose={close} />);
  const raise = await screen.findByText("+$100.00 (10.00%)");
  const cut = screen.getByText("-$100.00 (-9.09%)");
  expect(raise).toHaveClass("ant-tag-green");
  expect(cut).toHaveClass("ant-tag-red");
  const rows = screen.getAllByRole("row");
  expect(rows[1]).toHaveTextContent("Oct 25, 2026");
  expect(rows[2]).toHaveTextContent("Sep 1, 2026");
  expect(within(rows[1]).getByText("$1,000.00")).toBeInTheDocument();
  expect(within(rows[1]).getByText("$1,100.00")).toBeInTheDocument();
  expect(historyApi).toHaveBeenCalledWith(1, expect.any(AbortSignal));
});

test("shows n/a for a salary change starting from zero", async () => {
  historyApi.mockResolvedValue(makeSalaryHistoryResponse([makeSalaryHistoryEntry({
    old_salary_minor: 0, new_salary_minor: 500, change_minor: 500, change_bp: null,
  })]));
  renderWithQueryClient(<SalaryHistoryDrawer employee={makeEmployee()} onClose={close} />);
  expect(await screen.findByText("+$5.00 (n/a)")).toBeInTheDocument();
});

test("shows a clear empty state", async () => {
  historyApi.mockResolvedValue(makeSalaryHistoryResponse([]));
  renderWithQueryClient(<SalaryHistoryDrawer employee={makeEmployee()} onClose={close} />);
  expect(await screen.findByText("No salary changes recorded")).toBeInTheDocument();
});

test("shows loading skeleton while history is pending", () => {
  historyApi.mockReturnValue(new Promise(() => undefined));
  renderWithQueryClient(<SalaryHistoryDrawer employee={makeEmployee()} onClose={close} />);
  expect(screen.getByLabelText("Loading salary history").querySelector(".ant-skeleton"))
    .toBeInTheDocument();
});

test("retries a failed history query", async () => {
  historyApi.mockRejectedValueOnce(new Error("History unavailable"));
  renderWithQueryClient(<SalaryHistoryDrawer employee={makeEmployee()} onClose={close} />);
  expect(await screen.findByText("History unavailable")).toBeInTheDocument();
  fireEvent.click(screen.getByText("Retry"));
  expect(await screen.findByText("+$100.00 (10.00%)")).toBeInTheDocument();
  expect(historyApi).toHaveBeenCalledTimes(2);
});

test("does not fetch until an employee is selected and closes when requested", async () => {
  const view = renderWithQueryClient(<SalaryHistoryDrawer onClose={close} />);
  expect(historyApi).not.toHaveBeenCalled();
  view.unmount();
  renderWithQueryClient(<SalaryHistoryDrawer employee={makeEmployee()} onClose={close} />);
  await screen.findByText("+$100.00 (10.00%)");
  fireEvent.click(screen.getByLabelText("Close"));
  await waitFor(() => expect(close).toHaveBeenCalledOnce());
});
