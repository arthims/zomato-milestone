export interface RecommendRequest {
  location: string;
  budget?: "low" | "medium" | "high" | null;
  cuisines: string[];
  min_rating: number;
  additional_preferences?: string;
}

export interface RecommendedItem {
  rank: number;
  restaurant_id: string;
  name: string;
  location: string;
  cuisines: string[];
  rating: number;
  display_rating: string;
  cost_raw: string;
  display_cost: string;
  budget: string;
  restaurant_type: string;
  explanation: string;
}

export interface RecommendResponse {
  items: RecommendedItem[];
  source: "llm" | "fallback" | "no_candidates";
  candidate_count: number;
  filter_count: number;
  latency_ms: number;
}

export interface MetaResponse {
  cities: string[];
  total_restaurants: number;
}
