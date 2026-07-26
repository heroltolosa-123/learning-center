"""
Adds 3 more lessons to each course (bringing every course to 7 total), and
one "Further reading" lesson linking to legitimate free open resources
(OpenStax, LibreTexts, MIT OpenCourseWare, DOAB) relevant to that course.

Safe to re-run -- skips any lesson whose title already exists under that course.

Usage:
    DATABASE_URL="postgresql://...your neon connection string..." python3 seed_extended_curriculum.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal
from app import models

EXTRA_LESSONS = {
    "research-methodology-foundations": [
        ("Writing a Literature Review That Actually Supports Your Study",
         "A literature review isn't a book report -- it's an argument for why your study needs to exist. Organize "
         "it thematically (by concept or variable) rather than chronologically or paper-by-paper, so readers see "
         "how the field's understanding has developed rather than a list of summaries. Every source you include "
         "should do one of three jobs: establish what's already known, reveal a gap your study will address, or "
         "provide theoretical grounding for your framework. End the review by explicitly naming the gap and "
         "positioning your study as the response to it -- this is the paragraph a panel reads most carefully."),
        ("Building Your Conceptual Framework",
         "Your conceptual framework is the visual and logical map of how you believe your variables relate to "
         "each other, grounded in theory and prior research rather than intuition. Independent variables, "
         "dependent variables, and any mediating or moderating variables should all be clearly identified and "
         "connected with directional arrows showing hypothesized relationships. A weak framework borrows "
         "variables from unrelated studies without justifying why they belong together; a strong one draws each "
         "connection from a specific theory or a specific prior finding, cited directly beside the arrow it "
         "supports."),
        ("From Proposal to Final Defense: A Realistic Timeline",
         "Most research timelines fail not because of bad planning but because of unbudgeted delays: ethics "
         "review approval, data collection taking longer than expected, and revision cycles with your adviser. "
         "Build in buffer time at every stage rather than a single buffer at the end -- a delay in data collection "
         "cascades into every stage after it. A realistic skeleton: proposal defense, ethics approval, instrument "
         "pilot testing, full data collection, analysis, results write-up, full draft to adviser, revisions, "
         "final defense. Treat each stage as having its own deadline, not just the final defense date."),
    ],
    "applied-statistics-for-research": [
        ("Sample Size and Power Analysis for Your Specific Test",
         "A study with too few participants can't detect an effect even when a real one exists -- this is a "
         "power problem, and it's fixable before data collection, not after. Power analysis requires four "
         "inputs: your significance level (typically .05), your desired power (typically .80), your expected "
         "effect size, and your test type. G*Power is the standard free tool for this. Running a power analysis "
         "before you collect a single data point, and reporting it in your methodology chapter, preempts one of "
         "the most common panel questions: 'how did you arrive at this sample size?'"),
        ("Mediation and Moderation: What's Actually Different",
         "These two terms get confused constantly, but they answer different questions. Mediation asks: does "
         "variable M explain *how* or *why* X affects Y -- it sits on the causal pathway between them. Moderation "
         "asks: does variable Z change the *strength or direction* of the X-to-Y relationship, without being on "
         "the causal path itself. A mediation analysis (Baron & Kenny's steps, or more modern bootstrapping "
         "approaches) tests whether the direct effect of X on Y shrinks once M is included. A moderation analysis "
         "tests an interaction term (X multiplied by Z) directly in a regression model."),
        ("Preparing for Your Statistics Defense",
         "Panels don't just check whether your numbers are right -- they check whether you understand what they "
         "mean. Be ready to explain, in plain language and without your slides, why you chose each test, what "
         "assumption checks you ran and what you found, what your effect sizes actually indicate practically, "
         "and what a null result would have meant for your study. Practice defending your weakest finding, not "
         "just your strongest one -- that's almost always where the hardest questions land."),
    ],
    "basic-statistics": [
        ("Understanding Confidence Intervals",
         "A confidence interval gives you a range of plausible values for a population parameter, not just a "
         "single estimate -- and it's often more informative than a p-value alone. A 95% confidence interval "
         "means that if you repeated your sampling process many times, 95% of the intervals you'd calculate "
         "would contain the true population value. A wide interval signals more uncertainty (often from a "
         "smaller sample); a narrow one signals a more precise estimate. Always report confidence intervals "
         "alongside point estimates -- a mean of 50 with a confidence interval of 48 to 52 tells a very different "
         "story than one of 20 to 80."),
        ("Correlation: What It Does and Doesn't Tell You",
         "Correlation measures the strength and direction of a linear relationship between two continuous "
         "variables, ranging from -1 to +1. A correlation near 0 means little to no linear relationship -- but "
         "it doesn't rule out a strong non-linear one, which is why you should always look at a scatter plot, "
         "not just the correlation coefficient. And the phrase every statistics student needs tattooed somewhere: "
         "correlation is not causation. Two variables can move together because one causes the other, because "
         "both are caused by a third variable, or by pure coincidence -- the statistic alone can't distinguish "
         "between these."),
        ("Chi-Square Tests for Categorical Data",
         "When both your variables are categorical rather than continuous, chi-square tests are your standard "
         "tool. A chi-square test of independence asks whether two categorical variables are related (does "
         "smoking status relate to disease diagnosis). A chi-square goodness-of-fit test asks whether your "
         "observed frequencies match an expected distribution. Both compare observed counts to what you'd expect "
         "under the null hypothesis of no relationship. One requirement to watch: chi-square becomes unreliable "
         "when expected cell counts are too small (typically below 5), in which case Fisher's exact test is the "
         "better alternative."),
    ],
    "intermediate-statistics": [
        ("Logistic Regression for Binary Outcomes",
         "When your outcome variable has only two categories (yes/no, pass/fail, survived/didn't), linear "
         "regression is the wrong tool -- logistic regression is built for exactly this case. Rather than "
         "predicting the outcome directly, it predicts the log-odds of the outcome occurring, which you then "
         "convert to odds ratios for interpretation: an odds ratio of 2.0 for a predictor means the odds of the "
         "outcome roughly double for each one-unit increase in that predictor. Model fit is assessed differently "
         "than in linear regression too -- look at the Hosmer-Lemeshow test, classification accuracy, and the "
         "area under the ROC curve, rather than R-squared."),
        ("Factor Analysis: Finding Structure in Your Variables",
         "Factor analysis helps you discover whether a large set of observed variables can be explained by a "
         "smaller number of underlying, unobserved factors -- commonly used to validate a survey instrument "
         "before using it in your main study. Exploratory factor analysis (EFA) lets the data suggest the "
         "factor structure; confirmatory factor analysis (CFA) tests whether a theory-driven structure you've "
         "already specified actually fits your data. Before running EFA, check that your data is even suitable "
         "for factor analysis using the KMO measure and Bartlett's test of sphericity -- skipping this step is a "
         "common source of uninterpretable results."),
        ("Effect Sizes: Why p-Values Alone Aren't Enough",
         "A statistically significant result tells you an effect probably isn't zero; it says nothing about "
         "whether that effect actually matters. Effect sizes fix this gap by quantifying the magnitude of a "
         "finding in standardized, comparable units: Cohen's d for mean differences, eta-squared for ANOVA, "
         "r-squared or f-squared for regression. Cohen's conventional benchmarks (small, medium, large) are a "
         "starting point, not a rule -- a 'small' effect can be highly meaningful in some fields (medicine) and "
         "trivial in others. Reporting and interpreting effect size alongside significance is now expected in "
         "essentially every quantitative discipline."),
    ],
    "advanced-statistics": [
        ("Moderated Mediation and Complex PLS-SEM Models",
         "Real theoretical models often combine mediation and moderation in the same structure -- a moderated "
         "mediation model tests whether an indirect effect (through a mediator) itself depends on the level of a "
         "moderating variable. In PLS-SEM, this means adding interaction terms to specific structural paths "
         "rather than the whole model, and interpreting conditional indirect effects at different levels of the "
         "moderator (commonly the mean, and one standard deviation above and below it). This is advanced "
         "territory even for experienced researchers -- get your measurement model rock-solid before attempting "
         "this level of structural complexity."),
        ("Handling Missing Data the Right Way",
         "How you handle missing data can change your results as much as your choice of statistical test, yet "
         "it's often treated as an afterthought. First, diagnose the missingness mechanism: missing completely at "
         "random (MCAR), missing at random (MAR), or missing not at random (MNAR) -- this determines which "
         "methods are even valid. Listwise deletion is simple but can badly bias results under MAR or MNAR. "
         "Multiple imputation is the current gold standard for MAR data, generating several plausible completed "
         "datasets and pooling results across them rather than guessing a single replacement value."),
        ("Publishing and Peer Review for Quantitative Studies",
         "Getting a quantitative study published involves a distinct set of expectations beyond a thesis "
         "defense. Reviewers expect pre-registered hypotheses where applicable, complete reporting of all "
         "measures and conditions (not just the significant ones), and increasingly, a data and code availability "
         "statement. Reporting guidelines exist for specific study types -- STROBE for observational studies, "
         "CONSORT for randomized trials -- and following them explicitly, citing the guideline in your methods "
         "section, materially improves your odds of a smooth review process."),
    ],
    "ai-ml-for-practitioners": [
        ("Feature Engineering: Where Most of the Real Work Happens",
         "The features (input variables) you feed a model usually matter more than the algorithm you choose -- "
         "a well-engineered feature set with a simple model regularly beats a sophisticated model on raw, "
         "unprocessed data. Feature engineering includes creating interaction terms, encoding categorical "
         "variables appropriately (one-hot encoding, ordinal encoding, target encoding depending on the case), "
         "scaling numeric features so no single feature dominates due to its raw magnitude, and extracting "
         "meaningful components from complex data like dates (day of week, is-holiday flags) or text. This is "
         "usually where the majority of a practitioner's actual time goes, not model tuning."),
        ("Tree-Based Models: Decision Trees, Random Forests, and Gradient Boosting",
         "Tree-based methods are a workhorse of applied machine learning because they handle mixed data types "
         "well and require relatively little preprocessing. A single decision tree splits data repeatedly on "
         "feature thresholds to separate classes or predict values, but tends to overfit on its own. Random "
         "forests average many trees trained on random subsets of data and features, trading some "
         "interpretability for much better generalization. Gradient boosting (XGBoost, LightGBM) builds trees "
         "sequentially, each one correcting the errors of the ones before it, and frequently wins on structured, "
         "tabular data -- the kind most business and research applications actually involve."),
        ("Deploying a Model Responsibly",
         "A model that performs well in a notebook isn't automatically ready for production. Before deployment, "
         "check for data leakage (information from outside the training set that inflated your performance "
         "estimates), test on genuinely held-out data collected after model development, and monitor for concept "
         "drift once deployed, since real-world data patterns shift over time in ways your training data never "
         "captured. Document your model's known limitations and the population it was actually trained and "
         "validated on -- deploying a model outside the population it was built for is one of the most common "
         "and consequential production failures."),
    ],
    "data-management-essentials": [
        ("Master Data vs Transactional Data",
         "Understanding this distinction prevents a lot of downstream confusion. Master data describes the core "
         "entities your organization deals with repeatedly -- customers, products, employees, locations -- and "
         "changes relatively rarely. Transactional data records events involving those entities -- a specific "
         "sale, a specific claim, a specific login -- and grows continuously. Treating transactional-scale data "
         "with master-data governance (or vice versa) creates real problems: master data needs strict "
         "deduplication and a single source of truth, while transactional data needs to handle high volume "
         "efficiently more than it needs exhaustive validation on every field."),
        ("Data Governance Basics",
         "Data governance is the set of policies and responsibilities that determine who can access, modify, and "
         "be accountable for data across an organization -- not a bureaucratic afterthought once you're past a "
         "certain size. Core elements include: data ownership (who is accountable for a given dataset's "
         "accuracy), access control (who can view or edit what), a change log for anything mission-critical, and "
         "a clear policy for how long data is retained and when it's archived or deleted. Even a solo "
         "practitioner or small team benefits from writing these decisions down rather than relying on memory."),
        ("Choosing Between Spreadsheets, Databases, and Data Warehouses",
         "Not every project needs a database, and not every database needs to be a full warehouse -- picking the "
         "right tool for your actual scale saves significant time. Spreadsheets work well for small, mostly "
         "manual datasets a single person or small team manages directly. A relational database becomes "
         "worthwhile once you have related tables, multiple concurrent users, or a need for real query "
         "performance beyond what a spreadsheet can handle. A data warehouse becomes worthwhile once you're "
         "regularly combining data from multiple source systems specifically for reporting and analysis, as "
         "covered in the Data Warehousing Fundamentals course."),
    ],
    "data-warehousing-fundamentals": [
        ("Slowly Changing Dimensions",
         "Dimension data isn't actually static -- a customer's address changes, a product's category gets "
         "reclassified -- and how you handle these changes affects your historical reporting accuracy. Type 1 "
         "slowly changing dimensions simply overwrite the old value, losing history but keeping things simple. "
         "Type 2 preserves history by creating a new row for each change, with effective-date columns marking "
         "which version was active when. Type 3 keeps a limited history in additional columns (current value plus "
         "one previous value). The right choice depends entirely on whether your reporting needs to reflect "
         "'as it was then' or only 'as it is now.'"),
        ("Data Warehouse Performance and Indexing",
         "A dimensional model that's theoretically correct can still perform poorly without attention to how "
         "it's actually queried. Indexing your fact tables on the foreign keys used in joins with dimension "
         "tables dramatically speeds up the aggregation queries reporting tools generate constantly. "
         "Partitioning large fact tables (commonly by date) lets queries skip irrelevant partitions entirely "
         "rather than scanning the whole table. Materialized views or pre-aggregated summary tables trade some "
         "storage and refresh complexity for much faster response times on your most common, heaviest reporting "
         "queries."),
        ("Modern Cloud Data Warehouses",
         "Cloud data warehouses (Snowflake, BigQuery, Redshift) have largely replaced traditional on-premises "
         "warehouses for new projects, separating storage and compute so you pay for and scale each "
         "independently. This means you can run a heavy analytical query without provisioning permanent "
         "infrastructure for peak load, and store years of historical data cheaply since storage and compute no "
         "longer scale together. The dimensional modeling principles from earlier lessons still apply directly "
         "-- the cloud platforms changed the infrastructure underneath, not the fundamental logic of organizing "
         "facts and dimensions for reporting."),
    ],
    "business-intelligence-dashboards": [
        ("KPIs: Choosing Metrics That Actually Drive Decisions",
         "A dashboard full of metrics nobody acts on is decoration, not business intelligence. A genuine key "
         "performance indicator should be directly tied to a decision someone will actually make differently "
         "depending on its value, owned by a specific person or team accountable for moving it, and measurable "
         "consistently over time so trends are meaningful. Vanity metrics -- numbers that go up and to the right "
         "but don't connect to any decision -- are the most common trap in dashboard design. For every metric on "
         "a dashboard, ask: if this number changed dramatically tomorrow, would anyone do anything differently?"),
        ("Connecting Live Data Sources",
         "A dashboard is only as useful as the freshness of its underlying data. Most BI tools connect to live "
         "data through direct database connections, APIs, or scheduled data exports, each with different "
         "tradeoffs between real-time accuracy and system load. Direct live connections give the most current "
         "data but can slow down source systems under heavy query load; scheduled refreshes (hourly, daily) "
         "reduce that load at the cost of data being slightly stale. Match your refresh strategy to how the "
         "dashboard is actually used -- an operations dashboard checked hourly needs different freshness than an "
         "executive summary reviewed once a week."),
        ("Making Dashboards People Actually Trust",
         "Adoption fails just as often from trust problems as design problems. If a number on a dashboard ever "
         "visibly contradicts a number from another report, viewers quietly stop trusting the whole dashboard, "
         "even if the discrepancy was explainable. Document your metric definitions explicitly (does 'active "
         "user' mean logged in this week or this month?) and keep that definition consistent everywhere it "
         "appears. Version and date-stamp your dashboards so viewers know exactly when the underlying data was "
         "last refreshed -- ambiguity about data freshness is one of the fastest ways to erode confidence in an "
         "otherwise well-built report."),
    ],
}

FURTHER_READING = {
    "research-methodology-foundations": (
        "Further Reading (Free & Open)",
        "For deeper reading on research methodology, these are legitimate, freely available resources: "
        "OpenStax's Introduction to Sociology and Introductory Statistics texts (openstax.org) cover research "
        "design fundamentals with a Creative Commons license. LibreTexts' Social Sciences library "
        "(commons.libretexts.org) has extensive open research methods material. The Directory of Open Access "
        "Books (doabooks.org) indexes peer-reviewed, freely downloadable research methods books. MIT "
        "OpenCourseWare (ocw.mit.edu) offers full course materials from MIT's research methods courses at no "
        "cost. These are supplementary, not required -- everything you need for this course is in the lessons "
        "above."
    ),
    "applied-statistics-for-research": (
        "Further Reading (Free & Open)",
        "OpenStax's Introductory Statistics and Introductory Business Statistics (openstax.org) are free, "
        "peer-reviewed, and downloadable as PDF -- strong reference texts for the tests covered in this course. "
        "LibreTexts' Statistics library (stats.libretexts.org) covers the same material with worked examples. "
        "MIT OpenCourseWare's Introduction to Probability and Statistics course materials (ocw.mit.edu) are also "
        "free. These are optional supplementary references."
    ),
    "basic-statistics": (
        "Further Reading (Free & Open)",
        "OpenStax's Introductory Statistics (openstax.org) is the standout free resource here -- a full, "
        "peer-reviewed college statistics textbook, free to read online or download as PDF. LibreTexts' "
        "Statistics library (stats.libretexts.org) offers the same core content with additional worked problems. "
        "Both are openly licensed and safe to reference alongside these lessons."
    ),
    "intermediate-statistics": (
        "Further Reading (Free & Open)",
        "OpenStax's Introductory Business Statistics (openstax.org) covers regression and ANOVA with a business "
        "research lens. LibreTexts' Statistics library (stats.libretexts.org) has dedicated sections on "
        "multivariate methods and factor analysis. MIT OpenCourseWare (ocw.mit.edu) has full regression analysis "
        "course materials available at no cost."
    ),
    "advanced-statistics": (
        "Further Reading (Free & Open)",
        "The Directory of Open Access Books (doabooks.org) indexes several open-access texts on structural "
        "equation modeling and survival analysis. LibreTexts' Statistics library (stats.libretexts.org) has "
        "advanced sections covering multivariate and survival methods. MIT OpenCourseWare (ocw.mit.edu) offers "
        "graduate-level statistics course materials that touch on several of these advanced methods."
    ),
    "ai-ml-for-practitioners": (
        "Further Reading (Free & Open)",
        "MIT OpenCourseWare (ocw.mit.edu) publishes full machine learning course materials, including lecture "
        "notes and problem sets, at no cost. LibreTexts' Engineering library (eng.libretexts.org) has open "
        "content on statistical learning methods. The Directory of Open Access Books (doabooks.org) indexes "
        "several open machine learning texts as well."
    ),
    "data-management-essentials": (
        "Further Reading (Free & Open)",
        "MIT OpenCourseWare (ocw.mit.edu) has course materials on data management and databases available free. "
        "LibreTexts' Engineering library (eng.libretexts.org) covers data structuring and database fundamentals "
        "openly. These are useful supplementary references for the concepts in this course."
    ),
    "data-warehousing-fundamentals": (
        "Further Reading (Free & Open)",
        "MIT OpenCourseWare (ocw.mit.edu) offers database systems course materials covering warehousing "
        "concepts at no cost. LibreTexts' Engineering library (eng.libretexts.org) has open content on database "
        "and data systems design that complements this course."
    ),
    "business-intelligence-dashboards": (
        "Further Reading (Free & Open)",
        "MIT OpenCourseWare (ocw.mit.edu) has data visualization and analytics course materials available free. "
        "LibreTexts' Business library (biz.libretexts.org) covers business analytics and reporting fundamentals "
        "openly. These are optional supplementary references alongside the lessons in this course."
    ),
}


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    total_added, courses_touched = 0, 0
    try:
        for slug, lessons in EXTRA_LESSONS.items():
            course = db.query(models.Course).filter(models.Course.slug == slug).first()
            if not course:
                print(f"[missing] '{slug}' -- run seed_courses.py first.")
                continue

            existing_titles = {l.title for l in course.lessons}
            max_order = max([l.order for l in course.lessons], default=0)
            added_here = 0

            for title, content in lessons:
                if title in existing_titles:
                    continue
                max_order += 1
                db.add(models.Lesson(course_id=course.id, title=title, content=content, order=max_order))
                added_here += 1
                total_added += 1

            reading_title, reading_content = FURTHER_READING[slug]
            if reading_title not in existing_titles:
                max_order += 1
                db.add(models.Lesson(course_id=course.id, title=reading_title, content=reading_content, order=max_order))
                added_here += 1
                total_added += 1

            if added_here:
                courses_touched += 1
                print(f"[{course.title}] added {added_here} lesson(s)")
            else:
                print(f"[{course.title}] already up to date")

        db.commit()
    finally:
        db.close()

    print(f"\nDone. {total_added} lesson(s) added across {courses_touched} course(s).")


if __name__ == "__main__":
    run()
