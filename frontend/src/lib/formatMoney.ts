import { CURRENCY_EXPONENTS, CURRENCY_OPTIONS } from "../constants/filterOptions";
import { formatMinorUnitsPlain } from "./formatMinorUnitsPlain";

const DEFAULT_LOCALE = "en-US";

export function formatMinorUnits(amountMinor: number, currency: string): string {
  if (!CURRENCY_OPTIONS.includes(currency)) {
    return `${new Intl.NumberFormat(DEFAULT_LOCALE).format(amountMinor)} ${currency}`;
  }
  const digits = CURRENCY_EXPONENTS[currency];
  const sign = amountMinor < 0 ? "-" : "";
  const absoluteMinor = amountMinor < 0 ? -amountMinor : amountMinor;
  const [whole, fraction] = formatMinorUnitsPlain(absoluteMinor, currency).split(".");
  const parts = new Intl.NumberFormat(DEFAULT_LOCALE, {
    style: "currency", currency,
    minimumFractionDigits: digits, maximumFractionDigits: digits,
  }).formatToParts(BigInt(whole));
  return sign + parts.map((part) => part.type === "fraction" ? fraction : part.value).join("");
}
