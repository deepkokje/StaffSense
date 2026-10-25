const DEFAULT_API_BASE_URL = "http://localhost:8000";
const HTTP_STATUS_SUCCESS_MINIMUM = 200;
const HTTP_STATUS_SUCCESS_MAXIMUM = 300;

function detailMessage(detail: unknown): string | undefined {
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    const messages = detail.flatMap((entry: unknown) => {
      if (typeof entry !== "object" || entry === null || !("msg" in entry) ||
          typeof entry.msg !== "string") {
        return [];
      }
      return [entry.msg];
    });
    return messages.length ? messages.join("; ") : undefined;
  }
  return undefined;
}

type QueryValue = string | number | boolean;
export type QueryParameters = Record<
  string,
  QueryValue | readonly QueryValue[] | undefined
>;

export class ApiError extends Error {
  readonly status: number;
  readonly detail: unknown;

  constructor(status: number, message: string, detail: unknown = message) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
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

  return requestJson<T>(url, { signal });
}

export function sendJson<T>(
  path: string,
  method: "POST" | "PUT" | "DELETE",
  body?: unknown,
): Promise<T> {
  return requestJson<T>(new URL(path, getApiBaseUrl()), {
    method,
    headers: body === undefined ? undefined : { "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
}

async function requestJson<T>(url: URL, options: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  if (
    response.status < HTTP_STATUS_SUCCESS_MINIMUM ||
    response.status >= HTTP_STATUS_SUCCESS_MAXIMUM
  ) {
    const text = await response.text();
    let parsed: unknown;
    try {
      parsed = JSON.parse(text);
    } catch (error) {
      if (!(error instanceof SyntaxError)) {
        throw error;
      }
      throw new ApiError(response.status, `Request failed with status ${response.status}.`);
    }
    const detail = typeof parsed === "object" && parsed !== null && "detail" in parsed
      ? parsed.detail
      : undefined;
    const message = detailMessage(detail) ?? `Request failed with status ${response.status}.`;
    throw new ApiError(response.status, message, detail);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return (await response.json()) as T;
}
