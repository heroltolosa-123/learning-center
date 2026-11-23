# Deep course rewrite — status

Goal: every course lesson teaches well enough that a reader with no
background can learn the material from the page alone. Target depth is
~12,000–20,000 characters per lesson, built on the twelve-section
template described below.

Last updated 2026-11-24.

## Done (6 of 13)

| Course | Lessons | Median chars | Seed script |
|---|---:|---:|---|
| Design & Analysis of Experiments | 9 | 19,541 | `seed_deep_doe.py` |
| Nonparametric Statistics | 8 | 17,282 | `seed_deep_nonparametric.py` |
| Foundations of Research Methodology | 10 | 13,458 | `seed_deep_research_methodology.py` |
| Intermediate Statistics | 12 | 13,033 | `seed_deep_intermediate_statistics.py` |
| Basic Statistics | 12 | 12,565 | `seed_deep_basic_statistics.py` |
| Applied Statistics for Research | 9 | 12,509 | `seed_deep_applied_statistics.py` |

Catalogue total: **959,257 characters**.

## Remaining (7 of 13)

| Course | Slug | Lessons | Median |
|---|---|---:|---:|
| Probability & Mathematical Statistics | `probability-mathematical-statistics` | 11 | 2,273 |
| Advanced Statistics: PLS-SEM, Survival Analysis | `advanced-statistics` | 11 | 2,104 |
| AI & Machine Learning for Practitioners | `ai-ml-for-practitioners` | 9 | 2,077 |
| Data Warehousing Fundamentals | `data-warehousing-fundamentals` | 9 | 1,996 |
| Time Series Analysis & Forecasting | `time-series-analysis-forecasting` | 8 | 1,970 |
| Data Management Essentials | `data-management-essentials` | 9 | 1,812 |
| Business Intelligence: Dashboards & Automation | `business-intelligence-dashboards` | 9 | 1,794 |

Suggested order: Probability first (it is the theory the statistics
courses lean on), then Time Series, Advanced Statistics, then the four
applied/data courses, which need SQL and code walkthroughs rather than
verified arithmetic and are correspondingly faster to write.

## The working pattern

1. **Point the dev database at the scratchpad**, so the repo stays clean:

       DATABASE_URL=sqlite:////<scratchpad>/dev.db

   written to `.env`, and **deleted again before committing**. A stray
   `learning_center.db` in the repo root means the `.env` was missing.

2. **Rebuild the dev database** if the scratchpad was wiped, by running
   the seed scripts in this order:

       seed_courses, seed_full_curriculum, seed_extended_curriculum,
       seed_ched_core_courses, seed_rich_content,
       seed_basic_stats_elementary, seed_gap_lessons, seed_quizzes,
       seed_ched_deepening, then every seed_deep_*.py

3. **Compute every number first.** Write the whole numeric spine with
   scipy/statsmodels, save it to the scratchpad, then write prose
   against that file — never from memory. Numbers written from memory
   were wrong roughly one time in five across this project. Put the
   verified figures in the seed script's module docstring so the next
   reader can re-check them.

4. **Build the seed script incrementally** with `cat >> ... <<'PYEOF'`
   heredocs, compiling after each lesson:

       python3 -W error::SyntaxWarning -c "compile(open('seed_deep_x.py').read(),'x','exec')"

   `seed_deep_doe.py` keeps a `# MAIN` marker so new `L(...)` blocks can
   be spliced in at the right position without rewriting the file.

5. **Render-check before committing.** Flag raw tables, raw headings,
   unprocessed checkboxes and leftover LaTeX, excluding `<pre>` blocks
   so that absolute-value bars in worked examples do not false-positive.

6. **Commit per course**, delete `.env`, push to `main`.

## Lesson template (twelve sections)

1. What you will be able to do
2. The situation — a `callout-case` scenario
3. The idea before the formula
4. The formula, read term by term
5. A worked example with every arithmetic step shown
6. Doing it in software — Jamovi, SPSS, Excel, R
7. Reading the output
8. Writing it up — a `callout-write` APA template
9. Common mistakes
10. Practice — `<details markdown="1">` with fully worked answers
11. Before you move on — a task checklist
12. A quiz dict passed to `L(...)`

## Rendering conventions (hard-won)

- **No LaTeX.** There is no MathJax. Use
  `<div class="formula" markdown="1">` with HTML entities, or a fenced
  code block for multi-step arithmetic.
- **A table must have a blank line before it.** A table placed directly
  after a `<span class="callout-label">` line is swallowed into that
  paragraph and renders as literal pipes, with `smarty` turning the
  `|---|` separator into `|&mdash;|`.
- **Escape absolute-value bars in table cells** as `&#124;`, or the
  pipe breaks the column count.
- `- [ ]` checkboxes are transformed by `_TASK_ITEM` in
  `app/routers/courses.py`; they work in lists but not inside tables.
- Use `r"""` for any lesson containing a backslash, or
  `-W error::SyntaxWarning` will stop the compile.
