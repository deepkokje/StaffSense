const DEFAULT_LOCALE = "en-US";
const SUPPORTED_CURRENCIES = new Set([
  "USD",
  "EUR",
  "GBP",
  "INR",
  "JPY",
  "CAD",
  "AUD",
  "SGD",
]);

export function formatMinorUnits(amountMinor: number, currency: string): string {
  try {
    if (!SUPPORTED_CURRENCIES.has(currency)) {
      return `${new Intl.NumberFormat(DEFAULT_LOCALE).format(amountMinor)} ${currency}`;
    }
    const currencyDigits = new Intl.NumberFormat(DEFAULT_LOCALE, {
      style: "currency",
      currency,
    }).resolvedOptions().maximumFractionDigits ?? 2;
    return new Intl.NumberFormat(DEFAULT_LOCALE, {
      style: "currency",
      currency,
      minimumFractionDigits: currencyDigits,
      maximumFractionDigits: currencyDigits,
    }).format(amountMinor / 10 ** currencyDigits);
  } catch {
    return `${new Intl.NumberFormat(DEFAULT_LOCALE).format(amountMinor)} ${currency}`;
  }
}
