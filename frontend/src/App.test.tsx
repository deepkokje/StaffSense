import "@testing-library/jest-dom/vitest";
import { useQueryClient } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";

import App from "./App";
import AppProviders from "./AppProviders";

test("renders the placeholder title", () => {
  render(
    <AppProviders>
      <App />
    </AppProviders>,
  );

  expect(
    screen.getByRole("heading", { name: "Dashboard", level: 1 }),
  ).toBeInTheDocument();
});

test("provides a stable query client across rerenders", () => {
  const captureClient = vi.fn();

  function QueryClientConsumer() {
    captureClient(useQueryClient());
    return null;
  }

  const { rerender } = render(
    <AppProviders>
      <QueryClientConsumer />
    </AppProviders>,
  );
  const initialClient = captureClient.mock.lastCall?.[0];

  expect(initialClient).toBeDefined();

  rerender(
    <AppProviders>
      <QueryClientConsumer />
    </AppProviders>,
  );

  expect(captureClient).toHaveBeenCalledTimes(2);
  expect(captureClient.mock.lastCall?.[0]).toBe(initialClient);
});
