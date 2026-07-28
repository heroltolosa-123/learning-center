"""
Adds one multiple-choice quiz question to every substantive lesson (all lessons
except the "Further Reading" ones, which have no quiz gate). Students must
answer correctly to unlock the next lesson.

Safe to re-run -- overwrites the quiz_json for lessons matched by title.

Usage:
    DATABASE_URL="postgresql://...your neon connection string..." python3 seed_quizzes.py
"""
import os
import json
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal
from app import models

QUIZZES = {}
QUIZZES["research-methodology-foundations"] = {
    "What Makes a Research Question Researchable": {
        "question": "Which of these is a researchable question rather than just a broad topic?",
        "choices": [
            "Does technology affect society?",
            "Is remote work good or bad?",
            "Does the number of remote workdays per week correlate with self-reported job satisfaction among BPO employees in Metro Manila?",
            "What do people think about work?",
        ],
        "correct": 2,
    },
    "Choosing a Research Design": {
        "question": "If your research question asks 'why' employees leave their jobs in their own words, which design fits best?",
        "choices": ["Cross-sectional survey", "Experimental design", "Qualitative design", "Longitudinal design"],
        "correct": 2,
    },
    "Sampling: Getting a Group That Actually Represents Your Population": {
        "question": "Which sampling method guarantees proportional representation across known subgroups?",
        "choices": ["Convenience sampling", "Stratified sampling", "Snowball sampling", "Purposive sampling"],
        "correct": 1,
    },
    "Research Ethics and Informed Consent": {
        "question": "What is the key difference between confidentiality and anonymity?",
        "choices": [
            "They mean the same thing",
            "Confidentiality means no one can trace responses; anonymity means only the researcher can",
            "Anonymity means no one can trace a response to a person; confidentiality means the researcher knows but protects that identity",
            "Confidentiality only applies to minors",
        ],
        "correct": 2,
    },
    "Writing a Literature Review That Actually Supports Your Study": {
        "question": "What should a strong literature review end with?",
        "choices": [
            "A list of every source read",
            "An explicit statement of the research gap your study addresses",
            "The longest possible summary of each paper",
            "A description of the researcher's personal opinion",
        ],
        "correct": 1,
    },
    "Building Your Conceptual Framework": {
        "question": "In a conceptual framework, what should justify each arrow connecting two variables?",
        "choices": [
            "The researcher's personal intuition",
            "A specific theory or prior finding cited for that connection",
            "Nothing -- arrows are just for visual appeal",
            "Whatever variables were easiest to measure",
        ],
        "correct": 1,
    },
    "From Proposal to Final Defense: A Realistic Timeline": {
        "question": "Why do most thesis timelines fail?",
        "choices": [
            "Students don't work hard enough",
            "Unbudgeted delays at stages like ethics review and data collection cascade into later stages",
            "Advisers are too slow",
            "There is no reason -- timelines rarely fail",
        ],
        "correct": 1,
    },
}

QUIZZES["applied-statistics-for-research"] = {
    "From Research Question to Statistical Test": {
        "question": "Comparing the same group's scores before and after an intervention calls for which type of test?",
        "choices": ["Independent-samples test", "Paired/related-samples test", "Chi-square test", "Correlation only"],
        "correct": 1,
    },
    "Choosing the Right Test: A Decision Framework": {
        "question": "If your outcome is continuous and normality is badly violated in a small sample comparing two groups, what's the safer choice?",
        "choices": ["Independent t-test regardless", "Mann-Whitney U test", "Chi-square test", "Linear regression"],
        "correct": 1,
    },
    "Reading and Reporting Output the Way a Panel Expects": {
        "question": "Besides the test statistic and p-value, what else should always be reported?",
        "choices": ["Nothing else is needed", "An effect size", "The raw software screenshot", "The researcher's opinion"],
        "correct": 1,
    },
    "Common Mistakes That Get Flagged in Defense": {
        "question": "Running 15 t-tests without any adjustment and reporting 3 as significant risks which problem?",
        "choices": [
            "Nothing -- this is standard practice",
            "An inflated chance of false positives from multiple comparisons",
            "Too much statistical power",
            "Violating informed consent",
        ],
        "correct": 1,
    },
    "Sample Size and Power Analysis for Your Specific Test": {
        "question": "Power analysis should be conducted:",
        "choices": [
            "After data collection, to explain a non-significant result",
            "Before data collection, to justify the target sample size",
            "Only if the study fails",
            "It's not necessary if the topic is important",
        ],
        "correct": 1,
    },
    "Mediation and Moderation: What's Actually Different": {
        "question": "A variable that changes the STRENGTH of a relationship without being on the causal path is called a:",
        "choices": ["Mediator", "Moderator", "Confound", "Control variable"],
        "correct": 1,
    },
    "Preparing for Your Statistics Defense": {
        "question": "When a key hypothesis test comes back non-significant, the best approach in defense is to:",
        "choices": [
            "Hide the result",
            "Explain what it means for the study and any theoretical reason it's plausible",
            "Claim it was a data entry error",
            "Refuse to discuss it",
        ],
        "correct": 1,
    },
}

QUIZZES["basic-statistics"] = {
    "Descriptive Statistics: Making Sense of Raw Numbers": {
        "question": "Two datasets have the same mean but very different standard deviations. What does this tell you?",
        "choices": [
            "The datasets are identical",
            "One dataset's values are much more spread out than the other's",
            "The means must be wrong",
            "Standard deviation doesn't matter",
        ],
        "correct": 1,
    },
    "Probability Basics You Actually Need": {
        "question": "If a diagnostic test is 90% sensitive, does a positive result automatically mean a 90% chance the patient has the disease?",
        "choices": [
            "Yes, always",
            "No -- that also depends on specificity and how common the disease is",
            "Sensitivity is irrelevant to this question",
            "Only if the test is free",
        ],
        "correct": 1,
    },
    "The Normal Distribution and Why It Matters": {
        "question": "Roughly what percentage of data falls within one standard deviation of the mean in a normal distribution?",
        "choices": ["50%", "68%", "95%", "99.7%"],
        "correct": 1,
    },
    "Your First Hypothesis Test": {
        "question": "A low p-value leads you to:",
        "choices": [
            "Prove the alternative hypothesis is true",
            "Reject the null hypothesis in favor of the alternative",
            "Accept the null hypothesis",
            "Stop the study immediately",
        ],
        "correct": 1,
    },
    "Understanding Confidence Intervals": {
        "question": "A 95% confidence interval means:",
        "choices": [
            "There's a 95% chance this specific interval contains the true value",
            "If you repeated the sampling many times, 95% of such intervals would contain the true value",
            "95% of the data falls inside the interval",
            "The sample is 95% accurate",
        ],
        "correct": 1,
    },
    "Correlation: What It Does and Doesn't Tell You": {
        "question": "Ice cream sales and drowning incidents are positively correlated because:",
        "choices": [
            "Ice cream causes drowning",
            "Drowning causes people to buy ice cream",
            "Both are driven by a third variable -- hot weather",
            "The correlation is a coincidence with no explanation",
        ],
        "correct": 2,
    },
    "Chi-Square Tests for Categorical Data": {
        "question": "Chi-square becomes unreliable when:",
        "choices": [
            "The sample size is too large",
            "Expected cell counts are too small (typically below 5)",
            "Both variables are continuous",
            "It never becomes unreliable",
        ],
        "correct": 1,
    },
}

QUIZZES["intermediate-statistics"] = {
    "Simple and Multiple Linear Regression": {
        "question": "In multiple regression, a coefficient represents the effect of a predictor:",
        "choices": [
            "Ignoring all other variables in the model",
            "While holding the other predictors in the model constant",
            "Only for the first observation",
            "Averaged across all possible models",
        ],
        "correct": 1,
    },
    "ANOVA: Comparing More Than Two Groups": {
        "question": "A significant one-way ANOVA result tells you:",
        "choices": [
            "Every group differs from every other group",
            "At least one group differs from the others, but not which ones",
            "The groups are all identical",
            "You need a t-test instead",
        ],
        "correct": 1,
    },
    "Checking Your Assumptions": {
        "question": "When checking normality for a regression model, you should examine the normality of:",
        "choices": ["The raw outcome variable", "The residuals", "The predictor variables only", "The sample size"],
        "correct": 1,
    },
    "Introduction to Multivariate Thinking": {
        "question": "Why use MANOVA instead of several separate ANOVAs on related outcomes?",
        "choices": [
            "MANOVA is always more accurate",
            "Running many separate tests inflates the false-positive risk; MANOVA controls this",
            "MANOVA requires a smaller sample",
            "There's no real reason -- they're identical",
        ],
        "correct": 1,
    },
    "Logistic Regression for Binary Outcomes": {
        "question": "An odds ratio of 2.0 for a predictor in logistic regression means:",
        "choices": [
            "The outcome doubles in value",
            "The odds of the outcome roughly double for each one-unit increase in that predictor",
            "The model is twice as accurate",
            "The predictor is not significant",
        ],
        "correct": 1,
    },
    "Factor Analysis: Finding Structure in Your Variables": {
        "question": "Before running exploratory factor analysis, you should check:",
        "choices": [
            "Nothing -- you can run it on any data",
            "The KMO measure and Bartlett's test of sphericity",
            "Only the sample size",
            "The regression R-squared",
        ],
        "correct": 1,
    },
    "Effect Sizes: Why p-Values Alone Aren't Enough": {
        "question": "A study with 10,000 participants finds a statistically significant but tiny effect size. This means:",
        "choices": [
            "The finding is definitely important",
            "The large sample made a practically trivial effect statistically detectable",
            "The p-value must be wrong",
            "Effect size doesn't matter here",
        ],
        "correct": 1,
    },
}

QUIZZES["advanced-statistics"] = {
    "Structural Equation Modeling: The Big Picture": {
        "question": "What can SEM test that standard regression cannot?",
        "choices": [
            "Nothing -- they test the same things",
            "A whole network of hypothesized relationships simultaneously, including mediation",
            "Only simple two-variable relationships",
            "Only categorical outcomes",
        ],
        "correct": 1,
    },
    "PLS-SEM Step by Step": {
        "question": "In PLS-SEM, what must happen before you can trust the structural model results?",
        "choices": [
            "Nothing -- you can interpret paths immediately",
            "The measurement model must first pass reliability and validity checks",
            "You need at least 10,000 respondents",
            "The study must be published first",
        ],
        "correct": 1,
    },
    "Survival Analysis Fundamentals": {
        "question": "What does 'censoring' mean in survival analysis?",
        "choices": [
            "The data was deliberately hidden",
            "A subject hasn't experienced the event of interest by the study's end",
            "The researcher made an error",
            "The sample size was too small",
        ],
        "correct": 1,
    },
    "Firth Logistic Regression for Rare Events": {
        "question": "Firth's penalized regression is especially useful when:",
        "choices": [
            "The sample size is enormous",
            "The outcome event is rare or the sample is small, risking unstable standard logistic regression estimates",
            "You need a simpler model than logistic regression",
            "The outcome is continuous",
        ],
        "correct": 1,
    },
    "Moderated Mediation and Complex PLS-SEM Models": {
        "question": "Moderated mediation tests whether:",
        "choices": [
            "Two variables are correlated",
            "An indirect (mediated) effect itself changes depending on the level of a moderating variable",
            "A sample is representative",
            "A test is statistically significant",
        ],
        "correct": 1,
    },
    "Handling Missing Data the Right Way": {
        "question": "If higher earners are less likely to report their income, simply deleting those rows would:",
        "choices": [
            "Have no effect on the results",
            "Systematically bias the average income estimate downward",
            "Improve accuracy",
            "Only affect the sample size, not the estimate",
        ],
        "correct": 1,
    },
    "Publishing and Peer Review for Quantitative Studies": {
        "question": "Reporting guidelines like CONSORT or STROBE exist to:",
        "choices": [
            "Make papers longer",
            "Give reviewers a checklist to verify completeness and improve reproducibility",
            "Replace the need for statistics",
            "Only apply to qualitative studies",
        ],
        "correct": 1,
    },
}

QUIZZES["ai-ml-for-practitioners"] = {
    "What Machine Learning Actually Is (and Isn't)": {
        "question": "What best distinguishes supervised from unsupervised learning?",
        "choices": [
            "Supervised learning requires no data",
            "Supervised learning uses labeled data with known outcomes; unsupervised learning finds structure with no labels",
            "They are the same technique",
            "Unsupervised learning is always more accurate",
        ],
        "correct": 1,
    },
    "Classification vs Regression Problems": {
        "question": "Predicting 'will this customer churn' (yes/no) is an example of:",
        "choices": ["A regression problem", "A classification problem", "An unsupervised problem", "None of these"],
        "correct": 1,
    },
    "Training, Validation, and Test Sets": {
        "question": "Why should the test set only be touched once, at the very end?",
        "choices": [
            "To save computing time",
            "Using it repeatedly during development would make it stop being an honest, unbiased performance estimate",
            "It's a legal requirement",
            "There's no real reason",
        ],
        "correct": 1,
    },
    "Overfitting and How to Avoid It": {
        "question": "A model with 100% training accuracy but 68% test accuracy is likely:",
        "choices": [
            "Perfectly well-fitted",
            "Overfitting -- it memorized the training data rather than learning generalizable patterns",
            "Underfitting",
            "Impossible to diagnose",
        ],
        "correct": 1,
    },
    "Feature Engineering: Where Most of the Real Work Happens": {
        "question": "Turning a raw 'date' field into 'day of week' and 'is holiday' flags is an example of:",
        "choices": ["Overfitting", "Feature engineering", "Data leakage", "Model deployment"],
        "correct": 1,
    },
    "Tree-Based Models: Decision Trees, Random Forests, and Gradient Boosting": {
        "question": "Why do random forests generally outperform a single decision tree?",
        "choices": [
            "They use less data",
            "Averaging many trees trained on different subsets reduces overfitting and improves generalization",
            "They are always faster to train",
            "There is no real advantage",
        ],
        "correct": 1,
    },
    "Deploying a Model Responsibly": {
        "question": "What is 'concept drift'?",
        "choices": [
            "A bug in the code",
            "Real-world data patterns shifting over time in ways the training data didn't capture",
            "A type of data leakage",
            "A synonym for overfitting",
        ],
        "correct": 1,
    },
}

QUIZZES["data-management-essentials"] = {
    "What Good Data Structure Looks Like": {
        "question": "The 'tidy data' principle states that each row should represent:",
        "choices": [
            "Any random selection of data",
            "One observation, with one column per variable",
            "A whole dataset",
            "A single data type",
        ],
        "correct": 1,
    },
    "Data Cleaning Fundamentals": {
        "question": "When you encounter an unusually high sales figure (an outlier), you should:",
        "choices": [
            "Always delete it immediately",
            "Investigate it -- it could be an error or the most important finding in the data",
            "Ignore it completely",
            "Always keep it without question",
        ],
        "correct": 1,
    },
    "Data Validation Rules": {
        "question": "A rule that rejects an age value of 250 is an example of:",
        "choices": ["A referential check", "A range check", "A consistency check", "A format check"],
        "correct": 1,
    },
    "Documentation and Metadata": {
        "question": "A data dictionary should record, for every variable:",
        "choices": [
            "Only the variable's name",
            "Its name, meaning, data type, valid range, and how it was derived",
            "Nothing -- data dictionaries are unnecessary",
            "Only who collected the data",
        ],
        "correct": 1,
    },
    "Master Data vs Transactional Data": {
        "question": "Which of these is an example of master data rather than transactional data?",
        "choices": ["A single sale record", "A customer's profile information", "A login event", "A specific claim filed"],
        "correct": 1,
    },
    "Data Governance Basics": {
        "question": "A core element of data governance is:",
        "choices": [
            "Making data inaccessible to everyone",
            "Assigning clear ownership and access control for important datasets",
            "Avoiding any documentation",
            "Deleting all data regularly",
        ],
        "correct": 1,
    },
    "Choosing Between Spreadsheets, Databases, and Data Warehouses": {
        "question": "A team hitting version conflicts and slow load times in a shared spreadsheet with 15 concurrent users should consider:",
        "choices": [
            "Adding more spreadsheet tabs",
            "Moving to a proper relational database with real concurrency support",
            "Reducing the team to 1 person",
            "Nothing -- spreadsheets scale infinitely",
        ],
        "correct": 1,
    },
}

QUIZZES["data-warehousing-fundamentals"] = {
    "What a Data Warehouse Is (and Why Spreadsheets Aren't Enough)": {
        "question": "Why are data warehouses kept separate from operational systems?",
        "choices": [
            "Operational systems are optimized for fast individual transactions, not heavy analytical queries",
            "Warehouses are cheaper to build",
            "There's no real reason",
            "Operational systems can't store any data",
        ],
        "correct": 0,
    },
    "Dimensional Modeling: Facts and Dimensions": {
        "question": "In dimensional modeling, numeric measures like sales amount belong in:",
        "choices": ["Dimension tables", "Fact tables", "Neither", "Both equally"],
        "correct": 1,
    },
    "ETL Basics: Extract, Transform, Load": {
        "question": "The 'Transform' step in ETL is primarily responsible for:",
        "choices": [
            "Pulling raw data from source systems",
            "Cleaning, standardizing, and restructuring data into the warehouse's model",
            "Writing final data into warehouse tables",
            "Deleting old data",
        ],
        "correct": 1,
    },
    "Star Schema vs Snowflake Schema": {
        "question": "For most reporting and BI use cases, which schema is the practical default?",
        "choices": ["Snowflake schema, always", "Star schema", "Neither is ever used", "It never matters"],
        "correct": 1,
    },
    "Slowly Changing Dimensions": {
        "question": "If historical reports need to reflect 'as it was then' when an attribute like address changes, which approach fits?",
        "choices": ["Type 1 (overwrite)", "Type 2 (add new row with effective dates)", "Deleting the old value", "Ignoring the change"],
        "correct": 1,
    },
    "Data Warehouse Performance and Indexing": {
        "question": "Partitioning a large fact table by date primarily helps by:",
        "choices": [
            "Making the table smaller in total size",
            "Letting queries skip irrelevant partitions instead of scanning the whole table",
            "Removing the need for indexes",
            "Automatically cleaning the data",
        ],
        "correct": 1,
    },
    "Modern Cloud Data Warehouses": {
        "question": "What is the key infrastructure change cloud data warehouses introduced?",
        "choices": [
            "Abandoning dimensional modeling entirely",
            "Separating storage and compute so each scales and is priced independently",
            "Removing the need for any modeling",
            "Making data warehouses free",
        ],
        "correct": 1,
    },
}

QUIZZES["business-intelligence-dashboards"] = {
    "BI Tool Landscape: Choosing What Fits": {
        "question": "The right BI tool choice depends mainly on:",
        "choices": [
            "Whichever tool is most popular online",
            "Your actual audience, data change frequency, budget, and existing data sources",
            "The tool with the most colors available",
            "Whatever a competitor uses",
        ],
        "correct": 1,
    },
    "Dashboard Design Principles That Actually Get Used": {
        "question": "The most common reason dashboards fail is:",
        "choices": [
            "Too few metrics displayed",
            "Nobody keeps looking at it because it doesn't answer a specific recurring question clearly",
            "Too much white space",
            "The data refreshes too often",
        ],
        "correct": 1,
    },
    "Choosing the Right Chart for the Right Question": {
        "question": "For comparing market share across nine competitors, which chart type communicates the ranking most clearly?",
        "choices": ["A pie chart", "A sorted horizontal bar chart", "A 3D pie chart", "A line chart"],
        "correct": 1,
    },
    "Automating Recurring Reports": {
        "question": "Besides saving time, what's the biggest benefit of automating a recurring report?",
        "choices": [
            "It looks more impressive",
            "Consistency -- it eliminates small manual errors that creep in over time",
            "It requires no monitoring at all",
            "There is no other benefit",
        ],
        "correct": 1,
    },
    "KPIs: Choosing Metrics That Actually Drive Decisions": {
        "question": "A 'vanity metric' is one that:",
        "choices": [
            "Is always the most important number on a dashboard",
            "Looks impressive but doesn't connect to any actual decision",
            "Only appears in financial reports",
            "Is required by law",
        ],
        "correct": 1,
    },
    "Connecting Live Data Sources": {
        "question": "An executive summary reviewed weekly generally needs:",
        "choices": [
            "A live, real-time connection refreshing every second",
            "A scheduled refresh (e.g. nightly) -- true real-time isn't necessary",
            "No data connection at all",
            "Manual entry only",
        ],
        "correct": 1,
    },
    "Making Dashboards People Actually Trust": {
        "question": "Two dashboards show different 'total customers' numbers with no explanation. This most likely causes:",
        "choices": [
            "No effect on trust",
            "Viewers losing confidence in both dashboards, even if the difference was explainable",
            "Increased usage of both dashboards",
            "A completely unrelated problem",
        ],
        "correct": 1,
    },
}


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    total_updated, courses_touched = 0, 0
    try:
        for slug, lessons in QUIZZES.items():
            course = db.query(models.Course).filter(models.Course.slug == slug).first()
            if not course:
                print(f"[missing] '{slug}' -- run earlier seed scripts first.")
                continue

            updated_here = 0
            for lesson in course.lessons:
                if lesson.title in lessons:
                    q = lessons[lesson.title]
                    lesson.quiz_json = json.dumps([q])
                    updated_here += 1
                    total_updated += 1

            if updated_here:
                courses_touched += 1
                print(f"[{course.title}] added quiz to {updated_here} lesson(s)")

        db.commit()
    finally:
        db.close()

    print(f"\nDone. {total_updated} quiz question(s) added across {courses_touched} course(s).")


if __name__ == "__main__":
    run()
