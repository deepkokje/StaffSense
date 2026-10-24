import { fireEvent, screen } from "@testing-library/react";
import { describe, expect, test, vi } from "vitest";

import type { EmployeePage } from "../api/types";
import { renderWithQueryClient } from "../test/renderWithQueryClient";
import { makeEmployee, makeEmployeePage } from "../test/factories";
import EmployeeTable from "./EmployeeTable";

function renderTable(
  data: EmployeePage | undefined = makeEmployeePage(),
  onSortChange = vi.fn(),
) {
  return {
    onSortChange,
    ...renderWithQueryClient(
      <EmployeeTable
        data={data}
        isPlaceholderData={false}
        loading={false}
        onClearFilters={vi.fn()}
        onPageChange={vi.fn()}
        onSortChange={onSortChange}
        page={1}
        pageSize={25}
        sortBy="name"
        sortDir="asc"
      />,
    ),
  };
}

describe("EmployeeTable", () => {
  test("renders employee rows from its props", () => {
    renderTable(makeEmployeePage([makeEmployee({ name: "Grace Hopper" })]));

    expect(screen.getByText("Grace Hopper")).toBeInTheDocument();
    expect(screen.getByText("1 employees")).toBeInTheDocument();
  });

  test("formats local and USD salary fields for display", () => {
    renderTable();

    expect(screen.getByText("₹1,234.56")).toBeInTheDocument();
    expect(screen.getByText("$15,000.00")).toBeInTheDocument();
  });

  test("shows an empty message and clear action when there are no rows", () => {
    renderTable(makeEmployeePage([]));

    expect(screen.getByText("No employees match these filters")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Clear filters" })).toBeInTheDocument();
  });

  test("reports the sort field and direction when a sortable header is clicked", () => {
    const onSortChange = vi.fn();
    renderTable(makeEmployeePage(), onSortChange);

    fireEvent.click(screen.getByText("Salary (USD)"));

    expect(onSortChange).toHaveBeenCalledWith("salary_usd_minor", "asc");
  });
});
