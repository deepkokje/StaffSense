import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import { makeBandMinCost } from "../../test/whatIfFactories";
import CostPieChart from "./CostPieChart";

test("renders proportional pie slices and exact USD country labels", () => {
  const { container } = render(<CostPieChart report={makeBandMinCost({
    total_cost_usd_minor: 400,
    by_country: [
      { country: "US", currency: "USD", employees_affected: 1, cost_local_minor: 300, cost_usd_minor: 300 },
      { country: "JP", currency: "JPY", employees_affected: 1, cost_local_minor: 150, cost_usd_minor: 100 },
    ],
  })} />);
  expect(screen.getByRole("img", { name: "US: $3.00" })).toBeInTheDocument();
  expect(screen.getByRole("img", { name: "JP: $1.00" })).toBeInTheDocument();
  expect(container.querySelectorAll(".recharts-pie-sector")).toHaveLength(2);
  expect(screen.getByText("$4.00")).toBeInTheDocument();
  expect(screen.getByText("$1.00")).toBeInTheDocument();
});

test("zero total renders the exact total without an invalid or misleading pie", () => {
  const { container } = render(<CostPieChart report={makeBandMinCost({
    total_cost_usd_minor: 0, employees_affected: 0, by_country: [],
  })} />);
  expect(screen.getByText("$0.00")).toBeInTheDocument();
  expect(container.querySelector(".recharts-wrapper")).not.toBeInTheDocument();
});

test("Recharts renders a sector for each positive country cost", () => {
  const { container } = render(<CostPieChart report={makeBandMinCost({
    total_cost_usd_minor: 3,
    by_country: ["US", "JP", "IN"].map((country) => ({
      country, currency: "USD", employees_affected: 1, cost_local_minor: 1, cost_usd_minor: 1,
    })),
  })} />);
  expect(container.querySelectorAll(".recharts-pie-sector")).toHaveLength(3);
  expect(screen.getByRole("img", { name: "IN: $0.01" })).toBeInTheDocument();
});
