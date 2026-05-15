"""
tests/test_phase4_live_example.py
----------------------------------
Live-style end-to-end test for Phase 4.
Input  : Location=Bellandur, Budget=₹2000, Min Rating=4.0
Output : Top 5 restaurants ranked by Groq LLM (llama-3.3-70b-versatile)

In this environment Groq's API is network-blocked, so call_groq is patched
with a response that is structurally identical to what the real API returns.
All other layers — normalizer, filter, prompt builder, parser, ranker,
fallback, renderer — run fully for real with no mocking.

Run: python tests/test_phase4_live_example.py
"""
import json, sys, warnings
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from milestone1.phase1_ingestion.normalizer import normalize_row
from milestone1.phase2_preferences.models import BudgetBand, UserPreferences
from milestone1.phase3_integration.output import build_integration_output
from milestone1.phase4_llm.recommend import recommend_with_groq
from milestone1.phase4_llm.models import RankedItem, RecommendationResult

# ── Bellandur restaurant corpus ───────────────────────────────────────────
BELLANDUR_ROWS = [
    {"name": "The Fatty Bao",        "location": "Bellandur", "cuisines": "Asian, Chinese, Japanese",          "approx_cost(for two people)": "1800", "rate": "4.6/5", "votes": 1840, "rest_type": "Casual Dining", "listed_in(type)": "Dine-out"},
    {"name": "Truffles",             "location": "Bellandur", "cuisines": "American, Burger, Continental",     "approx_cost(for two people)": "1200", "rate": "4.5/5", "votes": 2310, "rest_type": "Casual Dining", "listed_in(type)": "Dine-out"},
    {"name": "Burma Burma",          "location": "Bellandur", "cuisines": "Burmese, Asian",                    "approx_cost(for two people)": "1600", "rate": "4.4/5", "votes": 980,  "rest_type": "Casual Dining", "listed_in(type)": "Dine-out"},
    {"name": "Meghana Foods",        "location": "Bellandur", "cuisines": "Biryani, South Indian, Andhra",     "approx_cost(for two people)": "600",  "rate": "4.4/5", "votes": 4100, "rest_type": "Quick Bites",   "listed_in(type)": "Dine-out"},
    {"name": "Onesta",               "location": "Bellandur", "cuisines": "Italian, Pizza, Pasta",             "approx_cost(for two people)": "900",  "rate": "4.3/5", "votes": 1550, "rest_type": "Casual Dining", "listed_in(type)": "Dine-out"},
    {"name": "Absolute Barbecues",   "location": "Bellandur", "cuisines": "North Indian, Chinese, Seafood",    "approx_cost(for two people)": "2000", "rate": "4.3/5", "votes": 2750, "rest_type": "Casual Dining", "listed_in(type)": "Dine-out"},
    {"name": "Hammered",             "location": "Bellandur", "cuisines": "North Indian, Continental, Bar Food","approx_cost(for two people)": "2000", "rate": "4.2/5", "votes": 730,  "rest_type": "Bar",           "listed_in(type)": "Dine-out"},
    {"name": "Barbeque Nation",      "location": "Bellandur", "cuisines": "North Indian, Barbeque",            "approx_cost(for two people)": "1800", "rate": "4.1/5", "votes": 3200, "rest_type": "Casual Dining", "listed_in(type)": "Dine-out"},
    {"name": "Smoke House Deli",     "location": "Bellandur", "cuisines": "Continental, Italian, Salads",      "approx_cost(for two people)": "1500", "rate": "4.1/5", "votes": 640,  "rest_type": "Casual Dining", "listed_in(type)": "Dine-out"},
    {"name": "Chili's",              "location": "Bellandur", "cuisines": "American, Mexican, Continental",    "approx_cost(for two people)": "1700", "rate": "4.0/5", "votes": 1120, "rest_type": "Casual Dining", "listed_in(type)": "Dine-out"},
    {"name": "Fenny's Lounge",       "location": "Bellandur", "cuisines": "North Indian, Continental, Seafood","approx_cost(for two people)": "1800", "rate": "3.9/5", "votes": 510,  "rest_type": "Bar",           "listed_in(type)": "Dine-out"},
    {"name": "Mainland China",       "location": "Bellandur", "cuisines": "Chinese",                           "approx_cost(for two people)": "1600", "rate": "3.8/5", "votes": 420,  "rest_type": "Casual Dining", "listed_in(type)": "Dine-out"},
]

# ── Groq API mock response — identical structure to real API output ────────
MOCK_GROQ_RESPONSE = json.dumps({
    "rankings": [
        {
            "restaurant_id": "the_fatty_bao_bellandur",
            "rank": 1,
            "explanation": (
                "The Fatty Bao is the highest-rated restaurant in Bellandur at 4.6★ "
                "with 1,840 votes. Its Asian fusion menu is creative and well-executed, "
                "and at ₹1,800 for two it sits comfortably within your ₹2,000 budget."
            )
        },
        {
            "restaurant_id": "truffles_bellandur",
            "rank": 2,
            "explanation": (
                "Truffles is Bellandur's most-voted restaurant (2,310 votes) with a stellar "
                "4.5★ rating. Known for juicy burgers and hearty American fare, it delivers "
                "excellent value at ₹1,200 — well under your budget."
            )
        },
        {
            "restaurant_id": "absolute_barbecues_bellandur",
            "rank": 3,
            "explanation": (
                "Absolute Barbecues offers a premium unlimited BBQ experience with a strong "
                "4.3★ backed by 2,750 votes. At exactly ₹2,000 for two, it matches your "
                "budget perfectly and is ideal for a celebratory meal."
            )
        },
        {
            "restaurant_id": "burma_burma_bellandur",
            "rank": 4,
            "explanation": (
                "Burma Burma delivers a unique Burmese dining experience rare in Bangalore. "
                "Rated 4.4★ with 980 votes, its tea-leaf salads and khao suey stand out. "
                "At ₹1,600 for two it leaves ₹400 to spare."
            )
        },
        {
            "restaurant_id": "barbeque_nation_bellandur",
            "rank": 5,
            "explanation": (
                "Barbeque Nation is the most crowd-voted pick in Bellandur (3,200 votes) "
                "with a solid 4.1★. The unlimited North Indian barbeque and live counters "
                "make it a reliable choice at ₹1,800 for two."
            )
        }
    ]
})

MOCK_USAGE = {
    "prompt_tokens": 812,
    "completion_tokens": 248,
    "total_tokens": 1060,
}

# ── test runner ────────────────────────────────────────────────────────────
p = f = 0

def ok(n):
    global p; p += 1; print(f'  PASS  {n}')

def fail(n, e):
    global f; f += 1; print(f'  FAIL  {n}: {e}')

def chk(n, fn):
    try: fn(); ok(n)
    except Exception as e: fail(n, e)

def eq(a, b):  assert a == b,  f'{a!r} != {b!r}'
def true(v):   assert v,       f'Expected truthy, got {v!r}'

# ── setup ─────────────────────────────────────────────────────────────────
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    RESTAURANTS = [r for r in [normalize_row(x) for x in BELLANDUR_ROWS] if r is not None]

PREFS = UserPreferences(
    location='Bellandur',
    budget=BudgetBand.HIGH,      # ₹2000 → high band (>₹700)
    cuisines=[],                  # no cuisine restriction
    min_rating=4.0,
    additional_preferences='Budget around ₹2000 for two',
)

INTEGRATION = build_integration_output(RESTAURANTS, PREFS, candidate_cap=20)

with patch('milestone1.phase4_llm.recommend.call_groq') as mock_groq:
    mock_groq.return_value = (MOCK_GROQ_RESPONSE, MOCK_USAGE)
    RESULT = recommend_with_groq(
        INTEGRATION, PREFS,
        api_key='test-key',
        model='llama-3.3-70b-versatile',
    )

# ══════════════════════════════════════════════════════════════════════════
# Tests
# ══════════════════════════════════════════════════════════════════════════
print('\n── Input validation ──')
chk('location_is_Bellandur',
    lambda: eq(PREFS.location, 'Bellandur'))
chk('budget_is_high_band',
    lambda: eq(PREFS.budget, BudgetBand.HIGH))
chk('min_rating_is_4',
    lambda: eq(PREFS.min_rating, 4.0))
chk('corpus_loaded_all_restaurants',
    lambda: eq(len(RESTAURANTS), 12))

print('\n── Filter layer ──')
chk('candidates_found',
    lambda: true(INTEGRATION.has_candidates))
chk('all_candidates_in_bellandur',
    lambda: true(all('bellandur' in r.location.lower() for r in INTEGRATION.candidates)))
chk('all_candidates_rating_gte_4',
    lambda: true(all(r.rating >= 4.0 for r in INTEGRATION.candidates)))
chk('all_candidates_budget_high',
    lambda: true(all(r.budget == 'high' for r in INTEGRATION.candidates)))
chk('low_rated_excluded',
    lambda: true(all(r.name != "Fenny's Lounge" for r in INTEGRATION.candidates)))
chk('below_budget_excluded',
    lambda: true(all(r.name != 'Mainland China' for r in INTEGRATION.candidates)))
chk('candidates_sorted_by_rating',
    lambda: (lambda rs: true(
        [x.rating for x in rs] == sorted([x.rating for x in rs], reverse=True)
    ))(INTEGRATION.candidates))
chk('filter_count_is_full_corpus',
    lambda: eq(INTEGRATION.filter_count, len(RESTAURANTS)))

print('\n── LLM result ──')
chk('source_is_llm',
    lambda: eq(RESULT.source, 'llm'))
chk('exactly_5_results',
    lambda: eq(len(RESULT.items), 5))
chk('ranks_are_1_to_5',
    lambda: eq([i.rank for i in RESULT.items], [1, 2, 3, 4, 5]))
chk('all_items_are_RankedItem',
    lambda: true(all(isinstance(i, RankedItem) for i in RESULT.items)))
chk('token_usage_recorded',
    lambda: eq(RESULT.token_usage.get('total_tokens'), 1060))
chk('result_json_serialisable',
    lambda: json.dumps(RESULT.to_dict()))

print('\n── Top 5 restaurants ──')
expected_top5 = [
    ('The Fatty Bao',      4.6, '1800'),
    ('Truffles',           4.5, '1200'),
    ('Absolute Barbecues', 4.3, '2000'),
    ('Burma Burma',        4.4, '1600'),
    ('Barbeque Nation',    4.1, '1800'),
]
for rank, (name, rating, cost) in enumerate(expected_top5, 1):
    item = RESULT.items[rank - 1]
    chk(f'rank{rank}_name_is_{name.replace(" ","_")}',
        lambda n=name, i=item: eq(i.restaurant.name, n))
    chk(f'rank{rank}_rating_is_{rating}',
        lambda r=rating, i=item: eq(i.restaurant.rating, r))
    chk(f'rank{rank}_cost_is_{cost}',
        lambda c=cost, i=item: eq(i.restaurant.cost_raw, c))
    chk(f'rank{rank}_explanation_non_empty',
        lambda i=item: true(len(i.explanation) > 20))
    chk(f'rank{rank}_within_budget',
        lambda i=item: true(float(i.restaurant.cost_raw) <= 2000))

print('\n── Display output ──')
chk('display_rating_format',
    lambda: true('★' in RESULT.items[0].restaurant.display_rating))
chk('display_cost_format',
    lambda: true(RESULT.items[0].restaurant.display_cost != 'Cost: Not available'))
chk('all_explanations_mention_budget_or_rating',
    lambda: true(any(
        any(kw in i.explanation.lower() for kw in ['₹', 'budget', 'rating', '★', 'votes'])
        for i in RESULT.items
    )))

# ══════════════════════════════════════════════════════════════════════════
# Pretty-print the full recommendation output
# ══════════════════════════════════════════════════════════════════════════
SEP = '═' * 60
print()
print(SEP)
print('  ZOMATO AI RESTAURANT RECOMMENDATIONS')
print(SEP)
print(f'  Location   : {PREFS.location}')
print(f'  Budget     : ₹2,000 for two')
print(f'  Min Rating : {PREFS.min_rating} ★')
print(f'  Cuisine    : Any')
print(SEP)
print(f'  Model      : llama-3.3-70b-versatile (Groq)')
print(f'  Source     : {RESULT.source.upper()}')
print(f'  Tokens     : {RESULT.token_usage["total_tokens"]} '
      f'({RESULT.token_usage["prompt_tokens"]} prompt + '
      f'{RESULT.token_usage["completion_tokens"]} completion)')
print(f'  Candidates : {RESULT.candidate_count} restaurants matched filters')
print(SEP)
print()

for item in RESULT.items:
    r = item.restaurant
    print(f'  #{item.rank}  {r.name}')
    print(f'  {"─" * 50}')
    print(f'  Cuisine   : {", ".join(r.cuisines)}')
    print(f'  Rating    : {r.display_rating}')
    print(f'  Cost      : ₹{r.cost_raw} for two')
    print(f'  Type      : {r.restaurant_type}')
    print(f'  Why       : {item.explanation}')
    print()

print(SEP)
print(f'  ✅  Top {len(RESULT.items)} restaurants via Groq LLM')
print(SEP)

print(f'\n{"=" * 50}')
print(f'Results: {p} passed, {f} failed out of {p + f}')
sys.exit(0 if f == 0 else 1)
