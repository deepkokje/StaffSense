import { expect, test } from "vitest";

import { formatPermille } from "./formatPermille";

test.each([
  [1_000, "100.0%"], [934, "93.4%"], [5, "0.5%"], [-201, "-20.1%"],
  [0, "0.0%"], [-5, "-0.5%"], [1, "0.1%"],
])("formats integer per-mille %i as %s", (value, expected) => {
  expect(formatPermille(value)).toBe(expected);
});
