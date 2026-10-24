import "@testing-library/jest-dom/vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, expect, test, vi } from "vitest";

import App from "./App";
import { NAVIGATION_ITEMS } from "./constants/navigation";
import { renderWithQueryClient } from "./test/renderWithQueryClient";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({ items: [], total: 0, page: 1, page_size: 25, total_pages: 0 }),
        { status: 200 },
      ),
    ),
  );
});

function renderApp(path = "/") {
  return renderWithQueryClient(
    <MemoryRouter initialEntries={[path]}><App /></MemoryRouter>,
  );
}

test("redirects the root route to the Employees page", () => {
  renderApp();

  expect(screen.getByText("StaffSense")).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Employees" })).toBeInTheDocument();
});

test("builds the menu from the shared navigation array", () => {
  renderApp();
  for (const item of NAVIGATION_ITEMS) {
    expect(screen.getByRole("link", { name: item.label })).toHaveAttribute("href", item.path);
  }
});

test("clicking Benchmarks navigates to its page and selects its menu item", async () => {
  renderApp("/employees");
  await userEvent.click(screen.getByRole("link", { name: "Benchmarks" }));
  expect(screen.getByRole("heading", { name: "Benchmarks" })).toBeInTheDocument();
  expect(screen.getByRole("menuitem", { name: "Benchmarks" })).toHaveClass(
    "ant-menu-item-selected",
  );
});
