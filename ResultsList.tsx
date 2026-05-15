import type { RecommendResponse } from "@/types";
import ResultCard from "./ResultCard";
import SourceBadge from "./SourceBadge";
import EmptyState from "./EmptyState";

interface Props {
  result: RecommendResponse;
  onReset: () => void;
}

export default function ResultsList({ result, onReset }: Props) {
  const isEmpty = result.items.length === 0;

  return (
    <div className="mt-6">
      {/* header row */}
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-gray-500">
          {isEmpty
            ? "No results"
            : `${result.items.length} recommendations · ${result.candidate_count} matched`}
        </p>
        <SourceBadge source={result.source} />
      </div>

      {isEmpty ? (
        <EmptyState kind="no_candidates" onReset={onReset} />
      ) : (
        <div className="flex flex-col gap-4">
          {result.items.map((item) => (
            <ResultCard key={item.restaurant_id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
