export const MIN_RAISE_BP = 1;
export const MAX_RAISE_BP = 5_000;

type ParsedPercent =
  | { ok: true; basisPoints: number }
  | { ok: false; reason: string };

const DECIMAL_DIGITS = 2;
const PERCENT_PATTERN = /^\d+(?:\.\d{1,2})?$/;
const INVALID_FORMAT_MESSAGE = "Enter a percentage with at most 2 decimal places.";
const OUT_OF_RANGE_MESSAGE = "Enter a percentage between 0.01 and 50.";

export function percentToBasisPoints(input: string): ParsedPercent {
  const text = input.trim();
  if (!PERCENT_PATTERN.test(text)) {
    return { ok: false, reason: INVALID_FORMAT_MESSAGE };
  }
  const [whole, fraction = ""] = text.split(".");
  const basisPoints = BigInt(`${whole}${fraction.padEnd(DECIMAL_DIGITS, "0")}`);
  if (basisPoints < BigInt(MIN_RAISE_BP) || basisPoints > BigInt(MAX_RAISE_BP)) {
    return { ok: false, reason: OUT_OF_RANGE_MESSAGE };
  }
  return { ok: true, basisPoints: Number(basisPoints) };
}
