import "@testing-library/jest-dom/vitest";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, expect, test, vi } from "vitest";

import App from "./App";
import { NAVIGATION_ITEMS } from "./constants/navigation";
import { makeBandsResponse } from "./test/attentionFactories";
import { makeBandMinCost } from "./test/whatIfFactories";
import { renderWithQueryClient } from "./test/renderWithQueryClient";

beforeEach(() => {
  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const path = new URL(String(input)).pathname;
      const body = path === "/insights/what-if/bring-to-band-min"
        ? makeBandMinCost()
        : path === "/insights/bands"
        ? makeBandsResponse({ items: [], total: 0 })
        : { items: [], total: 0, page: 1, page_size: 25, total_pages: 0 };
      return Promise.resolve(new Response(
        JSON.stringify(body),
        { status: 200 },
      ));
    }),
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

test("clicking Needs attention opens the band compliance tab", async () => {
  renderApp("/employees");
  await userEvent.click(screen.getByRole("link", { name: "Needs attention" }));
  expect(screen.getByRole("heading", { name: "Needs attention" })).toBeInTheDocument();
  expect(screen.getByRole("tab", { name: "Outside band" })).toHaveAttribute(
    "aria-selected", "true",
  );
  expect(screen.getByRole("menuitem", { name: "Needs attention" })).toHaveClass(
    "ant-menu-item-selected",
  );
});

test("clicking What-if opens the cost calculator and selects its menu item", async () => {
  renderApp("/employees");
  await userEvent.click(screen.getByRole("link", { name: "What-if" }));
  expect(screen.getByRole("heading", { name: "What-if" })).toBeInTheDocument();
  expect(screen.getByText("Bring everyone to band minimum")).toBeInTheDocument();
  expect(screen.getByRole("menuitem", { name: "What-if" })).toHaveClass(
    "ant-menu-item-selected",
  );
});
