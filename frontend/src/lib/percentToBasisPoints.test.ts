import { expect, test } from "vitest";

import { MAX_RAISE_BP, MIN_RAISE_BP, percentToBasisPoints } from "./percentToBasisPoints";

test.each([
  ["5", 500], ["2.5", 250], ["0.05", 5], [" 5 ", 500],
  ["0.01", 1], ["50", 5_000], ["50.00", 5_000], ["05.20", 520],
])("parses percent %s as integer basis points %i", (input, expected) => {
  expect(percentToBasisPoints(input)).toEqual({ ok: true, basisPoints: expected });
});

test.each([
  "", " ", "abc", "-1", "7.255", "5%", "0", "0.00", "50.01", "51", "1e1",
  "5,5", "Infinity", "99999999999999999999999999999999", "0.001",
])("rejects invalid percent %s with an explicit reason", (input) => {
  const result = percentToBasisPoints(input);
  expect(result.ok).toBe(false);
  if (!result.ok) expect(result.reason).not.toBe("");
});

test("exports the same inclusive basis point limits as the backend", () => {
  expect(MIN_RAISE_BP).toBe(1);
  expect(MAX_RAISE_BP).toBe(5_000);
});
