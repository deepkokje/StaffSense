import { describe, expect, test } from "vitest";

import { parseMoneyInput } from "./parseMoneyInput";

describe("parseMoneyInput", () => {
  test.each([
    ["1500.50", "USD", 150050],
    ["1500", "USD", 150000],
    ["1500.5", "USD", 150050],
    [" 1500.50 ", "USD", 150050],
    ["1,00,000", "INR", 10000000],
    ["1,50,000.00", "INR", 15000000],
    ["100,000", "USD", 10000000],
    ["1500", "JPY", 1500],
    ["123456789012", "JPY", 123456789012],
    ["1234567890.12", "USD", 123456789012],
    ["0.01", "USD", 1],
  ])("parses %s %s into integer minor units", (text, currency, amountMinor) => {
    expect(parseMoneyInput(text, currency)).toEqual({ ok: true, amountMinor });
  });

  test.each([
    ["1500.555", "USD"], ["1500.5", "JPY"], ["", "USD"], ["abc", "USD"],
    ["-5", "USD"], ["0", "USD"], ["1", "XYZ"], ["1234567890123", "JPY"],
    ["1,,000", "USD"], [",100", "USD"], ["1e3", "USD"], ["1.2,3", "USD"],
    ["1", "constructor"],
  ])("rejects invalid %s %s", (text, currency) => {
    expect(parseMoneyInput(text, currency).ok).toBe(false);
  });
});
