"""
One-time seed script: creates the 9 course shells requested for Hero Academy.
Safe to re-run — skips any course whose slug already exists.

Usage:
    # Local (uses sqlite:///./learning_center.db from your .env):
    python3 seed_courses.py

    # Against your live Render/Neon database, run this from your Mac with the
    # same DATABASE_URL Render uses (copy it from Render's Environment tab):
    DATABASE_URL="postgresql://...neon connection string..." python3 seed_courses.py

Every price below is a placeholder — edit prices, descriptions, and add real
lessons any time afterward from /admin. This script only creates the shells
and one placeholder "Course overview" lesson (marked as a free preview) so
each course isn't empty on day one.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal
from app import models

COURSES = [
    {
        "title": "Foundations of Research Methodology",
        "slug": "research-methodology-foundations",
        "category": "Research",
        "level": "Beginner",
        "price_php": 2500,
        "description": (
            "How to design a study that survives a panel defense: research questions, "
            "study design choices, sampling, instrument development, and ethics review — "
            "the groundwork every thesis and dissertation needs before any statistics happen."
        ),
    },
    {
        "title": "Applied Statistics for Research",
        "slug": "applied-statistics-for-research",
        "category": "Statistics",
        "level": "Intermediate",
        "price_php": 3500,
        "description": (
            "Bridging statistics and real research questions: choosing the right test, "
            "interpreting output the way a panel expects, and writing results sections "
            "that hold up to scrutiny. Built from years of thesis and dissertation consulting."
        ),
    },
    {
        "title": "Basic Statistics: A Practical Start",
        "slug": "basic-statistics",
        "category": "Statistics",
        "level": "Beginner",
        "price_php": 1500,
        "description": (
            "Descriptive statistics, probability basics, and your first hypothesis tests — "
            "taught the way you'd actually use them, not just the formulas."
        ),
    },
    {
        "title": "Intermediate Statistics: Building Real Models",
        "slug": "intermediate-statistics",
        "category": "Statistics",
        "level": "Intermediate",
        "price_php": 2800,
        "description": (
            "Regression, ANOVA, and multivariate basics. For learners who've cleared "
            "basic statistics and are ready to build models that answer real questions."
        ),
    },
    {
        "title": "Advanced Statistics: PLS-SEM, Survival Analysis & Beyond",
        "slug": "advanced-statistics",
        "category": "Statistics",
        "level": "Advanced",
        "price_php": 4500,
        "description": (
            "Structural equation modeling (PLS-SEM), survival analysis, Firth logistic "
            "regression, and other methods that show up in dissertation-level work — "
            "taught with the same rigor used in real panel-facing consulting."
        ),
    },
    {
        "title": "AI & Machine Learning for Practitioners",
        "slug": "ai-ml-for-practitioners",
        "category": "AI & Data Science",
        "level": "Intermediate",
        "price_php": 5000,
        "description": (
            "Practical machine learning: classification, model evaluation, avoiding "
            "overfitting, and applying ML to real business or research problems — "
            "grounded in production pipeline experience, not just theory."
        ),
    },
    {
        "title": "Data Management Essentials",
        "slug": "data-management-essentials",
        "category": "Data Engineering",
        "level": "Beginner",
        "price_php": 2000,
        "description": (
            "Structuring, cleaning, and governing data so it's actually usable — "
            "data quality, validation, documentation, and workflow habits that "
            "prevent the messes that ruin analysis later."
        ),
    },
    {
        "title": "Data Warehousing Fundamentals",
        "slug": "data-warehousing-fundamentals",
        "category": "Data Engineering",
        "level": "Intermediate",
        "price_php": 3000,
        "description": (
            "Designing data warehouses that scale: dimensional modeling, ETL basics, "
            "and structuring data for reporting and analytics rather than just storage."
        ),
    },
    {
        "title": "Business Intelligence: Dashboards & Automation",
        "slug": "business-intelligence-dashboards",
        "category": "Business Intelligence",
        "level": "Intermediate",
        "price_php": 3500,
        "description": (
            "Turning raw data into dashboards people actually check: BI tool "
            "fundamentals, dashboard design principles, and automating recurring "
            "reports so they stop eating your week."
        ),
    },
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    created, skipped = 0, 0
    try:
        for c in COURSES:
            existing = db.query(models.Course).filter(models.Course.slug == c["slug"]).first()
            if existing:
                print(f"[skip] '{c['title']}' already exists (slug: {c['slug']})")
                skipped += 1
                continue

            course = models.Course(
                title=c["title"],
                slug=c["slug"],
                description=c["description"],
                category=c["category"],
                level=c["level"],
                price_php=c["price_php"],
                instructor_name="Dr. Hero L. Tolosa",
                is_published=True,
            )
            db.add(course)
            db.flush()  # get course.id before adding the lesson

            lesson = models.Lesson(
                course_id=course.id,
                title="Course overview",
                content=(
                    f"Welcome to {c['title']}. This overview lesson is a placeholder — "
                    f"replace it with your real intro video and add the rest of your "
                    f"lessons from /admin/courses/{course.id}."
                ),
                order=1,
                is_preview=True,
            )
            db.add(lesson)
            print(f"[created] '{c['title']}' — ₱{c['price_php']} ({c['category']}, {c['level'] or 'no level'})")
            created += 1

        db.commit()
    finally:
        db.close()

    print(f"\nDone. {created} course(s) created, {skipped} skipped (already existed).")


if __name__ == "__main__":
    run()
