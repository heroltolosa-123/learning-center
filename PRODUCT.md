# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: Filipino graduate students and thesis/dissertation candidates who need to
choose the right statistical test, run it, and defend the result to a panel. They
arrive under deadline pressure, usually after a statistics subject that taught
formulas but not application, and often after being quoted a large sum by a private
"statistician for hire."

Secondary: working professionals in banking, government, and research offices who
need applied statistics, data management, warehousing, or BI dashboard skills for
their job, and who want a credential they can attach to an application.

Both audiences are adults, self-paced, mostly on mobile, mostly paying in PHP.
They are not children, and there are no parents in the funnel.

## Product Purpose

Hero Academy Learning System is a self-paced online course platform covering
research methodology, statistics, AI/ML, data engineering, and business
intelligence. Learners read lessons, pass a quiz on each lesson to unlock the
next, and receive a signed PDF certificate of completion.

Success = a learner finishes a track and can defend their own analysis without
outsourcing it.

## Positioning

**Free to learn, pay only for the certificate.** Every lesson of every course is
readable at no cost once enrolled; the fee (₱1,500–₱4,500 depending on course) is
charged only when a finisher wants the signed certificate. No paywall sits between
a student and the material.

The teaching is derived from actual thesis-consulting and enterprise work rather
than from a textbook syllabus, and it is taught by one named, credentialed person
rather than an anonymous content team.

## Operating Context

- Self-paced, asynchronous, no cohorts, no live sessions, no scheduled classes.
- Progress is enforced sequentially: a lesson with a quiz must be passed before
  the next lesson unlocks (`LessonProgress` table, admin exempt).
- Payments are PHP-denominated through PayMongo Checkout (GCash, Maya, card).
- Certificate is generated server-side as a PDF with a real scanned signature
  (`app/static/certificate_assets/signature.png`).
- Deployed on Render free tier; SQLite on ephemeral disk.

## Capabilities and Constraints

Confirmed functionality:

- Public catalog with keyword search and category filter (`/`)
- Course detail with lesson list, preview-lesson gating (`/courses/{slug}`)
- Free enrollment (`POST /courses/{slug}/enroll-free`)
- Lesson viewer with markdown content, optional embedded video, quiz gate
- `My Learning` dashboard with per-course progress percentage
- Certificate download, gated on 100% completion + certificate fee paid
- Admin CRUD for courses and lessons (`/admin`)
- Register / login / logout, session cookie auth

Technical constraints:

- FastAPI + Jinja2 + SQLAlchemy. **No build step, no JS framework, no bundler.**
  Any front-end work must be hand-authored CSS/JS served from `app/static/`.
- One stylesheet is shared by public site, learner app, and admin.
- Courses, lessons, categories, levels, prices, and instructor name all come from
  the database — never hard-code them into a template.
- `price_php` = certificate fee, not course price. `Course.is_free` means the
  certificate is also free.
- `Enrollment.status == "paid"` means "active enrollment", not "money received".

Undecided / absent:

- No reviews, ratings, or testimonial storage exists.
- No student count, completion rate, or satisfaction metric is recorded anywhere.
- No live tutoring, 1-on-1 booking, or scheduling feature exists.

## Brand Commitments

- Name: **Hero Academy Learning System** (`SITE_NAME`, overridable by env).
- Logo: blue shield with an "H" monogram and a graduation cap.
  `app/static/logo/hero-academy-logo-transparent.png` (256×256, transparent).
  Watermark and JPEG variants also exist. The mark is binding; it is used on the
  PDF certificate too.
- Instructor identity is binding and factual: **Dr. Hero Tolosa**, PD 997 Civil
  Service Eligible in Statistics, 16+ years across banking, government, and
  academe.
- Voice: direct, practitioner-to-practitioner, no hype. States limits plainly.
- **Standing visual preference (user-chosen, 2026-09-15):** the category standard.
  When a visual direction round is offered, the user's answer was the conventional
  premium education/SaaS page rather than an invented world. Craft bar named by the
  user: Linear / Vercel / Stripe for precision, Coursera / Brilliant / Maven for
  warmth. Execute the convention at full fidelity; do not smuggle in a quirk.

## Evidence on Hand

Real:

- 9 published courses across 5 categories (Research, Statistics,
  AI & Data Science, Data Engineering, Business Intelligence), 3 difficulty
  levels, with real long-form lesson content seeded from `seed_*.py`.
- 18 hand-authored instructional SVG diagrams in `app/static/diagrams/`
  (normal distribution, regression scatter, PCA directions, star schema,
  ETL pipeline, PLS-SEM path, hypothesis-testing flow, and more).
- Real scanned instructor signature used on certificates.
- MIT OpenCourseWare citations in the MLE / Bayesian / PCA lessons.

**Absent — must never be fabricated:**

- No testimonials, student quotes, or named alumni.
- No enrollment counts, pass rates, satisfaction percentages, or outcome stats.
- No partner logos, press mentions, accreditations, or awards.
- No photography of the instructor, students, or a physical location.

Any social-proof surface must be built from the two facts that are true — the
catalog's own size and the instructor's stated credentials — or shipped as an
explicitly marked placeholder for the user to fill.

## Product Principles

1. **The material is free; only the credential is paid.** Nothing in the design
   may imply a paywall on learning.
2. **One named expert, not a content mill.** Credibility is carried by a specific
   person with checkable credentials, so that person stays visible.
3. **Understanding is proven, not claimed.** Progress only advances through a
   passed quiz; the interface should reflect earned progress, not time spent.
4. **Content is database-driven.** Every course, price, level, and category is
   editable from `/admin` without touching a template.
5. **Never overstate.** No invented outcomes, counts, or endorsements.

## Accessibility & Inclusion

- Learners read long-form technical material for extended sessions; body copy
  must stay comfortably readable at length.
- Significant mobile usage; touch targets and reading measure matter.
- `prefers-reduced-motion` must be honored — an existing commitment in the
  current stylesheet that must survive the redesign.
