import { afterEach, describe, expect, test, vi } from "vitest";

import { ApiError, getJson, sendJson } from "./client";

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

  test("preserves parsed API detail and uses its message", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ detail: "email is already used by another employee" }), { status: 409 },
    )));
    await expect(sendJson("/employees", "POST", {})).rejects.toMatchObject({
      status: 409, detail: "email is already used by another employee",
      message: "email is already used by another employee",
    });
  });

  test("surfaces validation detail messages", async () => {
    const detail = [{ loc: ["body", "name"], msg: "Name is required" }];
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ detail }), { status: 422 },
    )));
    await expect(sendJson("/employees", "POST", {})).rejects.toMatchObject({
      status: 422, detail, message: "Name is required",
    });
  });

  test("sets the DELETE method and accepts an empty response", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 204 }));
    vi.stubGlobal("fetch", fetchMock);
    await expect(sendJson<void>("/employees/1", "DELETE")).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(expect.any(URL), expect.objectContaining({
      method: "DELETE", body: undefined,
    }));
  });

  test("sends integer write payloads as JSON", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ id: 1, salary_minor: 150050 }), { status: 201 },
    ));
    vi.stubGlobal("fetch", fetchMock);
    await sendJson("/employees", "POST", { salary_minor: 150050 });
    expect(fetchMock).toHaveBeenCalledWith(expect.any(URL), expect.objectContaining({
      method: "POST", headers: { "Content-Type": "application/json" },
      body: '{"salary_minor":150050}',
    }));
  });
});
