import type { RecommendedItem } from "@/types";

export default function ResultCard({ item }: { item: RecommendedItem }) {
  return (
    <div className="bg-white rounded-card shadow-card p-5 flex gap-4 hover:shadow-md transition-shadow">
      {/* rank */}
      <span className="text-3xl font-bold text-accent leading-none mt-0.5 min-w-[2rem]">
        #{item.rank}
      </span>

      <div className="flex-1 min-w-0">
        {/* name + type */}
        <div className="flex items-baseline gap-2 flex-wrap">
          <h3 className="text-base font-semibold text-gray-900 truncate">{item.name}</h3>
          {item.restaurant_type && (
            <span className="text-xs text-gray-400 shrink-0">{item.restaurant_type}</span>
          )}
        </div>

        {/* cuisine chips */}
        <div className="flex flex-wrap gap-1 mt-1.5">
          {item.cuisines.map((c) => (
            <span
              key={c}
              className="text-xs px-2 py-0.5 rounded-full bg-orange-50 text-orange-700 border border-orange-100"
            >
              {c}
            </span>
          ))}
        </div>

        {/* rating + cost */}
        <div className="flex items-center gap-4 mt-2 text-sm">
          <span className="font-medium text-amber-500">{item.display_rating}</span>
          <span className="text-gray-500">{item.display_cost}</span>
        </div>

        {/* AI explanation */}
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-xs text-gray-400 mb-1 uppercase tracking-wide">Why this pick</p>
          <p className="text-sm text-gray-600 italic leading-relaxed">{item.explanation}</p>
        </div>
      </div>
    </div>
  );
}
