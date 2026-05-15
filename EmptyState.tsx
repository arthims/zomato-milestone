"use client";

interface EmptyStateProps {
  kind: "no_candidates" | "llm_no_picks";
  onReset: () => void;
}

const CONFIG = {
  no_candidates: {
    icon: "🍽️",
    heading: "No restaurants match your filters",
    sub: "Try broadening your search — widen the budget, lower the minimum rating, or select fewer cuisines.",
    cta: "Adjust filters",
  },
  llm_no_picks: {
    icon: "🤖",
    heading: "AI couldn't find a strong match",
    sub: "Try adjusting your preferences or adding more cuisines.",
    cta: "Try again",
  },
};

export default function EmptyState({ kind, onReset }: EmptyStateProps) {
  const { icon, heading, sub, cta } = CONFIG[kind];
  return (
    <div className="flex flex-col items-center text-center py-16 gap-4">
      <span className="text-5xl">{icon}</span>
      <h2 className="text-lg font-semibold text-gray-800">{heading}</h2>
      <p className="text-sm text-gray-500 max-w-xs">{sub}</p>
      <button
        onClick={onReset}
        className="mt-2 px-5 py-2 rounded-input bg-accent text-white text-sm font-medium hover:bg-red-600 transition-colors"
      >
        {cta}
      </button>
    </div>
  );
}
