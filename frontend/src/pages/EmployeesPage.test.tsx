import { act, fireEvent, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, test, vi } from "vitest";

import { fetchEmployees } from "../api/employees";
import { renderWithQueryClient } from "../test/renderWithQueryClient";
import { makeEmployee, makeEmployeePage } from "../test/factories";
import EmployeesPage from "./EmployeesPage";

vi.mock("../api/employees", () => ({
  fetchEmployees: vi.fn(),
}));

const mockedFetchEmployees = vi.mocked(fetchEmployees);

describe("EmployeesPage", () => {
  beforeEach(() => {
    mockedFetchEmployees.mockReset();
  });

  test("renders the first page of employee rows", async () => {
    mockedFetchEmployees.mockResolvedValue(
      makeEmployeePage([makeEmployee({ name: "Ada Lovelace" })]),
    );
    renderWithQueryClient(<EmployeesPage />);

    expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();
    expect(mockedFetchEmployees).toHaveBeenCalledWith(
      expect.objectContaining({
        page: 1,
        page_size: 25,
        sort_by: "name",
        sort_dir: "asc",
      }),
      expect.any(AbortSignal),
    );
  });

  test("sends one debounced search request after typing", async () => {
    mockedFetchEmployees.mockResolvedValue(makeEmployeePage());
    vi.useFakeTimers();
    renderWithQueryClient(<EmployeesPage />);
    const searchInput = screen.getByPlaceholderText("Search name or email");
    fireEvent.change(searchInput, { target: { value: "Ada" } });
    await act(async () => {
      await vi.advanceTimersByTimeAsync(300);
      await Promise.resolve();
      await Promise.resolve();
      await vi.advanceTimersByTimeAsync(1);
    });

    const searchRequests = mockedFetchEmployees.mock.calls
      .map(([query]) => query)
      .filter((query) => query.q === "Ada");
    expect(mockedFetchEmployees).toHaveBeenCalledTimes(2);
    expect(searchRequests).toHaveLength(1);
  });

  test("retries a failed request and renders rows after success", async () => {
    mockedFetchEmployees
      .mockRejectedValueOnce(new Error("Service unavailable"))
      .mockResolvedValueOnce(makeEmployeePage([makeEmployee({ name: "Ada Lovelace" })]));
    renderWithQueryClient(<EmployeesPage />);

    expect(await screen.findByText("Service unavailable")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Retry" }));

    expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();
    expect(mockedFetchEmployees).toHaveBeenCalledTimes(2);
  });
});
