"use client";

import { useState } from "react";
import type { RecommendRequest } from "@/types";

const CUISINES = ["North Indian","Chinese","Italian","Continental","South Indian","American","Asian","Biryani"];
const BUDGETS  = ["low","medium","high"] as const;
const RATINGS  = [0, 1, 2, 3, 4, 5] as const;

interface Props {
  cities:   string[];
  onSubmit: (req: RecommendRequest) => void;
  loading:  boolean;
}

export default function PreferenceForm({ cities, onSubmit, loading }: Props) {
  const [location,   setLocation]  = useState("");
  const [budget,     setBudget]    = useState<"low"|"medium"|"high"|null>(null);
  const [cuisines,   setCuisines]  = useState<string[]>([]);
  const [minRating,  setMinRating] = useState<number>(0);
  const [extra,      setExtra]     = useState("");
  const [filtered,   setFiltered]  = useState<string[]>([]);
  const [showDrop,   setShowDrop]  = useState(false);

  function onLocation(val: string) {
    setLocation(val);
    setFiltered(val.length > 0
      ? cities.filter(c => c.toLowerCase().includes(val.toLowerCase())).slice(0, 6)
      : []);
    setShowDrop(true);
  }

  function toggleCuisine(c: string) {
    setCuisines(prev => prev.includes(c) ? prev.filter(x => x !== c) : [...prev, c]);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!location.trim()) return;
    onSubmit({ location, budget, cuisines, min_rating: minRating, additional_preferences: extra });
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-card shadow-card p-6 flex flex-col gap-5">

      {/* Location */}
      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 mb-1">Location *</label>
        <input
          value={location}
          onChange={e => onLocation(e.target.value)}
          onBlur={() => setTimeout(() => setShowDrop(false), 150)}
          placeholder="e.g. Bellandur, Indiranagar"
          className="w-full border border-gray-200 rounded-input px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent/40"
          required
        />
        {showDrop && filtered.length > 0 && (
          <ul className="absolute z-10 w-full bg-white border border-gray-100 rounded-input shadow-card mt-1 max-h-40 overflow-auto">
            {filtered.map(c => (
              <li key={c} onMouseDown={() => { setLocation(c); setShowDrop(false); }}
                className="px-3 py-2 text-sm hover:bg-orange-50 cursor-pointer">{c}</li>
            ))}
          </ul>
        )}
      </div>

      {/* Budget */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Budget</label>
        <div className="flex gap-2">
          {BUDGETS.map(b => (
            <button key={b} type="button" onClick={() => setBudget(budget === b ? null : b)}
              className={`flex-1 py-2 text-sm rounded-input border transition-colors capitalize
                ${budget === b ? "bg-accent text-white border-accent" : "border-gray-200 text-gray-600 hover:border-accent/50"}`}>
              {b}
            </button>
          ))}
        </div>
      </div>

      {/* Cuisine */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Cuisine</label>
        <div className="flex flex-wrap gap-2">
          {CUISINES.map(c => (
            <button key={c} type="button" onClick={() => toggleCuisine(c)}
              className={`px-3 py-1 text-xs rounded-full border transition-colors
                ${cuisines.includes(c) ? "bg-accent text-white border-accent" : "border-gray-200 text-gray-600 hover:border-accent/50"}`}>
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Minimum Rating — star buttons */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Minimum Rating
          <span className="ml-2 text-amber-500 font-semibold">
            {minRating === 0 ? "Any" : `${minRating} ★`}
          </span>
        </label>
        <div className="flex items-center gap-1">
          {RATINGS.map(r => (
            <button
              key={r}
              type="button"
              onClick={() => setMinRating(minRating === r ? 0 : r)}
              className="flex items-center gap-1 px-3 py-1.5 rounded-input border text-sm font-medium transition-colors"
              style={{
                background:   minRating > 0 && r <= minRating ? "#E23744" : "white",
                borderColor:  minRating > 0 && r <= minRating ? "#E23744" : "#E5E7EB",
                color:        minRating > 0 && r <= minRating ? "white"   : "#6B7280",
              }}
            >
              {r === 0 ? "Any" : <>{r} ★</>}
            </button>
          ))}
        </div>
        <p className="text-xs text-gray-400 mt-1">
          {minRating === 0 ? "Showing all ratings" : `Showing restaurants rated ${minRating}★ and above`}
        </p>
      </div>

      {/* Additional preferences */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Additional preferences</label>
        <textarea
          value={extra} onChange={e => setExtra(e.target.value.slice(0, 500))}
          placeholder="e.g. family-friendly, outdoor seating, quick service"
          rows={2}
          className="w-full border border-gray-200 rounded-input px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-accent/40" />
        <p className="text-xs text-gray-400 text-right">{extra.length}/500</p>
      </div>

      {/* Submit */}
      <button type="submit" disabled={loading || !location.trim()}
        className="w-full py-3 rounded-input bg-accent text-white font-semibold text-sm
          hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors
          flex items-center justify-center gap-2">
        {loading
          ? <><span className="h-4 w-4 rounded-full border-2 border-white border-t-transparent animate-spin" />Finding the best matches…</>
          : "Find Restaurants"}
      </button>

    </form>
  );
}
