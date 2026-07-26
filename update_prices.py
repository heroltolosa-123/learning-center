"""
Updates all 9 course prices to competitive, below-market rates.

For reference: Udemy courses in the Philippines typically run PHP 500-1,200,
subscription platforms (MMDC) run ~PHP 990/month, and Coursera certificates
run $29-99/month. This script prices Hero Academy's one-time, lifetime-access
courses below all of those, while still being a real paid product.

Safe to re-run -- always sets the price to the value below, so re-running
with updated numbers is how you change prices going forward too.

Usage:
    DATABASE_URL="postgresql://...your neon connection string..." python3 update_prices.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal
from app import models

NEW_PRICES = {
    "research-methodology-foundations": 299,
    "applied-statistics-for-research": 499,
    "basic-statistics": 299,
    "intermediate-statistics": 499,
    "advanced-statistics": 699,
    "ai-ml-for-practitioners": 599,
    "data-management-essentials": 299,
    "data-warehousing-fundamentals": 449,
    "business-intelligence-dashboards": 449,
}


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    updated = 0
    try:
        for slug, new_price in NEW_PRICES.items():
            course = db.query(models.Course).filter(models.Course.slug == slug).first()
            if not course:
                print(f"[missing] '{slug}' -- run seed_courses.py first.")
                continue
            old_price = course.price_php
            course.price_php = new_price
            print(f"[{course.title}] PHP {old_price} -> PHP {new_price}")
            updated += 1
        db.commit()
    finally:
        db.close()

    print(f"\nDone. {updated} course(s) repriced.")


if __name__ == "__main__":
    run()
