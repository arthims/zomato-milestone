import type { RecommendResponse } from "@/types";

const BADGE: Record<
  RecommendResponse["source"],
  { label: string; className: string } | null
> = {
  llm:           { label: "AI Ranked",     className: "bg-emerald-100 text-emerald-700" },
  fallback:      { label: "Top by Rating", className: "bg-amber-100 text-amber-700" },
  no_candidates: null,
};

export default function SourceBadge({ source }: { source: RecommendResponse["source"] }) {
  const badge = BADGE[source];
  if (!badge) return null;
  return (
    <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${badge.className}`}>
      {badge.label}
    </span>
  );
}
