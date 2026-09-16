"""
Adds the four CHED core statistics areas the catalog did not cover.

Grounded in CHED Memorandum Order No. 42, series of 2017 -- "Policies,
Standards, and Guidelines for the Bachelor of Science in Statistics (BS Stat)
Program" -- Annex B, Course Specifications. The official course descriptions,
prerequisites and topic sequences there are the basis for each course below;
the lesson text is written from scratch for self-paced learners, not copied.

Reference: https://legacy.ched.gov.ph/wp-content/uploads/2017/10/CMO-42-s-2017.pdf

Covered here (CMO 42 Table 4, statistics core, 39 units):
  - Mathematical Statistics 1, 2 and 3   -> Probability & Mathematical Statistics
  - Nonparametric Statistics             -> Nonparametric Statistics
  - Experimental Designs                 -> Design & Analysis of Experiments
  - Time Series Analysis                 -> Time Series Analysis & Forecasting

Safe to re-run. Courses are matched by slug and lessons by title, so an existing
lesson is updated in place rather than duplicated.

Usage:
    python3 seed_ched_core_courses.py
    DATABASE_URL="postgresql://..." python3 seed_ched_core_courses.py
"""
import json
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal, sync_columns
from app import models

CMO = "CHED CMO 42 s. 2017"


def L(title, content, quiz=None, preview=False):
    return {"title": title, "content": content, "quiz": quiz, "preview": preview}


# ---------------------------------------------------------------------------
# 1. Probability & Mathematical Statistics  (CMO 42: Mathematical Statistics 1-3)
# ---------------------------------------------------------------------------
PROBABILITY = {
    "title": "Probability & Mathematical Statistics",
    "slug": "probability-mathematical-statistics",
    "category": "Statistics",
    "level": "Advanced",
    "price_php": 4000,
    "description": (
        "The theory underneath every test you have ever run. Elements of probability, "
        "random variables and their distributions, mathematical expectation, joint and "
        "conditional distributions, where the t, chi-square and F distributions come from, "
        "the limit theorems, and the derivation of point estimators, interval estimators "
        "and tests of hypotheses. This is the course that turns statistical software output "
        "from a black box into something you can defend line by line."
    ),
    "curriculum_alignment": (
        f"{CMO} core -- Mathematical Statistics 1, 2 and 3 (9 units combined)"
    ),
    "prerequisites": (
        "Calculus I-III and Set Theory/Logic, per CMO 42\n"
        "Basic Statistics: A Practical Start, or equivalent introductory statistics"
    ),
    "learning_outcomes": (
        "Derive the properties of a probability function from the axiomatic definition of probability\n"
        "Distinguish discrete from continuous random variables and move between density and distribution functions\n"
        "Evaluate expectations, moments and moment generating functions\n"
        "Work with joint, marginal and conditional distributions, and establish independence\n"
        "Explain where Student's t, chi-square and Fisher's F distributions come from\n"
        "Derive point and interval estimators and examine their properties\n"
        "Construct tests of hypotheses and examine their properties"
    ),
    "lessons": [
        L(
            "Probability From the Axioms Up",
            """## Overview

Most people meet probability as a set of formulas to memorise. The formulas are consequences of three short axioms, and once you have seen the derivation you stop needing to memorise anything.

## Key Concepts

- **The sample space** is the set of every outcome an experiment can produce. An **event** is any subset of it. This is why set theory is a prerequisite -- unions, intersections and complements are the whole vocabulary.
- **Kolmogorov's three axioms**: probability is never negative; the probability of the whole sample space is 1; and for mutually exclusive events, the probability of their union is the sum of their probabilities.
- **Everything else is derived.** The complement rule, the addition rule for overlapping events, and the fact that an impossible event has probability zero are all theorems, not separate rules.
- **Conditional probability** is a definition, not an axiom: the probability of A given B is the probability of both divided by the probability of B, defined only when B has non-zero probability.
- **Independence** means the conditional probability equals the unconditional one -- knowing B happened tells you nothing about A.

![Diagram: The building blocks of probability](/static/diagrams/probability-basics.svg)

## Worked Example

A panel asks why you can add probabilities for "respondent is male" and "respondent is female" but not for "respondent is male" and "respondent smokes." The axiom answers it: the third axiom applies to mutually exclusive events. Male and female are mutually exclusive, so the probabilities add. Male and smoker overlap, so you need the general addition rule, which subtracts the intersection to stop double-counting the male smokers.

## Common Mistakes & Pro Tips

- Mutually exclusive and independent are not the same thing, and are in fact close to opposites. Two events with non-zero probability that are mutually exclusive cannot be independent -- if one happens, the other definitely did not.
- A probability of zero does not mean impossible once you are working with continuous variables. Any single exact value of a continuous random variable has probability zero.
- Write the sample space down explicitly for any problem you find confusing. Most probability errors are really set-definition errors.""",
            [{"question": "Two events are mutually exclusive and both have non-zero probability. What follows?",
              "choices": ["They must be independent", "They cannot be independent",
                          "Independence cannot be determined", "Their probabilities must be equal"],
              "correct": 1}],
            preview=True,
        ),
        L(
            "Random Variables and Distribution Functions",
            """## Overview

A random variable is not random and is not a variable. It is a function that assigns a number to every outcome in the sample space, and that reframing is what lets calculus be applied to chance.

## Key Concepts

- **A random variable maps outcomes to numbers.** "Number of defective units in a batch of 50" turns a messy physical experiment into an integer you can do arithmetic with.
- **Discrete random variables** take a countable set of values and are described by a **probability mass function**, which gives the probability of each exact value.
- **Continuous random variables** take values in an interval and are described by a **probability density function**. A density is not a probability -- it can exceed 1. Only the area under it over an interval is a probability.
- **The cumulative distribution function** works for both cases: the probability that the variable is less than or equal to some value. It is non-decreasing, runs from 0 to 1, and always exists.
- **You can move in both directions.** Differentiate the distribution function to get the density; integrate the density to get the distribution function. CMO 42 lists this explicitly as a course outcome.

## Worked Example

Waiting time at a clinic is modelled as exponential with density that decays over time. A student is asked for the probability that the wait is exactly 12 minutes and answers by plugging 12 into the density. That is wrong: for a continuous variable the probability of any exact value is zero. The right question is the probability of waiting between, say, 11 and 13 minutes, which is the area under the density over that interval -- or equivalently the difference of the distribution function evaluated at the two endpoints.

## Common Mistakes & Pro Tips

- Reporting a density value as if it were a probability is the single most common error in this topic. Densities are rates, not probabilities.
- Check that any candidate density is non-negative everywhere and integrates to exactly 1 over its support. If it does not, it is not a density.
- The distribution function is the safer tool in exams and in practice: it is always a probability, and every interval question reduces to a subtraction.""",
            [{"question": "For a continuous random variable, the probability of one exact value is:",
              "choices": ["Equal to the density at that value", "Zero",
                          "Always very small but positive", "Undefined"],
              "correct": 1}],
        ),
        L(
            "Expectation, Moments and Moment Generating Functions",
            """## Overview

Expectation is the centre of gravity of a distribution. Moments describe its shape. The moment generating function is a compact way of carrying all of them at once, and it is the tool that makes several later proofs short.

## Key Concepts

- **Expected value** is a probability-weighted average of the values a random variable can take. For a fair die it is 3.5 -- a value the die can never actually show, which is the point: expectation describes long-run behaviour, not any single trial.
- **Expectation is linear.** The expectation of a sum is the sum of the expectations, always, whether or not the variables are independent. This holds far more often than students expect and is worth leaning on.
- **Variance** is the expected squared deviation from the mean. It is the second central moment, and its square root is the standard deviation.
- **Higher moments** describe shape: the third relates to skewness, the fourth to kurtosis.
- **The moment generating function**, when it exists, produces every moment by repeated differentiation at zero. Two distributions with the same moment generating function are the same distribution -- which is how many derivations are closed.

## Worked Example

You need the variance of the sum of two correlated variables. Going back to the definition gives the familiar result: the variance of a sum is the sum of the variances plus twice the covariance. Note what this means in practice -- if two test items are positively correlated, the variance of the total score is larger than the sum of the item variances. Treating the items as independent would understate the spread of total scores, and any confidence interval built on it would be too narrow.

## Common Mistakes & Pro Tips

- Expectation of a sum is always the sum of expectations. Variance of a sum is only the sum of variances when the variables are uncorrelated. Mixing these up is the classic error.
- The expectation of a function is not the function of the expectation. This is Jensen's inequality territory, and it is why the mean of log-transformed data back-transforms to a median-like quantity, not the mean.
- Not every distribution has a moment generating function. The Cauchy distribution has no mean at all, let alone a moment generating function.""",
            [{"question": "The variance of the sum of two random variables equals the sum of their variances:",
              "choices": ["Always", "Only when they are uncorrelated",
                          "Only when both are normal", "Never"],
              "correct": 1}],
        ),
        L(
            "The Distributions You Will Actually Meet",
            """## Overview

CMO 42 calls these the "special parametric families of univariate distributions." In practice a small handful covers most applied work, and knowing which mechanism generates which distribution is more useful than memorising their formulas.

## Key Concepts

- **Bernoulli and binomial** count successes in a fixed number of independent trials with constant probability. Pass or fail, defective or not, responded or did not.
- **Poisson** counts events in a fixed interval when they occur independently at a constant average rate. Arrivals per hour, defects per square metre, typing errors per page.
- **Normal** arises whenever many small independent influences add together -- which is why it shows up in measurement error and in sampling distributions far more than in raw data.
- **Exponential and gamma** model waiting times. The exponential is memoryless: having waited ten minutes tells you nothing about how much longer you will wait.
- **Uniform** assigns equal density across an interval, and is the base from which simulation of other distributions is built.

![Diagram: The normal distribution and the empirical rule](/static/diagrams/normal-distribution.svg)

## Worked Example

A researcher counts the number of dengue cases reported per barangay per week and reaches for a normal model because the counts are "roughly bell-shaped." The generating mechanism says otherwise: these are counts of events in a fixed interval, so Poisson is the natural starting point. It matters. The normal model allows negative counts and forces the variance to be a free parameter, while the Poisson ties the variance to the mean -- a testable claim. If the observed variance far exceeds the mean, that overdispersion is itself a finding, pointing at clustering the Poisson assumes away.

## Common Mistakes & Pro Tips

- Choose the distribution from the mechanism that generated the data, not from the shape of the histogram. Shape is evidence; mechanism is reasoning.
- The normal distribution describes sampling distributions of means far more reliably than it describes raw measurements. Income, waiting times and counts are rarely normal.
- Check whether the memoryless property is plausible before using the exponential. Machine parts that wear out are not memoryless; radioactive decay is.""",
            [{"question": "Counts of independent events in a fixed interval at a constant rate are naturally modelled by:",
              "choices": ["The normal distribution", "The Poisson distribution",
                          "The uniform distribution", "The exponential distribution"],
              "correct": 1}],
        ),
        L(
            "Joint, Marginal and Conditional Distributions",
            """## Overview

Real research almost never involves one variable. The moment you have two, you need the machinery for describing how they vary together -- and for recovering one when you only care about one.

## Key Concepts

- **The joint distribution** gives the probability of combinations of values across two or more random variables at once.
- **Marginal distributions** are recovered by summing or integrating the joint distribution over the variables you are not interested in. You are collapsing a table down to one of its margins, which is where the name comes from.
- **Conditional distributions** fix one variable at a value and ask how the other is distributed given that. This is the formal version of "among respondents who finished college, what does income look like."
- **Stochastic independence** holds when the joint distribution factors into the product of the marginals. Equivalently, the conditional distribution does not depend on what you conditioned on.
- **Conditional expectation** -- the expected value of one variable given another -- is the foundation on which regression is built. A regression line is literally an estimate of a conditional mean.

## Worked Example

A two-way table cross-classifies 400 graduate students by programme and by whether they passed their statistics comprehensive on the first attempt. The marginal distribution of programme tells you how many students are in each programme. The conditional distribution of passing given programme tells you the pass rate within each programme. Only the second answers "does programme matter." Students routinely report the joint percentages -- the share of all 400 who are both in Programme A and passed -- and then interpret them as pass rates, which they are not.

## Common Mistakes & Pro Tips

- Be explicit about which denominator you used. Joint, marginal and conditional percentages from the same table are three different numbers and answer three different questions.
- Independence must hold for the whole joint distribution, not just at a couple of convenient cells.
- Conditional expectation is the bridge to everything that follows. When you fit a regression, you are modelling the conditional mean of the outcome given the predictors -- nothing more exotic than that.""",
            [{"question": "Recovering the distribution of one variable by summing the joint distribution over the other gives the:",
              "choices": ["Conditional distribution", "Marginal distribution",
                          "Joint distribution", "Sampling distribution"],
              "correct": 1}],
        ),
        L(
            "Where t, Chi-Square and F Come From",
            """## Overview

Three distributions do the heavy lifting in applied inference, and all three are constructed from normal random variables. Knowing the construction tells you exactly when each one is licensed.

## Key Concepts

- **Chi-square** is the distribution of a sum of squared independent standard normal variables. Its single parameter, degrees of freedom, is simply how many you added.
- **Student's t** is a standard normal divided by the square root of an independent chi-square over its degrees of freedom. It appears precisely because you had to estimate the standard deviation instead of knowing it, and its heavier tails are the price of that extra uncertainty.
- **Fisher's F** is a ratio of two independent chi-square variables, each divided by its degrees of freedom. Since variances are built from sums of squares, F is the natural distribution for comparing two variances -- which is what ANOVA does.
- **They are connected.** The square of a t variable is an F with one numerator degree of freedom, and as degrees of freedom grow, t approaches the standard normal.
- **The normality assumption enters here.** Every one of these constructions starts from normal variables, which is why the assumption matters even when your test statistic looks nothing like a normal.

## Worked Example

A student asks why a t-test with 200 participants gives virtually the same p-value as a z-test. The construction explains it: with large degrees of freedom the chi-square in the denominator concentrates tightly around 1, so the t statistic becomes a standard normal divided by roughly 1. The two tests converge. With 10 participants the denominator is genuinely variable, the tails are heavier, and the t critical value is noticeably larger than 1.96.

## Common Mistakes & Pro Tips

- Degrees of freedom are not an arbitrary bookkeeping number. They count how many independent squared normals went into the sum, which is why estimating a mean costs you one.
- These distributions are derived under normality. When the underlying data are badly non-normal and the sample is small, the derivation does not hold and the nominal error rate is wrong.
- If you can explain to a panel why the t distribution has fatter tails than the normal, you have understood the entire logic of small-sample inference.""",
            [{"question": "Student's t distribution has heavier tails than the standard normal because:",
              "choices": ["The sample mean is biased", "The standard deviation had to be estimated rather than known",
                          "The data are not normal", "It has more degrees of freedom"],
              "correct": 1}],
        ),
        L(
            "The Limit Theorems",
            """## Overview

Two theorems explain why statistics works at all: why larger samples give better estimates, and why the normal distribution keeps appearing in sampling distributions no matter what the population looks like.

## Key Concepts

- **The law of large numbers** says the sample mean converges to the population mean as the sample grows. It justifies estimation itself -- without it there is no reason to believe a sample average tells you anything about a population.
- **The central limit theorem** says the sampling distribution of the mean approaches normality as the sample grows, regardless of the population's shape, provided the variance is finite.
- **It is about the sampling distribution, not the data.** The theorem never claims your observations become normal. It claims the distribution of the mean across hypothetical repeated samples does.
- **"Large enough" depends on skewness.** For near-symmetric populations a sample of 15 may suffice. For heavily skewed ones, 30 is optimistic and several hundred may be needed.
- **Finite variance is required.** For distributions with infinite variance the theorem does not apply, and no sample size rescues it.

![Diagram: What a confidence interval actually represents](/static/diagrams/confidence-interval.svg)

## Worked Example

Household income in a municipality is strongly right-skewed. A reviewer objects that a t-test is invalid because the data are not normal. The central limit theorem is the answer, but only partly: the t-test assumes the sampling distribution of the mean is approximately normal, not the incomes. With 500 households and moderate skew that assumption is reasonable. With 12 households it is not, and the honest response is either a nonparametric test or a bootstrap -- not an appeal to the theorem.

## Common Mistakes & Pro Tips

- "n greater than 30 means normality" is a rule of thumb that has been promoted to a law. It is neither a theorem nor reliable for skewed data.
- The theorem says nothing about the normality of your raw observations, so testing your data for normality is answering the wrong question when the sample is large.
- Plot the data. Skewness and outliers tell you far more about whether the approximation is safe than any single normality test will.""",
            [{"question": "The central limit theorem describes the approximate normality of:",
              "choices": ["The raw observations", "The sampling distribution of the mean",
                          "The population", "The residuals"],
              "correct": 1}],
        ),
        L(
            "Point Estimation: Finding Estimators and Judging Them",
            """## Overview

An estimator is a recipe for turning a sample into a guess about a parameter. There are many possible recipes, and mathematical statistics gives you the criteria for deciding which are worth using.

## Key Concepts

- **The method of moments** sets sample moments equal to population moments and solves. It is simple and often a good starting value, but can produce estimates outside the parameter's legal range.
- **Maximum likelihood** chooses the parameter value that makes the observed data most probable. It is the workhorse behind logistic regression, survival models and structural equation modelling.
- **Unbiasedness** means the estimator is right on average across repeated samples. It is desirable but not decisive -- a biased estimator with much smaller variance is often the better choice.
- **Efficiency** compares variances among unbiased estimators. The smaller the variance, the more precisely you have pinned the parameter down.
- **Consistency** means the estimator converges to the truth as the sample grows. An estimator that is not consistent is hard to defend at any sample size.

![Diagram: Maximum likelihood finds the peak of the likelihood curve](/static/diagrams/mle-curve.svg)

## Worked Example

The sample variance divides by n minus 1 rather than n, and students are usually told this is "Bessel's correction" and left there. The reason is unbiasedness: dividing by n systematically underestimates the population variance, because deviations are taken from the sample mean, which sits closer to the data than the true mean does. Dividing by n minus 1 corrects exactly for that. Notice the trade-off in the other direction: the maximum likelihood estimator of the variance does divide by n, and is biased. Both are defensible; they optimise different criteria.

## Common Mistakes & Pro Tips

- Unbiased does not mean accurate for your particular sample. It is a statement about long-run average behaviour across samples you did not collect.
- Maximum likelihood estimates are generally biased in small samples but consistent, which is why they dominate in large-sample work and need care in small ones.
- When software offers a choice of estimator, find out which criterion it optimises before reporting the number.""",
            [{"question": "The sample variance divides by n-1 rather than n in order to be:",
              "choices": ["More efficient", "Unbiased for the population variance",
                          "Consistent", "The maximum likelihood estimate"],
              "correct": 1}],
        ),
        L(
            "Interval Estimation From First Principles",
            """## Overview

A point estimate without a measure of uncertainty is an opinion. Interval estimation is the machinery for attaching honest uncertainty, and the logic behind it is routinely mangled in thesis defences.

## Key Concepts

- **A confidence interval is built from a pivotal quantity** -- a function of the data and the parameter whose distribution does not depend on the parameter. The t statistic is the standard example.
- **The confidence level describes the procedure, not the interval.** Ninety-five percent of intervals constructed this way across repeated samples would contain the true parameter. Your particular interval either contains it or does not.
- **Width is driven by three things**: variability in the data, sample size, and the confidence level you chose. Only two of those are under your control.
- **Narrower is not automatically better.** An interval narrowed by dropping inconvenient observations is a worse interval, not a better one.
- **Interval and test are the same statement.** If a 95% interval excludes the null value, the corresponding two-sided test rejects at the 5% level.

## Worked Example

A defence panel asks a candidate what the 95% confidence interval [2.1, 4.7] means. The candidate answers, "there is a 95% probability the true mean is between 2.1 and 4.7." Under the frequentist framework that is wrong -- the true mean is a fixed constant, so it is either in the interval or it is not, and no probability attaches to it. The defensible phrasing is that the procedure produces intervals containing the true mean 95% of the time. If the candidate genuinely wants a probability statement about the parameter, the honest route is a Bayesian credible interval, which is a different object built on different assumptions.

## Common Mistakes & Pro Tips

- Never attach a probability to the parameter in a frequentist interval. This is the single most common phrasing error in defences.
- Report the interval alongside the point estimate every time. A coefficient with no interval hides how much the data actually constrain it.
- Two overlapping confidence intervals do not imply a non-significant difference. Test the difference directly.""",
            [{"question": "A frequentist 95% confidence interval means:",
              "choices": ["There is a 95% probability the parameter lies inside it",
                          "95% of intervals built this way across repeated samples contain the parameter",
                          "95% of the data lie inside it",
                          "The estimate is 95% accurate"],
              "correct": 1}],
        ),
        L(
            "Constructing Tests of Hypotheses",
            """## Overview

Hypothesis testing is usually taught as a recipe. CMO 42 asks for something harder and more useful: constructing tests and examining their properties, which means understanding what makes one test better than another.

## Key Concepts

- **The two hypotheses are not symmetric.** The null is the claim given the benefit of the doubt; the burden of evidence falls on the alternative.
- **Type I error** rejects a true null; **Type II error** fails to reject a false one. The significance level fixes the first. The second is what power addresses.
- **Power** is the probability of correctly rejecting a false null. It rises with sample size, with effect size, and with lower measurement noise.
- **The Neyman-Pearson lemma** identifies the most powerful test for a simple hypothesis against a simple alternative: the likelihood ratio test. Most standard tests are likelihood ratio tests in disguise.
- **Failing to reject is not accepting.** An underpowered study fails to reject almost everything, which is evidence about the study, not about the hypothesis.

![Diagram: Choosing and running a hypothesis test](/static/diagrams/hypothesis-testing-flow.svg)

## Worked Example

A thesis reports "no significant difference between the two teaching methods, therefore the methods are equally effective" with 18 participants per group. The conclusion does not follow. With that sample, power to detect a moderate effect is well under 50% -- the study was more likely than not to miss a real difference of practical size. The defensible statement is that the study did not detect a difference and was not powered to. If equivalence is genuinely the claim, it requires an equivalence test with a pre-specified margin, not a failed difference test.

## Common Mistakes & Pro Tips

- Compute power before collecting data, not after. Post-hoc power calculated from the observed effect adds no information beyond the p-value.
- A p-value is not the probability the null is true, and not the probability your result happened by chance. It is the probability of data at least this extreme if the null were true.
- Decide the significance level and the direction of the test before looking at results. Choosing them afterwards inflates the error rate you are claiming to control.""",
            [{"question": "Failing to reject the null hypothesis in a small, underpowered study means:",
              "choices": ["The null hypothesis is true", "The effect is zero",
                          "The study did not detect an effect it may well have missed",
                          "The alternative hypothesis is false"],
              "correct": 2}],
        ),
        L(
            "Further Reading (Free & Open)",
            """## Overview

The standard references for this material, plus openly licensed alternatives. The first two are the textbooks CMO 42 itself names for Mathematical Statistics 1-3.

## Key Concepts

- **Hogg, R.V. and Tanis, E.A. -- *Probability and Statistical Inference*** (Prentice Hall). Named in CMO 42 Annex B for all three Mathematical Statistics courses.
- **Mood, A.M., Graybill, F.A. and Boes, D.C. -- *Introduction to the Theory of Statistics*** (McGraw-Hill). The other CMO 42 reference; older, terser, and still excellent on derivations.
- **MIT OpenCourseWare 18.650, *Statistics for Applications*** -- full lecture videos and notes, openly licensed. The closest free equivalent to Mathematical Statistics 3.
- **MIT OpenCourseWare 6.041, *Probabilistic Systems Analysis*** -- outstanding treatment of the probability half, with worked problem sets.
- **Blitzstein and Hwang, *Introduction to Probability*** -- freely available online, unusually readable, strong on building intuition before formalism.

## Worked Example

If you are preparing for a comprehensive exam, work Hogg and Tanis for structure and use the MIT 18.650 problem sets for practice under time pressure. Derivations you can reproduce on paper are what examiners probe; recognising a formula is not the same thing.

## Common Mistakes & Pro Tips

- Reading proofs is not learning proofs. Close the book and reproduce the derivation.
- Do not skip the probability half to get to inference faster. Almost every confusion in inference traces back to a shaky grasp of conditional distributions.""",
        ),
    ],
}


# ---------------------------------------------------------------------------
# 2. Nonparametric Statistics  (CMO 42 core)
# ---------------------------------------------------------------------------
NONPARAMETRIC = {
    "title": "Nonparametric Statistics",
    "slug": "nonparametric-statistics",
    "category": "Statistics",
    "level": "Intermediate",
    "price_php": 2800,
    "description": (
        "What to do when the assumptions behind t-tests and ANOVA do not hold. Rank tests "
        "for one sample, two samples and k samples; tests for randomness; association tests; "
        "distribution tests; and tests for independence. Built for researchers working with "
        "ordinal scales, small samples and skewed data -- which in practice is most thesis "
        "data in the social sciences and health research."
    ),
    "curriculum_alignment": f"{CMO} core -- Nonparametric Statistics (3 units)",
    "prerequisites": (
        "Mathematical Statistics 3, per CMO 42\n"
        "Basic Statistics: A Practical Start, or equivalent introductory statistics"
    ),
    "learning_outcomes": (
        "Distinguish between parametric and nonparametric tests\n"
        "Know when to use each of the different nonparametric tests\n"
        "Apply these tests with flexibility and creativity to various problems"
    ),
    "lessons": [
        L(
            "When Parametric Assumptions Fail",
            """## Overview

Nonparametric methods are often presented as the fallback when something has gone wrong. That framing is misleading. For ordinal data and small skewed samples they are the correct first choice, not a consolation prize.

## Key Concepts

- **Nonparametric does not mean assumption-free.** These tests still assume independent observations, and most assume similarly shaped distributions across groups. What they drop is the requirement of a specific distributional family.
- **They work on ranks.** Replacing values with their ranks discards the exact magnitudes and keeps the ordering, which is precisely what makes them robust to outliers and to skew.
- **Ordinal data needs them.** Likert responses, satisfaction ratings and severity scales have order but no guaranteed equal spacing, so a mean is not strictly meaningful.
- **The cost is power** -- but less than most people assume. Under normality the Wilcoxon test retains roughly 95% of the t-test's power, and under non-normality it frequently has more.
- **The hypothesis changes.** Many rank tests are about medians or about stochastic dominance, not about means. Report what was actually tested.

## Worked Example

A researcher has 14 patients per group and a strongly right-skewed recovery-time outcome. The t-test is reached for by default, with a note that the central limit theorem applies. At 14 per group with marked skew it does not reliably. The Mann-Whitney U test makes no normality assumption, handles the skew, and with that sample size is likely to be more powerful, not less. The conclusion also becomes cleaner to state: one group tends to recover sooner than the other.

## Common Mistakes & Pro Tips

- Do not choose a nonparametric test because a normality test rejected. With large samples normality tests reject trivial departures; with small samples they miss real ones. Decide from the measurement scale and a plot.
- State the hypothesis in the terms the test actually addresses. Writing "no difference in means" after a Mann-Whitney test misdescribes the analysis.
- Nonparametric does not rescue dependent observations. Repeated measures still need the paired versions.""",
            [{"question": "Rank-based tests are robust to outliers because they:",
              "choices": ["Delete extreme values", "Use only the ordering of the values, not their magnitudes",
                          "Assume normality", "Require larger samples"],
              "correct": 1}],
            preview=True,
        ),
        L(
            "One Sample: Sign and Wilcoxon Signed-Rank Tests",
            """## Overview

The one-sample problem asks whether a population is centred at some hypothesised value. Two rank-based options exist, and they differ in how much they assume and how much power they deliver.

## Key Concepts

- **The sign test** counts how many observations fall above and below the hypothesised median and tests whether the split departs from an even one. It assumes almost nothing beyond independence.
- **The Wilcoxon signed-rank test** ranks the absolute deviations from the hypothesised value and sums the ranks of the positive ones. It uses more information than the sign test and is correspondingly more powerful.
- **Wilcoxon requires symmetry** of the distribution of differences around the centre. The sign test does not, which is why it survives where Wilcoxon should not be used.
- **Ties matter.** Values exactly equal to the hypothesised median are dropped by the sign test, and tied ranks need a correction in Wilcoxon.
- **Both extend to paired data** by working on the within-pair differences, which is how they replace the paired t-test.

## Worked Example

Thirty teachers rate a new module on a 1-to-10 scale. The question is whether the typical rating exceeds the neutral value of 5. The ratings are ordinal and clearly skewed toward the high end. The Wilcoxon signed-rank test on deviations from 5 is the natural choice, and the result is stated as evidence that the median rating exceeds neutral. If the deviations were visibly asymmetric, the sign test would be the more defensible fallback -- lower power, but its assumption is actually satisfied.

## Common Mistakes & Pro Tips

- The signed-rank test assumes symmetric differences. Check with a histogram of the differences, not of the raw values.
- For paired designs, compute the differences first and then apply the one-sample test. Running a two-sample test on paired data throws away the pairing and loses power.
- Report the median and an interquartile range alongside the test. A p-value with no descriptive summary is not interpretable.""",
            [{"question": "Compared with the sign test, the Wilcoxon signed-rank test:",
              "choices": ["Assumes less and has less power", "Assumes symmetry of differences and has more power",
                          "Requires normality", "Can only be used on paired data"],
              "correct": 1}],
        ),
        L(
            "Two Samples: Related and Independent",
            """## Overview

Two-sample comparison is the most common test in applied research. The rank-based versions split along the same line as their parametric counterparts: are the two sets of observations paired, or are they separate groups?

## Key Concepts

- **Related samples** -- the same subjects measured twice, or matched pairs -- are handled by the Wilcoxon signed-rank test applied to within-pair differences.
- **Independent samples** are handled by the **Mann-Whitney U test**, equivalently the Wilcoxon rank-sum test. Both names describe the same procedure.
- **Mann-Whitney pools and ranks** all observations together, then compares the rank totals. If one group systematically occupies the higher ranks, the statistic detects it.
- **It tests stochastic dominance**, not means. Under the additional assumption of identically shaped distributions it can be read as a test of medians.
- **Unequal group sizes are fine.** Unequal spread across groups is more of a problem, because it can produce significance without any location shift.

## Worked Example

A study compares stress scores between 22 nurses on rotating shifts and 19 on fixed shifts. Scores are bounded, skewed, and contain several extreme values. Mann-Whitney is applied and returns a significant result. The correct interpretation is that stress scores in the rotating-shift group tend to be higher -- an observation is more likely than not to be higher if drawn from that group. Writing "the mean stress score was significantly higher" overstates it, because no means were compared.

## Common Mistakes & Pro Tips

- Check that the two distributions have roughly similar shape before reading Mann-Whitney as a median comparison. Different spreads can trigger significance with identical medians.
- Paired data analysed as independent samples is a substantive error, not a stylistic one. It discards the design and usually loses power.
- Report an effect size. The rank-biserial correlation or the common-language effect size communicates far more than a p-value.""",
            [{"question": "The Mann-Whitney U test is appropriate for:",
              "choices": ["Paired observations on the same subjects", "Two independent groups",
                          "More than two related groups", "A single sample against a fixed value"],
              "correct": 1}],
        ),
        L(
            "k Samples: Kruskal-Wallis and Friedman",
            """## Overview

When there are more than two groups, running every pairwise comparison inflates the error rate. The rank-based world solves this the same way ANOVA does -- with an omnibus test first.

## Key Concepts

- **Kruskal-Wallis** extends Mann-Whitney to k independent groups. It is the rank-based counterpart of one-way ANOVA.
- **Friedman** extends the signed-rank test to k related samples -- the same subjects measured under several conditions. It is the counterpart of repeated-measures ANOVA.
- **Both are omnibus tests.** A significant result says the groups are not all alike; it does not say which differ.
- **Post-hoc comparisons follow**, with an adjustment such as Dunn's test for Kruskal-Wallis or pairwise Wilcoxon tests with a correction for multiplicity.
- **Friedman ranks within subjects**, which is exactly what makes it handle the dependence that would invalidate Kruskal-Wallis on the same data.

## Worked Example

Forty students are taught under three different review formats, each student experiencing all three in randomised order. Scores are ordinal. Because every student appears in all three conditions, the observations are related and Friedman is the correct omnibus test. A significant result is followed by pairwise Wilcoxon signed-rank tests with a Bonferroni or Holm adjustment. Using Kruskal-Wallis here would treat 120 dependent observations as if they were 120 independent ones, understating the standard errors and overstating significance.

## Common Mistakes & Pro Tips

- Reporting an omnibus result and then naming which group is highest, without post-hoc tests, is a conclusion the analysis did not support.
- Adjust for multiple comparisons and say which adjustment you used. Unadjusted pairwise testing across five groups gives ten chances to find a spurious effect.
- Match the test to the design, not to the number of groups alone. Related and independent are different tests at every group count.""",
            [{"question": "The same subjects are measured under four conditions. The appropriate omnibus rank test is:",
              "choices": ["Kruskal-Wallis", "Friedman", "Mann-Whitney U", "The sign test"],
              "correct": 1}],
        ),
        L(
            "Measures of Association: Spearman and Kendall",
            """## Overview

Pearson correlation measures linear association and assumes interval data. When the scale is ordinal or the relationship is monotone but curved, rank-based measures are the honest choice.

## Key Concepts

- **Spearman's rho** is Pearson's correlation computed on ranks. It measures monotone association: whether higher tends to go with higher, regardless of whether the relationship is a straight line.
- **Kendall's tau** is built from concordant and discordant pairs. It has a cleaner probabilistic interpretation and handles ties and small samples better than Spearman.
- **Both range from -1 to 1**, with zero indicating no monotone association. Tau is typically smaller in magnitude than rho on the same data; they are not interchangeable numbers.
- **Neither implies causation**, and neither detects non-monotone relationships. A perfect U-shape yields a correlation near zero in all three measures.
- **Ordinal scales need these.** Correlating two Likert items with Pearson assumes the spacing between "agree" and "strongly agree" equals the spacing between "neutral" and "agree."

## Worked Example

A study correlates a five-point service satisfaction rating with a five-point likelihood-to-recommend rating across 80 respondents. Pearson is reported at 0.62. Spearman on the same data gives 0.66, and Kendall's tau gives 0.55. All three agree there is a solid positive association, but only the rank measures are defensible given the scales. Report Spearman, and note that tau would give a smaller number by construction so the two should never be compared as if on the same scale.

## Common Mistakes & Pro Tips

- Always plot the scatter before reporting any correlation. A near-zero coefficient with an obvious curve is a finding about the measure, not the relationship.
- Do not compare a Spearman coefficient from one study with a Kendall coefficient from another. They are different quantities.
- With many ties -- common on short ordinal scales -- Kendall's tau-b, which corrects for ties, is preferable to Spearman.""",
            [{"question": "Spearman's rho differs from Pearson's r in that it measures:",
              "choices": ["Causal strength", "Monotone association using ranks rather than linear association",
                          "Only negative relationships", "Association between categorical variables"],
              "correct": 1}],
        ),
        L(
            "Tests for Randomness and Goodness of Fit",
            """## Overview

Two questions sit slightly apart from group comparison: is this sequence random, and does this sample come from a particular distribution? Both have standard nonparametric answers.

## Key Concepts

- **The runs test** examines a sequence for randomness by counting runs -- consecutive stretches of the same type. Too few runs suggests clustering; too many suggests alternation.
- **Randomness matters in data collection.** A runs test on the order of responses can reveal that an enumerator fabricated a block of interviews or that respondents were not approached in the intended order.
- **The Kolmogorov-Smirnov test** compares the empirical distribution function of a sample with a hypothesised distribution, using the largest vertical gap between them.
- **The Anderson-Darling test** does the same but weights the tails more heavily, making it more sensitive where the tails matter.
- **Chi-square goodness of fit** compares observed and expected frequencies across categories, and is the only one of these that works naturally on already-categorical data.

## Worked Example

An enumerator's questionnaires arrive with responses to a yes/no screening item in the order Y Y Y Y Y Y N N N N N N. A runs test finds only two runs where roughly seven would be expected by chance. That is strong evidence the sequence is not random. It does not prove misconduct -- the sample may have been collected by area, clustering similar households -- but it is exactly the kind of data-quality check CMO 42 places under survey operations, and it needs explaining before analysis proceeds.

## Common Mistakes & Pro Tips

- Kolmogorov-Smirnov loses validity when the hypothesised distribution's parameters were estimated from the same sample. Use the Lilliefors correction in that case.
- Goodness-of-fit tests with large samples reject for departures too small to matter. Pair the p-value with a plot of the fitted against the empirical distribution.
- Failing to reject a goodness-of-fit test is not proof the distribution is correct. It means the data did not contradict it.""",
            [{"question": "A runs test is used to assess:",
              "choices": ["Whether two medians differ", "Whether a sequence of observations is random",
                          "Whether variances are equal", "Whether a correlation is significant"],
              "correct": 1}],
        ),
        L(
            "Chi-Square Tests of Independence",
            """## Overview

The chi-square test of independence asks whether two categorical variables are related. It is probably the most-used and most-misused test in thesis work.

## Key Concepts

- **The logic is comparison to expectation.** Expected counts are computed under the assumption of independence, and the statistic measures how far observed counts stray from them.
- **Expected counts drive validity.** The usual guidance is that all expected counts should be at least 1 and no more than 20% below 5. Violating this makes the chi-square approximation unreliable.
- **Fisher's exact test** is the correct alternative for small tables with sparse cells, and computes the probability directly rather than approximating it.
- **Significance says related, not how strongly.** Report Cramer's V or the phi coefficient for effect size.
- **It detects any departure from independence**, not a direction. Interpretation requires inspecting the residuals cell by cell.

![Diagram: Reading a contingency table](/static/diagrams/contingency-table.svg)

## Worked Example

A 2x4 table cross-classifies employment status against highest educational attainment for 90 respondents. Three of the eight expected counts fall below 5. The chi-square statistic is significant, but the approximation it relies on is not trustworthy at those counts. The defensible options are to collapse adjacent education categories into a coarser but substantively meaningful grouping, or to run Fisher's exact test. Reporting the raw chi-square with a footnote acknowledging the violation is the option panels tend to challenge.

## Common Mistakes & Pro Tips

- Check expected counts before reading the p-value. Most software reports them, and most students skip them.
- A significant chi-square on a large table tells you very little on its own. Standardised residuals identify which cells drive the result.
- Never run chi-square on repeated measures of the same subjects. McNemar's test handles the paired categorical case.""",
            [{"question": "Chi-square tests of independence become unreliable when:",
              "choices": ["The sample is large", "Several expected cell counts fall below 5",
                          "The variables are nominal", "The table has more than two rows"],
              "correct": 1}],
        ),
        L(
            "Further Reading (Free & Open)",
            """## Overview

The references CMO 42 names for Nonparametric Statistics, plus practical open resources.

## Key Concepts

- **Gibbons, J.D. and Chakraborti, S. -- *Nonparametric Statistical Inference*** (CRC Press). The primary reference named in CMO 42 Annex B.
- **Siegel, S. and Castellan, N.J. -- *Nonparametric Statistics for the Behavioral Sciences*** (McGraw-Hill). Also named in CMO 42; the classic for social-science applications.
- **Hollander, M. and Wolfe, D.A. -- *Nonparametric Statistical Methods*** (Wiley). The third CMO 42 reference, strongest on theory.
- **The R `coin` package vignette** -- free, and unusually clear on the permutation logic that underlies most of these tests.
- **Jamovi and JASP** -- both free and both expose the standard nonparametric tests with output a panel will recognise.

## Worked Example

If you are working in a Philippine graduate programme, Siegel and Castellan is the reference most likely to be on your adviser's shelf and the one whose notation your panel will recognise. Use Gibbons and Chakraborti when you need to justify an assumption formally.

## Common Mistakes & Pro Tips

- Learn the permutation reasoning behind these tests once. It makes the whole family obvious rather than a list to memorise.
- Free software is not a weaker choice. Jamovi and JASP run the same tests as commercial packages and produce output in APA format.""",
        ),
    ],
}


# ---------------------------------------------------------------------------
# 3. Design & Analysis of Experiments  (CMO 42: Experimental Designs)
# ---------------------------------------------------------------------------
EXPERIMENTS = {
    "title": "Design & Analysis of Experiments",
    "slug": "design-analysis-experiments",
    "category": "Statistics",
    "level": "Advanced",
    "price_php": 3800,
    "description": (
        "Getting the design right before any data is collected. Principles of "
        "experimentation, completely randomized design, randomized complete block design, "
        "Latin-square design, factorial experiments, split-plot designs, treatment mean "
        "comparison and analysis of covariance. Aimed at agricultural, health, education "
        "and industrial researchers who need a design a panel or a regulator will accept."
    ),
    "curriculum_alignment": f"{CMO} core -- Experimental Designs (3 units)",
    "prerequisites": (
        "Regression Analysis, per CMO 42\n"
        "Intermediate Statistics: Building Real Models, or equivalent"
    ),
    "learning_outcomes": (
        "Explain the principles of designing experiments for statistical analysis\n"
        "Design experiments for statistical analysis\n"
        "Analyze statistically designed experiments\n"
        "Use statistical software for analyzing statistically designed experiments"
    ),
    "lessons": [
        L(
            "The Three Principles of Experimentation",
            """## Overview

No analysis rescues a broken design. Three principles, stated by Fisher a century ago, determine whether an experiment can answer the question it was built for.

## Key Concepts

- **Randomization** assigns treatments to units by chance. It is what licenses causal inference: it breaks any systematic link between treatment and the unmeasured characteristics of the units.
- **Replication** means several units per treatment. Without it there is no way to estimate experimental error, and with no error estimate there is no test.
- **Local control**, usually blocking, groups similar units together so that comparisons happen within homogeneous sets. It removes a known nuisance source of variation from the error term.
- **Experimental unit versus observational unit.** The unit to which the treatment is independently applied is what counts for the analysis. Measuring five leaves on one treated plant gives you one experimental unit, not five.
- **Confounding** occurs when a treatment effect cannot be separated from another influence. Good design prevents it; no amount of modelling reliably repairs it afterwards.

## Worked Example

A researcher applies a new fertiliser to all plots on the east side of a field and the control to all plots on the west, because it is easier to manage. The fertiliser appears to work. It is uninterpretable: soil moisture, drainage and sun exposure differ systematically east to west, and those effects are perfectly confounded with treatment. Randomising treatment assignment across all plots would have broken the confound. If the east-west gradient is known in advance, blocking on it is better still -- it removes the gradient from error rather than merely averaging over it.

## Common Mistakes & Pro Tips

- Pseudo-replication -- treating repeated measurements on one unit as independent replicates -- is the most common fatal flaw in student experiments. Count experimental units, not data points.
- Convenience assignment is not randomisation. Alternating treatments, or assigning by arrival order, leaves systematic patterns intact.
- Decide the design before collecting data and write it down. A design reconstructed after the fact is almost always weaker than it looks.""",
            [{"question": "Five leaves are measured on each of six treated plants. The number of experimental units is:",
              "choices": ["30", "6", "5", "1"], "correct": 1}],
            preview=True,
        ),
        L(
            "Completely Randomized Design",
            """## Overview

The simplest design: every experimental unit has an equal chance of receiving any treatment. When units are genuinely homogeneous, nothing more complicated is needed.

## Key Concepts

- **Assignment is purely random** across all units, with no restriction. With 20 units and four treatments, any allocation of five units per treatment is equally likely.
- **The analysis is one-way ANOVA.** Total variation is partitioned into variation between treatments and variation within treatments, and their ratio is compared to an F distribution.
- **Degrees of freedom follow the design**: treatments minus one for the numerator, total units minus number of treatments for the denominator.
- **It tolerates unequal group sizes** more gracefully than most designs, which matters when units are lost.
- **Its weakness is homogeneity.** If the units differ in some known way, that variation lands in the error term and buries the treatment effect.

## Worked Example

Twenty-four identical laboratory samples are randomly assigned to three storage conditions, eight each. One-way ANOVA gives an F statistic on 2 and 21 degrees of freedom. Suppose the F is significant. All that has been established is that the three condition means are not all equal. Which conditions differ requires a treatment mean comparison procedure, covered later in this course -- the omnibus F does not identify them.

## Common Mistakes & Pro Tips

- A completely randomized design on visibly heterogeneous units wastes information. If you know a nuisance factor, block on it.
- Check the residuals for constant variance and approximate normality. ANOVA is reasonably robust to mild departures and much less so to unequal variances with unequal group sizes.
- Report the mean square error. It is the estimate of experimental error, and every subsequent comparison rests on it.""",
            [{"question": "In a completely randomized design with 4 treatments and 24 units, the error degrees of freedom are:",
              "choices": ["23", "20", "3", "4"], "correct": 1}],
        ),
        L(
            "Randomized Complete Block Design",
            """## Overview

When the experimental units differ in a known, measurable way, blocking turns that nuisance into an advantage instead of leaving it in the error term.

## Key Concepts

- **A block is a set of similar units.** Fields divided by soil type, patients grouped by age band, students grouped by prior achievement.
- **Complete** means every treatment appears exactly once in every block. Randomisation happens within each block, not across the whole experiment.
- **The gain is precision.** Block-to-block variation is estimated and removed from the error term, so the same treatment effect becomes easier to detect.
- **Degrees of freedom shift.** Blocks consume degrees of freedom that would otherwise go to error, which is the price paid for the reduction in error variance.
- **Blocks are usually not of interest.** They are a design device, and a significant block effect simply confirms blocking was worthwhile.

## Worked Example

A teaching intervention is tested across four schools. Schools differ substantially in baseline performance. Running a completely randomized design across all students pools that school-level variation into error, and the intervention effect drowns in it. Blocking by school and randomising students to treatment within each school removes between-school differences from error. The treatment comparison is then made within schools, where units are far more alike, and the same effect becomes detectable with the same number of students.

## Common Mistakes & Pro Tips

- Block on variables known before the experiment and expected to influence the outcome. Blocking on something measured afterwards is not blocking.
- Do not test and interpret the block effect as a finding. Blocks were not randomly assigned, so no causal reading applies.
- If a treatment cannot be applied within every block, the design is incomplete and needs a balanced incomplete block analysis instead.""",
            [{"question": "The main benefit of blocking is that it:",
              "choices": ["Increases the number of treatments", "Removes a known source of variation from the error term",
                          "Eliminates the need for randomization", "Guarantees normality"],
              "correct": 1}],
        ),
        L(
            "Latin Square Designs",
            """## Overview

When two nuisance factors are present at once, blocking on one leaves the other in the error. The Latin square blocks on both simultaneously.

## Key Concepts

- **Rows and columns are two blocking factors**, and treatments are arranged so each appears exactly once in every row and every column.
- **The square must be complete**: with t treatments you need exactly t rows and t columns, giving t-squared units. Four treatments require sixteen units, not fewer.
- **It is efficient but rigid.** Only one observation exists per treatment-row-column combination, so degrees of freedom for error are limited -- with three treatments, only two remain.
- **The additivity assumption is strong.** Row, column and treatment effects are assumed not to interact. If they do, the analysis is biased and the design cannot detect it.
- **Replication of small squares** is the usual remedy for the shortage of error degrees of freedom.

## Worked Example

Four tyre compounds are tested on four cars over four positions. Cars differ, and wheel position matters through alignment and load. A Latin square assigns compounds so each appears once per car and once per position, requiring sixteen wheel-tests. Both nuisance factors leave the error term. With only six error degrees of freedom the test is not powerful, so the study is repeated with a second square and the two are analysed jointly.

## Common Mistakes & Pro Tips

- Latin squares with fewer than five treatments have too few error degrees of freedom to be useful alone. Replicate the square.
- The design assumes no interaction between the blocking factors and treatment. If interaction is plausible, use a factorial design instead.
- Randomise the square -- choose one at random from the possible arrangements rather than writing down the first one that fits.""",
            [{"question": "A Latin square design with 5 treatments requires how many experimental units?",
              "choices": ["5", "10", "25", "125"], "correct": 2}],
        ),
        L(
            "Factorial Experiments and Interaction",
            """## Overview

Most real questions involve more than one factor, and the interesting part is usually whether the factors modify each other. Factorial designs are built to answer exactly that.

## Key Concepts

- **Every combination of factor levels is run.** A 2x3 factorial has six treatment combinations, and each is replicated.
- **Main effects** describe the average effect of one factor across the levels of the other. **Interaction** describes whether that effect changes depending on the other factor's level.
- **Interaction is often the research question.** "Does the new teaching method work better for low-achieving students?" is an interaction hypothesis, not a main-effect one.
- **Efficiency is the practical argument.** A factorial gets main effects for both factors from the same units a one-factor-at-a-time study would need for one.
- **Interaction changes interpretation.** When interaction is significant, main effects should not be interpreted on their own -- report simple effects within each level instead.

## Worked Example

A 2x2 study crosses two fertiliser rates with two irrigation levels. Fertiliser raises yield by 10 units under high irrigation and lowers it by 2 under low irrigation. The main effect of fertiliser averages to +4, which describes neither condition accurately. Reporting "fertiliser increased yield" would be actively misleading to a farmer with limited water. The correct reporting leads with the interaction and gives the simple effect at each irrigation level.

## Common Mistakes & Pro Tips

- Test and plot the interaction before reading main effects. An interaction plot with crossing lines is the clearest possible evidence.
- A non-significant interaction in a small study is not evidence of no interaction. Interaction tests are typically much lower-powered than main-effect tests.
- Resist adding factors without replication. A 2x2x2x2 with one observation per cell has no error estimate at all.""",
            [{"question": "When a significant interaction is present, main effects should be:",
              "choices": ["Interpreted as usual", "Interpreted with caution, reporting simple effects at each level",
                          "Removed from the model", "Averaged together"],
              "correct": 1}],
        ),
        L(
            "Split-Plot Designed Experiments",
            """## Overview

Sometimes one factor simply cannot be randomised at the same scale as another. Split-plot designs handle that constraint honestly instead of pretending it does not exist.

## Key Concepts

- **Two sizes of experimental unit.** Whole plots receive one factor; each whole plot is divided into subplots that receive the other.
- **Two error terms.** Whole-plot error and subplot error are different, and each effect is tested against the correct one. This is what most analyses get wrong.
- **The subplot factor is tested more precisely** than the whole-plot factor, because subplot error is typically smaller.
- **Design the constraint deliberately.** Put the factor you care most about at the subplot level whenever the practical constraint allows it.
- **It arises constantly in practice** -- irrigation applied by field but variety planted by row, or training delivered by school but materials assigned by class.

## Worked Example

Irrigation must be applied to whole fields because of how the pipes run, while three crop varieties can be planted in strips within each field. Irrigation is the whole-plot factor and variety the subplot factor. Analysing this as a standard factorial uses a single error term and tests irrigation against subplot error, which is far too small. The result is a wildly overstated F for irrigation. The split-plot analysis tests irrigation against whole-plot error -- of which there is much less -- and reports it honestly as the less precisely estimated effect.

## Common Mistakes & Pro Tips

- Identify the randomisation structure before choosing the model. If two factors were randomised at different scales, a single-error-term model is wrong.
- Most general-purpose software will happily fit the wrong model here. You must specify the error structure explicitly.
- Whole-plot effects are weakly tested by construction. Plan for that when deciding which factor goes where.""",
            [{"question": "A split-plot design requires:",
              "choices": ["One error term", "Two error terms, one for whole plots and one for subplots",
                          "No randomization", "Equal numbers of factor levels"],
              "correct": 1}],
        ),
        L(
            "Treatment Mean Comparison",
            """## Overview

A significant F says the treatment means are not all equal. It does not say which differ. Choosing the follow-up procedure is a decision about how much protection against false positives you want.

## Key Concepts

- **Planned contrasts** are comparisons specified before the data are seen. They are the most powerful option and need the least correction.
- **Tukey's HSD** controls the error rate across all pairwise comparisons. It is the standard choice when every pair is of interest.
- **Dunnett's test** compares each treatment against a single control, which is fewer comparisons and therefore more power than all-pairs procedures.
- **Bonferroni** is simple and general but conservative, especially with many comparisons.
- **Least significant difference without adjustment** does not control the family-wise error rate and should not be used unprotected.

## Worked Example

Five treatments are compared, so there are ten pairwise comparisons. Testing each at the 5% level gives roughly a 40% chance of at least one false positive if all means are truly equal. Tukey's HSD adjusts the critical value so the chance of any false positive across the whole family stays at 5%. If the study only ever cared about comparing four new treatments against the standard, Dunnett's test makes four comparisons instead of ten and delivers noticeably more power for the same protection.

## Common Mistakes & Pro Tips

- Decide the comparison procedure before looking at the means. Choosing it after seeing which pairs look promising invalidates the error control.
- Report the adjusted p-values or the procedure used. "Post-hoc tests were significant" is not reportable.
- Do not run post-hoc tests after a non-significant omnibus F unless the comparisons were planned in advance.""",
            [{"question": "Comparing several treatments against a single control is most efficiently handled by:",
              "choices": ["Tukey's HSD", "Dunnett's test", "Bonferroni on all pairs", "Unadjusted LSD"],
              "correct": 1}],
        ),
        L(
            "Analysis of Covariance",
            """## Overview

ANCOVA combines ANOVA and regression: it compares treatment means after adjusting statistically for a continuous covariate measured before treatment.

## Key Concepts

- **The covariate must be pre-treatment.** Adjusting for something the treatment itself affected removes part of the effect you are trying to measure.
- **Two benefits.** Error variance falls because the covariate explains some of it, and any chance imbalance in the covariate across groups is corrected.
- **Homogeneity of regression slopes is required.** The covariate-outcome relationship must be the same in each group. If slopes differ, that is an interaction and ANCOVA's adjusted means are misleading.
- **Adjusted means are estimates** of what the group means would have been had all groups had the same covariate mean. Report them alongside the raw means.
- **It is not a fix for non-random assignment.** Adjusting for baseline differences in an observational study does not recover a causal comparison.

## Worked Example

Two teaching methods are compared on a post-test, with a pre-test as covariate. Adjusting for pre-test scores removes prior-knowledge differences from error and sharpens the comparison considerably. Before reporting, the slopes must be checked: if the new method helps low scorers and the old helps high scorers, the slopes differ, the interaction is the finding, and a single adjusted difference hides it.

## Common Mistakes & Pro Tips

- Test the treatment-by-covariate interaction first. If it is significant, do not report ANCOVA's adjusted means as the answer.
- A covariate measured after treatment is a mediator, not a covariate. Adjusting for it biases the treatment effect toward zero.
- In a randomised experiment, ANCOVA improves precision. In an observational study, it adjusts for one measured variable and leaves every unmeasured one untouched.""",
            [{"question": "ANCOVA's covariate must be measured:",
              "choices": ["After treatment", "Before treatment, unaffected by it",
                          "At the same time as the outcome", "On a subset of units"],
              "correct": 1}],
        ),
        L(
            "Further Reading (Free & Open)",
            """## Overview

The reference CMO 42 names for Experimental Designs, plus open material for practice.

## Key Concepts

- **Montgomery, D.C. -- *Design and Analysis of Experiments*** (Wiley). The reference named in CMO 42 Annex B, and the standard text worldwide.
- **Cochran and Cox, *Experimental Designs*** -- older, and still the best source for the agricultural designs used across Philippine research institutions.
- **The R `agricolae` package** -- free, written for agricultural experiments, and implements CRD, RCBD, Latin square, split-plot and the standard mean comparison procedures.
- **PSA and PhilRice technical bulletins** -- worked local examples using exactly these designs, useful for seeing the conventions your panel expects.
- **NIST/SEMATECH e-Handbook of Statistical Methods** -- free, thorough, and strong on factorial and fractional factorial designs.

## Worked Example

Before finalising any design, generate the randomisation with software and save the output. Having the randomisation plan on file, dated before data collection, is the cleanest answer to a panel asking how units were assigned.

## Common Mistakes & Pro Tips

- Design before you collect. This is the one course where reading afterwards cannot fix the problem.
- Consult a statistician at the design stage, not the analysis stage. Fisher's line about calling one in afterwards being a post-mortem still holds.""",
        ),
    ],
}


# ---------------------------------------------------------------------------
# 4. Time Series Analysis & Forecasting  (CMO 42: Time Series Analysis)
# ---------------------------------------------------------------------------
TIMESERIES = {
    "title": "Time Series Analysis & Forecasting",
    "slug": "time-series-analysis-forecasting",
    "category": "Statistics",
    "level": "Advanced",
    "price_php": 3800,
    "description": (
        "Data collected over time breaks the independence assumption every standard test "
        "relies on. Classical decomposition and smoothing, stationarity and the "
        "autocorrelation functions, ARIMA models, the Box-Jenkins method, forecasting and "
        "forecast evaluation, intervention analysis and GARCH. For anyone forecasting "
        "sales, prices, caseloads, enrolment or demand."
    ),
    "curriculum_alignment": f"{CMO} core -- Time Series Analysis (3 units)",
    "prerequisites": (
        "Regression Analysis, per CMO 42\n"
        "Intermediate Statistics: Building Real Models, or equivalent"
    ),
    "learning_outcomes": (
        "Familiarize with concepts in time series analysis\n"
        "Develop models for time series data\n"
        "Produce and evaluate forecasts from fitted models"
    ),
    "lessons": [
        L(
            "Why Time Series Data Breaks Ordinary Methods",
            """## Overview

Every standard test assumes independent observations. Data collected over time is almost never independent, and ignoring that does not produce slightly wrong answers -- it produces confidently wrong ones.

## Key Concepts

- **Autocorrelation** means an observation is correlated with earlier observations of itself. Today's sales resemble yesterday's.
- **The consequence is understated standard errors.** Dependent observations carry less information than the same number of independent ones, so ordinary formulas overstate precision and p-values come out far too small.
- **Four components** are traditionally separated: trend, seasonality, cycle and the irregular remainder. Distinguishing seasonality, which has a fixed known period, from cycle, which does not, matters for model choice.
- **Order is information.** Shuffling time series data destroys the signal, which is a useful way to see that these are not ordinary samples.
- **Spurious regression** is the trap. Two unrelated series that both trend upward will correlate strongly, and a regression of one on the other will look excellent and mean nothing.

## Worked Example

A researcher regresses monthly ice cream sales on monthly drowning incidents across five years and finds a strong, highly significant relationship. Both series rise every summer. The correlation is real and the causal reading is absurd. Two series sharing a seasonal pattern will correlate whether or not they are related. The fix is to model or remove the seasonality from both before examining the relationship, or to work with changes rather than levels.

## Common Mistakes & Pro Tips

- Plot the series first, every time. Trend, seasonality, level shifts and outliers are usually visible immediately and tell you what model class to reach for.
- Never run a standard t-test or regression on raw time series without checking residual autocorrelation. The Durbin-Watson or Ljung-Box statistic is the minimum check.
- A high R-squared in a regression of one trending series on another is a warning sign, not a result.""",
            [{"question": "Autocorrelation in residuals causes standard errors to be:",
              "choices": ["Correctly estimated", "Typically understated, making p-values too small",
                          "Typically overstated", "Irrelevant to inference"],
              "correct": 1},
            ],
            preview=True,
        ),
        L(
            "Classical Decomposition and Smoothing",
            """## Overview

Before any model is fitted, classical methods separate a series into its components and smooth out noise. These techniques are old, transparent and often surprisingly competitive.

## Key Concepts

- **Additive decomposition** assumes the components add together and suits series whose seasonal swing stays a constant size. **Multiplicative** assumes they multiply, and suits series whose seasonal swing grows with the level.
- **Moving averages** smooth a series by averaging neighbouring points. The window length sets the trade-off: longer windows are smoother but lag further behind turning points.
- **Simple exponential smoothing** weights recent observations more heavily, with the weight decaying geometrically. It suits series with no trend and no seasonality.
- **Holt's method** adds a trend component; **Holt-Winters** adds seasonality on top. Together these cover a large share of routine business forecasting.
- **Smoothing is not modelling.** It produces forecasts but no inference, no standard errors from theory, and no test of structure.

## Worked Example

Monthly enrolment at a review centre rises every year, with a large spike each June. The seasonal spike grows as total enrolment grows -- June is consistently about 40% above the annual average rather than a fixed 200 students above it. That proportional behaviour points to a multiplicative decomposition, or to taking logarithms first and using an additive one. Choosing additive on the raw scale would leave a seasonal pattern in the residuals that grows over time, visible immediately in a residual plot.

## Common Mistakes & Pro Tips

- Choose additive or multiplicative by looking at whether the seasonal amplitude grows with the level. Do not default to additive because it is simpler.
- A centred moving average of even order needs an extra averaging step, or the smoothed series will sit half a period off.
- Exponential smoothing methods still need their parameters chosen sensibly. Fitting them by minimising one-step-ahead error is standard; eyeballing them is not.""",
            [{"question": "A series whose seasonal swing grows as the level grows is best handled by:",
              "choices": ["Additive decomposition", "Multiplicative decomposition",
                          "No decomposition", "Differencing twice"],
              "correct": 1}],
        ),
        L(
            "Stationarity, ACF and PACF",
            """## Overview

Almost every time series model assumes stationarity. Understanding what it means, how to check it and how to achieve it is the gateway to everything that follows.

## Key Concepts

- **A stationary series** has a constant mean, constant variance and an autocovariance that depends only on the lag, not on where in the series you look. In practice: no trend, no changing spread.
- **Differencing** removes trend. Taking first differences converts a series with linear trend to a stationary one; seasonal differencing removes a repeating seasonal pattern.
- **The autocorrelation function (ACF)** plots correlation against lag. A slow linear decay signals non-stationarity; a sharp cutoff after lag q suggests a moving average of order q.
- **The partial autocorrelation function (PACF)** gives the correlation at each lag with intervening lags removed. A cutoff after lag p suggests an autoregressive model of order p.
- **Unit root tests** such as the Augmented Dickey-Fuller test the stationarity question formally, with non-stationarity as the null.

## Worked Example

Quarterly GDP shows a clear upward trend. Its ACF decays very slowly, staying high out to lag 20 -- the signature of non-stationarity. First differencing gives quarterly growth, which fluctuates around a stable mean. The ACF of the differenced series drops off quickly, with one notable spike at lag 4 reflecting the quarterly seasonality. A seasonal difference on top of that leaves a series ready for model identification.

## Common Mistakes & Pro Tips

- Over-differencing is a real cost. It inflates variance and introduces artificial negative autocorrelation. If the ACF of a differenced series has a large negative spike at lag 1, you have probably gone too far.
- Read the ACF and PACF together. Either one alone is ambiguous between AR and MA behaviour.
- Log-transform before differencing when the variance grows with the level. Differencing fixes the mean, not the variance.""",
            [{"question": "An ACF that decays very slowly across many lags indicates:",
              "choices": ["A stationary series", "A non-stationary series needing differencing",
                          "A moving average process", "White noise"],
              "correct": 1}],
        ),
        L(
            "ARIMA Models",
            """## Overview

ARIMA is the standard parametric framework for time series. Its three letters correspond to three ideas, and once those are separated the notation stops being intimidating.

## Key Concepts

- **AR, the autoregressive part**, regresses the series on its own past values. An AR(1) says today depends on yesterday plus noise.
- **I, integration**, is the number of times the series was differenced to reach stationarity. This is the d in ARIMA(p,d,q).
- **MA, the moving average part**, regresses the series on past forecast errors rather than past values. It captures shocks that persist for a few periods and then vanish.
- **Seasonal ARIMA** adds a second set of terms operating at the seasonal lag, written with capital letters and the period.
- **Parsimony is the goal.** ARIMA models with many terms fit the past beautifully and forecast poorly. Information criteria such as AIC and BIC penalise complexity for exactly this reason.

## Worked Example

Monthly dengue cases are modelled. The series needs one regular difference for trend and one seasonal difference at lag 12. The differenced series shows a PACF cutoff after lag 1 and an ACF spike at lag 12. That pattern suggests ARIMA(1,1,0)(0,1,1) with period 12. The model is fitted, residuals are checked for remaining autocorrelation with a Ljung-Box test, and only then is it used to forecast. Fitting the model and forecasting without the residual check is where most applied time series work goes wrong.

## Common Mistakes & Pro Tips

- A lower AIC on the training data does not guarantee better forecasts. Hold out the last portion of the series and compare forecast accuracy there.
- Automatic ARIMA selection routines are a good starting point and a poor final answer. Inspect what they chose and whether it makes sense.
- Compare every model against a naive benchmark -- last value carried forward, or the seasonal naive. A model that cannot beat the naive forecast is not worth deploying.""",
            [{"question": "In ARIMA(p,d,q), the d refers to:",
              "choices": ["The number of predictors", "The number of times the series was differenced",
                          "The seasonal period", "The forecast horizon"],
              "correct": 1}],
        ),
        L(
            "The Box-Jenkins Method",
            """## Overview

Box-Jenkins is not a model but a disciplined loop for arriving at one: identify, estimate, diagnose, and only then forecast.

## Key Concepts

- **Identification.** Plot the series, transform and difference to stationarity, then read the ACF and PACF to propose candidate orders.
- **Estimation.** Fit the candidates by maximum likelihood and check that coefficients are significant and that the model is stationary and invertible.
- **Diagnostic checking.** Residuals should be indistinguishable from white noise -- no autocorrelation in the residual ACF, a non-significant Ljung-Box statistic, and no obvious structure in a residual plot.
- **Iterate.** Failed diagnostics send you back to identification with the residual pattern as the clue, not forward to forecasting anyway.
- **Forecast last.** Only a model that has survived diagnostics earns the right to produce forecasts and intervals.

## Worked Example

A first attempt at modelling monthly remittance inflows gives a residual ACF with a clear spike at lag 12. The diagnostic has failed, and the spike names the problem: unmodelled seasonality. Rather than reporting the model with a caveat, the loop sends you back to add a seasonal term. The revised model's residuals pass Ljung-Box, and the forecast intervals from it are trustworthy in a way the first model's were not.

## Common Mistakes & Pro Tips

- Skipping diagnostics is the most common shortcut and the most expensive. Structure left in the residuals means the forecast intervals are wrong.
- Significant residual autocorrelation is a specification failure, not a minor imperfection.
- Keep a record of the models you rejected and why. A panel will ask how you arrived at your specification.""",
            [{"question": "In the Box-Jenkins method, residuals from an adequate model should resemble:",
              "choices": ["The original series", "White noise", "A trending series", "A seasonal pattern"],
              "correct": 1}],
        ),
        L(
            "Forecasting and Evaluating Forecasts",
            """## Overview

A forecast without an honest accuracy assessment is a guess with decimal places. Evaluation is what separates a usable model from a plausible-looking one.

## Key Concepts

- **Point forecast and interval.** The interval is the more informative half, and it widens with the horizon because uncertainty compounds.
- **Hold out a test period.** Fit on earlier data, forecast the held-out portion, and compare. Never evaluate on the data the model was fitted to.
- **Scale-dependent measures** -- mean absolute error and root mean squared error -- are interpretable in the original units but cannot be compared across series.
- **Scale-free measures** -- MAPE and MASE -- allow comparison across series. MAPE breaks down when actual values are near zero; MASE does not.
- **Always benchmark.** Compare against the naive forecast. Beating it is the minimum bar for a model to justify its complexity.

## Worked Example

Two models forecast quarterly sales. Model A has lower RMSE on the fitted data; Model B has lower RMSE on a four-quarter holdout. Model B is the better forecasting model. Model A has fitted the noise in the training period -- the classic overfitting signature in time series, where extra ARIMA terms always improve in-sample fit. If neither beats a seasonal naive forecast on the holdout, the honest report is that neither model adds value.

## Common Mistakes & Pro Tips

- Rolling-origin evaluation -- re-fitting and forecasting at successive points -- is more reliable than a single holdout, because one holdout can be unrepresentative.
- Forecast intervals from ARIMA assume the model is correct. Real intervals are wider than the nominal ones; say so.
- Report the horizon with every accuracy figure. One-step-ahead accuracy tells you nothing about twelve-step-ahead accuracy.""",
            [{"question": "Models should be compared on forecast accuracy measured on:",
              "choices": ["The data used to fit them", "A held-out test period they never saw",
                          "The full series", "The residual ACF"],
              "correct": 1}],
        ),
        L(
            "Intervention Analysis, Non-Stationary Models and GARCH",
            """## Overview

Three extensions cover situations the standard ARIMA framework handles badly: a known event that shifted the series, a variance that changes over time, and relationships between series.

## Key Concepts

- **Intervention analysis** adds a term for a known event at a known date -- a policy change, a lockdown, a price shock -- and estimates its effect while the rest of the model absorbs normal dynamics.
- **The intervention's shape matters.** A step function models a permanent level shift; a pulse models a one-off; a decaying response models an effect that fades.
- **GARCH models the variance**, not the mean. It is built for series where calm periods and volatile periods cluster, which is the norm in financial returns.
- **Volatility clustering** is the pattern GARCH exists to capture: large changes tend to follow large changes, of either sign.
- **Regression with ARIMA errors** lets you include external predictors while modelling the autocorrelation properly, rather than ignoring it.

## Worked Example

Monthly tourist arrivals are modelled across a period containing a volcanic eruption that closed an airport for two months. Fitting a plain ARIMA treats those two months as extreme random shocks, which inflates the error variance and widens every subsequent forecast interval. Intervention analysis with a pulse at the eruption date and a decaying recovery estimates the disruption explicitly. The rest of the model's parameters are then estimated on clean dynamics, and the forecast intervals narrow to something usable.

## Common Mistakes & Pro Tips

- Intervention dates must be known in advance from substantive knowledge. Searching for the date that best improves fit is data dredging.
- GARCH models variance and does nothing for the mean. Series needing GARCH usually need an ARIMA mean equation alongside it.
- Including an external predictor in a time series regression without modelling the error structure reintroduces the spurious regression problem.""",
            [{"question": "GARCH models are used when a series exhibits:",
              "choices": ["A linear trend", "Volatility that clusters over time",
                          "Seasonal peaks", "Missing values"],
              "correct": 1}],
        ),
        L(
            "Further Reading (Free & Open)",
            """## Overview

The reference CMO 42 names for Time Series Analysis, plus the best free practical resources.

## Key Concepts

- **Wei, W.W.S. -- *Time Series Analysis: Univariate and Multivariate Methods*** (Wiley). The reference named in CMO 42 Annex B.
- **Box, Jenkins, Reinsel and Ljung -- *Time Series Analysis: Forecasting and Control***. The original source of the method, still the definitive treatment.
- **Hyndman and Athanasopoulos, *Forecasting: Principles and Practice*** -- free and complete online, with R code throughout. The best modern practical introduction available at any price.
- **The R `forecast` and `fable` packages** -- free, well documented, and the reference implementations for most of this material.
- **PSA OpenSTAT and BSP statistical tables** -- real Philippine series for practice, with the seasonality and level shifts textbook data usually lacks.

## Worked Example

Work Hyndman and Athanasopoulos chapter by chapter against a real PSA series rather than a textbook dataset. Local data has irregular reporting, revisions and genuine structural breaks, and handling those is the actual skill.

## Common Mistakes & Pro Tips

- Learn to read ACF and PACF plots fluently. Everything else in this field depends on that one skill.
- Do not let automatic model selection substitute for understanding. You will be asked to justify the specification, not the software's default.""",
        ),
    ],
}


COURSES = [PROBABILITY, NONPARAMETRIC, EXPERIMENTS, TIMESERIES]


def upsert(db, spec):
    course = db.query(models.Course).filter(models.Course.slug == spec["slug"]).first()
    created = course is None
    if created:
        course = models.Course(slug=spec["slug"])
        db.add(course)

    course.title = spec["title"]
    course.description = spec["description"]
    course.category = spec["category"]
    course.level = spec["level"]
    course.price_php = spec["price_php"]
    course.instructor_name = os.getenv("INSTRUCTOR_NAME", "Dr. Hero L. Tolosa")
    course.is_published = True
    course.curriculum_alignment = spec["curriculum_alignment"]
    course.prerequisites = spec["prerequisites"]
    course.learning_outcomes = spec["learning_outcomes"]
    db.flush()

    added = updated = 0
    for order, spec_lesson in enumerate(spec["lessons"]):
        lesson = (
            db.query(models.Lesson)
            .filter(models.Lesson.course_id == course.id, models.Lesson.title == spec_lesson["title"])
            .first()
        )
        if lesson is None:
            lesson = models.Lesson(course_id=course.id, title=spec_lesson["title"])
            db.add(lesson)
            added += 1
        else:
            updated += 1
        lesson.content = spec_lesson["content"]
        lesson.order = order
        lesson.is_preview = spec_lesson["preview"]
        lesson.quiz_json = json.dumps(spec_lesson["quiz"]) if spec_lesson["quiz"] else ""

    db.commit()
    verb = "created" if created else "updated"
    print(f"[{verb}] {course.title} -- {added} lesson(s) added, {updated} updated")


def main():
    Base.metadata.create_all(bind=engine)
    sync_columns()
    db = SessionLocal()
    try:
        for spec in COURSES:
            upsert(db, spec)
    finally:
        db.close()
    print(f"\nDone. {len(COURSES)} CHED core course(s) processed.")


if __name__ == "__main__":
    main()
