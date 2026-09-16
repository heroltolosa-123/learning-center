"""
Deepens the nine original courses against the national curriculum sources, and
records curriculum alignment, prerequisites and learning outcomes for each.

Sources
  - CHED Memorandum Order No. 42, s. 2017 -- Policies, Standards and Guidelines
    for the BS Statistics program (Annex B, Course Specifications)
    https://legacy.ched.gov.ph/wp-content/uploads/2017/10/CMO-42-s-2017.pdf
  - UST BS Data Science and Analytics curriculum
    https://www.ust.edu.ph/academics/programs/bachelor-of-science-in-data-science-and-analytics/
  - UP Diliman Data Science tracks
    https://sites.google.com/science.upd.edu.ph/upd-data-science/1/tracks
  - UP Diliman College of Engineering, MEng in Artificial Intelligence
    https://coe.upd.edu.ph/masters-of-engineering-in-artificial-intelligence/

Lesson text is written from scratch for self-paced learners. Only the course
descriptions, topic coverage and outcome wording are grounded in those sources.

Safe to re-run: courses are matched by slug, lessons by title. A "Further
Reading" lesson is always pushed to the end of its course.

Usage:
    python3 seed_ched_deepening.py
    DATABASE_URL="postgresql://..." python3 seed_ched_deepening.py
"""
import json
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal, sync_columns
from app import models

CMO = "CHED CMO 42 s. 2017"
UST = "UST BS Data Science & Analytics"


def L(title, content, quiz=None):
    return {"title": title, "content": content, "quiz": quiz}


# ===========================================================================
# Curriculum metadata for the nine original courses
# ===========================================================================
METADATA = {
    "basic-statistics": {
        "description": (
            "Basic statistical concepts and statistical measurement: levels of measurement, "
            "collection, organization and presentation of data, measures of central tendency, "
            "location, dispersion, skewness and kurtosis, boxplots and stem-and-leaf displays, "
            "measures of association, rates, ratios and proportions, and the construction of "
            "index numbers and official statistics indicators. Taught the way you would "
            "actually use them, not just the formulas."
        ),
        "curriculum_alignment": f"{CMO} core -- Descriptive Statistics (3 units)",
        "prerequisites": "Algebra and trigonometry from senior high school, per CMO 42",
        "learning_outcomes": (
            "Familiarize with statistical terminologies\n"
            "Know the different methods of data collection, organization, and presentation\n"
            "Understand basic concepts in survey sampling\n"
            "Process and summarize data in terms of location, spread, and other descriptive measures\n"
            "Guard against misuses of statistics and recognize the importance of using the most "
            "appropriate measures and data presentation methods"
        ),
    },
    "applied-statistics-for-research": {
        "description": (
            "Bridging statistical theory and real research questions: choosing the right test "
            "for your design, interpreting output the way a panel expects, justifying sample "
            "size, and reporting results that hold up to scrutiny. Built from years of thesis "
            "and dissertation consulting, and organised around the decision-making and "
            "communication competencies CMO 42 requires of a statistics graduate."
        ),
        "curriculum_alignment": (
            f"{CMO} core competencies -- Problem-solving, Decision-making, and Ethics & integrity; "
            "supports Mathematical Statistics 3 in application"
        ),
        "prerequisites": "Basic Statistics: A Practical Start, or equivalent introductory statistics",
        "learning_outcomes": (
            "Translate real-life research problems into statistical problems\n"
            "Identify appropriate statistical tests and methods and use them properly\n"
            "Interpret solutions in the context of a viable environment\n"
            "Communicate decisions and results to stakeholders\n"
            "Adhere to data integrity and report results as honestly as possible"
        ),
    },
    "research-methodology-foundations": {
        "description": (
            "How to design a study that survives a panel defense: research questions, design "
            "choices, probability and non-probability sampling, the full survey operation from "
            "questionnaire design through data coding and quality control, instrument "
            "development, and ethics review. Covers the groundwork every thesis and "
            "dissertation needs before any statistics happen."
        ),
        "curriculum_alignment": (
            f"{CMO} core -- Survey Sampling and Survey Operations (6 units combined)"
        ),
        "prerequisites": "None. This is the recommended starting point for thesis candidates.",
        "learning_outcomes": (
            "Define the objectives of a survey and identify the data needed to achieve them\n"
            "Construct, implement and evaluate a sampling design\n"
            "Draft questionnaires that will gather such data\n"
            "Understand challenges, options and tradeoffs involved in data collection\n"
            "Organize survey response data and interpret it accurately\n"
            "Present research findings to target users"
        ),
    },
    "intermediate-statistics": {
        "description": (
            "The linear model and everything that can go wrong with it. Simple and multiple "
            "regression, the classical assumptions, regression diagnostics and remedial "
            "measures, outliers, non-normality and heteroskedasticity, multicollinearity and "
            "shrinkage estimators, dummy variables and interaction, model selection, ANOVA, "
            "logistic regression and factor analysis."
        ),
        "curriculum_alignment": (
            f"{CMO} core -- Regression Analysis (3 units); introduces Multivariate Analysis"
        ),
        "prerequisites": (
            "Mathematical Statistics 3 and Linear Algebra and Matrix Theory, per CMO 42\n"
            "Basic Statistics: A Practical Start, or equivalent"
        ),
        "learning_outcomes": (
            "Understand the concepts, limitations, interpretations and uses of a regression model\n"
            "Analyze linear models: intuition, implementation and interpretation\n"
            "Detect and remedy outliers, non-normality, heteroskedasticity, autocorrelation and multicollinearity\n"
            "Interpret regression results in solving real-life problems"
        ),
    },
    "advanced-statistics": {
        "description": (
            "The methods that appear in published quantitative research and rarely in "
            "coursework. Structural equation modeling and PLS-SEM, survival analysis, "
            "categorical data analysis with loglinear and logit models, Bayesian inference "
            "including hierarchical models, Firth logistic regression for rare events, "
            "moderated mediation, and principled handling of missing data."
        ),
        "curriculum_alignment": (
            f"{CMO} core -- Categorical Data Analysis and Bayesian Statistics (6 units combined); "
            "extends Multivariate Analysis"
        ),
        "prerequisites": (
            "Regression Analysis and Mathematical Statistics 3, per CMO 42\n"
            "Intermediate Statistics: Building Real Models, or equivalent"
        ),
        "learning_outcomes": (
            "Perform tests of association between categorical variables\n"
            "Build models and assess their fit for categorical variables and draw conclusions from them\n"
            "Distinguish between Bayesian and non-Bayesian frameworks\n"
            "Do basic Bayesian modeling\n"
            "Apply multivariate methods appropriately and interpret the results exhaustively"
        ),
    },
    "ai-ml-for-practitioners": {
        "description": (
            "Practical machine learning for people who already understand statistics. "
            "Classification and regression, training/validation/test discipline, overfitting, "
            "feature engineering, tree-based models, principal component analysis, and "
            "responsible deployment. Mapped to the artificial intelligence and machine "
            "learning strands of the UST and UP Diliman data science programs."
        ),
        "curriculum_alignment": (
            f"{UST} -- Artificial Intelligence, Machine Learning and Data Mining 1; "
            "UP Diliman MEng Artificial Intelligence, applied strand"
        ),
        "prerequisites": (
            "Intermediate Statistics: Building Real Models, or equivalent regression background\n"
            "Comfort with a programming language is helpful but not required"
        ),
        "learning_outcomes": (
            "Distinguish classification from regression problems and choose appropriately\n"
            "Apply training, validation and test discipline to avoid overfitting\n"
            "Engineer features and evaluate model performance honestly\n"
            "Reduce dimensionality without losing interpretability\n"
            "Deploy and monitor a model responsibly"
        ),
    },
    "data-management-essentials": {
        "description": (
            "The unglamorous work that determines whether any analysis is possible: data "
            "structure, cleaning, validation rules, documentation and metadata, master versus "
            "transactional data, governance, and information security and data privacy under "
            "the Philippine Data Privacy Act. Mapped to the information management strand of "
            "the UST data science curriculum."
        ),
        "curriculum_alignment": (
            f"{UST} -- Information Management; Information Security and Data Privacy"
        ),
        "prerequisites": "None. Suitable as a first course for research assistants and analysts.",
        "learning_outcomes": (
            "Structure data so that analysis is possible without rework\n"
            "Apply validation rules and document datasets with usable metadata\n"
            "Distinguish master from transactional data and govern each appropriately\n"
            "Handle personal data lawfully under RA 10173 and its implementing rules"
        ),
    },
    "data-warehousing-fundamentals": {
        "description": (
            "Designing data stores that scale: dimensional modeling, facts and dimensions, "
            "ETL, star and snowflake schemas, slowly changing dimensions, indexing and "
            "performance, cloud warehouses, and the principles of big data. Mapped to the "
            "data management and warehousing strand of the UST data science curriculum."
        ),
        "curriculum_alignment": f"{UST} -- Data Management and Warehousing; Principles of Big Data",
        "prerequisites": "Data Management Essentials, or equivalent experience with structured data",
        "learning_outcomes": (
            "Model a subject area dimensionally with facts and conformed dimensions\n"
            "Design and reason about an ETL pipeline\n"
            "Choose between star and snowflake schemas and justify the choice\n"
            "Handle changing dimension attributes without losing history\n"
            "Recognise when a workload genuinely requires big-data infrastructure"
        ),
    },
    "business-intelligence-dashboards": {
        "description": (
            "Turning a warehouse into decisions people actually make. BI tool selection, "
            "information presentation and visualization, dashboard design, chart choice, KPI "
            "definition, report automation, live data connections, and building trust in what "
            "the numbers say. Mapped to the business intelligence and visualization strand of "
            "the UST data science curriculum."
        ),
        "curriculum_alignment": f"{UST} -- Business Intelligence; Information Presentation and Visualization",
        "prerequisites": "Data Management Essentials, or equivalent. Data Warehousing Fundamentals helps.",
        "learning_outcomes": (
            "Choose a BI tool that fits the organisation rather than the demo\n"
            "Encode quantitative information in the visual channels people read most accurately\n"
            "Define KPIs that drive decisions rather than describe activity\n"
            "Automate recurring reporting and connect live data sources\n"
            "Build dashboards stakeholders trust and use"
        ),
    },
}


# ===========================================================================
# Gap-filling lessons, keyed by course slug
# ===========================================================================
NEW_LESSONS = {
    # -- Descriptive Statistics gaps from CMO 42 Annex B -------------------
    "basic-statistics": [
        L(
            "Levels of Measurement and Why They Decide Everything",
            """## Overview

Before any statistic is computed, one question settles which statistics are even legal: what kind of scale is this variable measured on? Getting this wrong invalidates everything downstream, and it is the first topic CMO 42 lists under Descriptive Statistics.

## Key Concepts

- **Nominal** scales name categories with no order. Civil status, region, blood type. Only counts, modes and proportions are meaningful.
- **Ordinal** scales have order but unequal or unknown spacing. Rankings, Likert responses, disease severity stages. Medians and percentiles are meaningful; means are questionable.
- **Interval** scales have equal spacing but an arbitrary zero. Temperature in Celsius, calendar years. Differences are meaningful; ratios are not -- 40 degrees is not twice as hot as 20.
- **Ratio** scales have equal spacing and a true zero. Height, income, counts, time elapsed. Every arithmetic operation is meaningful.
- **The scale constrains the statistic, not the software.** Any package will happily compute a mean of civil status codes. The result is arithmetic on labels.

## Worked Example

A researcher codes region as 1 for Luzon, 2 for Visayas, 3 for Mindanao and reports a mean of 1.8. The number is arithmetically correct and substantively meaningless -- there is no sense in which the average respondent is four-fifths of the way from Luzon to Visayas. The appropriate summary is the frequency of each region and the mode. The same error appears more subtly with Likert items: averaging a single five-point agreement item treats the gap between "neutral" and "agree" as identical to the gap between "agree" and "strongly agree", which the scale never promised.

## Common Mistakes & Pro Tips

- Numeric codes are not numeric data. Record the measurement level in your codebook alongside the variable name.
- Summated Likert scales built from many items are conventionally treated as interval, and that convention is defensible. A single item is not.
- When you are unsure, the safe move is to treat the scale as one level lower and use the more conservative statistic.""",
            [{"question": "Temperature in Celsius is measured on which scale?",
              "choices": ["Nominal", "Ordinal", "Interval", "Ratio"], "correct": 2}],
        ),
        L(
            "Skewness, Kurtosis and the Shape of a Distribution",
            """## Overview

Central tendency and spread describe where data sits and how widely. Shape describes whether it is lopsided and how heavy its tails are -- and shape is what decides whether the mean is a sensible summary at all.

## Key Concepts

- **Skewness** measures asymmetry. Positive or right skew has a long right tail: most values are low and a few are very high. Income is the canonical example.
- **The mean chases the tail.** In a right-skewed distribution the mean sits above the median. That gap is itself a useful diagnostic.
- **Kurtosis** describes tail weight relative to a normal distribution. High kurtosis means more extreme values than normal, which matters because extreme values dominate variance.
- **Excess kurtosis** is reported by most software: it subtracts 3 so that a normal distribution scores zero. Check which your package reports before interpreting.
- **Rules of thumb exist but are soft.** Absolute skewness under 1 and excess kurtosis under 2 is a common working guide, not a theorem.

![Diagram: Comparing spread and shape](/static/diagrams/spread-comparison.svg)

## Worked Example

Monthly household income in a barangay has a mean of ₱28,000 and a median of ₱17,500. The mean sits 60% above the median, which is a strong signal of right skew driven by a small number of high earners. Reporting the mean alone would badly misrepresent the typical household. The honest summary leads with the median, reports the interquartile range for spread, and mentions the mean only with the skew noted -- exactly the "guard against misuses of statistics" outcome CMO 42 lists for this course.

## Common Mistakes & Pro Tips

- A large mean-median gap is the fastest skewness check available, and it needs no software.
- Skewness and kurtosis statistics are themselves unstable in small samples. With under 50 observations, trust the histogram over the coefficient.
- High kurtosis is usually a small number of extreme values. Find them and decide whether they are errors or genuine before transforming anything.""",
            [{"question": "In a right-skewed distribution, the mean typically sits:",
              "choices": ["Below the median", "Above the median", "Exactly at the median", "At the mode"],
              "correct": 1}],
        ),
        L(
            "Exploratory Data Analysis: Boxplots and Stem-and-Leaf",
            """## Overview

Before testing anything, look. Exploratory data analysis is a discipline of displays designed to reveal structure, outliers and errors that summary statistics hide. CMO 42 devotes two weeks of Descriptive Statistics to it.

## Key Concepts

- **The five-number summary** -- minimum, first quartile, median, third quartile, maximum -- describes a distribution without assuming any shape.
- **A boxplot draws it.** The box spans the interquartile range, the line inside is the median, and whiskers extend to the most extreme points within 1.5 times the IQR.
- **Points beyond the whiskers are flagged as outliers** by that convention. Flagged is not the same as wrong, and the 1.5 rule is a convention, not a test.
- **Side-by-side boxplots** are the single most informative display for comparing groups, showing centre, spread, skew and outliers at once.
- **Stem-and-leaf displays** keep the actual digits while showing shape, so you can read individual values off a distribution. They are ideal for small datasets and for spotting digit-preference errors.

## Worked Example

Side-by-side boxplots of test scores across four sections reveal that one section has a much larger box than the others. The medians are similar, so a comparison of means would find nothing. The spread difference is the finding: that section contains both the highest and lowest scorers, suggesting the class is not being taught at a level that fits everyone. A stem-and-leaf display of the same section then shows scores clustering at 60 and 75 with a gap between -- two groups, not one, which no summary statistic would have revealed.

## Common Mistakes & Pro Tips

- Never delete a point because a boxplot flagged it. Investigate whether it is a recording error, a different population, or a genuine extreme value.
- Boxplots hide multimodality. A bimodal distribution can produce an entirely ordinary-looking box. Pair them with a histogram.
- Digit preference -- values clustering on multiples of 5 or 10 -- shows up immediately in stem-and-leaf and is strong evidence of estimated rather than measured data.""",
            [{"question": "In a standard boxplot, whiskers extend to the most extreme points within:",
              "choices": ["One standard deviation", "1.5 times the interquartile range",
                          "The 5th and 95th percentiles", "Two standard deviations"],
              "correct": 1}],
        ),
        L(
            "Rates, Ratios, Index Numbers and Official Statistics",
            """## Overview

Much of the statistics a Filipino researcher actually consumes is not raw data but constructed indicators: inflation rates, poverty incidence, employment rates, price indices. CMO 42 devotes the closing weeks of Descriptive Statistics to how these are built and how to read them.

## Key Concepts

- **A ratio** compares two quantities by division. **A proportion** is a ratio where the numerator is part of the denominator. **A rate** is a proportion over a defined time period or population base.
- **The denominator carries the meaning.** "50 cases" is uninterpretable; "50 cases per 100,000 population per year" is comparable across places and times.
- **Crude versus specific rates.** A crude death rate mixes all ages together, so a region with more elderly residents looks unhealthier. Age-specific or age-standardised rates remove that.
- **Index numbers** track change relative to a base period set to 100. The Consumer Price Index is the familiar example; the base year matters and is periodically rebased.
- **Official statistics** in the Philippines come mainly from the Philippine Statistics Authority, with NEDA and the Bangko Sentral publishing derived indicators. Each carries a defined methodology you can and should cite.

## Worked Example

A student compares dengue "cases" across two provinces and concludes the larger province has a worse outbreak. It has four times the population. Converting to incidence per 100,000 reverses the ranking. A second correction may be needed: if one province has a much younger population and dengue incidence is age-related, even the crude incidence rate misleads, and an age-standardised rate is the defensible comparison.

## Common Mistakes & Pro Tips

- Always state the denominator and the period with any rate. A rate without them is a count wearing a disguise.
- Index numbers cannot be averaged across different base years. Rebase to a common year first.
- Cite the PSA methodology note for any official indicator you use. Definitions of "unemployed" and "poor" are technical and have changed over time.""",
            [{"question": "Comparing disease counts between provinces of different sizes requires converting to:",
              "choices": ["A ratio of totals", "A rate with a defined population denominator",
                          "An index number", "A proportion of the national total"],
              "correct": 1}],
        ),
    ],

    # -- Regression Analysis gaps from CMO 42 Annex B ----------------------
    "intermediate-statistics": [
        L(
            "Regression Diagnostics: Outliers, Non-Normality and Heteroskedasticity",
            """## Overview

Fitting a regression is the easy part. CMO 42 allocates roughly half of Regression Analysis to what comes after: detecting when the classical assumptions fail, and what to do about it.

## Key Concepts

- **Outliers, leverage and influence are three different things.** An outlier has a large residual. A high-leverage point has unusual predictor values. An influential point changes the fitted model when removed -- and only that third one is necessarily a problem.
- **Cook's distance** measures influence directly, combining residual size and leverage. It is the statistic to report when a panel asks about extreme cases.
- **Non-normal residuals** matter mainly for small samples and for prediction intervals. Coefficient estimates stay unbiased; their inference is what suffers.
- **Heteroskedasticity** means residual variance changes with the fitted value -- the classic funnel shape in a residual plot. Coefficients stay unbiased, standard errors do not.
- **Remedial measures** in order of preference: transform the outcome, use robust standard errors, or fit weighted least squares. Deleting inconvenient points is not on the list.

## Worked Example

A regression of household spending on income shows a clear funnel in the residual plot: low-income households cluster tightly around the line, high-income households scatter widely. The coefficient on income is unbiased, but its standard error is wrong, so the confidence interval and p-value cannot be trusted. Taking logs of both variables often stabilises this and changes the interpretation to an elasticity, which is frequently what the researcher wanted anyway. If the log form does not fit the theory, heteroskedasticity-consistent standard errors fix the inference while leaving the model alone.

## Common Mistakes & Pro Tips

- Plot residuals against fitted values for every regression you fit. It is one line of code and it catches more problems than any test.
- Normality tests on residuals are close to useless in large samples, where they reject trivial departures. Use a Q-Q plot.
- Report that you checked assumptions and what you found. "Assumptions were met" with no evidence is the answer panels probe hardest.""",
            [{"question": "Heteroskedasticity primarily biases:",
              "choices": ["The coefficient estimates", "The standard errors and therefore the p-values",
                          "The R-squared", "The sample size"], "correct": 1}],
        ),
        L(
            "Multicollinearity, Ridge Regression and Shrinkage",
            """## Overview

When predictors carry overlapping information, the model cannot tell their effects apart. The fit stays fine; the individual coefficients become unstable and uninterpretable. CMO 42 gives this three weeks of Regression Analysis.

## Key Concepts

- **Multicollinearity is about predictors, not the outcome.** It arises when predictors are strongly correlated with each other.
- **The symptom is instability.** Coefficients swing wildly when a variable is added or a few cases are dropped, standard errors balloon, and signs flip against theory -- all while R-squared stays high.
- **The variance inflation factor (VIF)** quantifies it. A VIF of 10 means that coefficient's variance is ten times what it would be with uncorrelated predictors. Above 5 warrants attention; above 10 is usually treated as serious.
- **Principal component regression** replaces correlated predictors with uncorrelated components, solving the instability at the cost of interpretability.
- **Ridge regression and other shrinkage estimators** deliberately accept a little bias in exchange for a large reduction in variance, which often produces better predictions.

## Worked Example

A model predicts academic performance from study hours per week, study hours per day, and total study hours per semester. All three measure the same thing. VIFs exceed 30, two coefficients come out negative against all theory, and the overall F test is strongly significant. The model predicts well and explains nothing. The fix is substantive, not statistical: choose the one measure that matches the research question and drop the rest. Ridge regression would stabilise the estimates but would not make three measures of one construct meaningful.

## Common Mistakes & Pro Tips

- Multicollinearity does not hurt prediction. If the model is purely predictive, high VIFs may be acceptable. If you intend to interpret coefficients, they are not.
- Check VIFs before interpreting any multiple regression. A sign that contradicts theory is a prompt to check collinearity, not to rewrite the theory.
- Centring predictors removes the artificial collinearity that interaction terms create, but does nothing for genuine collinearity between the underlying variables.""",
            [{"question": "A variance inflation factor of 10 for a predictor indicates:",
              "choices": ["The predictor explains 10% of variance", "That coefficient's variance is 10 times larger than with uncorrelated predictors",
                          "Ten outliers are present", "The model needs 10 more observations"], "correct": 1}],
        ),
        L(
            "Dummy Variables, Interaction and Comparing Models Across Groups",
            """## Overview

Regression needs numbers, but much of what matters is categorical. Dummy variables bring categories into the linear model, and interaction terms let the model's slope differ across them.

## Key Concepts

- **A dummy variable is coded 0 or 1** for the absence or presence of a category. With k categories you create k-1 dummies; the omitted one becomes the reference.
- **Every coefficient is read against the reference.** Change the reference category and the coefficients change, though the model's fit does not. Always state which category was omitted.
- **The dummy variable trap** is including all k dummies plus an intercept, which makes the model unsolvable because the dummies sum to the intercept.
- **Interaction between a dummy and a continuous predictor** lets the slope differ by group. This is how you test whether a relationship holds equally for everyone.
- **Testing for parallelism** -- whether slopes differ across groups -- is exactly the interaction test, and CMO 42 lists it explicitly.

## Worked Example

A model predicts salary from years of experience, with a dummy for sector. The dummy's coefficient shifts the intercept: one sector starts higher. Adding an experience-by-sector interaction tests something different -- whether each additional year of experience is rewarded equally in both sectors. If the interaction is significant, the two sectors have different slopes, and reporting a single "effect of experience" is wrong. The defensible report gives the simple slope within each sector.

## Common Mistakes & Pro Tips

- Always name the reference category in your write-up. "The coefficient for public sector was 4,200" is uninterpretable without it.
- Never interpret a main effect on its own once its interaction term is in the model and significant. The main effect is now the effect at the reference level only.
- Centre continuous predictors before creating interaction terms. It removes artificial collinearity and makes the main effects interpretable at a meaningful value.""",
            [{"question": "With 4 categories, how many dummy variables should a model with an intercept include?",
              "choices": ["4", "3", "2", "5"], "correct": 1}],
        ),
    ],

    # -- Survey Sampling and Survey Operations, from CMO 42 Annex B --------
    "research-methodology-foundations": [
        L(
            "Sampling Designs: From Simple Random to Multistage",
            """## Overview

CMO 42 devotes a full 3-unit course to survey sampling. The design you choose determines what your estimates mean and how their standard errors must be computed -- and most thesis work gets the second part wrong.

## Key Concepts

- **Probability sampling** gives every unit a known, non-zero chance of selection. Only probability designs support statistical inference to the population.
- **Simple random sampling** gives every unit an equal chance. It is the reference against which other designs are measured, and it requires a complete sampling frame you usually do not have.
- **Systematic sampling** takes every kth unit after a random start. Simple in the field, but dangerous if the frame has a periodic pattern matching k.
- **Stratified sampling** divides the population into homogeneous strata and samples within each. It improves precision and guarantees representation of small groups.
- **Cluster and multistage sampling** select groups rather than individuals -- barangays, then households, then respondents. Cheaper in the field, but less precise per unit because members of a cluster resemble each other.
- **Probability proportional to size** gives larger clusters a greater chance of selection, which keeps the design self-weighting when combined with a fixed take per cluster.

## Worked Example

A study samples 30 barangays and then 20 households within each, giving 600 households. Analysing these as 600 independent observations understates the standard errors, often severely, because households within a barangay resemble one another. The design effect quantifies how much: with an intracluster correlation of 0.05 and 20 per cluster, the effective sample size is closer to 300 than 600. Reporting a confidence interval computed as though the sample were simple random makes it roughly 40% too narrow.

## Common Mistakes & Pro Tips

- Convenience and purposive samples are non-probability designs. They can be appropriate for qualitative or exploratory work, but they do not support inference to a population, and no sample size formula rescues them.
- Compute and report the design effect for any clustered design. Panels increasingly ask for it.
- Stratify on variables related to the outcome. Stratifying on something unrelated costs complexity and buys nothing.""",
            [{"question": "Analysing a clustered sample as if it were simple random typically makes confidence intervals:",
              "choices": ["Too wide", "Too narrow", "Correctly sized", "Impossible to compute"],
              "correct": 1}],
        ),
        L(
            "Survey Operations: From Questionnaire to Clean Data",
            """## Overview

CMO 42 gives survey operations its own 3-unit course, covering everything between having a sampling design and having analysable data. This is where most thesis data quality is won or lost.

## Key Concepts

- **Non-sampling error usually exceeds sampling error.** Sampling error shrinks with sample size; non-response, measurement error and processing error do not.
- **Questionnaire design is measurement.** Double-barrelled questions, leading wording, and response options that do not exhaust the possibilities all produce data that cannot be repaired afterwards.
- **Pre-testing is not optional.** A pilot on 20 to 30 respondents from the target population catches ambiguity, ordering effects and timing problems while they are still cheap to fix.
- **Field operations** -- enumerator training, supervision, call-back rules for non-contacts -- determine whether the realised sample resembles the designed one.
- **Coding, encoding and quality control** convert responses to analysable values. Double entry, range checks and consistency checks catch errors that silently distort every later result.
- **Document the response rate and the reasons for non-response.** A 40% response rate is not fatal if you can characterise who is missing; it is fatal if you cannot.

## Worked Example

A questionnaire asks "Are you satisfied with the speed and quality of service?" A respondent who found service fast but poor cannot answer truthfully. This is a double-barrelled item, and no analysis can separate the two constructs afterwards because the data never contained them separately. Splitting it into two items costs one line in the instrument and saves the construct. Pre-testing would have surfaced it; the item survived because no one ran a pilot.

## Common Mistakes & Pro Tips

- Report the response rate, how non-response was handled, and any comparison between respondents and non-respondents. Panels ask about this routinely.
- Build range and consistency checks into the encoding stage rather than the analysis stage. An age of 150 is cheaper to fix at entry than to explain at defence.
- Keep the raw data file untouched and do all cleaning in a script. An undocumented manual edit is unreproducible, and reproducibility is what integrity of data means in practice.""",
            [{"question": "\"Are you satisfied with the speed and quality of service?\" is flawed because it is:",
              "choices": ["Too long", "Double-barrelled, asking about two things at once",
                          "Leading", "Open-ended"], "correct": 1}],
        ),
    ],

    # -- Categorical Data Analysis and Bayesian Statistics, from CMO 42 ----
    "advanced-statistics": [
        L(
            "Categorical Data Analysis: Loglinear and Logit Models",
            """## Overview

Chi-square tells you two categorical variables are associated. It cannot handle three variables, control for anything, or quantify the association's size. Loglinear and logit models can.

## Key Concepts

- **Cross-classification tables** extend beyond two dimensions. With three or more variables, chi-square runs out of room and modelling becomes necessary.
- **Loglinear models** treat the cell counts as the outcome and model their logarithm as a function of the variables and their interactions. No variable is singled out as dependent.
- **Interaction terms are the associations.** A model with all main effects and no interactions is the independence model; adding a two-way interaction says those two variables are associated.
- **Logit models** single out one binary variable as the outcome and model the log odds. When the predictors are all categorical, a logit model is a loglinear model rearranged.
- **Odds ratios are the effect size.** An odds ratio of 1 means no association; the further from 1, the stronger. They are the standard currency in epidemiology and health research.

![Diagram: Reading a contingency table](/static/diagrams/contingency-table.svg)

## Worked Example

A study cross-classifies smoking status, sex and respiratory symptoms. A chi-square on smoking by symptoms finds an association. But men in this sample both smoke more and report more symptoms, so sex could produce the association on its own. A loglinear model including all three variables lets you test whether the smoking-symptom interaction survives once the sex associations are in the model. If it does, the association is not explained by sex. This is Simpson's paradox territory -- and a two-way chi-square cannot detect it.

## Common Mistakes & Pro Tips

- Report odds ratios with confidence intervals, not just p-values. An odds ratio of 1.05 can be highly significant in a large sample and clinically irrelevant.
- Odds ratios are not risk ratios. For common outcomes they diverge substantially, and reporting one as the other overstates the effect.
- Use hierarchical model selection: never include an interaction without the main effects it is built from.""",
            [{"question": "An advantage of loglinear models over a two-way chi-square test is that they:",
              "choices": ["Require smaller samples", "Handle three or more variables and control for their associations",
                          "Do not need expected counts", "Work on continuous outcomes"], "correct": 1}],
        ),
        L(
            "Bayesian Inference: Priors, Posteriors and Hierarchical Models",
            """## Overview

The Bayesian framework answers the question researchers actually ask -- what should I believe about this parameter given my data -- rather than the frequentist question about long-run behaviour of procedures. CMO 42 makes it a required core course.

## Key Concepts

- **The parameter is treated as random.** This is the fundamental break from the frequentist framework, where the parameter is a fixed unknown constant.
- **Prior, likelihood, posterior.** The prior encodes belief before seeing the data, the likelihood carries what the data say, and Bayes' theorem combines them into the posterior.
- **Specifying priors is the contested part.** Informative priors encode real prior knowledge; weakly informative priors constrain to plausible ranges; flat priors attempt neutrality and are not always as neutral as they look.
- **Credible intervals mean what people wrongly think confidence intervals mean.** A 95% credible interval genuinely has a 95% posterior probability of containing the parameter.
- **Hierarchical models** let parameters vary across groups while borrowing strength between them -- the natural framework for multi-site, multi-school or multi-region studies.
- **Empirical Bayes** estimates the prior from the data itself, a pragmatic middle path CMO 42 lists explicitly.

![Diagram: How a prior updates to a posterior](/static/diagrams/bayesian-updating.svg)

## Worked Example

A small pilot with 18 patients estimates a treatment effect with a very wide frequentist confidence interval, and the study is dismissed as uninformative. A Bayesian analysis with a weakly informative prior centred on no effect and ruling out implausibly large effects yields a posterior that is still wide but genuinely interpretable: the probability the effect exceeds a clinically meaningful threshold can be stated directly. The prior must be pre-registered and its influence shown through sensitivity analysis -- otherwise the objection that the conclusion was chosen in advance is fair.

## Common Mistakes & Pro Tips

- Always report a sensitivity analysis across several reasonable priors. If the conclusion changes, the data are not driving it and you should say so.
- A flat prior is a choice, not an absence of one, and on a transformed scale it can be strongly informative.
- Do not switch to Bayesian analysis because a frequentist test failed to reach significance. Choose the framework for the question, and say so before you see the result.""",
            [{"question": "A 95% Bayesian credible interval means:",
              "choices": ["95% of repeated intervals would contain the parameter",
                          "There is a 95% posterior probability the parameter lies within it",
                          "95% of the data fall inside it", "The prior was 95% accurate"], "correct": 1}],
        ),
    ],

    # -- Ethics and data integrity, CMO 42 core competency E ---------------
    "applied-statistics-for-research": [
        L(
            "Data Integrity and the Ethics of Statistical Practice",
            """## Overview

CMO 42 lists "Ethics and integrity" as one of five core competencies a statistics graduate must have, and program outcome (o) is simply "commit to the integrity of data." This lesson is about what that means when a deadline is close and the result is not cooperating.

## Key Concepts

- **p-hacking** is trying analyses until one reaches significance. Dropping outliers, adding covariates, splitting subgroups, switching tests -- each defensible alone, and collectively a machine for manufacturing false positives.
- **HARKing** is hypothesising after results are known: presenting an exploratory finding as though it had been predicted. It converts a hypothesis-generating result into a fake confirmation.
- **Selective reporting** omits analyses that did not work. The published estimate is then conditioned on having been significant, which biases it upward.
- **Pre-registration** is the strongest available protection: state the hypotheses, the primary outcome and the analysis plan before collecting data.
- **Exploratory analysis is legitimate and necessary** -- provided it is labelled as exploratory rather than dressed as confirmatory.
- **Reproducibility is the operational test.** If someone with your data and your script cannot reproduce your table, the result is not yet a result.

## Worked Example

A researcher's main analysis returns p = 0.08. They then remove three influential cases, add a control variable, and report p = 0.04 with no mention of the original analysis. Each step has a technical justification. The combination means the reported p-value no longer describes the procedure that generated it -- the real error rate is far above 5%. The defensible route is to report the pre-specified analysis as the primary result, report the alternative specifications as sensitivity analyses, and let the reader see that the finding is fragile. That is a weaker-sounding paper and a more honest one.

## Common Mistakes & Pro Tips

- Write the analysis plan before data collection ends, and keep the dated file. It is the cleanest possible answer to a panel asking whether the analysis was decided in advance.
- Report every analysis you ran on the primary question, not only the one that worked.
- "The data were cleaned" is not a method. Document every exclusion with its rule and its count, and report the sample size at each stage.""",
            [{"question": "Presenting an exploratory finding as if it had been predicted in advance is called:",
              "choices": ["p-hacking", "HARKing", "Pre-registration", "Sensitivity analysis"], "correct": 1}],
        ),
    ],

    # -- UST BSDSA strands -------------------------------------------------
    "data-management-essentials": [
        L(
            "Information Security and Data Privacy",
            """## Overview

Research data about people is regulated in the Philippines. The Data Privacy Act of 2012 (RA 10173) applies to thesis datasets, clinic records and survey responses alike, and compliance is a design decision, not a formality at the end.

## Key Concepts

- **Personal information** identifies an individual. **Sensitive personal information** covers health, education, genetic, sexual life, offences, and government-issued identifiers, and carries stricter conditions for processing.
- **Consent must be informed, specific and freely given**, and evidenced. A general consent to "research" does not cover later reuse for a different purpose.
- **Data minimisation.** Collect only what the research question needs. Every unnecessary identifier is a liability with no analytical return.
- **De-identification is a spectrum.** Removing names is not anonymisation: a combination of barangay, age, occupation and sex frequently identifies one person.
- **The three security dimensions** the law requires are organisational, physical and technical -- policies, locked storage, and encryption plus access control respectively.
- **Breach notification** is time-bound. The National Privacy Commission and affected individuals must be notified within 72 hours of knowledge of a qualifying breach.

## Worked Example

A student stores a survey dataset on a shared drive with respondent names, exact birthdates and barangay. The analysis needs age in years and municipality only. Under data minimisation the identifiers should never have been retained past the point of linkage. The correct design generates a random respondent ID at encoding, keeps the linking file encrypted and separate with restricted access, and does the analysis on the de-identified extract. This costs an hour at setup and removes the most common source of privacy exposure in thesis work.

## Common Mistakes & Pro Tips

- Ethics clearance and privacy compliance are different requirements. Approval from a research ethics board does not exempt you from RA 10173.
- Write a retention and disposal plan. Holding identifiable data indefinitely "in case it is useful" is the situation the law is designed to prevent.
- Keep identifiers in a separate encrypted file from the analysis dataset, and never put both in the same cloud folder.""",
            [{"question": "Under RA 10173, health information is classified as:",
              "choices": ["Public information", "Sensitive personal information",
                          "Anonymous data", "Non-personal data"], "correct": 1}],
        ),
    ],
    "data-warehousing-fundamentals": [
        L(
            "Principles of Big Data",
            """## Overview

"Big data" is used loosely enough to be almost meaningless. The useful version is specific: a workload is big when it no longer fits the architecture you have, and the right response depends on which dimension broke.

## Key Concepts

- **Volume, velocity and variety** are the classic three dimensions. Volume is size, velocity is the rate of arrival, variety is structural heterogeneity. Veracity -- data quality at scale -- is often added and is usually the hardest.
- **Scale up versus scale out.** Scaling up buys a bigger machine and is simpler. Scaling out distributes across many machines and is what "big data" architecture usually means.
- **Distributed processing splits the work.** The map-reduce pattern partitions data across nodes, computes locally, then combines -- the model underneath Hadoop and, in a more modern form, Spark.
- **Storage and compute are now separate.** Cloud warehouses keep data in object storage and spin compute up on demand, which is why costs scale with queries rather than with data held.
- **Most organisations do not have big data.** A dataset that fits in memory on a laptop is not big, and reaching for distributed infrastructure to process it adds cost, latency and failure modes for no benefit.

![Diagram: A typical ETL pipeline](/static/diagrams/etl-pipeline.svg)

## Worked Example

An organisation with 40 million transaction rows per year proposes a Hadoop cluster. Forty million rows is roughly a few gigabytes -- comfortably handled by a single Postgres instance with appropriate indexing, or by a columnar warehouse at trivial cost. The genuine constraint turns out to be that a monthly report takes six hours, which is an indexing and query-design problem, not a volume problem. Diagnosing which dimension is actually binding is the whole skill; the architecture follows from it.

## Common Mistakes & Pro Tips

- Measure before architecting. Profile the slow query and the actual data size before concluding you need distributed infrastructure.
- Variety is usually the real problem in Philippine organisations: the same entity spelled six ways across four systems. No amount of compute fixes that; conformed dimensions do.
- Distributed systems trade consistency for availability and partition tolerance. Understand which trade your chosen tool made before it surprises you in production.""",
            [{"question": "The most common reason an organisation does NOT need distributed big-data infrastructure is that:",
              "choices": ["Their data arrives too fast", "Their data comfortably fits on a single machine",
                          "They have too many data sources", "Their data is unstructured"], "correct": 1}],
        ),
    ],
    "business-intelligence-dashboards": [
        L(
            "Information Presentation and Visualization",
            """## Overview

A dashboard is an argument made in pictures. The research on how people read visual encodings tells you which pictures make the argument accurately, and which ones quietly mislead.

## Key Concepts

- **Visual channels differ in accuracy.** People judge position along a common scale most accurately, then length, then angle, then area, then colour saturation. Encode your most important quantity in the most accurate channel available.
- **This is why pie charts underperform.** They encode with angle and area, the two weakest channels, which is why comparing adjacent slices is difficult. A bar chart uses length and wins.
- **Bar charts must start at zero.** Length is the encoding, so truncating the axis distorts the ratio the reader perceives. Line charts, which encode change by slope, do not carry the same obligation.
- **Colour has jobs.** Sequential palettes for ordered magnitudes, diverging for values around a meaningful midpoint, categorical for unordered groups. Never use a rainbow palette for ordered data -- it creates boundaries that are not in the data.
- **Accessibility is a requirement.** Around 8% of men have some colour vision deficiency, so colour must never be the only channel carrying meaning.
- **The data-ink ratio.** Every gridline, border and shadow competes with the data. Remove anything that does not help the reader.

![Diagram: A dashboard layout](/static/diagrams/dashboard-mockup.svg)

## Worked Example

A regional sales dashboard shows seventeen regions as a pie chart. Readers cannot rank the middle regions, cannot see which are growing, and cannot read the labels. Replacing it with a horizontal bar chart sorted by value makes the ranking immediate, gives labels room to breathe, and frees a colour channel to encode growth direction. The same data, the same space, and a chart that answers the question the viewer actually has.

## Common Mistakes & Pro Tips

- Sort bars by value unless the categories have a natural order such as time. Alphabetical ordering hides the pattern.
- Dual axes invite false conclusions because the apparent crossing point depends entirely on arbitrary scaling. Use two aligned panels instead.
- Label directly on the chart where you can. A legend forces the reader to look away and back for every series.""",
            [{"question": "People judge quantitative differences most accurately when values are encoded as:",
              "choices": ["Colour saturation", "Position along a common scale", "Area", "Angle"],
              "correct": 1}],
        ),
    ],
}


def apply_metadata(db):
    for slug, meta in METADATA.items():
        course = db.query(models.Course).filter(models.Course.slug == slug).first()
        if course is None:
            print(f"[skip] no course with slug {slug!r} -- run seed_courses.py first")
            continue
        course.description = meta["description"]
        course.curriculum_alignment = meta["curriculum_alignment"]
        course.prerequisites = meta["prerequisites"]
        course.learning_outcomes = meta["learning_outcomes"]
        print(f"[metadata] {course.title}")
    db.commit()


def add_lessons(db):
    for slug, lessons in NEW_LESSONS.items():
        course = db.query(models.Course).filter(models.Course.slug == slug).first()
        if course is None:
            print(f"[skip] no course with slug {slug!r}")
            continue

        # New lessons go after the existing substantive ones. "Further Reading"
        # is pulled to the very end afterwards so it always closes the course.
        next_order = max((l.order for l in course.lessons), default=-1) + 1
        added = updated = 0

        for spec in lessons:
            lesson = (
                db.query(models.Lesson)
                .filter(models.Lesson.course_id == course.id, models.Lesson.title == spec["title"])
                .first()
            )
            if lesson is None:
                lesson = models.Lesson(course_id=course.id, title=spec["title"], order=next_order)
                db.add(lesson)
                next_order += 1
                added += 1
            else:
                updated += 1
            lesson.content = spec["content"]
            lesson.quiz_json = json.dumps(spec["quiz"]) if spec["quiz"] else ""

        db.flush()
        for lesson in course.lessons:
            if lesson.title.startswith("Further Reading"):
                lesson.order = 999
        db.commit()
        print(f"[lessons] {course.title} -- {added} added, {updated} updated")


def renumber(db):
    """Close any gaps left by reordering so lesson numbering reads 01, 02, 03..."""
    for course in db.query(models.Course).all():
        for index, lesson in enumerate(sorted(course.lessons, key=lambda l: (l.order, l.id))):
            lesson.order = index
    db.commit()


def main():
    Base.metadata.create_all(bind=engine)
    sync_columns()
    db = SessionLocal()
    try:
        apply_metadata(db)
        print()
        add_lessons(db)
        renumber(db)
    finally:
        db.close()
    total = sum(len(v) for v in NEW_LESSONS.values())
    print(f"\nDone. {len(METADATA)} course(s) updated, {total} deepening lesson(s) processed.")


if __name__ == "__main__":
    main()
