# Design

<!-- impeccable:design-schema 1 -->

## World

**The category standard, played straight.** The user took the standing exit in the
direction round: build what a premium education/SaaS product ships, at full craft,
without irony or smuggled quirk.

Craft bar, set by the user: **Linear / Vercel / Stripe** (engineering precision —
tight type scale, hairline borders, restrained layered shadows, obsessive spacing,
fast purposeful motion) crossed with **Coursera / Brilliant / Maven** (education
warmth — generous cards, clear program taxonomy, learner progress as a first-class
surface).

Where the canon's slots demand things this product does not have — star ratings,
student counts, testimonials — the slot is **removed or replaced with real proof**,
never filled with invented content. That is the one non-negotiable edit to the canon.

## Mode

- `/` — **Persuade**
- `/courses/{slug}`, `/dashboard` — **Persuade → Operate** hybrid
- `/lessons/{id}` — **Read** (longest dwell on the site; reading comfort outranks expression)
- `/admin/*` — **Operate**

## Color

Strategy: **Restrained** (neutral ground + one decisive accent), with two
**committed** full-bleed bands — the results strip and the final CTA — where deep
navy owns the whole region.

Light, not dark. Use scene: a thesis candidate reading long technical material at
11pm on a laptop, and professionals reading at a desk in daylight. Long-form
reading decides it.

Brand blue is sampled from the existing logo shield (a binding asset), not invented.

| Token | Value | Role |
|---|---|---|
| `--brand` | `#0A4FA8` | primary action, links, active state (8.2:1 on white) |
| `--brand-700` | `#083E85` | pressed / hover |
| `--brand-050` | `#EEF4FD` | tint fields, chips |
| `--navy` | `#071B35` | committed dark bands, headings |
| `--ink` | `#0B1524` | body text |
| `--ink-2` | `#4C5A70` | secondary text (4.6:1 on white) |
| `--ink-3` | `#6E7C93` | tertiary / meta |
| `--line` | `#E3E7EE` | hairlines |
| `--ground` | `#F7F8FB` | page ground |
| `--surface` | `#FFFFFF` | cards |
| `--gold` / `--gold-ink` | `#E9A83C` / `#96671B` | **certificate / achievement only** — never a generic accent |
| `--green` / `--green-ink` | `#16A06B` / `#0C6B47` | progress, passed, free |
| `--red` / `--red-ink` | `#E05252` | errors, locked |

Gold is semantic, not decorative: it appears only where a certificate or a completed
achievement is the subject. Green means *earned or free*. Everything else is blue or
neutral.

## Type

Two families, both self-consistent, loaded from Google Fonts with a real fallback stack.

- **Geist** — display and body. 400/500/600/700. Display sizes run at `-0.035em`
  tracking and `1.02` line-height; body at `1.65`.
- **Geist Mono** — only for genuine data and measurement: lesson counts, percentages,
  fees, lesson indices, registry-style values. Never as a "technical" costume.

Fluid scale, clamped:

| Step | Size |
|---|---|
| display | `clamp(2.75rem, 1.55rem + 5.3vw, 5.25rem)` |
| h2 | `clamp(2rem, 1.35rem + 2.9vw, 3.25rem)` |
| h3 | `clamp(1.25rem, 1.12rem + 0.6vw, 1.5rem)` |
| body | `clamp(1.0625rem, 1.03rem + 0.16vw, 1.1875rem)` |
| small | `0.875rem` · label `0.8125rem` |

Body measure caps at **68ch**; lesson prose at **66ch**.

## Space & form

- 4px base scale: 4 8 12 16 20 24 32 40 48 64 80 96 128 160.
- Container 1200px, gutters 20px → 32px → 40px.
- Radii: `6` inputs · `10` buttons/chips · `16` cards · `24` panels · `999` pills.
  The brief's 16–28px range applies to cards and panels, not to controls.
- Shadows always carry offset + soft blur, layered in two parts, tinted with the navy
  hue rather than neutral black. Four steps: `sm md lg xl`.
- Borders are 1px hairlines at `--line`. No colored left-borders above 1px.

## Motion

- Easing: `--ease` `cubic-bezier(0.16, 1, 0.3, 1)` (exponential out) for everything
  entering; `cubic-bezier(0.65, 0, 0.35, 1)` for state changes.
- Durations: `120ms` micro · `220ms` standard · `560ms` reveal · `760ms` hero.
- **One authored moment:** the hero load. Headline, sub, actions and trust line rise
  in a 70ms-stepped stagger; the layered proof composition settles last with a small
  overshoot, then its floating cards begin a very slow, offset drift.
- Everything else is quieter and secondary: section fade-up on intersect (staggered
  children), counters that count once, hover lift on cards, arrow translate on hover,
  animated nav underline, nav compacting to glass on scroll.
- All animated properties are `transform`, `opacity`, `filter` or `clip-path`.
- `prefers-reduced-motion: reduce` disables every transition and animation and
  renders all revealed content at its final state. Counters print final values.

## Components

`.btn` (primary / secondary / ghost / on-dark, + sizes) · `.card` · `.course-card`
(fixed three-slot line stack: meta row, title, description) · `.chip` · `.badge` ·
`.field` · `.stat` · `.step` · `.route` (lesson list) · `.progress` · `.marquee` ·
`.carousel` · `.site-nav` · `.site-footer` · `.prose` (lesson body) · `.admin-table`.

## Icons

Authored inline SVG, 24×24 viewBox, `1.6` stroke, `round` cap and join,
`currentColor`. Defined once as Jinja macros in `templates/_icons.html`.
**No emoji, no unicode glyphs as icons** — this replaces the previous 🔒 and 🎓.

## Browser surfaces

Themed, not left to defaults: `::selection`, caret color, focus ring
(`2px --brand` + `2px` offset), custom scrollbar on dark bands,
`text-underline-offset`, and `font-variant-numeric: tabular-nums` on every numeric
readout.

## Not used

Eyebrows/kickers above headings · gradient text · glass as decoration ·
hard offset shadows · emoji icons · star ratings · invented testimonials, student
counts or satisfaction percentages · monospace as a technical costume.
