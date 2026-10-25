import { CURRENCY_EXPONENTS, CURRENCY_OPTIONS } from "../constants/filterOptions";

export function formatMinorUnitsPlain(amountMinor: number, currency: string): string {
  const exponent = CURRENCY_EXPONENTS[currency];
  if (!CURRENCY_OPTIONS.includes(currency) || !Number.isSafeInteger(amountMinor) || amountMinor < 0) {
    throw new Error("Expected non-negative integer minor units and a supported currency.");
  }
  const digits = String(amountMinor).padStart(exponent + 1, "0");
  return exponent === 0
    ? digits
    : `${digits.slice(0, -exponent)}.${digits.slice(-exponent)}`;
}
