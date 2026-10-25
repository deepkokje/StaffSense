import { expect, test } from "vitest";

import { formatBasisPoints } from "./formatBasisPoints";

test.each([
  [1000, "10.00%"], [-150, "-1.50%"], [0, "0.00%"],
  [1, "0.01%"], [-1, "-0.01%"], [10000, "100.00%"],
])("formats %s integer basis points as %s", (value, expected) => {
  expect(formatBasisPoints(value)).toBe(expected);
});
