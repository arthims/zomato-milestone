# Google Stitch UI Prompt — Zomato AI Restaurant Recommendation

## What to generate

Generate a complete set of UI screens for an AI-powered restaurant recommendation web app built with **Next.js + Tailwind CSS**. The app takes user preferences and returns LLM-ranked restaurant suggestions.

---

## Screens to generate

### Screen 1 — Home / Preference Form

A clean, full-width search form. Header at top with app name **"Zomato AI"** and a subtitle **"Find your next meal, powered by AI"**.

Form fields (vertical stack, card container, max-width 560px, centered):

- **Location** — text input with dropdown autocomplete. Placeholder: `e.g. Bellandur, Indiranagar`
- **Budget** — segmented button group with 3 options: `Low`, `Medium`, `High`. Default unselected.
- **Cuisine** — multi-select pill chips. Options: `North Indian`, `Chinese`, `Italian`, `Continental`, `South Indian`, `American`, `Asian`, `Biryani`. User can tap multiple.
- **Minimum rating** — horizontal slider, range 0.0 to 5.0, step 0.5. Shows current value as `★ 4.0` beside the slider.
- **Additional preferences** — textarea, max 500 characters. Placeholder: `e.g. family-friendly, outdoor seating, quick service`
- **Submit button** — full-width, prominent, label: `Find Restaurants`. Disabled while loading.

Style: white card on a warm off-white background. Subtle red accent color (`#E23744`) matching Zomato brand. Rounded corners. Clean sans-serif font.

---

### Screen 2 — Loading State

Same layout as Screen 1 but the submit button is replaced with a pulsing spinner and the text **"Finding the best matches…"**. Form fields are dimmed/disabled. A subtle skeleton shimmer below the form hints that results are loading.

---

### Screen 3 — Results Page

Header unchanged. Below the form (collapsed to a compact summary bar showing the search params), show a results section:

**Source badge** (top-right of results section):
- Green badge `AI Ranked` when `source === "llm"`
- Yellow badge `Top by Rating` when `source === "fallback"`
- Gray badge — hidden when `source === "no_candidates"`

**Result cards** — vertical stack, each card contains:
- Rank number `#1`, `#2` etc. — large, left-aligned, accent color
- Restaurant name — bold, 18px
- Cuisine tags — small pill chips (e.g. `Asian` `Chinese` `Japanese`)
- Rating — star icon + `4.6 ★` in amber
- Estimated cost — `₹1,800 for two`
- Restaurant type — muted label e.g. `Casual Dining`
- AI explanation — italic text block below a thin divider, slightly muted color. Label: `Why this pick`

Show 5 cards. Each card has a subtle hover lift shadow.

---

### Screen 4 — Empty State

Two variants (show as two sub-screens side by side or stacked):

**Variant A — No filter match:**
Illustration placeholder (simple icon — a bowl with a question mark). Heading: `No restaurants match your filters`. Subtext: `Try broadening your search — widen the budget, lower the minimum rating, or select fewer cuisines.` Button: `Adjust filters`.

**Variant B — AI could not rank:**
Different icon (robot/star). Heading: `AI couldn't find a strong match`. Subtext: `Try adjusting your preferences or adding more cuisines.` Button: `Try again`.

---

### Screen 5 — Mobile view (375px)

Responsive version of Screen 3 (results). Single-column layout. Cards stack full width. Cuisine chips wrap. Rating and cost on separate lines. Compact header.

---

## Design specifications

| Token | Value |
|---|---|
| Primary accent | `#E23744` (Zomato red) |
| Background | `#FFF8F0` (warm off-white) |
| Card background | `#FFFFFF` |
| Text primary | `#1C1C1E` |
| Text secondary | `#6B7280` |
| Rating amber | `#F59E0B` |
| Success green | `#10B981` |
| Border radius | `12px` cards, `8px` inputs |
| Font | Inter or system sans-serif |
| Card shadow | `0 2px 8px rgba(0,0,0,0.08)` |
| Max content width | `720px` centered |

---

## API contract (for wiring context)

The UI calls one endpoint:

```
POST /api/v1/recommendations
Content-Type: application/json

{
  "location": "Bellandur",
  "budget": "high",
  "cuisines": ["Chinese", "Asian"],
  "min_rating": 4.0,
  "additional_preferences": "family-friendly"
}
```

Response shape:

```json
{
  "items": [
    {
      "rank": 1,
      "name": "The Fatty Bao",
      "location": "Bellandur",
      "cuisines": ["Asian", "Chinese", "Japanese"],
      "display_rating": "4.6 ★",
      "display_cost": "₹1,800 for two",
      "restaurant_type": "Casual Dining",
      "explanation": "Top-rated Asian fusion within your ₹2,000 budget."
    }
  ],
  "source": "llm",
  "candidate_count": 9,
  "filter_count": 12,
  "latency_ms": 312.4
}
```

Source values: `llm` → show green AI badge. `fallback` → show yellow badge. `no_candidates` → show empty state A.

Meta endpoint for city dropdown:
```
GET /api/v1/meta
→ { "cities": ["Bellandur", "Indiranagar", ...], "total_restaurants": 4832 }
```

---

## Next.js file structure to scaffold

```
frontend/
├── app/
│   ├── layout.tsx          # root layout, metadata
│   ├── page.tsx            # home — renders PreferenceForm
│   └── results/
│       └── page.tsx        # results page (or same page with state)
├── components/
│   ├── PreferenceForm.tsx  # all 5 form fields + submit
│   ├── ResultCard.tsx      # single restaurant card
│   ├── ResultsList.tsx     # maps items → ResultCard
│   ├── SourceBadge.tsx     # llm / fallback / no_candidates badge
│   └── EmptyState.tsx      # no_candidates + llm_no_picks variants
├── lib/
│   └── api.ts              # typed fetch wrapper for POST /api/v1/recommendations
├── types/
│   └── index.ts            # RecommendRequest, RecommendedItem, RecommendResponse
└── .env.local
    NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

---

## Interaction notes

- City dropdown populates from `GET /api/v1/meta` on page load.
- Submit is disabled until `location` is filled.
- While fetching, show Screen 2 (loading state).
- On success, transition to Screen 3 (results).
- On empty `items` with `source === "no_candidates"`, show Empty State A.
- On network error, show a banner: `Could not connect to the recommendation service. Please try again.`
- Re-submitting the form clears previous results and shows loading state again.
