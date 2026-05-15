import type { MetaResponse, RecommendRequest, RecommendResponse } from "@/types";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchMeta(): Promise<MetaResponse> {
  const res = await fetch(`${BASE}/api/v1/meta`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load meta");
  return res.json();
}

export async function fetchRecommendations(
  body: RecommendRequest
): Promise<RecommendResponse> {
  const res = await fetch(`${BASE}/api/v1/recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail ?? `Request failed (${res.status})`);
  }
  return res.json();
}
