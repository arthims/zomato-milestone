"use client";

import { useEffect, useState } from "react";
import PreferenceForm from "@/components/PreferenceForm";
import ResultsList from "@/components/ResultsList";
import { fetchMeta, fetchRecommendations } from "@/lib/api";
import type { RecommendRequest, RecommendResponse } from "@/types";

export default function Home() {
  const [cities, setCities]     = useState<string[]>([]);
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState<RecommendResponse | null>(null);
  const [error, setError]       = useState<string | null>(null);

  useEffect(() => {
    fetchMeta().then(m => setCities(m.cities)).catch(() => {});
  }, []);

  async function handleSubmit(req: RecommendRequest) {
    setLoading(true);
    setResult(null);
    setError(null);
    try {
      const res = await fetchRecommendations(req);
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <PreferenceForm cities={cities} onSubmit={handleSubmit} loading={loading} />

      {error && (
        <div className="rounded-input border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {loading && (
        <div className="flex flex-col gap-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-36 rounded-card shimmer" />
          ))}
        </div>
      )}

      {result && !loading && (
        <ResultsList result={result} onReset={() => setResult(null)} />
      )}
    </div>
  );
}
