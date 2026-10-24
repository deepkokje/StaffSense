import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, useLocation } from "react-router-dom";
import { beforeEach, expect, test, vi } from "vitest";

import { fetchBands, fetchOutliers } from "../api/insights";
import {
  makeBandsResponse, makeFlaggedEmployee, makeOutlier, makeOutliersResponse,
} from "../test/attentionFactories";
import { renderWithQueryClient } from "../test/renderWithQueryClient";
import AttentionPage from "./AttentionPage";

vi.mock("../api/insights", () => ({
  fetchBands: vi.fn(), fetchOutliers: vi.fn(),
}));
const bandsApi = vi.mocked(fetchBands);
const outliersApi = vi.mocked(fetchOutliers);

function LocationIndicator() {
  return <output aria-label="Current URL">{useLocation().search}</output>;
}

function renderPage(search = "") {
  return renderWithQueryClient(
    <MemoryRouter initialEntries={[`/insights/attention${search}`]}>
      <AttentionPage />
      <LocationIndicator />
    </MemoryRouter>,
  );
}

beforeEach(() => {
  bandsApi.mockReset().mockResolvedValue(makeBandsResponse());
  outliersApi.mockReset().mockResolvedValue(makeOutliersResponse());
});

test("bands tab renders summary counts, formatted ratio and local gap", async () => {
  renderPage();
  expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();
  expect(within(screen.getByRole("button", { name: "Below min" })).getByText("3"))
    .toBeInTheDocument();
  expect(screen.getByText("Within band")).toBeInTheDocument();
  expect(screen.getByText("20")).toBeInTheDocument();
  expect(screen.getByText("No band")).toBeInTheDocument();
  expect(screen.getByText("70.0%")).toBeInTheDocument();
  expect(screen.getByText("$100.00")).toBeInTheDocument();
  expect(screen.getByText("$700.00")).toBeInTheDocument();
  expect(outliersApi).not.toHaveBeenCalled();
});

test("clicking Below min filters status and clicking again clears it", async () => {
  renderPage();
  await screen.findByText("Ada Lovelace");
  await userEvent.click(screen.getByRole("button", { name: "Below min" }));
  await waitFor(() => expect(bandsApi).toHaveBeenLastCalledWith(
    expect.objectContaining({ status: "below_min", page: 1 }), expect.any(AbortSignal),
  ));
  await userEvent.click(screen.getByRole("button", { name: "Below min" }));
  await waitFor(() => expect(bandsApi).toHaveBeenLastCalledWith(
    expect.objectContaining({ status: undefined, page: 1 }), expect.any(AbortSignal),
  ));
});

test("band pagination requests a new page and a country filter resets page to one", async () => {
  bandsApi.mockResolvedValue(makeBandsResponse({ total: 26 }));
  renderPage();
  await screen.findByText("Ada Lovelace");
  await userEvent.click(screen.getByRole("button", { name: "right" }));
  await waitFor(() => expect(bandsApi).toHaveBeenLastCalledWith(
    expect.objectContaining({ page: 2 }), expect.any(AbortSignal),
  ));
  fireEvent.mouseDown(screen.getByRole("combobox", { name: "Attention country" }));
  await userEvent.click(await screen.findByRole("option", { name: "JP" }));
  await waitFor(() => expect(bandsApi).toHaveBeenLastCalledWith(
    expect.objectContaining({ country: ["JP"], page: 1 }), expect.any(AbortSignal),
  ));
});

test("bands tab shows the empty state", async () => {
  bandsApi.mockResolvedValue(makeBandsResponse({ items: [], total: 0 }));
  renderPage();
  expect(await screen.findByText("Nobody matches these filters")).toBeInTheDocument();
});

test("bands tab displays an error and Retry loads rows", async () => {
  bandsApi.mockRejectedValueOnce(new Error("Bands unavailable"));
  renderPage();
  expect(await screen.findByText("Bands unavailable")).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "Retry" }));
  expect(await screen.findByText("Ada Lovelace")).toBeInTheDocument();
});

test("outliers tab reads the URL and renders signed deviations", async () => {
  outliersApi.mockResolvedValue(makeOutliersResponse({ items: [
    makeOutlier(), makeOutlier({
      employee_id: 3, name: "Below Peer", deviation_permille: -201, direction: "below",
    }),
  ] }));
  renderPage("?tab=outliers");
  expect(screen.getByRole("tab", { name: "Outliers vs peers" })).toHaveAttribute(
    "aria-selected", "true",
  );
  expect(await screen.findByText("Grace Hopper")).toBeInTheDocument();
  expect(screen.getByText("+30.0%")).toBeInTheDocument();
  expect(screen.getByText("-20.1%")).toBeInTheDocument();
  expect(bandsApi).not.toHaveBeenCalled();
});

test("outlier direction and pagination change requests and direction resets page", async () => {
  outliersApi.mockResolvedValue(makeOutliersResponse({ total: 26 }));
  renderPage("?tab=outliers");
  await screen.findByText("Grace Hopper");
  await userEvent.click(screen.getByRole("button", { name: "right" }));
  await waitFor(() => expect(outliersApi).toHaveBeenLastCalledWith(
    expect.objectContaining({ page: 2 }), expect.any(AbortSignal),
  ));
  await userEvent.click(screen.getByText("Below", { selector: ".ant-segmented-item-label" }));
  await waitFor(() => expect(outliersApi).toHaveBeenLastCalledWith(
    expect.objectContaining({ direction: "below", page: 1 }), expect.any(AbortSignal),
  ));
});

test("changing tabs updates the URL and preserves unrelated search parameters", async () => {
  renderPage("?other=keep");
  await userEvent.click(screen.getByRole("tab", { name: "Outliers vs peers" }));
  expect(screen.getByLabelText("Current URL")).toHaveTextContent("other=keep&tab=outliers");
  await userEvent.click(screen.getByRole("tab", { name: "Outside band" }));
  expect(screen.getByLabelText("Current URL")).toHaveTextContent("tab=bands");
});

test("outliers tab handles empty and retry states", async () => {
  outliersApi.mockRejectedValueOnce(new Error("Outliers unavailable"))
    .mockResolvedValue(makeOutliersResponse({ items: [], total: 0 }));
  renderPage("?tab=outliers");
  expect(await screen.findByText("Outliers unavailable")).toBeInTheDocument();
  await userEvent.click(screen.getByRole("button", { name: "Retry" }));
  expect(await screen.findByText("Nobody matches these filters")).toBeInTheDocument();
});

test("band summary counts remain visible after filtering the status", async () => {
  bandsApi.mockResolvedValue(makeBandsResponse({
    items: [makeFlaggedEmployee({ status: "above_max" })],
  }));
  renderPage();
  await screen.findByText("Ada Lovelace");
  await userEvent.click(screen.getByRole("button", { name: "Above max" }));
  await waitFor(() => expect(bandsApi).toHaveBeenLastCalledWith(
    expect.objectContaining({ status: "above_max" }), expect.any(AbortSignal),
  ));
  expect(within(screen.getByRole("button", { name: "Below min" })).getByText("3"))
    .toBeInTheDocument();
});
