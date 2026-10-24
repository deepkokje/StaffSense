import { useEffect, useState } from "react";

export const DEBOUNCE_DELAY_MILLISECONDS = 300;

export function useDebouncedValue<T>(
  value: T,
  delayMilliseconds: number = DEBOUNCE_DELAY_MILLISECONDS,
): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => setDebouncedValue(value), delayMilliseconds);
    return () => window.clearTimeout(timeoutId);
  }, [delayMilliseconds, value]);

  return debouncedValue;
}
