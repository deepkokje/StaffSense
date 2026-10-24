const DEFAULT_LOCALE = "en-US";
const ISO_DATE_PATTERN = /^(\d{4})-(\d{2})-(\d{2})$/;
const MONTH_INDEX_OFFSET = 1;

export function formatDate(isoDate: string): string {
  const match = ISO_DATE_PATTERN.exec(isoDate);
  if (!match) {
    return isoDate;
  }
  const [, year, month, day] = match;
  const date = new Date(Number(year), Number(month) - MONTH_INDEX_OFFSET, Number(day));
  return new Intl.DateTimeFormat(DEFAULT_LOCALE, {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(date);
}
