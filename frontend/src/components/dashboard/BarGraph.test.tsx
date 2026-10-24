import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import BarGraph from "./BarGraph";

test("scales bar geometry against the largest value while preserving exact labels", () => {
  render(<BarGraph label="Counts" items={[
    { label: "First", value: 10, displayValue: "10", color: "red" },
    { label: "Second", value: 5, displayValue: "5", color: "blue" },
  ]} />);
  expect(screen.getByRole("img", { name: "First: 10" }).lastChild)
    .toHaveAttribute("width", "1000");
  expect(screen.getByRole("img", { name: "Second: 5" }).lastChild)
    .toHaveAttribute("width", "500");
});

test("zero values render empty bars without invalid geometry", () => {
  render(<BarGraph label="Zero cost" items={[
    { label: "US", value: 0, displayValue: "$0.00", color: "blue" },
  ]} />);
  expect(screen.getByRole("img", { name: "US: $0.00" }).lastChild)
    .toHaveAttribute("width", "0");
});
