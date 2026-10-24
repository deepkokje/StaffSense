import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, test, vi } from "vitest";

import { fetchBenchmarks } from "../api/insights";
import { makeBenchmark } from "../test/benchmarkFactories";
import { renderWithQueryClient } from "../test/renderWithQueryClient";
import BenchmarksPage from "./BenchmarksPage";

vi.mock("../api/insights", () => ({ fetchBenchmarks: vi.fn() }));
const mockedFetchBenchmarks = vi.mocked(fetchBenchmarks);

beforeEach(() => {
  mockedFetchBenchmarks.mockReset();
  mockedFetchBenchmarks.mockResolvedValue({ items: [makeBenchmark()] });
});

test("renders USD and JPY groups using their own local currency", async () => {
  mockedFetchBenchmarks.mockResolvedValue({ items: [
    makeBenchmark(),
    makeBenchmark({
      key: { title: "Designer", level: 2, country: "JP" }, currency: "JPY",
      stats: { min: 100, p25: 125, median: 150, p75: 175, max: 200 },
    }),
  ] });
  renderWithQueryClient(<BenchmarksPage />);

  expect(await screen.findByText("$1,500.00")).toBeInTheDocument();
  expect(screen.getByText("¥150")).toBeInTheDocument();
});

test("shows an insufficient tag and dashes instead of statistics for small groups", async () => {
  mockedFetchBenchmarks.mockResolvedValue({ items: [
    makeBenchmark({ headcount: 4, stats: null, insufficient_data: true }),
  ] });
  renderWithQueryClient(<BenchmarksPage />);

  const tag = await screen.findByText("Insufficient data (n < 5)");
  const row = tag.closest("tr");
  if (!row) throw new Error("Expected an insufficient peer-group table row");
  expect(within(row).getAllByText("-")).toHaveLength(5);
});

test("toggling show small groups updates the include_insufficient request parameter", async () => {
  renderWithQueryClient(<BenchmarksPage />);
  await screen.findByText("$1,500.00");
  await userEvent.click(screen.getByRole("switch", { name: "Show small groups" }));

  await waitFor(() => expect(mockedFetchBenchmarks).toHaveBeenLastCalledWith(
    expect.objectContaining({ include_insufficient: false }), expect.any(AbortSignal),
  ));
});

test("changing a country filter requests the selected countries", async () => {
  renderWithQueryClient(<BenchmarksPage />);
  await screen.findByText("$1,500.00");
  fireEvent.mouseDown(screen.getByRole("combobox", { name: "Benchmark country" }));
  await userEvent.click(await screen.findByRole("option", { name: "JP" }));

  await waitFor(() => expect(mockedFetchBenchmarks).toHaveBeenLastCalledWith(
    expect.objectContaining({ country: ["JP"] }), expect.any(AbortSignal),
  ));
});

test("shows a clear empty state when no peer groups match", async () => {
  mockedFetchBenchmarks.mockResolvedValue({ items: [] });
  renderWithQueryClient(<BenchmarksPage />);
  expect(await screen.findByText("No peer groups match these filters")).toBeInTheDocument();
});

test("paginates groups locally and resets to the first page when filters change", async () => {
  mockedFetchBenchmarks.mockResolvedValue({
    items: Array.from({ length: 26 }, (_, index) => makeBenchmark({
      key: { country: "US", title: `Role ${index}`, level: 1 },
    })),
  });
  renderWithQueryClient(<BenchmarksPage />);
  await screen.findByText("Role 0");
  expect(screen.queryByText("Role 25")).not.toBeInTheDocument();

  await userEvent.click(within(screen.getByTitle("Next Page")).getByRole("button"));
  expect(await screen.findByText("Role 25")).toBeInTheDocument();
  expect(screen.queryByText("Role 0")).not.toBeInTheDocument();
  expect(mockedFetchBenchmarks).toHaveBeenCalledTimes(1);

  await userEvent.click(screen.getByRole("switch", { name: "Show small groups" }));
  expect(await screen.findByText("Role 0")).toBeInTheDocument();
  expect(screen.queryByText("Role 25")).not.toBeInTheDocument();
});

test("shows an error and retries the benchmark request", async () => {
  mockedFetchBenchmarks.mockRejectedValueOnce(new Error("Benchmarks unavailable"));
  renderWithQueryClient(<BenchmarksPage />);
  expect(await screen.findByText("Benchmarks unavailable")).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "Retry" }));

  expect(await screen.findByText("$1,500.00")).toBeInTheDocument();
  expect(mockedFetchBenchmarks).toHaveBeenCalledTimes(2);
});
