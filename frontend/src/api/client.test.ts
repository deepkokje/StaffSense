import { afterEach, describe, expect, test, vi } from "vitest";

import { ApiError, getJson } from "./client";

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("getJson", () => {
  test("encodes repeated values and omits undefined parameters", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), { status: 200 }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await getJson<{ ok: boolean }>("/employees", {
      country: ["IN", "US"],
      page: 1,
      missing: undefined,
    });

    const requestedUrl = new URL(fetchMock.mock.calls[0][0] as string);
    expect(requestedUrl.searchParams.getAll("country")).toEqual(["IN", "US"]);
    expect(requestedUrl.searchParams.get("page")).toBe("1");
    expect(requestedUrl.searchParams.has("missing")).toBe(false);
  });

  test("throws ApiError with the response status for server errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("failure", { status: 500 })),
    );

    await expect(getJson("/employees")).rejects.toMatchObject({
      name: "ApiError",
      status: 500,
    } satisfies Partial<ApiError>);
  });
});
