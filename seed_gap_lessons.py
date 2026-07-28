"""
Adds three new original lessons filling genuine gaps identified against MIT
OpenCourseWare 18.650's topic coverage (Maximum Likelihood Estimation,
Bayesian Statistics, PCA) -- written from scratch, not copied from MIT's
materials. Also adds a proper citation link to the real MIT OCW 18.650
course page in the relevant "Further Reading" lessons.

Usage:
    DATABASE_URL="postgresql://...your neon connection string..." python3 seed_gap_lessons.py
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal
from app import models

NEW_LESSONS = {
    "intermediate-statistics": {
        "title": "How Statistical Models Are Actually Fit: Maximum Likelihood Estimation",
        "content": """## Overview

Every time you run a regression or logistic regression, software is quietly solving an optimization problem behind the scenes to find the "best" parameter values. Maximum likelihood estimation (MLE) is the principle behind how that happens for most of the models covered in this course.

## Key Concepts

- **The core idea**: MLE asks, "out of all the possible parameter values, which one makes the data I actually observed most probable?" That value is the maximum likelihood estimate.
- **The likelihood function**: a mathematical function that, for a given set of data, tells you how probable that data would be under different candidate parameter values.
- **Why it matters practically**: linear regression's least-squares coefficients, logistic regression's coefficients, and many other estimation methods are all specific cases of maximum likelihood estimation under the hood.
- **Estimates have uncertainty too**: MLE doesn't just give you a single best-guess number -- the same theory also produces standard errors, which is where the confidence intervals and p-values you already report actually come from.

![Diagram: The likelihood curve and its maximum](/static/diagrams/mle-curve.svg)

## Worked Example

Suppose you're estimating the probability that a manufacturing process produces a defective item, based on a sample of 100 items where 8 were defective. Intuitively, 8/100 = 8% seems like the "obvious" estimate -- and maximum likelihood estimation confirms this formally: out of every possible defect-rate value between 0% and 100%, an 8% rate makes observing "8 defects out of 100" more probable than any other rate would. This matches intuition here, but for more complex models (like logistic regression with several predictors), MLE finds the best-fitting values in situations where intuition alone can't.

## Common Mistakes & Pro Tips

- MLE assumes your model's underlying assumptions are reasonably correct -- a badly misspecified model can still produce an MLE estimate, but that estimate won't mean much.
- Software packages compute MLE for you automatically in regression and logistic regression -- you rarely calculate it by hand, but understanding the principle helps you interpret warnings like "failed to converge," which usually means the optimization process searching for the maximum likelihood value ran into trouble.
- Method of moments is an older, simpler alternative estimation approach that matches sample statistics (like the mean) to theoretical ones -- it's more intuitive but generally less statistically efficient than MLE, which is why MLE became the standard for most modern modeling.""",
        "quiz": {
            "question": "What does the maximum likelihood estimate represent?",
            "choices": [
                "The parameter value that makes the observed data most probable",
                "The average of all possible parameter values",
                "A value chosen at random from the data",
                "The smallest possible parameter value",
            ],
            "correct": 0,
        },
    },
    "advanced-statistics": {
        "title": "An Introduction to Bayesian Statistics",
        "content": """## Overview

Everything covered elsewhere in this course follows the "frequentist" school of statistics -- the traditional approach taught in most programs. Bayesian statistics is a genuinely different way of reasoning about uncertainty, and it's increasingly common in modern applied work, from A/B testing to machine learning.

## Key Concepts

- **The frequentist question**: "if I repeated this study many times, how often would I see data this extreme, assuming the null hypothesis is true?"
- **The Bayesian question**: "given what I believed before, and given the new data I've now collected, what should I believe now?"
- **Prior**: your belief about a parameter *before* seeing the current data -- this can come from previous studies, expert judgment, or a deliberately neutral starting point.
- **Likelihood**: how probable your observed data is, under different possible parameter values (the same concept from maximum likelihood estimation).
- **Posterior**: your *updated* belief after combining the prior with the new data -- this is the actual output of a Bayesian analysis, and it's a full probability distribution, not just a single number.

![Diagram: Prior belief updated by data into a posterior belief](/static/diagrams/bayesian-updating.svg)

## Worked Example

A researcher believes, based on prior studies, that a new teaching method probably improves test scores by somewhere around 3-5 points, but isn't fully certain. This is the prior. They then run a new study and collect fresh data. A Bayesian analysis combines that prior belief with the new data's likelihood to produce a posterior: an updated, narrower range of plausible improvement values that reflects both the prior knowledge and the new evidence together -- rather than treating the new study as the only source of information, the way a purely frequentist analysis would.

## Common Mistakes & Pro Tips

- A "wrong" or overly strong prior can bias your posterior -- Bayesian analysis is only as trustworthy as the prior belief you bring into it, so priors should be justified and reported explicitly, not chosen to get a desired result.
- Bayesian and frequentist methods often produce similar practical conclusions when you have a lot of data and a reasonably neutral prior -- the difference matters most with smaller samples or strong prior information.
- Bayesian methods are increasingly common in modern A/B testing and machine learning specifically because they naturally express "how confident are we" as a full distribution, which is often more useful for decision-making than a single p-value.""",
        "quiz": {
            "question": "In Bayesian statistics, the posterior represents:",
            "choices": [
                "Your belief before seeing any data",
                "Your updated belief after combining your prior belief with new data",
                "The exact true value of the parameter",
                "A synonym for the p-value",
            ],
            "correct": 1,
        },
    },
    "ai-ml-for-practitioners": {
        "title": "Principal Component Analysis: Reducing Dimensions Without Losing the Story",
        "content": """## Overview

Real datasets often have dozens or hundreds of features, many of which overlap in the information they carry. Principal Component Analysis (PCA) is a standard technique for compressing that complexity down to a much smaller number of dimensions while preserving as much of the meaningful variation as possible.

## Key Concepts

- **The core problem PCA solves**: when features are correlated with each other, much of your data's "spread" can actually be captured by just a few well-chosen combined directions, rather than needing every original feature separately.
- **Principal components**: new, artificial variables that PCA constructs, each one a specific combination of your original features, ranked by how much of the data's total variation they capture.
- **The first principal component (PC1)** captures the single direction of greatest variation in the data. Each subsequent component captures the next-most variation, while staying mathematically independent (uncorrelated) with the ones before it.
- **Dimensionality reduction**: keeping only the first several principal components -- often just 2 or 3 -- lets you represent most of a dataset's meaningful structure in far fewer dimensions than you started with.

![Diagram: Finding the directions of greatest variance in the data](/static/diagrams/pca-directions.svg)

## Worked Example

A retailer has customer data with 20 correlated features: total spend, visit frequency, average basket size, loyalty points earned, and so on -- many of which move together because they're all really reflecting "how engaged is this customer." Running PCA on this data might reveal that the first two principal components alone capture 85% of the meaningful variation across customers. The retailer can now plot every customer in just two dimensions instead of twenty, making patterns and customer segments visually obvious in a way that twenty separate features never could.

## Common Mistakes & Pro Tips

- Always scale your features (standardize to comparable ranges) before running PCA -- features on larger numeric scales will otherwise dominate the principal components purely due to their scale, not their actual importance.
- Principal components are combinations of original features and often don't have a clean, intuitive real-world meaning on their own -- this interpretability trade-off is the main cost of dimensionality reduction.
- PCA captures variance, not necessarily predictive power for a specific outcome -- a component that explains a lot of variance isn't guaranteed to be the most useful one for a particular prediction task, so it's worth checking both before finalizing a reduced feature set.""",
        "quiz": {
            "question": "What does the first principal component (PC1) represent?",
            "choices": [
                "A randomly chosen original feature",
                "The direction capturing the greatest amount of variation in the data",
                "The average of all features",
                "The least important feature in the dataset",
            ],
            "correct": 1,
        },
    },
}

FURTHER_READING_ADDITIONS = {
    "intermediate-statistics": "\n\n**On maximum likelihood estimation specifically**: MIT OpenCourseWare's 18.650 Statistics for Applications (Prof. Philippe Rigollet) covers parametric estimation in real depth and is free to read at ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/.",
    "advanced-statistics": "\n\n**On Bayesian statistics specifically**: MIT OpenCourseWare's 18.650 Statistics for Applications (Prof. Philippe Rigollet) has a dedicated unit on Bayesian methods and is free to read at ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/.",
    "ai-ml-for-practitioners": "\n\n**On PCA and dimensionality reduction specifically**: MIT OpenCourseWare's 18.650 Statistics for Applications (Prof. Philippe Rigollet) covers PCA free at ocw.mit.edu/courses/18-650-statistics-for-applications-fall-2016/.",
}


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    added = 0
    try:
        for slug, data in NEW_LESSONS.items():
            course = db.query(models.Course).filter(models.Course.slug == slug).first()
            if not course:
                print(f"[missing] '{slug}' -- run earlier seed scripts first.")
                continue

            existing_titles = {l.title for l in course.lessons}
            if data["title"] in existing_titles:
                print(f"[skip] '{data['title']}' already exists in {course.title}")
                continue

            # Insert as the second-to-last lesson (before "Further Reading")
            reading_lesson = next((l for l in course.lessons if l.title == "Further Reading (Free & Open)"), None)
            insert_order = reading_lesson.order if reading_lesson else (max([l.order for l in course.lessons], default=0) + 1)

            if reading_lesson:
                reading_lesson.order += 1

            lesson = models.Lesson(
                course_id=course.id,
                title=data["title"],
                content=data["content"],
                order=insert_order,
                is_preview=False,
                quiz_json=json.dumps([data["quiz"]]),
            )
            db.add(lesson)
            added += 1
            print(f"[added] '{data['title']}' to {course.title}")

            if reading_lesson and slug in FURTHER_READING_ADDITIONS:
                reading_lesson.content = reading_lesson.content + FURTHER_READING_ADDITIONS[slug]
                print(f"  [updated] Further Reading citation in {course.title}")

        db.commit()
    finally:
        db.close()

    print(f"\nDone. {added} new lesson(s) added.")


if __name__ == "__main__":
    run()
