import "@testing-library/jest-dom/vitest";
import { screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import App from "./App";
import { renderWithQueryClient } from "./test/renderWithQueryClient";

test("renders the StaffSense employee page", () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({ items: [], total: 0, page: 1, page_size: 25, total_pages: 0 }),
        { status: 200 },
      ),
    ),
  );
  renderWithQueryClient(<App />);

  expect(screen.getByText("StaffSense")).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Employees" })).toBeInTheDocument();
});
