const BASIS_POINTS_DECIMAL_DIGITS = 2;

export function formatBasisPoints(basisPoints: number): string {
  if (!Number.isSafeInteger(basisPoints)) {
    throw new Error("Basis points must be a safe integer.");
  }
  const negative = basisPoints < 0;
  const digits = String(basisPoints).replace("-", "")
    .padStart(BASIS_POINTS_DECIMAL_DIGITS + 1, "0");
  return `${negative ? "-" : ""}${digits.slice(0, -BASIS_POINTS_DECIMAL_DIGITS)}.${digits.slice(-BASIS_POINTS_DECIMAL_DIGITS)}%`;
}
