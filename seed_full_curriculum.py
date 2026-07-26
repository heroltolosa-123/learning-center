"""
Populates real, substantive lessons for the 9 Hero Academy courses, replacing
the "Course overview" placeholder created by the original seed_courses.py.

Safe to re-run: for each course, it removes any lesson literally titled
"Course overview" (the old placeholder) and then adds any curriculum lesson
whose title doesn't already exist under that course. Existing real lessons
you've already written yourself are left untouched.

Usage (same DATABASE_URL pattern as seed_courses.py):
    DATABASE_URL="postgresql://...your neon connection string..." python3 seed_full_curriculum.py

This is a first pass, written to be accurate and genuinely useful, not
filler — but it's still a starting point. Replace, expand, or add video
lessons from /admin any time.
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal
from app import models

CURRICULUM = {
    "research-methodology-foundations": [
        ("What Makes a Research Question Researchable",
         "Not every question worth asking is a question you can study. A researchable question is specific, "
         "measurable, and answerable with data you can realistically collect. \"Does social media affect mental "
         "health?\" is a topic, not a research question -- it's too broad to design a study around. \"Does daily "
         "time spent on social media correlate with self-reported anxiety scores among college students?\" is "
         "researchable: it names a population, a variable you can measure, and a relationship you can test. "
         "Before you touch any statistics, spend real time narrowing your topic down to something this specific. "
         "A tight, well-defined question makes every later step -- design, sampling, analysis -- dramatically easier. "
         "A vague one guarantees trouble at every stage after it."),
        ("Choosing a Research Design",
         "Your research question dictates your design, not the other way around. If you're asking whether "
         "something causes a change, you likely need an experimental or quasi-experimental design with some form "
         "of comparison group. If you're describing what exists right now, a cross-sectional survey design fits. "
         "If you're tracking change over time, you need a longitudinal design. If you're exploring lived "
         "experience rather than testing a hypothesis, a qualitative design -- phenomenology, grounded theory, "
         "case study -- is the right tool, not a statistical one. A common mistake is picking a design because "
         "it's familiar or fast, then trying to force a research question to fit it. Work in the other direction: "
         "let the question determine the design, even when the resulting design is more work."),
        ("Sampling: Getting a Group That Actually Represents Your Population",
         "Your results are only as trustworthy as your sample. Probability sampling -- simple random, stratified, "
         "systematic, cluster -- lets you make statistical claims about a wider population because every member had "
         "a known chance of being selected. Non-probability sampling -- convenience, purposive, snowball -- is "
         "often necessary in practice, especially for qualitative or hard-to-reach populations, but it limits how "
         "far you can generalize your findings. Sample size matters too: too small, and you can't detect real "
         "effects even when they exist (a power problem); too large relative to your resources, and you waste time "
         "and money on precision you didn't need. Use a formula like Cochran's to justify your sample size "
         "up front, rather than picking a round number and hoping it holds up under review."),
        ("Research Ethics and Informed Consent",
         "Every study involving people carries an ethical obligation before it carries a statistical one. "
         "Informed consent means participants understand what they're agreeing to: the purpose of the study, what "
         "will be asked of them, any risks, and that they can withdraw at any point without penalty. Confidentiality "
         "and anonymity are not the same thing -- confidentiality means you know who participated but protect that "
         "information, anonymity means you have no way to trace a response back to a person at all. Vulnerable "
         "populations (minors, patients, prisoners, employees reporting on their own employer) require extra "
         "safeguards. Most institutions require ethics review board approval before data collection begins -- "
         "build that timeline into your research plan from day one, not as an afterthought once your instrument "
         "is already built."),
    ],
    "applied-statistics-for-research": [
        ("From Research Question to Statistical Test",
         "Every statistical test answers a specific kind of question, and picking the wrong one is the single "
         "most common error panels flag. Ask yourself three things: how many groups or variables are you "
         "comparing, what type of data do you have (categorical, ordinal, continuous), and is your data "
         "independent or paired/related? Comparing two independent groups on a continuous outcome points to a "
         "t-test. Comparing more than two groups points to ANOVA. Looking at the relationship between two "
         "continuous variables points to correlation or regression. Comparing categorical variables points to "
         "chi-square. Write your research question down, then walk through these three questions before opening "
         "any software -- the test should follow logically from the question, not from whichever test you're "
         "most comfortable running."),
        ("Choosing the Right Test: A Decision Framework",
         "Build yourself a simple decision tree and use it every time, even once you're experienced: is the "
         "outcome variable continuous or categorical? If continuous, are you comparing groups (t-test/ANOVA) or "
         "looking at relationships (correlation/regression)? If categorical, are you looking at frequencies "
         "(chi-square) or predicting group membership (logistic regression)? Also check your assumptions before "
         "committing to a parametric test -- normality, homogeneity of variance, independence. When assumptions "
         "are violated, non-parametric alternatives exist for nearly every parametric test: Mann-Whitney instead "
         "of an independent t-test, Kruskal-Wallis instead of one-way ANOVA. Panels notice when a student runs a "
         "parametric test on clearly non-normal data without at least acknowledging the violation."),
        ("Reading and Reporting Output the Way a Panel Expects",
         "Statistical software gives you far more numbers than you need to report, and knowing which ones matter "
         "is a skill in itself. For most tests, a panel expects: the test statistic (t, F, chi-square value), "
         "degrees of freedom, the p-value, and an effect size (Cohen's d, eta-squared, or similar) -- a significant "
         "p-value alone tells you an effect exists, not whether it's meaningful in practice. Report results in "
         "APA format consistently: \"t(48) = 2.31, p = .025, d = 0.66\" rather than a screenshot of raw software "
         "output. Always interpret the result in plain language immediately after reporting the statistics -- "
         "what does this number mean for your actual research question, in a sentence a non-statistician could "
         "follow."),
        ("Common Mistakes That Get Flagged in Defense",
         "The same handful of errors show up again and again in thesis and dissertation defenses. Running "
         "multiple tests without correcting for the increased chance of false positives (no Bonferroni or similar "
         "adjustment). Confusing statistical significance with practical importance -- a p-value of .001 on a "
         "trivial effect size is not a strong finding. Treating ordinal data (Likert scales) as if it were "
         "continuous without justification. Failing to check or report whether assumptions were met. Overstating "
         "causation from correlational or cross-sectional data. Each of these is fixable if you catch it before "
         "your defense -- build a checklist and run your analysis chapter against it before anyone else sees it."),
    ],
    "basic-statistics": [
        ("Descriptive Statistics: Making Sense of Raw Numbers",
         "Before any inference, you need to describe what your data actually looks like. Measures of central "
         "tendency -- mean, median, mode -- tell you where the center of your data sits, but each behaves "
         "differently with outliers: the mean is pulled toward extreme values, the median isn't. Measures of "
         "spread -- range, variance, standard deviation -- tell you how tightly your data clusters around that "
         "center. A dataset with a mean of 50 and a standard deviation of 2 looks very different from one with "
         "the same mean and a standard deviation of 20, even though the \"average\" is identical. Always look at "
         "both center and spread together, and visualize your data with a histogram or boxplot before running any "
         "test -- numbers alone can hide a shape that changes everything about which test is appropriate."),
        ("Probability Basics You Actually Need",
         "You don't need a full probability theory course to do applied statistics well, but a few ideas are "
         "essential. Probability is a number between 0 and 1 describing how likely an event is. Independent "
         "events don't affect each other's probability (a coin flip doesn't \"remember\" the last flip). "
         "Conditional probability -- the chance of one event given that another has occurred -- underlies concepts "
         "like sensitivity and specificity in diagnostic testing. The idea of a sampling distribution -- that if "
         "you took many samples from a population, the sample means would themselves form a predictable "
         "distribution -- is the conceptual bridge between simple probability and everything that follows in "
         "hypothesis testing."),
        ("The Normal Distribution and Why It Matters",
         "The normal distribution -- the familiar bell curve -- matters because so much statistical theory assumes "
         "it, directly or indirectly. It's symmetric around the mean, and a fixed percentage of data always falls "
         "within one, two, and three standard deviations of that mean (roughly 68%, 95%, and 99.7%). Many natural "
         "phenomena approximate this shape, and even when your raw data doesn't, the Central Limit Theorem tells "
         "you that the distribution of sample means will approach normal as your sample size grows -- which is why "
         "many parametric tests still work reasonably well even on non-normal data, provided your sample is large "
         "enough. Checking for normality (visually with a histogram or Q-Q plot, or formally with Shapiro-Wilk) is "
         "a standard early step before choosing a test."),
        ("Your First Hypothesis Test",
         "Every hypothesis test follows the same basic logic. You start with a null hypothesis (no effect or no "
         "difference) and an alternative hypothesis (there is an effect or difference). You collect data, "
         "calculate a test statistic, and ask: how likely would this result be if the null hypothesis were true? "
         "If that likelihood (your p-value) is low enough -- conventionally below .05 -- you reject the null in "
         "favor of the alternative. This doesn't prove the alternative is true; it means the data would be "
         "unusual if the null were true. A one-sample t-test, comparing a sample mean to a known value, is the "
         "simplest place to practice this logic before moving to comparisons between groups."),
    ],
    "intermediate-statistics": [
        ("Simple and Multiple Linear Regression",
         "Regression models the relationship between a continuous outcome and one or more predictors. Simple "
         "linear regression uses one predictor; multiple regression uses several at once, letting you see each "
         "predictor's effect while holding the others constant. The regression coefficient tells you how much the "
         "outcome changes for a one-unit change in the predictor. R-squared tells you what proportion of the "
         "variance in your outcome the model explains -- useful, but not the whole story; a model can have high "
         "R-squared and still violate assumptions, or low R-squared and still be theoretically meaningful. Always "
         "report both the coefficients and their statistical significance, and be explicit about which variables "
         "you controlled for and why."),
        ("ANOVA: Comparing More Than Two Groups",
         "Analysis of variance (ANOVA) extends the t-test logic to three or more groups without inflating your "
         "false-positive rate the way running multiple t-tests would. A significant ANOVA result tells you that "
         "at least one group differs from the others -- it doesn't tell you which ones. That's what post-hoc "
         "tests (Tukey's HSD, Bonferroni-corrected pairwise comparisons) are for, and you should always plan to "
         "run them alongside your ANOVA rather than treating the omnibus test as the final answer. Two-way ANOVA "
         "lets you examine two categorical predictors at once, including whether they interact -- whether the "
         "effect of one depends on the level of the other."),
        ("Checking Your Assumptions",
         "Every parametric test rests on assumptions, and skipping the check is one of the fastest ways to "
         "undermine an otherwise solid analysis. For regression and ANOVA: check normality of residuals (not "
         "your raw data -- the residuals), homogeneity of variance across groups (Levene's test), independence of "
         "observations, and for regression specifically, linearity and absence of severe multicollinearity "
         "(variance inflation factor). When assumptions are violated, you have three real options: transform your "
         "data, use a robust or non-parametric alternative, or proceed with the parametric test while explicitly "
         "acknowledging and discussing the violation -- silence is the only wrong option."),
        ("Introduction to Multivariate Thinking",
         "Most real research questions involve more than one variable interacting at once, which is why "
         "multivariate methods exist. Where regression predicts one outcome from several predictors, multivariate "
         "techniques like MANOVA examine several outcome variables simultaneously, and factor analysis looks for "
         "underlying structure among many observed variables. The shift in thinking that matters most here is "
         "moving away from \"does X affect Y\" toward \"how do these variables relate to each other as a system\" "
         "-- a mindset you'll need fully developed before tackling structural equation modeling in the advanced "
         "course."),
    ],
    "advanced-statistics": [
        ("Structural Equation Modeling: The Big Picture",
         "Structural equation modeling (SEM) lets you test an entire theoretical model at once -- relationships "
         "between multiple latent (unobserved) constructs, each measured by several observed indicators. Where "
         "regression tests one outcome against predictors, SEM tests a whole web of hypothesized relationships "
         "simultaneously, including mediation and moderation effects. There are two main flavors: covariance-based "
         "SEM (CB-SEM), which tests how well your theoretical model fits the observed covariance structure, and "
         "partial least squares SEM (PLS-SEM), which is prediction-oriented and more forgiving of smaller samples "
         "and non-normal data -- which is exactly why it shows up so often in applied social science and business "
         "research."),
        ("PLS-SEM Step by Step",
         "A PLS-SEM analysis follows a consistent sequence. First, assess the measurement model: check indicator "
         "reliability, internal consistency (composite reliability, Cronbach's alpha), convergent validity "
         "(average variance extracted), and discriminant validity (HTMT ratio) -- this is the step most students "
         "get flagged on, especially reverse-coded items that weren't handled correctly before analysis. Only "
         "after the measurement model passes these checks do you move to the structural model: path coefficients, "
         "R-squared for endogenous constructs, effect sizes (f-squared), and predictive relevance (Q-squared). "
         "Bootstrapping (typically 5,000 subsamples) generates the significance tests for your path coefficients, "
         "since PLS-SEM doesn't assume a known sampling distribution the way traditional regression does."),
        ("Survival Analysis Fundamentals",
         "Survival analysis handles a specific data problem regular regression can't: time-to-event data with "
         "censoring, where some subjects haven't yet experienced the event of interest by the end of your study. "
         "The Kaplan-Meier estimator gives you a non-parametric picture of survival probability over time and is "
         "usually your first descriptive step. The log-rank test compares survival curves between groups. Cox "
         "proportional hazards regression lets you model the effect of multiple covariates on survival time while "
         "handling censored data correctly -- its key assumption, proportional hazards, needs to be checked "
         "explicitly (commonly via Schoenfeld residuals) rather than assumed."),
        ("Firth Logistic Regression for Rare Events",
         "Standard logistic regression struggles when you have rare outcomes or small samples -- coefficients can "
         "become unstable or fail to converge entirely, a problem known as separation. Firth's penalized "
         "likelihood approach corrects for this by adding a small bias-reduction term, producing stable, "
         "interpretable estimates even when your outcome event is uncommon or your sample is modest. This comes "
         "up constantly in clinical and comparative studies with small sample sizes -- surgical outcome studies "
         "comparing two techniques, for instance, where one complication type occurs in only a handful of cases. "
         "Recognizing when standard logistic regression is quietly failing you, rather than trusting an output "
         "that looks fine on the surface, is the real skill here."),
    ],
    "ai-ml-for-practitioners": [
        ("What Machine Learning Actually Is (and Isn't)",
         "Machine learning is, at its core, a set of methods for finding patterns in data and using them to make "
         "predictions on new data -- it is not magic, and it is not automatically better than a well-specified "
         "statistical model. Supervised learning (the most common starting point) means training a model on "
         "labeled data, where you already know the outcome for each example, so the model learns the mapping "
         "from inputs to outputs. Unsupervised learning finds structure in data with no labels at all -- clustering "
         "similar customers together, for instance. The distinction between ML and traditional statistics is "
         "less about the math (much of it overlaps heavily) and more about the goal: statistics traditionally "
         "prioritizes interpretability and inference, ML traditionally prioritizes predictive accuracy, even at "
         "the cost of interpretability."),
        ("Classification vs Regression Problems",
         "The first decision in any supervised learning project is what kind of outcome you're predicting. "
         "Classification problems predict a category -- will this customer churn or not, is this transaction "
         "fraudulent or not, which of five categories does this image belong to. Regression problems (in the ML "
         "sense, same underlying idea as statistical regression) predict a continuous number -- next month's "
         "revenue, a patient's expected recovery time. This distinction determines which algorithms are even "
         "appropriate: logistic regression, decision trees, and random forests all have classification and "
         "regression variants, but the evaluation metrics differ completely -- accuracy and F1-score for "
         "classification, RMSE and R-squared for regression."),
        ("Training, Validation, and Test Sets",
         "A model that performs beautifully on the data it was trained on and poorly on new data is worthless in "
         "practice -- this is why you never evaluate a model on the same data you trained it on. The standard "
         "approach splits your data three ways: a training set the model learns from, a validation set used to "
         "tune hyperparameters and make decisions during development, and a test set touched exactly once, at "
         "the very end, to get an honest estimate of real-world performance. Cross-validation (commonly k-fold) "
         "extends this idea by rotating which portion of your data serves as validation across several rounds, "
         "giving you a more stable performance estimate when your dataset is limited."),
        ("Overfitting and How to Avoid It",
         "Overfitting happens when a model learns the noise in your training data rather than the underlying "
         "signal -- it memorizes rather than generalizes, and performs far worse on new data than its training "
         "performance would suggest. Signs of overfitting include a large gap between training accuracy and "
         "validation accuracy, and models that get more complex without improving on held-out data. Common "
         "countermeasures: regularization (L1/L2, which penalizes overly complex models), simplifying the model, "
         "gathering more training data, and using cross-validation religiously rather than trusting a single "
         "train/test split. The discipline used in serious production ML pipelines to fight overfitting exists "
         "precisely because this failure mode is so easy to fall into and so costly once deployed."),
    ],
    "data-management-essentials": [
        ("What Good Data Structure Looks Like",
         "Well-structured data follows a simple rule: one row per observation, one column per variable, and "
         "consistent data types within each column -- this is often called \"tidy data,\" and almost every "
         "downstream problem in analysis traces back to a violation of it. Common structural mistakes: mixing "
         "units within a column (some rows in kilograms, others in pounds), embedding multiple variables in one "
         "column (a \"name\" field containing both first and last name), or using merged cells and multiple "
         "header rows in a spreadsheet, which breaks nearly every analysis tool. Fixing structure before "
         "collecting a single row of real data -- by designing your data entry template correctly from the start "
         "-- saves far more time than cleaning up a mess after the fact."),
        ("Data Cleaning Fundamentals",
         "Real data is never clean on arrival. Missing values need a deliberate strategy -- deletion, imputation, "
         "or flagging -- chosen based on why the data is missing, not just filled in reflexively. Duplicate "
         "records, especially from merged datasets, need explicit detection rules rather than a visual scan. "
         "Inconsistent categorical values (\"Male,\" \"M,\" \"male\" all meaning the same thing) need standardizing "
         "before any grouping or analysis. Outliers need investigation, not automatic deletion -- some outliers "
         "are genuine data entry errors, others are the most interesting finding in your dataset. Document every "
         "cleaning decision you make; a cleaning process nobody can reconstruct later is itself a data quality "
         "risk."),
        ("Data Validation Rules",
         "Validation catches errors at the point of entry, which is far cheaper than catching them during "
         "analysis. Range checks (an age field shouldn't accept 250), format checks (a date field should reject "
         "non-date text), consistency checks (an end date shouldn't precede a start date), and referential checks "
         "(a foreign key should match an existing record) all prevent the same handful of error types that "
         "otherwise take hours to track down later. Building these rules into your data entry forms or "
         "spreadsheet templates -- rather than relying on manual review -- is the difference between a dataset you "
         "trust and one you're constantly second-guessing."),
        ("Documentation and Metadata",
         "A dataset without documentation is a liability, even to the person who created it, six months later. "
         "A proper data dictionary records, for every variable: its name, its meaning in plain language, its data "
         "type, its valid range or categories, and how it was derived if it wasn't collected directly. Metadata "
         "about the dataset as a whole -- collection dates, sampling method, known limitations, version history -- "
         "belongs alongside it. This isn't bureaucratic overhead; it's what lets someone else (or you, much "
         "later) actually reuse the data correctly instead of guessing at what a column labeled \"score_2\" was "
         "supposed to mean."),
    ],
    "data-warehousing-fundamentals": [
        ("What a Data Warehouse Is (and Why Spreadsheets Aren't Enough)",
         "A data warehouse is a centralized repository designed specifically for analysis and reporting, pulling "
         "together data from multiple operational systems into one consistent structure. Spreadsheets and "
         "individual operational databases break down at scale for a specific reason: operational systems are "
         "optimized for fast individual transactions (recording one sale), not for aggregating millions of them "
         "for a report. A data warehouse separates these concerns -- operational systems keep doing their job, "
         "while a warehouse periodically pulls, cleans, and restructures that data specifically for querying and "
         "reporting, without slowing down the systems people rely on to actually run the business."),
        ("Dimensional Modeling: Facts and Dimensions",
         "Dimensional modeling is the standard approach to structuring a data warehouse for reporting. Fact "
         "tables hold the measurable events you care about -- a sale, a claim, a lab result -- along with numeric "
         "measures (amount, quantity, duration). Dimension tables hold the descriptive context around those "
         "facts -- customer details, product details, time periods, locations -- that let you slice and filter "
         "the facts meaningfully. A sales fact table paired with customer, product, and date dimension tables "
         "lets you answer \"total sales by region, by month, by product category\" without redesigning anything, "
         "because the dimensions already contain that descriptive structure."),
        ("ETL Basics: Extract, Transform, Load",
         "ETL describes the process of moving data into your warehouse. Extract pulls raw data from source "
         "systems -- databases, APIs, exported files. Transform cleans, standardizes, and restructures that data "
         "into your warehouse's dimensional model -- this is where data cleaning and validation rules actually "
         "get applied at scale. Load writes the transformed data into the warehouse tables, either replacing "
         "existing data or appending new records depending on your update strategy. Modern practice increasingly "
         "uses ELT (load first, transform after, inside the warehouse itself) rather than strict ETL, but the "
         "underlying three concerns -- get the data, fix the data, store the data correctly -- remain the same "
         "regardless of which order you do them in."),
        ("Star Schema vs Snowflake Schema",
         "A star schema keeps dimension tables denormalized -- flat, with some redundancy -- which makes queries "
         "simpler and faster because reporting tools need fewer joins to answer a question. A snowflake schema "
         "normalizes those dimension tables further, splitting them into related sub-tables, which reduces "
         "storage redundancy but adds query complexity. For most reporting and BI use cases, star schema is the "
         "practical default: storage is cheap, and query simplicity matters more than eliminating redundancy. "
         "Reach for snowflake schema only when a dimension is genuinely large and complex enough that the "
         "normalization meaningfully pays off."),
    ],
    "business-intelligence-dashboards": [
        ("BI Tool Landscape: Choosing What Fits",
         "Business intelligence tools generally fall into a few tiers: spreadsheet-based tools (still legitimate "
         "for small-scale, low-frequency reporting), dedicated BI platforms (Power BI, Tableau, Looker) built "
         "specifically for interactive dashboards connected to live data sources, and embedded or custom solutions "
         "built for a specific product. The right choice depends less on which tool is \"best\" in the abstract "
         "and more on your actual constraints: who needs to view the dashboard, how often the underlying data "
         "changes, your budget, and what your data sources already are. A tool chosen because it's popular, "
         "rather than because it fits your actual data infrastructure and audience, is a common and costly "
         "mistake."),
        ("Dashboard Design Principles That Actually Get Used",
         "The most common dashboard failure isn't technical -- it's that nobody actually looks at it after the "
         "first week. Good dashboards answer a specific, recurring question for a specific audience, rather than "
         "displaying every metric available \"just in case.\" Put the most important number where the eye lands "
         "first (top-left in most reading patterns). Group related metrics together visually. Use consistent "
         "color coding across the whole dashboard, not different meanings for the same color on different "
         "sections. Avoid decorative chart junk -- 3D effects, unnecessary gridlines, excessive color -- that adds "
         "visual noise without adding information. If a viewer needs a legend to understand a color's meaning "
         "instead of the color making it obvious, reconsider the palette."),
        ("Choosing the Right Chart for the Right Question",
         "Different questions call for genuinely different chart types, and the wrong choice actively misleads "
         "even with correct underlying data. Comparing categories: bar chart. Showing change over time: line "
         "chart. Showing part-to-whole relationships: stacked bar or, sparingly, a pie chart (only when you have "
         "very few categories). Showing relationship between two continuous variables: scatter plot. Showing "
         "distribution: histogram or box plot. A frequent mistake is defaulting to a pie chart for data with many "
         "categories or similar-sized slices, where humans genuinely struggle to compare angles accurately -- a "
         "simple bar chart communicates the same data far more clearly in almost every case."),
        ("Automating Recurring Reports",
         "If you're manually rebuilding the same report every week, that time is almost always automatable. Most "
         "BI tools support scheduled refresh, pulling live data on a set interval so the dashboard is always "
         "current without manual intervention. For reports that need to be pushed out (emailed, posted to a "
         "channel) rather than pulled by viewers, scheduled exports or API-triggered automation handle the "
         "delivery side. The real automation win isn't just saved time -- it's consistency: an automated report "
         "runs the same way every time, eliminating the small manual errors (a missed filter, a stale copy-paste) "
         "that creep into hand-built reports over weeks and months."),
    ],
}


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    total_added, total_skipped, courses_touched = 0, 0, 0
    try:
        for slug, lessons in CURRICULUM.items():
            course = db.query(models.Course).filter(models.Course.slug == slug).first()
            if not course:
                print(f"[missing] No course found with slug '{slug}' -- run seed_courses.py first.")
                continue

            placeholder = (
                db.query(models.Lesson)
                .filter(models.Lesson.course_id == course.id, models.Lesson.title == "Course overview")
                .first()
            )
            if placeholder:
                db.delete(placeholder)
                db.flush()

            existing_titles = {l.title for l in course.lessons}
            added_here = 0
            for i, (title, content) in enumerate(lessons, start=1):
                if title in existing_titles:
                    total_skipped += 1
                    continue
                lesson = models.Lesson(
                    course_id=course.id,
                    title=title,
                    content=content,
                    order=i,
                    is_preview=(i == 1),
                )
                db.add(lesson)
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

    print(f"\nDone. {total_added} lesson(s) added across {courses_touched} course(s), {total_skipped} already existed.")


if __name__ == "__main__":
    run()
