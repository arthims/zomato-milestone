"""phase6_api.schemas — request and response Pydantic models."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class RecommendRequest(BaseModel):
    location: str = Field(..., min_length=1, max_length=100)
    budget: Optional[str] = Field(None, description="low | medium | high | null")
    cuisines: list[str] = Field(default_factory=list)
    min_rating: float = Field(0.0, ge=0.0, le=5.0)
    additional_preferences: str = Field("", max_length=500)

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, v: Optional[str]) -> Optional[str]:
        if v and v not in ("low", "medium", "high", "any", ""):
            raise ValueError("budget must be low, medium, high, or null")
        return v or None


class RecommendedItem(BaseModel):
    rank: int
    restaurant_id: str
    name: str
    location: str
    cuisines: list[str]
    rating: float
    display_rating: str
    cost_raw: str
    display_cost: str
    budget: str
    restaurant_type: str
    explanation: str


class RecommendResponse(BaseModel):
    items: list[RecommendedItem]
    source: str                  # llm | fallback | no_candidates
    candidate_count: int
    filter_count: int
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    groq_configured: bool


class MetaResponse(BaseModel):
    cities: list[str]
    total_restaurants: int
