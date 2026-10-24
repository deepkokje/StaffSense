import { fireEvent, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";

import { fetchBringToBandMin, fetchRaiseCost } from "../api/insights";
import { renderWithQueryClient } from "../test/renderWithQueryClient";
import { makeBandMinCost, makeRaiseCost } from "../test/whatIfFactories";
import WhatIfPage from "./WhatIfPage";

vi.mock("../api/insights", () => ({
  fetchBringToBandMin: vi.fn(), fetchRaiseCost: vi.fn(),
}));
const bandApi = vi.mocked(fetchBringToBandMin);
const raiseApi = vi.mocked(fetchRaiseCost);

beforeEach(() => {
  bandApi.mockReset().mockResolvedValue(makeBandMinCost());
  raiseApi.mockReset().mockResolvedValue(makeRaiseCost());
});

async function selectDepartment() {
  fireEvent.mouseDown(screen.getByLabelText("Department"));
  fireEvent.click(await screen.findByText("Engineering", {
    selector: ".ant-select-item-option-content",
  }));
}

async function calculate(percent: string) {
  await selectDepartment();
  fireEvent.change(screen.getByLabelText("Percent"), {
    target: { value: percent },
  });
  fireEvent.click(screen.getByText("Calculate"));
}

test("band minimum scenario automatically loads and renders USD cost, count and local cost", async () => {
  renderWithQueryClient(<WhatIfPage />);
  const summary = await screen.findByLabelText("Band minimum cost summary");
  expect(within(summary).getByText("$1,234.56")).toBeInTheDocument();
  expect(within(summary).getByText("3")).toBeInTheDocument();
  expect(screen.getByText("₹102,880.00")).toBeInTheDocument();
  expect(bandApi).toHaveBeenCalledWith({}, expect.any(AbortSignal));
  expect(raiseApi).not.toHaveBeenCalled();
});

test("zero band minimum cost shows Everyone is within band", async () => {
  bandApi.mockResolvedValue(makeBandMinCost({
    employees_affected: 0, total_cost_usd_minor: 0, by_country: [],
  }));
  renderWithQueryClient(<WhatIfPage />);
  expect(await screen.findByText("Everyone is within band")).toBeInTheDocument();
});

test("changing band minimum countries changes the request", async () => {
  renderWithQueryClient(<WhatIfPage />);
  await screen.findByLabelText("Band minimum cost summary");
  fireEvent.mouseDown(screen.getByLabelText("Band minimum country", { selector: "input" }));
  fireEvent.click(await screen.findByText("JP", { selector: ".ant-select-item-option-content" }));
  await waitFor(() => expect(bandApi).toHaveBeenLastCalledWith(
    { country: ["JP"] }, expect.any(AbortSignal),
  ));
});

test("band minimum error displays Retry and recovers", async () => {
  bandApi.mockRejectedValueOnce(new Error("Cost unavailable"));
  renderWithQueryClient(<WhatIfPage />);
  expect(await screen.findByText("Cost unavailable")).toBeInTheDocument();
  fireEvent.click(screen.getByText("Retry"));
  expect(await screen.findByLabelText("Band minimum cost summary")).toBeInTheDocument();
});

test("invalid percent shows an inline error and does not request raise cost", async () => {
  renderWithQueryClient(<WhatIfPage />);
  await calculate("7.255");
  expect(await screen.findByText("Enter a percentage with at most 2 decimal places."))
    .toBeInTheDocument();
  expect(raiseApi).not.toHaveBeenCalled();
});

test("a valid submission sends integer basis points and renders USD cost and payroll", async () => {
  renderWithQueryClient(<WhatIfPage />);
  await calculate("2.5");
  await waitFor(() => expect(raiseApi).toHaveBeenCalledWith(
    { department: "Engineering", raise_bp: 250 }, expect.any(AbortSignal),
  ));
  const result = await screen.findByLabelText("Department raise cost summary");
  expect(within(result).getByText("$150.00")).toBeInTheDocument();
  expect(within(result).getByText("4")).toBeInTheDocument();
  expect(screen.getByText("$3,000.00")).toBeInTheDocument();
  expect(screen.getByText("$3,150.00")).toBeInTheDocument();
  expect(Number.isInteger(raiseApi.mock.calls[0][0].raise_bp)).toBe(true);
});

test("editing a draft does not fetch before another valid submission", async () => {
  renderWithQueryClient(<WhatIfPage />);
  await calculate("5");
  await screen.findByLabelText("Department raise cost summary");
  fireEvent.change(screen.getByLabelText("Percent"), {
    target: { value: "10" },
  });
  expect(raiseApi).toHaveBeenCalledTimes(1);
});

test("raise country is passed only after calculating", async () => {
  renderWithQueryClient(<WhatIfPage />);
  fireEvent.mouseDown(screen.getByLabelText("Raise country", { selector: "input" }));
  fireEvent.click(await screen.findByText("IN", { selector: ".ant-select-item-option-content" }));
  expect(raiseApi).not.toHaveBeenCalled();
  await calculate("5");
  await waitFor(() => expect(raiseApi).toHaveBeenCalledWith(
    { department: "Engineering", country: "IN", raise_bp: 500 }, expect.any(AbortSignal),
  ));
});

test("empty raise selection shows a clear message", async () => {
  raiseApi.mockResolvedValue(makeRaiseCost({
    employees_affected: 0, total_cost_usd_minor: 0,
    current_payroll_usd_minor: 0, new_payroll_usd_minor: 0, by_country: [],
  }));
  renderWithQueryClient(<WhatIfPage />);
  await calculate("5");
  expect(await screen.findByText("No employees in this selection")).toBeInTheDocument();
});

test("raise errors can be retried without changing the submitted scenario", async () => {
  raiseApi.mockRejectedValueOnce(new Error("Raise unavailable"));
  renderWithQueryClient(<WhatIfPage />);
  await calculate("5");
  expect(await screen.findByText("Raise unavailable")).toBeInTheDocument();
  fireEvent.click(screen.getByText("Retry"));
  expect(await screen.findByLabelText("Department raise cost summary")).toBeInTheDocument();
});
