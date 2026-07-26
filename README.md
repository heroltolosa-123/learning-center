# The Learning Center

A complete paid online-course platform: FastAPI + SQLite backend, server-rendered Jinja2 frontend,
PayMongo checkout (GCash, Maya, cards), student accounts, course/lesson management, and an admin panel.
No JavaScript framework, no build step — runs as one Python process.

## What's included

- **Public site** — course catalog, course detail pages, free preview lessons
- **Student accounts** — register/login, "My Learning" dashboard, gated lesson access
- **Paid enrollment** — PayMongo Checkout Sessions (GCash/Maya/card), webhook + fallback verification
- **Admin panel** (`/admin`) — create/edit/publish courses, add/reorder lessons, see paid enrollment counts
- **Free courses** — set price to 0 and it becomes a one-click free enrollment, no payment gateway involved

## 1. Install

Requires Python 3.10+.

```bash
cd learning_center
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configure

```bash
cp .env.example .env
```

Open `.env` and fill in:

1. **PayMongo keys** — sign up free at https://dashboard.paymongo.com, then go to
   Developers → API Keys. Start with the `sk_test_...` / `pk_test_...` pair — test mode lets you
   run full checkouts with fake card numbers before you touch real money.
2. **SESSION_SECRET** — generate one with:
   ```bash
   python3 -c "import secrets; print(secrets.token_hex(32))"
   ```
3. **ADMIN_EMAIL / ADMIN_PASSWORD** — whatever you want to log into `/admin` with. This account
   is created automatically the first time the app starts.

Leave `PAYMONGO_WEBHOOK_SECRET` and `BASE_URL` as placeholders for now — you only need those once
you deploy (step 5).

## 3. Run it

```bash
uvicorn app.main:app --reload
```

Open **http://localhost:8000**. Log in at `/login` with your `ADMIN_EMAIL` / `ADMIN_PASSWORD`,
then go to **/admin** to create your first course:

1. `/admin/courses/new` — title, slug, description, price (0 = free)
2. Inside the course page, **Add lesson** for each lesson — title, optional embeddable video URL
   (e.g. `https://www.youtube.com/embed/VIDEO_ID`), and text content
3. Mark at least one lesson as **Free preview** so visitors can sample the course before buying
4. Check **Published**, save — it now appears on the homepage

Test the buyer flow in a second browser (or incognito window): register a student account, open
the course, click enroll. In test mode PayMongo's checkout page accepts fake test card numbers
(listed in their docs) so you can walk through a full payment without spending anything.

## 4. How payment works

- Clicking **Enroll** creates a `pending` enrollment, opens a PayMongo Checkout Session, and
  redirects the buyer to PayMongo's hosted payment page (GCash, Maya, or card).
- On success, PayMongo redirects back to `/checkout/success`, which asks PayMongo directly
  "was this actually paid?" and only then marks the enrollment `paid`. This works even without
  a public URL, so it's enough for local testing.
- The `/webhooks/paymongo` endpoint is also wired up as the reliable, production-grade path —
  PayMongo calls it server-to-server the moment a payment clears, so enrollment stays correct
  even if a buyer closes the tab before the redirect finishes. Webhooks only work once this app
  has a public URL (see deployment below).

## 5. Deploy (Render, same setup you're already using for Matik LMS)

1. Push this folder to a GitHub repo.
2. On Render: New → Web Service → connect the repo.
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Add all the variables from `.env` as Render environment variables. Set `BASE_URL` to your
   Render URL (e.g. `https://your-app.onrender.com`).
4. **Switch to live PayMongo keys** (`sk_live_...` / `pk_live_...`) once you're ready to accept
   real payments — PayMongo requires business verification before live keys work.
5. In the PayMongo dashboard, go to Developers → Webhooks → add endpoint:
   `https://your-app.onrender.com/webhooks/paymongo`, subscribe to `checkout_session.payment.paid`.
   Copy the webhook's signing secret into `PAYMONGO_WEBHOOK_SECRET`.
6. Render's free tier disk is ephemeral — SQLite data will reset on redeploy. For anything beyond
   a prototype, switch `DATABASE_URL` to a Render Postgres instance (SQLAlchemy connects to
   Postgres with no code changes, just `pip install psycopg2-binary` and a `postgresql://...` URL).

## Project layout

```
app/
  main.py              FastAPI app, startup (creates tables + seeds admin)
  database.py          SQLAlchemy engine/session
  models.py            User, Course, Lesson, Enrollment, Payment
  auth.py              bcrypt hashing, session-based login
  paymongo.py           PayMongo Checkout Sessions client + webhook signature check
  routers/
    auth.py            register / login / logout
    courses.py         catalog, course detail, lesson viewer, dashboard
    payments.py        checkout start, success/cancel, webhook receiver
    admin.py           course & lesson CRUD
  templates/           Jinja2 templates (server-rendered, no JS framework)
  static/css/style.css design system
```

## Extending it

- **Certificates on completion** — add a `completed_at` field to `Enrollment`, mark it when a
  student views the last lesson, generate a PDF with the `pdf` toolkit.
- **Progress tracking** — add a `LessonProgress` table (user_id, lesson_id, completed_at).
- **Discount codes** — add a `Coupon` model, apply the discount before calling
  `create_checkout_session`.
- **Drip content** — add a `release_offset_days` field to `Lesson`, check it against
  `enrollment.paid_at` in the unlock logic in `courses.py`.
