import { describe, expect, test } from "vitest";

import { formatMinorUnits } from "./formatMoney";

describe("formatMinorUnits", () => {
  test("formats USD with two fraction digits", () => {
    expect(formatMinorUnits(12_345, "USD")).toBe("$123.45");
  });

  test("formats JPY with no fraction digits", () => {
    expect(formatMinorUnits(12_345, "JPY")).toBe("¥12,345");
  });

  test("formats INR using its currency symbol and minor digits", () => {
    expect(formatMinorUnits(123_456, "INR")).toBe("₹1,234.56");
  });

  test("formats unknown currency with a readable fallback", () => {
    expect(formatMinorUnits(123_456, "XYZ")).toBe("123,456 XYZ");
  });

  test("formats a zero amount", () => {
    expect(formatMinorUnits(0, "USD")).toBe("$0.00");
  });
});
