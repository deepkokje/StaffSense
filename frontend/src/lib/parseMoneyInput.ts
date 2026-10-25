import { CURRENCY_EXPONENTS, CURRENCY_OPTIONS } from "../constants/filterOptions";

export const MAX_MONEY_DIGITS = 12;
type ParseMoneyResult =
  | { ok: true; amountMinor: number }
  | { ok: false; reason: string };

export function parseMoneyInput(text: string, currency: string): ParseMoneyResult {
  const exponent = CURRENCY_EXPONENTS[currency];
  if (!CURRENCY_OPTIONS.includes(currency)) {
    return { ok: false, reason: "Unsupported currency." };
  }
  const trimmed = text.trim();
  const [whole, fraction = ""] = trimmed.split(".");
  const validWhole = /^(?:\d+|\d{1,3}(?:,\d{3})+|\d{1,2}(?:,\d{2})*,\d{3})$/;
  if (
    !validWhole.test(whole) ||
    !/^\d+(?:\.\d+)?$/.test(trimmed.replaceAll(",", "")) ||
    fraction.length > exponent
  ) {
    return { ok: false, reason: `Enter a positive salary with at most ${exponent} decimal places.` };
  }
  const digits = whole.replaceAll(",", "") + fraction;
  if (digits.length > MAX_MONEY_DIGITS) {
    return { ok: false, reason: `Salary must contain at most ${MAX_MONEY_DIGITS} digits.` };
  }
  const amountMinor = Number(whole.replaceAll(",", "") + fraction.padEnd(exponent, "0"));
  if (!Number.isSafeInteger(amountMinor) || amountMinor <= 0) {
    return { ok: false, reason: "Salary must be greater than zero." };
  }
  return { ok: true, amountMinor };
}
