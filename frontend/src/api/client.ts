const DEFAULT_API_BASE_URL = "http://localhost:8000";
const HTTP_STATUS_SUCCESS_MINIMUM = 200;
const HTTP_STATUS_SUCCESS_MAXIMUM = 300;

type QueryValue = string | number | boolean;
export type QueryParameters = Record<
  string,
  QueryValue | readonly QueryValue[] | undefined
>;

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function getApiBaseUrl(): string {
  return import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL;
}

export async function getJson<T>(
  path: string,
  params: QueryParameters = {},
  signal?: AbortSignal,
): Promise<T> {
  const url = new URL(path, getApiBaseUrl());
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined) {
      continue;
    }
    const values = Array.isArray(value) ? value : [value];
    for (const item of values) {
      url.searchParams.append(key, String(item));
    }
  }

  const response = await fetch(url, { signal });
  if (
    response.status < HTTP_STATUS_SUCCESS_MINIMUM ||
    response.status >= HTTP_STATUS_SUCCESS_MAXIMUM
  ) {
    throw new ApiError(response.status, `Request failed with status ${response.status}.`);
  }
  return (await response.json()) as T;
}
