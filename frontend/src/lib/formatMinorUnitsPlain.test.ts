import { expect, test } from "vitest";

import { formatMinorUnitsPlain } from "./formatMinorUnitsPlain";

test.each([
  [150050, "USD", "1500.50"], [1500, "JPY", "1500"],
  [150010, "USD", "1500.10"], [150000, "USD", "1500.00"], [0, "USD", "0.00"],
])("formats %s %s without grouping", (amount, currency, expected) => {
  expect(formatMinorUnitsPlain(amount, currency)).toBe(expected);
});
