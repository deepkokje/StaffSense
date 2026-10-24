import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, expect, test, vi } from "vitest";

import { fetchBands, fetchBringToBandMin, fetchOutliers } from "../api/insights";
import { makeBandsResponse, makeOutliersResponse } from "../test/attentionFactories";
import { renderWithQueryClient } from "../test/renderWithQueryClient";
import { makeBandMinCost } from "../test/whatIfFactories";
import DashboardPage from "./DashboardPage";

vi.mock("../api/insights", () => ({
  fetchBands: vi.fn(), fetchOutliers: vi.fn(), fetchBringToBandMin: vi.fn(),
}));
const bandsApi = vi.mocked(fetchBands);
const outliersApi = vi.mocked(fetchOutliers);
const costApi = vi.mocked(fetchBringToBandMin);

function renderDashboard() {
  return renderWithQueryClient(<MemoryRouter><DashboardPage /></MemoryRouter>);
}

function card(title: string) {
  return within(screen.getByRole("region", { name: title }));
}

beforeEach(() => {
  bandsApi.mockReset().mockResolvedValue(makeBandsResponse());
  outliersApi.mockReset().mockResolvedValue(makeOutliersResponse({ total: 17 }));
  costApi.mockReset().mockResolvedValue(makeBandMinCost());
});

test("renders four dashboard cards without a pay equity placeholder", async () => {
  renderDashboard();
  expect(await card("Below band").findByText("3")).toBeInTheDocument();
  expect(await card("Above band").findByText("2")).toBeInTheDocument();
  expect(await card("Outliers").findByText("17")).toBeInTheDocument();
  expect((await card("Cost to reach band minimum").findAllByText("$1,234.56")).length).toBeGreaterThan(0);
  expect(card("Cost to reach band minimum").getByText("3 employees affected, per year"))
    .toBeInTheDocument();
  expect(screen.queryByRole("region", { name: "Pay equity" })).not.toBeInTheDocument();
  expect(screen.getAllByRole("region")).toHaveLength(4);
  expect(card("Below band").getByRole("img", { name: "Below minimum: 3" })).toBeInTheDocument();
  expect(card("Above band").getByRole("img", { name: "Above maximum: 2" })).toBeInTheDocument();
  expect(card("Outliers").getByRole("img", { name: "Flagged employees: 17" })).toBeInTheDocument();
  expect(card("Cost to reach band minimum").getByRole("img", { name: "IN: $1,234.56" }))
    .toBeInTheDocument();
});

test("requests existing hooks with summary-sized unfiltered queries only once", async () => {
  renderDashboard();
  await card("Below band").findByText("3");
  expect(bandsApi).toHaveBeenCalledExactlyOnceWith(
    { page: 1, page_size: 1 }, expect.any(AbortSignal),
  );
  expect(outliersApi).toHaveBeenCalledExactlyOnceWith(
    { page: 1, page_size: 1 }, expect.any(AbortSignal),
  );
  expect(costApi).toHaveBeenCalledExactlyOnceWith({}, expect.any(AbortSignal));
});

test("links supported headline titles to the correct detail routes", () => {
  renderDashboard();
  expect(card("Below band").getByRole("link")).toHaveAttribute("href", "/insights/attention?tab=bands");
  expect(card("Above band").getByRole("link")).toHaveAttribute("href", "/insights/attention?tab=bands");
  expect(card("Outliers").getByRole("link")).toHaveAttribute("href", "/insights/attention?tab=outliers");
  expect(card("Cost to reach band minimum").getByRole("link")).toHaveAttribute("href", "/insights/what-if");
});

test("zero values show independent empty messages instead of loading or errors", async () => {
  bandsApi.mockResolvedValue(makeBandsResponse({
    summary: { below_min: 0, within_band: 8, above_max: 0, no_band: 0 },
  }));
  outliersApi.mockResolvedValue(makeOutliersResponse({ total: 0, items: [] }));
  costApi.mockResolvedValue(makeBandMinCost({
    total_cost_usd_minor: 0, employees_affected: 0, by_country: [],
  }));
  renderDashboard();
  expect(await card("Cost to reach band minimum").findByText("Everyone is within band")).toBeInTheDocument();
  expect(card("Cost to reach band minimum").getByText("$0.00")).toBeInTheDocument();
  expect(await card("Below band").findByText("Nobody is below band minimum")).toBeInTheDocument();
  expect(await card("Above band").findByText("Nobody is above band maximum")).toBeInTheDocument();
  expect(await card("Outliers").findByText("No outliers")).toBeInTheDocument();
});

test("one failing query stays within its card and Retry refetches only that query", async () => {
  outliersApi.mockRejectedValueOnce(new Error("Outlier summary unavailable"));
  renderDashboard();
  expect(await card("Outliers").findByText("Outlier summary unavailable")).toBeInTheDocument();
  expect(await card("Below band").findByText("3")).toBeInTheDocument();
  expect(await card("Above band").findByText("2")).toBeInTheDocument();
  expect((await card("Cost to reach band minimum").findAllByText("$1,234.56")).length).toBeGreaterThan(0);
  expect(screen.getAllByRole("button", { name: "Retry" })).toHaveLength(1);
  fireEvent.click(card("Outliers").getByRole("button", { name: "Retry" }));
  expect(await card("Outliers").findByText("17")).toBeInTheDocument();
  expect(outliersApi).toHaveBeenCalledTimes(2);
  expect(bandsApi).toHaveBeenCalledTimes(1);
  expect(costApi).toHaveBeenCalledTimes(1);
});

test("shared band request errors leave cost and outliers cards intact", async () => {
  bandsApi.mockRejectedValue(new Error("Band summary unavailable"));
  renderDashboard();
  expect(await card("Below band").findByText("Band summary unavailable")).toBeInTheDocument();
  expect(await card("Above band").findByText("Band summary unavailable")).toBeInTheDocument();
  expect(await card("Outliers").findByText("17")).toBeInTheDocument();
  expect((await card("Cost to reach band minimum").findAllByText("$1,234.56")).length).toBeGreaterThan(0);
});

test("each pending request shows a skeleton in its dashboard card", async () => {
  bandsApi.mockReturnValue(new Promise(() => {}));
  outliersApi.mockReturnValue(new Promise(() => {}));
  costApi.mockReturnValue(new Promise(() => {}));
  renderDashboard();
  for (const title of ["Below band", "Above band", "Outliers", "Cost to reach band minimum"]) {
    expect(card(title).getByLabelText(`Loading ${title}`)).toBeInTheDocument();
  }
  await waitFor(() => expect(bandsApi).toHaveBeenCalledTimes(1));
});
