"""Site-wide editable content.

Everything here is *copy and contact detail*, not database content. Courses,
lessons, prices and categories always come from the database — never add them
here. Anything in this file can be overridden with an environment variable so
it can be changed on Render without a redeploy of code changes.
"""
import os


def _env(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


# --- Who teaches ------------------------------------------------------------
INSTRUCTOR = {
    "name": _env("INSTRUCTOR_NAME", "Dr. Hero Tolosa"),
    "title": _env("INSTRUCTOR_TITLE", "Statistician & Research Consultant"),
    "credential": _env("INSTRUCTOR_CREDENTIAL", "PD 997 Civil Service Eligible in Statistics"),
    "years": _env("INSTRUCTOR_YEARS", "16"),
    "sectors": ["Banking", "Government", "Academe"],
}

# --- How to reach the school ------------------------------------------------
CONTACT = {
    "email": _env("CONTACT_EMAIL", "heroltolosa@gmail.com"),
    "phone": _env("CONTACT_PHONE", ""),           # blank = hidden
    "location": _env("CONTACT_LOCATION", "Philippines — online, self-paced"),
    "hours": _env("CONTACT_HOURS", "Replies within 1–2 business days"),
}

# Social links render only when set. Add e.g. SOCIAL_FACEBOOK=https://...
SOCIAL = {
    key: _env(f"SOCIAL_{key.upper()}")
    for key in ("facebook", "linkedin", "youtube", "x")
}

# --- Contact-form options ---------------------------------------------------
WORKING_ON_OPTIONS = [
    "Thesis or dissertation",
    "Graduate coursework",
    "A work project",
    "Just exploring",
]

# --- Testimonials -----------------------------------------------------------
# Deliberately empty. The testimonial section renders ONLY when this list has
# entries, so the site never displays an invented quote. To publish real ones,
# add dicts in this shape — nothing else needs changing:
#
#     {"quote": "...", "name": "...", "role": "MA Psychology, 2025"}
#
TESTIMONIALS: list[dict] = []


def as_template_context() -> dict:
    return {
        "instructor": INSTRUCTOR,
        "contact": CONTACT,
        "social": {k: v for k, v in SOCIAL.items() if v},
        "testimonials": TESTIMONIALS,
        "working_on_options": WORKING_ON_OPTIONS,
    }
