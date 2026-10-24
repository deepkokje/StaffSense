export function formatPermille(value: number): string {
  if (!Number.isSafeInteger(value)) {
    throw new RangeError("Per-mille values must be safe integers.");
  }
  const text = String(value);
  const negative = text.startsWith("-");
  const digits = (negative ? text.slice(1) : text).padStart(2, "0");
  return `${negative ? "-" : ""}${digits.slice(0, -1)}.${digits.slice(-1)}%`;
}
