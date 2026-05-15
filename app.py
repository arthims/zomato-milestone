"""
phase9_streamlit.app
--------------------
Single-process Streamlit app — imports phases 1-5 directly, no HTTP.
Secrets: st.secrets["GROQ_API_KEY"] on Cloud, .env locally.

Run locally:
    streamlit run streamlit_app.py
"""
from __future__ import annotations

import warnings
import streamlit as st

from milestone1.phase0.settings import load_settings
from milestone1.phase1_ingestion.loader import (
    load_restaurants, get_unique_cities, DatasetUnavailableError, EmptyCorpusError,
)
from milestone1.phase2_preferences.models import BudgetBand, UserPreferences
from milestone1.phase2_preferences.parser import preferences_from_mapping, PreferencesError
from milestone1.phase2_preferences.cities import allowed_cities_from_restaurants
from milestone1.phase3_integration.output import build_integration_output
from milestone1.phase4_llm.recommend import recommend_with_groq
from milestone1.phase5_output.empty_states import EmptyStateKind, empty_state_message

# ── page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Zomato AI",
    page_icon="🍽️",
    layout="centered",
)

# ── custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .rank-card {
    background: #fff;
    border: 1px solid #eee;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
  }
  .rank-num  { font-size: 2rem; font-weight: 700; color: #E23744; }
  .r-name    { font-size: 1.05rem; font-weight: 600; }
  .r-meta    { font-size: 0.85rem; color: #666; margin: 4px 0; }
  .r-why     { font-size: 0.85rem; color: #555; font-style: italic; }
  .badge-llm { background:#D1FAE5; color:#065F46; padding:2px 10px; border-radius:20px; font-size:.75rem; font-weight:500; }
  .badge-fb  { background:#FEF3C7; color:#92400E; padding:2px 10px; border-radius:20px; font-size:.75rem; font-weight:500; }
</style>
""", unsafe_allow_html=True)


# ── API key — st.secrets (Cloud) or .env (local) ──────────────────────────
def _get_api_key() -> str:
    try:
        return st.secrets.get("GROQ_API_KEY", "") or load_settings().groq_api_key
    except Exception:
        return load_settings().groq_api_key


def _get_model() -> str:
    try:
        return st.secrets.get("GROQ_MODEL", "") or load_settings().groq_model
    except Exception:
        return load_settings().groq_model


# ── corpus (cached so it only loads once per session) ─────────────────────
@st.cache_resource(show_spinner="Loading restaurant data…")
def _load_corpus():
    settings = load_settings()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        restaurants = load_restaurants(
            dataset_name=settings.hf_dataset_name,
            revision=settings.hf_dataset_revision,
            hf_token=settings.hf_token or None,
            load_limit=settings.load_limit,
        )
    cities = get_unique_cities(restaurants)
    return restaurants, cities


# ── main ───────────────────────────────────────────────────────────────────
def main() -> None:
    st.markdown("# 🍽️ Zomato AI")
    st.caption("Find your next meal, powered by AI")
    st.divider()

    # Load corpus
    try:
        restaurants, cities = _load_corpus()
    except (DatasetUnavailableError, EmptyCorpusError) as exc:
        st.error(f"Could not load restaurant data: {exc}")
        st.stop()

    st.caption(f"{len(restaurants):,} restaurants loaded across {len(cities)} cities")

    # ── Form ──────────────────────────────────────────────────────────────
    with st.form("preferences"):
        location = st.selectbox("Location *", options=[""] + cities,
                                format_func=lambda x: "Select a city…" if x == "" else x)

        col1, col2 = st.columns(2)
        with col1:
            budget_label = st.select_slider(
                "Budget", options=["Any", "Low", "Medium", "High"], value="Any"
            )
        with col2:
            min_rating = st.slider("Minimum rating", 0.0, 5.0, 0.0, step=0.5,
                                   format="%.1f ★")

        cuisines = st.multiselect(
            "Cuisine (optional)",
            options=["North Indian","Chinese","Italian","Continental",
                     "South Indian","American","Asian","Biryani"],
        )

        extra = st.text_area("Additional preferences (optional)",
                             placeholder="e.g. family-friendly, outdoor seating",
                             max_chars=500)

        submitted = st.form_submit_button("🔍 Find Restaurants", use_container_width=True)

    if not submitted:
        return

    # ── Validate ──────────────────────────────────────────────────────────
    if not location:
        st.warning("Please select a location.")
        return

    api_key = _get_api_key()
    if not api_key:
        st.error("GROQ_API_KEY is not set. Add it to `.env` or Streamlit secrets.")
        return

    budget = None if budget_label == "Any" else budget_label.lower()

    try:
        allowed = allowed_cities_from_restaurants(restaurants)
        prefs = preferences_from_mapping(
            {"location": location, "budget": budget,
             "cuisines": cuisines, "min_rating": min_rating,
             "additional_preferences": extra},
            allowed_cities=allowed,
        )
    except PreferencesError as exc:
        for field, msg in exc.field_errors.items():
            st.error(f"{field}: {msg}")
        return

    # ── Recommend ─────────────────────────────────────────────────────────
    integration = build_integration_output(restaurants, prefs, candidate_cap=20)

    if not integration.has_candidates:
        st.warning(empty_state_message(EmptyStateKind.NO_CANDIDATES))
        return

    with st.spinner("Asking Groq LLM for recommendations…"):
        result = recommend_with_groq(
            integration, prefs,
            api_key=api_key,
            model=_get_model(),
            timeout=30.0,
        )

    # ── Results header ─────────────────────────────────────────────────────
    st.divider()
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"**{len(result.items)} recommendations** · "
                    f"{result.candidate_count} matched · "
                    f"{result.latency_ms:.0f} ms")
    with col_h2:
        if result.source == "llm":
            st.markdown('<span class="badge-llm">AI Ranked</span>', unsafe_allow_html=True)
        elif result.source == "fallback":
            st.markdown('<span class="badge-fb">Top by Rating</span>', unsafe_allow_html=True)

    if result.source == "fallback":
        st.caption("⚠ AI ranking unavailable — showing top matches by rating.")

    if result.is_empty:
        st.info(empty_state_message(EmptyStateKind.LLM_NO_PICKS))
        return

    # ── Result cards ───────────────────────────────────────────────────────
    for item in result.items:
        r = item.restaurant
        cuisines_str = ", ".join(r.cuisines) if r.cuisines else "N/A"
        with st.container():
            st.markdown(
                f"""
                <div class="rank-card">
                  <span class="rank-num">#{item.rank}</span>
                  <span class="r-name">&nbsp;{r.name}</span>
                  <div class="r-meta">
                    {cuisines_str} &nbsp;·&nbsp; {r.display_rating}
                    &nbsp;·&nbsp; {r.display_cost} &nbsp;·&nbsp; {r.restaurant_type or ""}
                  </div>
                  <div class="r-why">{item.explanation}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Debug expander ─────────────────────────────────────────────────────
    with st.expander("Raw JSON / telemetry"):
        st.json(result.to_dict())
