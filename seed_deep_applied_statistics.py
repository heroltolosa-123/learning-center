"""
Rewrites Applied Statistics for Research at teaching depth.

This is the course a thesis candidate takes when they have data and a panel
date. It is organised around decisions, not formulas: which test, which
assumptions, which numbers to report, and how to defend all three.

One study runs through the whole course. Every figure was computed and checked:

  Independent-samples design (posttest, two sections)
    control   n=15  sum=1080  mean=72.00  SD=5.68
    treatment n=15  sum=1180  mean=78.67  SD=6.21
    pooled SD 5.95, SE 2.173, t(28)=3.068, p=.0047, d=1.12
    mean difference 6.67, 95% CI [2.22, 11.12]
    Levene p=.704, Shapiro p=.999 / .988

  Paired design (pretest/posttest, 10 students)
    pre sum=680 mean=68   post sum=740 mean=74
    differences sum=60, mean 6.00, SS=114, SD=3.56, SE=1.126
    t(9)=5.331, p=.0005, dz=1.69, 95% CI [3.45, 8.55]
    the SAME data run wrongly as independent gives t=-2.02, p=.058

  One-way ANOVA (three strands, n=8 each)
    STEM 84.00, ABM 75.75, HUMSS 73.50, grand mean 77.75
    SSB=489, SSW=325.5, SST=814.5, MSB=244.5, MSW=15.5
    F(2,21)=15.774, p=.00007, eta-squared=.600, omega-squared=.552

  Power (alpha .05, two-tailed, equal groups)
    n per group for 80% power: d=0.2 -> 394, d=0.5 -> 64, d=0.8 -> 26
    power at n=15/group with d=1.12 -> .84
    power at n=8/group  with d=0.50 -> .15

Safe to re-run. Lessons are matched by title and replaced in place.

Usage:
    python3 seed_deep_applied_statistics.py
"""
import json
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal, sync_columns
from app import models

COURSE_SLUG = "applied-statistics-for-research"
LESSONS = []


def L(title, content, quiz=None, preview=False):
    LESSONS.append({"title": title, "content": content, "quiz": quiz, "preview": preview})


# ===========================================================================
L(
    "From Research Question to Statistical Test",
    """## What you will be able to do

Take any research question and translate it into a statistical hypothesis with named variables, a measurement level for each, and a design label -- the four things that between them determine which test you run. This is the step almost every struggling thesis skipped.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
A candidate walks into consultation and says: *"I want to know if my module is effective."*

That is not yet a statistical question. It names no variables, no comparison, no measurement. Until it is translated, no software can help and no test can be chosen.

By the end of this lesson you will be able to do that translation in four moves.
</div>

## The study we will use all course

<div class="callout callout-case" markdown="1">
<span class="callout-label">Our study</span>
**Title.** Effectiveness of a self-paced statistics module on the achievement of Grade 11 students.

**Design.** Two intact sections. One receives the module (treatment, n = 15), one receives the usual lecture (control, n = 15). Both sit the same 100-item posttest.

**Results, which we will keep returning to:**

| Group | n | Mean | SD |
|---|---:|---:|---:|
| Control (lecture) | 15 | 72.00 | 5.68 |
| Treatment (module) | 15 | 78.67 | 6.21 |
</div>

## Move 1 -- Name the variables

Every statistical question involves at least two variables and a claimed relationship between them.

| Role | Question to ask | In our study |
|---|---|---|
| **Independent (IV)** | What did I manipulate, or what groups am I comparing? | Teaching method (module vs lecture) |
| **Dependent (DV)** | What did I measure as the outcome? | Posttest achievement score |
| **Covariate** | What else might influence the DV that I measured? | Pretest score |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The most common failure</span>
"I want to know if my module is effective" has **no DV**. Effective at what? Achievement? Retention? Motivation? Time on task?

Until the outcome is named and measured, there is nothing to test. Panels open with this question because it exposes whether the study was designed or merely performed.
</div>

## Move 2 -- Give each variable its measurement level

You did this in Basic Statistics. It now decides the test.

| Variable | Level | Consequence |
|---|---|---|
| Teaching method | **Nominal**, 2 categories | It is a grouping variable |
| Posttest score | **Ratio** | A mean is meaningful, so a t-test is possible |

Swap either one and the answer changes completely. If the outcome were "passed / failed" (nominal), no mean exists and you would need chi-square instead.

## Move 3 -- Name the design

Three questions settle it:

1. **How many groups am I comparing?** One, two, or three-plus?
2. **Are the groups made of different people, or the same people measured more than once?** Independent or related?
3. **Am I comparing groups, or looking at a relationship between two continuous variables?** Difference or association?

Our study: **two groups, different people, comparing a difference** &rarr; independent-samples design.

## Move 4 -- Write the hypotheses

<div class="formula" markdown="1">
**H&#8320;: &mu;<sub>module</sub> = &mu;<sub>lecture</sub>**
<span class="formula-note">**H&#8321;: &mu;<sub>module</sub> &ne; &mu;<sub>lecture</sub>**</span>
</div>

Rules, all of which panels check:

- Hypotheses are about **population parameters** (&mu;), never sample statistics (x&#772;)
- H&#8320; carries the equality
- Two-tailed unless a strong, pre-registered theory justifies direction
- The **statistical** hypothesis and the **research** hypothesis are different sentences. The research hypothesis is "the module improves achievement." The statistical hypothesis is the equation above. Your thesis needs both, clearly labelled.

## The full translation, worked

| Stage | Statement |
|---|---|
| Vague question | "Is my module effective?" |
| Research question | "Is there a significant difference in posttest achievement between students taught with the self-paced module and those taught by lecture?" |
| Variables | IV = teaching method (nominal, 2 levels); DV = posttest score (ratio) |
| Design | Two independent groups, comparing a difference |
| H&#8320; | &mu;<sub>module</sub> = &mu;<sub>lecture</sub> |
| H&#8321; | &mu;<sub>module</sub> &ne; &mu;<sub>lecture</sub> |
| Test | Independent-samples *t*-test |

Every row follows from the one above it. That is the whole method.

## Statement of the Problem, and how it maps

Philippine thesis formats normally require a numbered Statement of the Problem. Each numbered item should map to exactly one analysis.

```
1. What is the level of achievement of students taught by lecture?
   -> descriptive: mean and SD

2. What is the level of achievement of students taught with the module?
   -> descriptive: mean and SD

3. Is there a significant difference between the two groups?
   -> inferential: independent-samples t-test
```

<div class="callout callout-key" markdown="1">
<span class="callout-label">The test panels apply</span>
**Every numbered problem must have exactly one analysis, and every analysis must answer a numbered problem.**

If you ran an analysis that answers no stated problem, a panel will ask why it is there. If a stated problem has no analysis, you have not finished. Build the mapping table before you run anything.
</div>

## Descriptive and inferential are different jobs

| | Descriptive | Inferential |
|---|---|---|
| Answers | What does my sample look like? | What can I say about the population? |
| Examples | Mean, SD, frequency, percentage | t-test, ANOVA, chi-square, correlation |
| Needs a hypothesis? | No | Yes |
| Needs random sampling? | No | Yes, for the conclusion to generalise |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The intact-groups problem</span>
Our study uses **intact sections**, not randomly assigned students. That makes it **quasi-experimental**, not experimental.

The t-test still runs and the arithmetic is identical. What changes is the **conclusion you may draw**: the two sections may have differed before the intervention, and any pre-existing difference is confounded with the treatment.

Two honest responses, and panels accept both:

1. Report it as a limitation, explicitly, in your Chapter 1 and Chapter 5.
2. Measure the pretest and use **ANCOVA** to adjust for it.

What is not acceptable is writing "the module caused the improvement" from a design that cannot support the word *caused*.
</div>

## Doing it in software

There is nothing to compute yet -- this lesson is the thinking that precedes software. But set your data up now, in the shape every package expects:

**Long format, one row per participant:**

```
id   group      pretest   posttest
1    lecture    64        62
2    lecture    68        65
...
16   module     66        68
17   module     70        70
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The spreadsheet mistake that costs a week</span>
Students routinely build **two side-by-side columns**, one per group:

```
lecture_scores   module_scores
62               68
65               70
```

Jamovi, SPSS and R all expect **one column for the outcome and one column identifying the group**. Wide layout forces a restructure later, and restructuring is where data gets mismatched.

Set it up long from the first day of collection.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- Chapter 3, research design</span>
This study employed a *quasi-experimental*, *non-equivalent control group* design. The independent variable was *teaching method*, operationalised as *the self-paced module* and *conventional lecture*. The dependent variable was *achievement*, measured by a *100-item researcher-made posttest*. Because intact sections were used, random assignment was not possible; *pretest scores* were therefore collected and used as a covariate.
</div>

## Common mistakes

- **Starting from the test.** "I will use ANOVA" before naming the variables is backwards. The design picks the test.
- **A research question with no measurable DV.** "Is it effective?" is not answerable.
- **Hypotheses about the sample.** They are about the population.
- **A Statement of the Problem that does not map one-to-one onto analyses.**
- **Calling a quasi-experiment an experiment.** Random assignment is what separates them.
- **Wide data layout.** Costs you a restructure and risks a mismatch.

## Practice

**1.** Translate this into a full statistical specification: "I want to know if there is a relationship between study habits and academic performance."

<details markdown="1">
<summary>Show the worked answer</summary>

**Variables.**
- Study habits -- measured how? If by a summated questionnaire scale, treat as interval. Say so explicitly.
- Academic performance -- general weighted average, ratio.

Note there is **no IV and DV in the causal sense** here. This is an association question, so the variables are simply X and Y.

**Design.** One group, two continuous variables, looking at a **relationship**, not a difference.

**Hypotheses.**
```
H0: rho = 0    (no linear relationship in the population)
H1: rho != 0
```
Note the parameter is Greek **rho**, the population correlation, not the sample *r*.

**Test.** Pearson correlation, if both variables are interval and roughly linear. Spearman if study habits is a single ordinal item or the relationship is monotone but curved.

**Research question, properly stated.** "Is there a significant relationship between study habits, as measured by the Study Habits Inventory, and academic performance, as measured by general weighted average, among Grade 11 students?"

**What you may conclude.** Association only. Even a strong significant *r* would not license "good study habits improve performance" -- reverse causation and confounding by conscientiousness are both live.
</details>

**2.** A student has one group of 30 nurses measured on burnout before and after a wellness programme. They plan an independent-samples t-test. What is wrong?

<details markdown="1">
<summary>Show the answer</summary>

**The design is related, not independent.** The same 30 nurses are measured twice, so the two sets of scores are paired.

Running an independent-samples t-test:

- Treats 60 dependent observations as 60 independent ones
- Throws away the pairing, which is the design's main source of precision
- Almost always **loses power**, so a real effect may go undetected

You will see exactly how much this costs in lesson 3 of this course: the same dataset gives *p* = .0005 analysed correctly as paired, and *p* = .058 analysed wrongly as independent. Same numbers, opposite conclusion.

**The correct test is the paired-samples t-test**, computed on the within-person differences.

**A design note worth raising:** with one group and no control, even a correct paired test cannot separate the programme's effect from maturation, testing effects, or anything else that happened over the same period. A control group would.
</details>

**3.** Your Statement of the Problem has five numbered questions but your Chapter 4 has seven tables. Is that a problem?

<details markdown="1">
<summary>Show the answer</summary>

**Probably yes, and a panel will ask about it.**

Two possibilities:

**Benign.** Some questions legitimately need more than one table -- question 1 might need a demographic profile table plus a descriptive statistics table. That is fine **if you label each table with the question it answers.**

**Not benign.** You ran analyses that answer no stated question. This is the visible symptom of exploratory analysis presented as confirmatory, and it is what a panel is probing for. Every extra test raises the chance of a false positive.

**What to do:**

1. Build the mapping table: question &rarr; analysis &rarr; table number. Put it in Chapter 3.
2. For each unmapped table, decide: does it belong to a question you forgot to state, or was it exploratory?
3. If it was exploratory, either **remove it** or **label it explicitly as exploratory** and say it was not hypothesised in advance.

Honest exploratory analysis is legitimate research. Exploratory analysis dressed as confirmatory is not.
</details>

## Before you move on

- [ ] I can name the IV, DV and any covariate in my own study
- [ ] I can state the measurement level of each variable
- [ ] I can label my design: how many groups, independent or related, difference or association
- [ ] I can write hypotheses about population parameters, with H&#8320; carrying the equality
- [ ] Every numbered problem in my Statement of the Problem maps to exactly one analysis
- [ ] My data file is in long format, one row per participant

Next: the decision framework that turns those four moves into a named test, every time.""",
    [{"question": "A research question asks whether there is a difference in scores between the same 30 students before and after training. The design is:",
      "choices": ["Two independent groups", "One group measured twice (related/paired)",
                  "Three or more groups", "An association between two continuous variables"], "correct": 1},
     {"question": "Statistical hypotheses should be written about:",
      "choices": ["Sample statistics such as x-bar", "Population parameters such as mu",
                  "The p-value", "The sample size"], "correct": 1}],
    preview=True,
)


# ===========================================================================
L(
    "Choosing the Right Test: A Decision Framework",
    """## What you will be able to do

Walk any research question through a four-question decision tree and arrive at a named test -- and know the nonparametric alternative for each, so a violated assumption never leaves you stuck.

## The four questions

<div class="callout callout-key" markdown="1">
<span class="callout-label">Ask in this order, every time</span>

1. **Am I looking at a difference between groups, or a relationship between variables?**
2. **What is the measurement level of my outcome?**
3. **How many groups or measurements?**
4. **Are the groups independent, or related (same people measured more than once)?**
</div>

Four answers, one test. No memorising a list.

## The full decision table

### Differences, continuous outcome

| Groups | Design | Parametric test | Nonparametric alternative |
|---|---|---|---|
| 1 vs a fixed value | -- | One-sample *t*-test | Wilcoxon signed-rank |
| 2 | Independent | Independent-samples *t*-test | Mann-Whitney *U* |
| 2 | Related | Paired-samples *t*-test | Wilcoxon signed-rank |
| 3+ | Independent | One-way ANOVA | Kruskal-Wallis *H* |
| 3+ | Related | Repeated-measures ANOVA | Friedman |
| 2+ IVs | Independent | Factorial ANOVA | (no clean equivalent) |
| 2+ with covariate | Independent | ANCOVA | (quantile regression) |

### Differences, categorical outcome

| Situation | Test |
|---|---|
| One categorical variable against expected proportions | Chi-square goodness of fit |
| Two categorical variables, independent | Chi-square test of independence |
| Two categorical variables, sparse cells | Fisher's exact test |
| Same subjects, binary outcome, measured twice | McNemar |

### Relationships

| Both variables | Test |
|---|---|
| Interval/ratio, linear | Pearson *r* |
| Ordinal, or non-linear monotone, or outliers present | Spearman rho |
| One continuous outcome predicted from 1+ predictors | Linear regression |
| Binary outcome predicted from 1+ predictors | Logistic regression |

## Working our study through it

<div class="callout callout-case" markdown="1">
<span class="callout-label">Our study</span>
Two sections, module vs lecture, posttest achievement scores.

1. **Difference or relationship?** Difference -- I am comparing two groups.
2. **Outcome level?** Posttest score, ratio. Continuous.
3. **How many groups?** Two.
4. **Independent or related?** Independent -- different students in each section.

&rarr; **Independent-samples *t*-test.**
</div>

## Checking assumptions, and what to do when they fail

Each test carries assumptions. Checking them is not a formality -- it decides whether your p-value means anything.

### Independent-samples t-test

| Assumption | How to check | If violated |
|---|---|---|
| Independent observations | By design | No fix. Use a paired or multilevel model |
| Continuous outcome | Measurement level | Use chi-square or logistic regression |
| Approximate normality **within each group** | Shapiro-Wilk, Q-Q plot | Large n: proceed. Small n: Mann-Whitney |
| Equal variances (homogeneity) | **Levene's test** | Use **Welch's** t-test |

<div class="callout callout-key" markdown="1">
<span class="callout-label">How to read Levene's test</span>
Levene's null hypothesis is that the variances **are equal**. So:

- **Levene p > .05** &rarr; variances are similar &rarr; use the standard ("equal variances assumed") row
- **Levene p < .05** &rarr; variances differ &rarr; use **Welch's** ("equal variances not assumed") row

This is the one place where a **non-significant** result is what you want. Students routinely misread it.

Our data: **Levene p = .704**, so variances are comparable and the standard t-test is appropriate.
</div>

### Normality: check the right thing

For an independent t-test, normality is assumed **within each group separately**, not for the combined dataset. Running Shapiro-Wilk on all 30 scores pooled is the wrong test -- a genuine group difference makes the pooled distribution bimodal and the test rejects for the wrong reason.

Our data:
```
Shapiro-Wilk, control group   : W = .998, p = .999
Shapiro-Wilk, treatment group : W = .988, p = .988
```
Neither rejects. Normality is satisfied.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Do not over-trust normality tests</span>
With **n over about 300**, Shapiro-Wilk rejects departures far too small to matter. With **n under about 20** it has almost no power and misses real ones.

Use the **Q-Q plot** as your primary evidence and the test as support. And remember the t-test is fairly robust to moderate non-normality once each group has 15 or more cases.
</div>

## Parametric or nonparametric: deciding honestly

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The wrong way to decide</span>
Running a normality test, and switching to nonparametric whenever it rejects, is **not** a defensible procedure. It makes your choice of test depend on the data, which inflates your error rate.

Decide from three things, in this order:

1. **The measurement level.** Ordinal outcome &rarr; nonparametric, full stop.
2. **The sample size.** Under about 15 per group, normality matters a lot and is hard to verify.
3. **A plot.** Obvious severe skew or extreme outliers &rarr; nonparametric.

State your decision rule in Chapter 3, **before** you see results.
</div>

## Two or more IVs

If you have two grouping variables -- say teaching method **and** sex -- you have three questions, not one:

- Main effect of method
- Main effect of sex
- **Interaction**: does the method work differently for different sexes?

That is a **two-way ANOVA**, and the interaction is usually the interesting part. Running two separate t-tests instead cannot test the interaction at all, and inflates your error rate by testing twice.

## Doing it in software

### Jamovi
The menu mirrors the decision tree:

- **T-Tests** &rarr; Independent Samples / Paired Samples / One Sample
- **ANOVA** &rarr; One-Way ANOVA / ANOVA / Repeated Measures ANOVA / ANCOVA
- **Regression** &rarr; Correlation Matrix / Linear Regression / Logistic Regression
- **Frequencies** &rarr; the chi-square family

Every T-Test and ANOVA panel has an **Assumption Checks** section. Tick **Normality test**, **Q-Q plot** and **Homogeneity test** every time.

### SPSS
- <kbd>Analyze</kbd> &rarr; <kbd>Compare Means</kbd> &rarr; the t-tests and One-Way ANOVA
- <kbd>Analyze</kbd> &rarr; <kbd>General Linear Model</kbd> &rarr; Univariate (factorial ANOVA, ANCOVA)
- <kbd>Analyze</kbd> &rarr; <kbd>Nonparametric Tests</kbd> &rarr; Independent / Related Samples
- Levene's test appears automatically in the Independent-Samples T Test output

### R
```r
# independent samples
t.test(score ~ group, data = dat, var.equal = TRUE)    # standard
t.test(score ~ group, data = dat)                      # Welch, R's default

# assumption checks
car::leveneTest(score ~ group, data = dat)
by(dat$score, dat$group, shapiro.test)                 # per group, not pooled

# nonparametric alternative
wilcox.test(score ~ group, data = dat)
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">R's default differs from SPSS</span>
`t.test()` in R runs **Welch's** test by default. SPSS shows both rows and most students quote the standard one.

They usually agree, but when group sizes and variances both differ they can diverge. Say which you used. Welch is the safer default and many methodologists now recommend it routinely.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- Chapter 3, data analysis</span>
Data were analysed using *jamovi 2.3*. Descriptive statistics (mean, standard deviation) summarised achievement by group. An independent-samples *t*-test compared posttest scores between the *module* and *lecture* groups. Normality was assessed within each group using the Shapiro-Wilk test and Q-Q plots; homogeneity of variance was assessed using Levene's test. Cohen's *d* was computed as the measure of effect size. The level of significance was set at *.05*.
</div>

Write this paragraph **before** you run anything. It becomes your pre-registration, and it is the cleanest possible answer to a panel asking whether the analysis was decided in advance.

## Common mistakes

- **Reading Levene backwards.** p > .05 means equal variances, which is what you want.
- **Testing normality on pooled data** instead of within each group.
- **Choosing the test after seeing which gives a smaller p.**
- **Running multiple t-tests instead of ANOVA.** Three groups means three pairwise tests, and the family-wise error rate climbs to about .14.
- **Using a parametric test on an ordinal outcome** without justification.
- **Ignoring the related/independent distinction.** The single most consequential error in the tree.

## Practice

**1.** A researcher compares mean job satisfaction across four departments. Satisfaction is a summated 20-item scale. Which test, and what is the nonparametric alternative?

<details markdown="1">
<summary>Show the answer</summary>

Walk the tree:

1. **Difference or relationship?** Difference.
2. **Outcome level?** Summated scale across 20 items -- conventionally treated as **interval**. Continuous.
3. **How many groups?** Four.
4. **Independent or related?** Independent -- different employees in each department.

&rarr; **One-way ANOVA.**

**Nonparametric alternative:** **Kruskal-Wallis H**.

**Two things to add:**

- ANOVA is an **omnibus** test. A significant F says the four means are not all equal; it does not say which differ. Follow with a post-hoc test -- **Tukey's HSD** if all pairwise comparisons matter.
- Check **Levene's test**. With four groups of unequal size and unequal variance, use **Welch's ANOVA** and **Games-Howell** post-hocs instead.
</details>

**2.** Levene's test returns p = .03. What do you do?

<details markdown="1">
<summary>Show the answer</summary>

**p = .03 is below .05, so the null of equal variances is rejected. The variances differ.**

**Do not use the standard t-test row.** Use **Welch's t-test** -- SPSS's "Equal variances not assumed" row, and R's default.

What Welch does: it does not pool the two variances into one estimate. It uses each group's own variance and adjusts the degrees of freedom downward (often to a non-integer value like 27.78). That adjustment is what keeps the error rate correct.

**What not to do:**

- Transform the data purely to fix the variance. You may, but the interpretation changes and Welch is simpler.
- Delete cases from the more variable group.
- Report the standard t-test with a footnote acknowledging the violation.

**Worth noting:** many methodologists now recommend using Welch's test **routinely**, regardless of Levene, because it performs as well as the standard test when variances are equal and much better when they are not. Deciding in advance to always use Welch is a defensible, pre-registerable rule.
</details>

**3.** A student wants to compare pretest and posttest scores for one group of 25, and also compare that group against a control group's posttest. How many tests, and which ones?

<details markdown="1">
<summary>Show the answer</summary>

**Two different questions, two different designs, two different tests.**

**Question 1 -- did the treatment group improve?**
Same 25 students measured twice &rarr; **related** design &rarr; **paired-samples t-test** on the within-person differences.

**Question 2 -- did the treatment group outperform the control at posttest?**
Different students in each group &rarr; **independent** design &rarr; **independent-samples t-test** on posttest scores.

**The design point that matters more than the tests:** question 1 alone cannot establish the treatment worked. A single group measured before and after is confounded with maturation, practice effects on the test, and anything else that happened during the period. The control group in question 2 is what makes the comparison interpretable.

**A better single analysis:** **ANCOVA** on posttest scores, with group as the factor and **pretest as the covariate**. This answers "did the groups differ at posttest, adjusting for where they started" in one test, uses all the information, and has more power than either t-test alone. For a non-equivalent control group design, which ours is, ANCOVA is the standard recommendation.
</details>

## Before you move on

- [ ] I can run the four questions from memory and land on a named test
- [ ] I know the nonparametric alternative for each parametric test
- [ ] I read Levene's test correctly: p > .05 means equal variances
- [ ] I test normality within each group, not on pooled data
- [ ] My decision rule for parametric vs nonparametric is written in Chapter 3, in advance
- [ ] I know that three or more groups means ANOVA, not repeated t-tests

Next: we run the test and read every number the software gives back.""",
    [{"question": "Levene's test returns p = .70. What does this tell you?",
      "choices": ["The groups differ significantly", "The variances are similar, so the standard t-test is appropriate",
                  "You must use Welch's test", "The data is not normal"], "correct": 1},
     {"question": "Comparing four group means on a continuous outcome calls for:",
      "choices": ["Six independent t-tests", "One-way ANOVA followed by post-hoc tests",
                  "Chi-square", "Pearson correlation"], "correct": 1}],
)


# ===========================================================================
L(
    "Reading and Reporting Output the Way a Panel Expects",
    """## What you will be able to do

Run the independent-samples t-test on our study by hand, then read every number in the software output and convert it into an APA sentence and a defence-ready table. You will also see, with real numbers, what happens when a paired design is analysed as independent.

## Computing it by hand first

Do it once by hand and the output stops being mysterious.

<div class="callout callout-case" markdown="1">
<span class="callout-label">Our data</span>

| Group | n | Mean | SD |
|---|---:|---:|---:|
| Control (lecture) | 15 | 72.00 | 5.68 |
| Treatment (module) | 15 | 78.67 | 6.21 |
</div>

### Step 1 -- pool the two variances

Because we are assuming equal variances (Levene said we may), the two group variances are combined into one estimate, weighted by degrees of freedom.

<div class="formula" markdown="1">
**s&sup2;<sub>p</sub> = [ (n&#8321;&minus;1)s&#8321;&sup2; + (n&#8322;&minus;1)s&#8322;&sup2; ] / (n&#8321; + n&#8322; &minus; 2)**
</div>

```
s1^2 = 5.68^2 = 32.29
s2^2 = 6.21^2 = 38.52

s^2_p = [14 x 32.29 + 14 x 38.52] / (15 + 15 - 2)
      = [452.06 + 539.28] / 28
      = 991.34 / 28
      = 35.40

s_p = sqrt(35.40) = 5.95
```

### Step 2 -- the standard error of the difference

<div class="formula" markdown="1">
**SE = s<sub>p</sub> &times; &radic;(1/n&#8321; + 1/n&#8322;)**
</div>

```
SE = 5.95 x sqrt(1/15 + 1/15)
   = 5.95 x sqrt(0.1333)
   = 5.95 x 0.3651
   = 2.173
```

### Step 3 -- t and df

<div class="formula" markdown="1">
**t = (x&#772;&#8321; &minus; x&#772;&#8322;) / SE** &nbsp;&nbsp;&nbsp; **df = n&#8321; + n&#8322; &minus; 2**
</div>

```
t  = (78.67 - 72.00) / 2.173
   = 6.67 / 2.173
   = 3.068

df = 15 + 15 - 2 = 28
```

### Step 4 -- decide

```
critical t(.025, 28) = 2.048
|3.068| > 2.048        ->  reject H0
p = .0047              ->  .0047 < .05, reject H0
```

### Step 5 -- effect size

<div class="formula" markdown="1">
**Cohen's d = (x&#772;&#8321; &minus; x&#772;&#8322;) / s<sub>p</sub>**
</div>

```
d = 6.67 / 5.95 = 1.12
```

By convention 0.2 is small, 0.5 medium, 0.8 large. **d = 1.12 is a large effect.**

### Step 6 -- confidence interval for the difference

```
95% CI = 6.67 +/- 2.048 x 2.173
       = 6.67 +/- 4.45
       = [2.22, 11.12]
```

The interval **excludes zero**, which is the same fact as p < .05 seen a second way.

## Reading the output

SPSS gives you this. Every number is one you just computed.

```
Group Statistics
              group        N      Mean    Std. Deviation   Std. Error Mean
score         lecture     15     72.00        5.682             1.467
              module      15     78.67         6.207            1.603

Independent Samples Test

                     Levene's Test          t-test for Equality of Means
                      F      Sig.        t      df   Sig.(2-t)  Mean Diff  SE Diff   95% CI
Equal var assumed    0.148   .704      3.068    28     .005       6.667     2.173   [2.22, 11.12]
Equal var not assumed                  3.068  27.78    .005       6.667     2.173   [2.22, 11.12]
```

Read it in this order:

1. **Levene's Sig. = .704.** Above .05, so variances are comparable &rarr; use the **first** row.
2. **t = 3.068, df = 28.** Matches our hand calculation.
3. **Sig. (2-tailed) = .005.** This is the p-value. Below .05.
4. **Mean Difference = 6.667** in the original score points.
5. **95% CI [2.22, 11.12].** Excludes zero.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">SPSS prints .000. Never write it.</span>
When p is very small SPSS displays `.000`. No p-value is exactly zero.

**Write *p* < .001.** Writing *p* = .000 is the single most reliable way to tell a panel that the student does not understand what a p-value is.
</div>

## What happens if you get the design wrong

Here is why lesson 2 insisted on the independent/related distinction. A separate pre/post dataset, 10 students:

| | Sum | Mean |
|---|---:|---:|
| Pretest | 680 | 68.00 |
| Posttest | 740 | 74.00 |
| Differences | 60 | 6.00 |

**Analysed correctly as paired:**
```
SD of differences = 3.56
SE = 3.56 / sqrt(10) = 1.126
t  = 6.00 / 1.126 = 5.331,  df = 9
p  = .0005        ->  SIGNIFICANT
dz = 6.00 / 3.56  = 1.69   (large)
95% CI [3.45, 8.55]
```

**The same 20 numbers analysed wrongly as independent:**
```
t = -2.02, df = 18
p = .058    ->  NOT significant
```

<div class="callout callout-key" markdown="1">
<span class="callout-label">Same data. Opposite conclusion.</span>
The paired test is more powerful because it removes **between-person variation**. Students differ a lot from each other (SD about 6) but each student's *gain* is far more consistent (SD 3.56). The paired test works on the gains and ignores the noise.

Throwing away the pairing threw away the study.
</div>

## The table your Chapter 4 needs

Panels expect a table, not a paragraph of numbers.

| Group | n | Mean | SD | t | df | p | Cohen's d |
|---|---:|---:|---:|---:|---:|---:|---:|
| Lecture | 15 | 72.00 | 5.68 | | | | |
| Module | 15 | 78.67 | 6.21 | 3.07 | 28 | .005 | 1.12 |

Rules for APA tables:

- No vertical lines; horizontal lines only at the top, under the headers, and at the bottom
- Table number and title **above** the table, title in italics
- Notes below, starting with *Note.*
- Align decimals; two decimal places throughout
- Every abbreviation defined in the note

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- significant independent-samples result</span>
An independent-samples *t*-test was conducted to compare posttest achievement between students taught with the *self-paced module* and those taught by *conventional lecture*. Levene's test indicated equal variances (*F* = *0.15*, *p* = *.704*). There was a significant difference in scores between the *module* group (*M* = *78.67*, *SD* = *6.21*) and the *lecture* group (*M* = *72.00*, *SD* = *5.68*); *t*(*28*) = *3.07*, *p* = *.005*, *d* = *1.12*, 95% CI [*2.22*, *11.12*]. The magnitude of the difference was *large*.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- paired result</span>
A paired-samples *t*-test showed a significant increase from pretest (*M* = *68.00*) to posttest (*M* = *74.00*), a mean gain of *6.00* points, *t*(*9*) = *5.33*, *p* &lt; *.001*, *d<sub>z</sub>* = *1.69*, 95% CI [*3.45*, *8.55*].
</div>

Every element is required: both means with SDs, the test statistic with df, the exact p, an effect size, and the confidence interval.

## Doing it in software

### Jamovi
1. **Analyses** &rarr; **T-Tests** &rarr; **Independent Samples T-Test**
2. `score` into **Dependent Variables**, `group` into **Grouping Variable**
3. **Tests**: tick **Student's** and **Welch's**
4. **Additional Statistics**: tick **Mean difference**, **Confidence interval**, **Effect size**, **Descriptives**
5. **Assumption Checks**: tick **Normality test**, **Q-Q plot**, **Homogeneity test**

Jamovi output is already APA-formatted, which saves retyping and retyping is where transcription errors come from.

### SPSS
<kbd>Analyze</kbd> &rarr; <kbd>Compare Means</kbd> &rarr; <kbd>Independent-Samples T Test</kbd>. Put `score` in **Test Variable(s)**, `group` in **Grouping Variable**, click **Define Groups** and enter the two codes. SPSS does not give Cohen's d in older versions -- compute it by hand from the output.

### Excel
```
=T.TEST(A2:A16, B2:B16, 2, 2)   -> 0.0047   two-tailed, equal variance
=T.TEST(A2:A16, B2:B16, 2, 3)   -> Welch
=T.TEST(A2:A16, B2:B16, 2, 1)   -> paired
```
The third argument is tails, the fourth is type: 1 = paired, 2 = equal variance, 3 = Welch.

### R
```r
t.test(score ~ group, data = dat, var.equal = TRUE)
#   t = 3.0684, df = 28, p-value = 0.00474
#   95 percent confidence interval: 2.2161 11.1172
#   mean in group module 78.66667   mean in group lecture 72.00000

effectsize::cohens_d(score ~ group, data = dat)   # 1.12
car::leveneTest(score ~ group, data = dat)        # F = 0.148, p = 0.704

# paired
t.test(post, pre, paired = TRUE)   # t = 5.331, df = 9, p = 0.000474
```

## Common mistakes

- **Writing p = .000.** Write *p* < .001.
- **Omitting the effect size.** A p-value with no d is half a result.
- **Omitting the confidence interval.** Increasingly required by journals.
- **Reporting the wrong Levene row.**
- **Reporting a t with no df.** *t* = 3.07 alone is uninterpretable.
- **Not reporting both group means and SDs.**
- **Pasting raw SPSS output into the thesis.** Build a proper APA table.

## Practice

**1.** Two groups: n&#8321; = 20, M&#8321; = 45.2, SD&#8321; = 8.1; n&#8322; = 20, M&#8322; = 50.6, SD&#8322; = 7.4. Compute the pooled SD, SE, t, df and Cohen's d.

<details markdown="1">
<summary>Show the worked answer</summary>

```
Step 1  pooled variance
        s1^2 = 8.1^2 = 65.61     s2^2 = 7.4^2 = 54.76
        s^2_p = [19 x 65.61 + 19 x 54.76] / 38
              = [1246.59 + 1040.44] / 38
              = 2287.03 / 38
              = 60.19
        s_p = sqrt(60.19) = 7.76

Step 2  SE = 7.76 x sqrt(1/20 + 1/20)
           = 7.76 x sqrt(0.10)
           = 7.76 x 0.3162
           = 2.454

Step 3  t  = (50.6 - 45.2) / 2.454 = 5.4 / 2.454 = 2.20
        df = 20 + 20 - 2 = 38

Step 4  critical t(.025, 38) = 2.024
        2.20 > 2.024  ->  significant, p = .034

Step 5  d = 5.4 / 7.76 = 0.70   (medium to large)
```

**Report:** *t*(38) = 2.20, *p* = .034, *d* = 0.70.

Note how close this is to the boundary. With a slightly smaller sample it would not have reached significance, while the effect size would be unchanged -- which is exactly why d must be reported alongside p.
</details>

**2.** A thesis reports: "There was a significant difference between groups (p = .000)." List everything wrong.

<details markdown="1">
<summary>Show the answer</summary>

**Five problems:**

1. **p = .000 is impossible.** Write *p* < .001.
2. **No test statistic or df.** Which test was this? *t*(28) = 3.07 is required.
3. **No group means or SDs.** The reader cannot tell which group scored higher, or by how much.
4. **No effect size.** Significant tells you it is detectable, not whether it matters.
5. **No confidence interval.** The plausible range of the difference is missing.

**Also worth noting:** "a significant difference between groups" does not say the **direction**. A reader should never have to guess which group did better.

**The corrected sentence:**

> Students taught with the module (*M* = 78.67, *SD* = 6.21) scored significantly higher than those taught by lecture (*M* = 72.00, *SD* = 5.68), *t*(28) = 3.07, *p* = .005, *d* = 1.12, 95% CI [2.22, 11.12].

One sentence, every required element, direction unambiguous.
</details>

**3.** Your paired t-test gives t(9) = 5.33, p < .001, but your supervisor says "the sample is only 10, that cannot be significant." How do you respond?

<details markdown="1">
<summary>Show the answer</summary>

**Small samples can absolutely produce significant results when the effect is large relative to the variability.** Significance depends on the ratio of effect to noise, not on n alone.

The specifics here:

```
mean gain      = 6.00 points
SD of gains    = 3.56 points
SE             = 3.56 / sqrt(10) = 1.126
t              = 6.00 / 1.126 = 5.33
```

The gain is over five standard errors from zero. Even with only 9 degrees of freedom, where the critical value is a demanding 2.262, that clears the bar comfortably.

**Why the paired design makes this possible:** it removes between-person differences entirely. Students vary a lot from each other, but each student's *own* gain is consistent -- every one of the 10 improved, by between 2 and 11 points. That consistency is what drives the large t.

**What the supervisor is right to worry about, though:**

- **Generalisability.** Ten students from one section will not represent a population. Significance is not external validity.
- **No control group.** A significant pre-post gain cannot separate the intervention from maturation or practice effects on the test.

So the honest response: the statistic is correct and defensible; the **design** is what limits the conclusion, not the sample size.
</details>

## Before you move on

- [ ] I can compute pooled SD, SE, t, df and Cohen's d by hand
- [ ] I read the Levene row first and pick the correct t row
- [ ] I never write p = .000
- [ ] Every result sentence has both means, SDs, t, df, p, an effect size and a CI
- [ ] I can explain why the paired test is more powerful, with the numbers
- [ ] I build an APA table rather than pasting software output

Next: the errors that panels catch most often, and how to avoid every one.""",
    [{"question": "SPSS displays Sig. = .000. How should this be reported?",
      "choices": ["p = .000", "p < .001", "p = 0", "p is not significant"], "correct": 1},
     {"question": "Why is a paired t-test usually more powerful than an independent t-test on the same measurements?",
      "choices": ["It uses a larger sample", "It removes between-person variation by working on within-person differences",
                  "It has more degrees of freedom", "It assumes normality"], "correct": 1}],
)


# ===========================================================================
L(
    "Common Mistakes That Get Flagged in Defense",
    """## What you will be able to do

Run a pre-defence audit on your own Chapter 4 and catch the twelve errors panels raise most often -- before the panel does.

## Why this lesson exists

Panels ask a narrow, predictable set of questions. Almost none of them are about advanced statistics. They are about whether you understand what you already ran.

<div class="callout callout-key" markdown="1">
<span class="callout-label">The pattern</span>
A panel member rarely knows your topic better than you do. What they can always check is whether your **numbers, your design and your sentences agree with each other.** Every item below is a place where they commonly do not.
</div>

## The twelve, with the fix

### 1. Claiming causation from a correlational design

**Flagged as:** "You wrote that X *improves* Y. How do you know it is not the reverse?"

**The fix.** Unless you randomly assigned participants, use **associational verbs**: *is associated with*, *is related to*, *predicts*. Never *causes*, *improves*, *affects*, *leads to*, *results in*.

Our own study uses intact sections, so even with p = .005 the defensible sentence is *"students taught with the module scored significantly higher,"* not *"the module caused higher scores."*

### 2. Accepting the null hypothesis

**Flagged as:** "You concluded there is no difference. Can you prove that?"

**The fix.** You **fail to reject**. Absence of evidence is not evidence of absence, especially with a small sample. If equivalence is genuinely your claim, it needs an **equivalence test** with a pre-specified margin -- a different procedure entirely.

### 3. p = .000

**The fix.** Write ***p* < .001**. Always.

### 4. No effect size

**Flagged as:** "It is significant, but is it important?"

**The fix.** Report *d*, &eta;&sup2;, *r*, &phi; or Cram&eacute;r's *V* beside every p-value, with its conventional label.

| Test | Effect size | Small / Medium / Large |
|---|---|---|
| t-test | Cohen's *d* | .20 / .50 / .80 |
| ANOVA | eta-squared | .01 / .06 / .14 |
| Correlation | *r* | .10 / .30 / .50 |
| Chi-square | &phi; or Cram&eacute;r's *V* | .10 / .30 / .50 |

### 5. Assumptions never mentioned

**Flagged as:** "Did you check normality?"

**The fix.** A short paragraph in Chapter 4 reporting Shapiro-Wilk (per group), Levene's test, and what you concluded. Silence reads as "did not check."

### 6. Wrong test for the design

**Flagged as:** "These are the same students measured twice. Why an independent t-test?"

**The fix.** Run the four questions from lesson 2. You saw the cost in lesson 3: p = .0005 correct, p = .058 wrong.

### 7. Multiple t-tests instead of ANOVA

**Flagged as:** "You ran six t-tests. What is your actual error rate?"

**The fix.** With three groups you have three comparisons and a family-wise error rate of about **.14**, not .05. With four groups, six comparisons and about **.26**.

```
family-wise alpha = 1 - (1 - .05)^number of comparisons
3 comparisons: 1 - .95^3 = .1426
6 comparisons: 1 - .95^6 = .2649
```

Run **one ANOVA**, then post-hoc tests with an adjustment.

### 8. Sample size never justified

**Flagged as:** "Why 30 respondents?"

**The fix.** An a-priori power analysis, covered in the next lesson. "It was what I could get" is honest but weak; "G*Power indicated 64 per group for a medium effect at 80% power; I obtained 30, so the study was powered only to detect large effects" is a defensible limitation.

### 9. Ignoring the sampling design

**Flagged as:** "You sampled by barangay clusters but analysed as simple random. What happened to the design effect?"

**The fix.** Clustered samples need standard errors that account for clustering, or at minimum an acknowledged design effect. Convenience samples cannot support population inference at all -- say so.

### 10. Tables that do not match the text

**Flagged as:** "Your text says 78.67 but Table 5 says 78.60."

**The fix.** Generate tables from output; never retype. Check every number in the text against its table before printing. This one destroys credibility disproportionately, because it is checkable in seconds.

### 11. Over-interpreting a non-significant trend

**Flagged as:** "What does 'approaching significance' mean?"

**The fix.** Nothing. It is not a thing. Report the exact p and the effect size, and let the reader judge. *p* = .073 with *d* = 0.74 is honestly described as "a medium-sized difference that this sample was not powered to detect."

### 12. Conclusions wider than the sample

**Flagged as:** "You studied one school. Your conclusion says 'Filipino students.'"

**The fix.** Conclusions must match the sampling frame. One school means one school. Say so and put the rest in Recommendations.

## The pre-defence audit

Work this checklist on your own Chapter 4 the week before.

<div class="callout callout-key" markdown="1">
<span class="callout-label">Numbers</span>

- [ ] Every number in the text matches its table exactly
- [ ] No *p* = .000 anywhere
- [ ] Every p-value has a test statistic and df beside it
- [ ] Every inferential result has an effect size
- [ ] Every mean has an SD
- [ ] Decimal places are consistent, normally two
- [ ] *n* reported for every group, and they sum to the stated total
</div>

<div class="callout callout-key" markdown="1">
<span class="callout-label">Logic</span>

- [ ] Every numbered problem has exactly one analysis
- [ ] Every analysis answers a numbered problem
- [ ] The test matches the design (groups, level, independent/related)
- [ ] Assumptions are reported, not just checked
- [ ] Causal language appears only if I randomly assigned
- [ ] Conclusions do not exceed the sampling frame
- [ ] Limitations name the design's actual weaknesses
</div>

## Practising the answers out loud

Prepare a one-sentence answer for each. Rehearse them.

| Question | Your answer should contain |
|---|---|
| Why this test? | Design, measurement level, number of groups |
| Did you check assumptions? | The test names and their p-values |
| Why this sample size? | The power analysis, or an honest limitation |
| What does your p-value mean? | Probability of data this extreme **if H&#8320; were true** |
| Is the effect important? | The effect size and its label |
| Can you claim causation? | Only with random assignment |
| What are your limitations? | Design, sampling, instrument, generalisability |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The answer that ends badly</span>
*"That is what the software gave."*

Panels are testing whether you understand the analysis or merely operated it. If you cannot explain why a number is what it is, you have found something to study before the defence -- not something to bluff.
</div>

## Practice

**1.** A thesis concludes: "Since p = .08 > .05, the null hypothesis is accepted. There is no difference between the two teaching methods." Rewrite it.

<details markdown="1">
<summary>Show the answer</summary>

Two errors: **accepting** the null, and asserting **no difference**.

**Corrected:**

> Since *p* = .08 exceeds the .05 level, the null hypothesis is **not rejected**. The study did not detect a statistically significant difference between the two teaching methods.

**Better still**, add what the study could actually see:

> ...*t*(28) = 1.81, *p* = .081, *d* = 0.66. Although the difference did not reach significance, the effect size was medium, and with 15 per group the study had approximately 38% power to detect an effect of this magnitude. A larger sample is needed before concluding the methods are equivalent.

That version is honest, quantified, and pre-empts the obvious follow-up question.
</details>

**2.** A researcher compares five barangays on mean household income using ten pairwise t-tests at &alpha; = .05. What is the real error rate, and what should they have done?

<details markdown="1">
<summary>Show the worked answer</summary>

```
Number of pairwise comparisons with 5 groups = 5 x 4 / 2 = 10

family-wise alpha = 1 - (1 - .05)^10
                  = 1 - .95^10
                  = 1 - .5987
                  = .4013
```

**About a 40% chance of at least one false positive**, if all five barangays truly have the same mean income. That is eight times the claimed rate.

**What they should have done:**

1. **One-way ANOVA** as the omnibus test. If F is not significant, stop.
2. If F **is** significant, run post-hoc comparisons with an adjustment -- **Tukey's HSD** for all pairs, which controls the family-wise rate at .05.
3. Check assumptions first. Household income is nearly always right-skewed, so either log-transform or use **Kruskal-Wallis** with Dunn's post-hoc.

**A design point:** if only specific comparisons were of interest -- say, each barangay against the municipal average -- **planned contrasts** or **Dunnett's test** would give more power than all-pairs procedures, because they make fewer comparisons.
</details>

**3.** Your Table 5 reports M = 78.67 but your text says "approximately 79." Is that acceptable?

<details markdown="1">
<summary>Show the answer</summary>

**In prose, yes -- with care. In a results statement, no.**

Acceptable in discussion: *"Students in the module group averaged approximately 79 points, nearly seven points above the lecture group."* Rounding for readability in interpretive text is normal.

**Not acceptable** in the formal results sentence. That must carry the exact figure matching the table:

> *(M* = 78.67, *SD* = 6.21)

**The rule:** the **Results** section is a precise record and must match the tables digit for digit. The **Discussion** may round for readability, provided it never contradicts the table.

**What panels actually flag** is inconsistency they cannot explain -- 78.67 in one place and 78.60 in another. That looks like a transcription error or, worse, a figure that changed between analyses. Generate tables from output rather than retyping, and the problem disappears.
</details>

## Before you move on

- [ ] I have run the numbers checklist on my own Chapter 4
- [ ] I have run the logic checklist
- [ ] My verbs match my design -- no causal language without random assignment
- [ ] I can give a one-sentence answer to each of the seven panel questions
- [ ] I know the family-wise error rate for the number of comparisons I ran

Next: the question "why this sample size?" deserves a real answer.""",
    [{"question": "Running 10 pairwise t-tests at alpha = .05 gives a family-wise error rate of about:",
      "choices": [".05", ".40", ".10", ".50"], "correct": 1},
     {"question": "Without random assignment, which verb is defensible?",
      "choices": ["caused", "improved", "is associated with", "resulted in"], "correct": 2}],
)


# ===========================================================================
L(
    "Sample Size and Power Analysis for Your Specific Test",
    """## What you will be able to do

Compute the sample size your study actually needs before collecting a single case, and -- if the data is already collected -- report an honest power limitation that a panel will accept.

## The question you will be asked

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
Panel member: *"Why did you use 30 respondents?"*

Candidate: *"That was the size of the section."*

That answer is honest and weak. This lesson gives you the strong version -- and shows you how to salvage the situation when the data is already in.
</div>

## The four quantities

Power analysis relates four things. **Fix any three and the fourth is determined.**

| Quantity | Symbol | Usual value | Meaning |
|---|---|---|---|
| Significance level | &alpha; | .05 | Chance of a false positive |
| Power | 1 &minus; &beta; | .80 | Chance of detecting a real effect |
| Effect size | *d*, *f*, *r* | from theory | How big the effect is |
| Sample size | *n* | what you solve for | Cases needed |

<div class="callout callout-key" markdown="1">
<span class="callout-label">What power means</span>
**Power is the probability of correctly rejecting a false null hypothesis** -- of finding an effect that is really there.

Power of .80 means: if the effect truly exists at the size you specified, you have an 80% chance of detecting it, and a **20% chance of missing it**. That 20% is &beta;, the Type II error rate.

Convention is .80. Some fields ask for .90. Below .80 your study is likely to waste everyone's time.
</div>

## The two directions

### A-priori: before data collection (what you should do)

Fix &alpha; = .05, power = .80, and the effect size you expect. Solve for **n**.

### Post-hoc: after data collection (mostly useless)

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Do not compute observed power</span>
Post-hoc power computed **from your own observed effect size** adds no information. It is a deterministic function of your p-value: a non-significant result always yields low observed power. Reporting it tells the reader nothing they did not already know from p.

**What is legitimate**: a **sensitivity analysis** -- given the n you actually had, what is the smallest effect you could have detected at 80% power? That is informative and defensible.
</div>

## Sample size for an independent t-test

The numbers you should know, for &alpha; = .05 two-tailed, power = .80, equal groups:

| Expected effect | Cohen's *d* | **n per group** | Total |
|---|---:|---:|---:|
| Small | 0.20 | **394** | 788 |
| Medium | 0.50 | **64** | 128 |
| Large | 0.80 | **26** | 52 |
| Very large (ours) | 1.12 | **14** | 28 |

<div class="callout callout-key" markdown="1">
<span class="callout-label">Read that table again</span>
Detecting a **small** effect needs nearly **400 per group**. This is why most thesis-scale studies can only detect large effects -- and why so many report non-significant results for effects that are probably real.

Our study had 15 per group. With the large effect we actually found (*d* = 1.12), power was **.84** -- adequate. Had the true effect been medium (*d* = 0.50), power would have been about **.26**, and we would most likely have missed it.
</div>

## Worked example: planning our study properly

**Step 1 -- choose the effect size you expect.** Three defensible sources, in order of preference:

1. **A meta-analysis** in your field. Best evidence.
2. **A previous similar study.** Take its reported *d*.
3. **The smallest effect that would matter practically.** For an achievement test, perhaps 5 points. With an expected SD of 6, that is *d* = 5/6 = 0.83.

Never pick an effect size because it gives you the n you can afford. That is the calculation run backwards.

**Step 2 -- set &alpha; and power.** &alpha; = .05, power = .80.

**Step 3 -- solve.** For *d* = 0.83, G*Power returns **n = 24 per group**, 48 total.

**Step 4 -- add for attrition.** Expect 10-20% loss. 24 &times; 1.2 &asymp; **29 per group**.

**Step 5 -- write it into Chapter 3** before collecting.

## Sample size for other tests

| Test | Effect size | Medium effect, 80% power |
|---|---|---|
| Independent t-test | *d* = 0.50 | 64 per group |
| Paired t-test | *d<sub>z</sub>* = 0.50 | 34 total |
| One-way ANOVA, 3 groups | *f* = 0.25 | 52 per group |
| Correlation | *r* = 0.30 | 85 total |
| Chi-square, 2&times;2 | *w* = 0.30 | 88 total |
| Multiple regression, 3 predictors | *f&sup2;* = 0.15 | 77 total |

Note the paired test needs about **half** the participants of the independent test for the same effect. That is the design advantage you saw numerically in lesson 3.

## Doing it in software

### G*Power (free, and what most panels recognise)

Download from the Heinrich Heine University Düsseldorf site. For our study:

1. **Test family**: `t tests`
2. **Statistical test**: `Means: Difference between two independent means (two groups)`
3. **Type of power analysis**: `A priori: Compute required sample size`
4. **Tails**: `Two`
5. **Effect size d**: `0.83`
6. **&alpha; err prob**: `0.05`
7. **Power (1-&beta;)**: `0.80`
8. **Allocation ratio N2/N1**: `1`
9. Click **Calculate**

Output gives **Sample size per group** and the total. Screenshot it for your appendix -- panels like seeing it.

G*Power also has an **Effect size drawer** that converts means and SDs into *d* for you.

### R
```r
install.packages("pwr")
library(pwr)

# independent t-test, n per group
pwr.t.test(d = 0.83, sig.level = 0.05, power = 0.80, type = "two.sample")
#   n = 23.9  ->  24 per group

# what could we detect with the 15 per group we actually had?
pwr.t.test(n = 15, sig.level = 0.05, power = 0.80, type = "two.sample")
#   d = 1.06  ->  sensitivity: only effects of d >= 1.06 were detectable

# power we actually had, given the effect we found
pwr.t.test(n = 15, d = 1.12, sig.level = 0.05, type = "two.sample")
#   power = 0.84

# one-way ANOVA
pwr.anova.test(k = 3, f = 0.25, sig.level = 0.05, power = 0.80)   # n = 52 per group

# correlation
pwr.r.test(r = 0.30, sig.level = 0.05, power = 0.80)              # n = 84.1 -> 85
```

### Jamovi
Install the **jpower** module from the module library (the `+` icon). It handles t-tests with a clear plot of the power curve, which is useful in a defence.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- a-priori, the strong version</span>
An a-priori power analysis was conducted using G*Power *3.1* to determine the required sample size. With *&alpha;* = *.05* (two-tailed), power = *.80*, and an expected effect size of *d* = *0.83* based on *Santos (2023)*, the analysis indicated a minimum of *24* participants per group. Anticipating *20%* attrition, *29* participants per group were recruited.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- the honest salvage, when data is already collected</span>
The sample comprised *15* participants per group, determined by the size of the available intact sections. A sensitivity analysis indicated that this sample provided *80%* power to detect effects of *d* &ge; *1.06* or larger. The study was therefore adequately powered to detect large effects but not small or medium ones, and the absence of a significant finding should not be interpreted as evidence of no effect. This is acknowledged as a limitation.
</div>

That second template is the one most theses need, and panels respect it far more than silence.

## Common mistakes

- **Reporting observed (post-hoc) power.** Use sensitivity analysis instead.
- **Choosing the effect size to justify the n you already have.** Backwards, and visible.
- **Ignoring attrition.** Recruit above the computed minimum.
- **Using a rule of thumb.** "30 is enough" is not a power analysis.
- **Running the analysis for the wrong test.** A paired design needs the paired calculation.
- **Confusing &alpha; and &beta;.** &alpha; is the false-positive rate; &beta; is the false-negative rate.

## Practice

**1.** You expect a medium correlation (*r* = .30) and want 80% power at &alpha; = .05. How many participants, and what if you can only get 50?

<details markdown="1">
<summary>Show the answer</summary>

**Required: n = 85.**

```r
pwr.r.test(r = 0.30, sig.level = 0.05, power = 0.80)   # n = 84.07 -> round up to 85
```

**With only 50**, run it the other way:

```r
pwr.r.test(n = 50, sig.level = 0.05, power = 0.80)     # r = 0.387
pwr.r.test(n = 50, r = 0.30, sig.level = 0.05)         # power = 0.56
```

Two honest statements, both reportable:

- **Sensitivity:** with 50 participants you can detect *r* &ge; **.39** at 80% power.
- **Power:** if the true correlation is .30, you have about a **56%** chance of detecting it -- worse than a coin flip on a real effect.

**What to write:**

> A sensitivity analysis indicated that the achieved sample of 50 provided 80% power to detect correlations of *r* = .39 or larger. The study was therefore underpowered to detect the medium-sized association anticipated, and a non-significant result should be interpreted with that limitation in mind.

**What to do if you can:** collect more. Going from 50 to 85 is 35 more participants for a jump from 56% to 80% power -- usually the cheapest improvement available to a thesis.
</details>

**2.** A panel member says "your study found no significant difference, so the intervention does not work." You had 12 per group. Respond.

<details markdown="1">
<summary>Show the answer</summary>

**Run the sensitivity analysis and let the number answer.**

```r
pwr.t.test(n = 12, sig.level = 0.05, power = 0.80, type = "two.sample")
#   d = 1.19
```

With 12 per group you could only reliably detect effects of *d* &ge; **1.19** -- a very large effect. Most educational interventions produce effects around *d* = 0.40.

```r
pwr.t.test(n = 12, d = 0.40, sig.level = 0.05, type = "two.sample")
#   power = 0.16
```

**Only a 16% chance of detecting a typical intervention effect.** The study was more than five times more likely to miss a real effect than to find it.

**The response:**

> The study did not detect a significant difference, but it was powered only to detect very large effects (*d* &ge; 1.19). For an effect of the size typically reported in this literature (*d* &asymp; 0.40), power was approximately 16%. The finding is therefore inconclusive rather than evidence that the intervention is ineffective. A study with approximately 100 per group would be needed to test this properly.

This turns a weakness into a demonstration that you understand your own design -- which is what the panel is actually assessing.
</details>

**3.** Why does a paired design need roughly half the participants of an independent design?

<details markdown="1">
<summary>Show the answer</summary>

**Because it removes between-person variation from the error term.**

In an **independent** design the noise includes everything that makes people differ from one another -- prior knowledge, aptitude, motivation. That variation sits in the denominator of t and makes the test less sensitive.

In a **paired** design each person is their own control. Subtracting pre from post cancels every stable individual characteristic. What remains is only the change, which is far less variable.

**The numbers from lesson 3 show it exactly:**

```
SD of individual scores   = about 6.0      <- between-person variation
SD of within-person gains = 3.56           <- much smaller
```

The standard error shrinks in proportion, t grows, and fewer participants are needed for the same power.

**The trade-off you must still respect:** a paired design cannot separate the intervention from maturation, practice effects on the instrument, or history. It is statistically more efficient and causally weaker unless you add a control group. The strongest common design combines both -- two groups, each measured pre and post, analysed with ANCOVA or a mixed ANOVA.
</details>

## Before you move on

- [ ] I can name the four quantities and know that fixing three determines the fourth
- [ ] I know roughly how many cases a small, medium and large effect needs
- [ ] I can run an a-priori analysis in G*Power or `pwr` for my own test
- [ ] I know why observed power is useless and sensitivity analysis is not
- [ ] I have a power paragraph, or an honest limitation paragraph, written for my study

Next: two words panels use interchangeably and which mean completely different things.""",
    [{"question": "For an independent t-test at alpha = .05 and 80% power, detecting a MEDIUM effect (d = 0.50) needs about how many per group?",
      "choices": ["26", "64", "394", "15"], "correct": 1},
     {"question": "After a non-significant result, which is the defensible analysis to report?",
      "choices": ["Observed (post-hoc) power from the obtained effect size",
                  "A sensitivity analysis showing the smallest detectable effect",
                  "Nothing; power is irrelevant afterwards",
                  "A repeat of the same test at alpha = .10"], "correct": 1}],
)


# ===========================================================================
L(
    "Mediation and Moderation: What's Actually Different",
    r"""## What you will be able to do

Tell mediation and moderation apart in one sentence, draw each as a path diagram, run both, and read the output. These two get confused constantly, and they answer completely different questions.

## The one-sentence distinction

<div class="callout callout-key" markdown="1">
<span class="callout-label">Learn this and the rest follows</span>

- **Mediation** answers ***how*** or ***why***. X affects Y **through** M. The mediator is the mechanism.
- **Moderation** answers ***when*** or ***for whom***. The effect of X on Y **depends on the level of** W. The moderator changes the strength of the relationship.

Mediation is a **chain**. Moderation is a **switch**.
</div>

| | Mediation | Moderation |
|---|---|---|
| Question | How does X affect Y? | When does X affect Y? |
| Variable role | M sits **between** X and Y | W **interacts with** X |
| Path | X &rarr; M &rarr; Y | X &times; W &rarr; Y |
| Timing | M must occur **after** X | W usually pre-exists |
| Tested by | Indirect effect (a &times; b) | Interaction term |

### The same study, both ways

**Mediation.** Study hours &rarr; self-efficacy &rarr; achievement.
*Studying raises confidence, and confidence raises achievement.* Self-efficacy is the mechanism.

**Moderation.** Study hours &rarr; achievement, moderated by sleep quality.
*Studying helps a lot for well-rested students and barely at all for exhausted ones.* Sleep is the condition.

## Mediation, step by step

### The three paths

```
                 M  (self-efficacy)
               /   \
          a  /       \  b
           /           \
         X --------------> Y
       (hours)    c'     (achievement)

   c  = total effect of X on Y        (before M enters)
   c' = direct effect of X on Y       (with M in the model)
   ab = indirect effect through M
```

<div class="formula" markdown="1">
**c = c&prime; + ab**
<span class="formula-note">the total effect decomposes exactly into direct plus indirect</span>
</div>

### Worked example with real output

<div class="callout callout-case" markdown="1">
<span class="callout-label">Our mediation study</span>
n = 120. X = study-hours index, M = academic self-efficacy, Y = achievement.
</div>

**Step 1 -- the a path.** Regress M on X.
```
a = 0.573,  SE = 0.070,  p < .001      X predicts M
```

**Step 2 -- the c path (total effect).** Regress Y on X alone.
```
c = 0.277,  SE = 0.063,  p < .001      X predicts Y
```

**Step 3 -- the b and c' paths.** Regress Y on M **and** X together.
```
b  = 0.328,  SE = 0.078,  p < .001     M predicts Y, controlling for X
c' = 0.089,  SE = 0.074,  p = .233     X no longer predicts Y
```

**Step 4 -- the indirect effect.**
```
ab = 0.573 x 0.328 = 0.188
```

**Step 5 -- check the decomposition.**
```
c' + ab = 0.089 + 0.188 = 0.277 = c    correct
```

**Step 6 -- test the indirect effect.** The Sobel test:
```
SE(ab) = 0.050
z      = 0.188 / 0.050 = 3.73
p      < .001                          the indirect effect is significant
```

**Step 7 -- proportion mediated.**
```
ab / c = 0.188 / 0.277 = 0.68          68% of the total effect runs through M
```

<div class="callout callout-key" markdown="1">
<span class="callout-label">Reading this result</span>
The direct effect fell from a significant **.277** to a non-significant **.089** once self-efficacy entered the model. That pattern is called **full mediation** -- self-efficacy accounts for essentially the whole relationship.

If c' had stayed significant but shrunk, that would be **partial mediation**.

Modern practice: report the **indirect effect and its confidence interval** as the finding. Whether c' happens to cross .05 is much less informative than the size and precision of ab.
</div>

### Bootstrapping beats Sobel

The Sobel test assumes the indirect effect is normally distributed. It usually is not, because *ab* is a product of two estimates.

**Use bootstrapped confidence intervals instead** -- 5,000 resamples, bias-corrected. If the 95% CI for *ab* excludes zero, the indirect effect is significant. This is what Hayes' PROCESS macro does and what reviewers now expect.

## Moderation, step by step

### The model

<div class="formula" markdown="1">
**Y = b&#8320; + b&#8321;X + b&#8322;W + b&#8323;(X &times; W) + e**
<span class="formula-note">b&#8323;, the coefficient on the product term, IS the moderation</span>
</div>

**If b&#8323; is significant, moderation is present.** That is the whole test.

### The procedure

**Step 1 -- centre the continuous predictors.** Subtract the mean from X and from W.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Why centring matters</span>
Without centring, X and X&times;W are strongly correlated, which inflates standard errors and makes b&#8321; and b&#8322; uninterpretable.

After centring, b&#8321; is the effect of X **when W is at its mean** -- a meaningful value. Centring does **not** change b&#8323; or the model's fit; it only makes the lower-order terms readable.
</div>

**Step 2 -- create the product term** from the centred variables.

**Step 3 -- enter in blocks.**
```
Block 1: X, W               ->  R-squared
Block 2: add X x W          ->  R-squared change
```
A significant **R-squared change** confirms the interaction adds explanatory power.

**Step 4 -- probe the interaction.** A significant b&#8323; says the effect varies; it does not say how. Compute **simple slopes**: the effect of X at low (&minus;1 SD), mean, and high (+1 SD) values of W.

**Step 5 -- plot it.** Two or three lines, one per level of W. Converging or crossing lines are the visual signature of moderation, and panels find the plot far more convincing than the coefficient.

## Doing it in software

### Jamovi -- the easiest route
Install the **medmod** module from the module library.

- **Analyses** &rarr; **medmod** &rarr; **Mediation**: assign Dependent, Mediator, Predictor. Tick **Estimate** and **Bootstrap**. It gives the indirect effect with a bootstrapped CI.
- **Analyses** &rarr; **medmod** &rarr; **Moderation**: assign Dependent, Predictor, Moderator. Jamovi centres automatically and offers a **Simple slopes analysis** and plot.

### SPSS -- PROCESS macro
Download Hayes' PROCESS from processmacro.org and install it as a custom dialog.

- <kbd>Analyze</kbd> &rarr; <kbd>Regression</kbd> &rarr; <kbd>PROCESS</kbd>
- **Model 4** = simple mediation
- **Model 1** = simple moderation
- Set **Bootstrap samples** to 5000, confidence intervals to **Percentile** or **Bias-corrected**
- Under Options, tick **Mean center for products** for moderation

### R
```r
# --- mediation with bootstrapped CI ---
install.packages("mediation")
library(mediation)

m_model <- lm(efficacy ~ hours, data = dat)
y_model <- lm(achieve ~ efficacy + hours, data = dat)
med <- mediate(m_model, y_model, treat = "hours", mediator = "efficacy",
               boot = TRUE, sims = 5000)
summary(med)
#   ACME (indirect)   0.188   95% CI [0.10, 0.29]   p < .001
#   ADE  (direct)     0.089   95% CI [-0.06, 0.24]  p = .233
#   Total effect      0.277
#   Prop. mediated    0.68

# --- moderation ---
dat$hours_c <- scale(dat$hours, scale = FALSE)
dat$sleep_c <- scale(dat$sleep, scale = FALSE)
mod <- lm(achieve ~ hours_c * sleep_c, data = dat)
summary(mod)          # the hours_c:sleep_c row is the interaction

install.packages("interactions")
library(interactions)
sim_slopes(mod, pred = hours_c, modx = sleep_c)   # simple slopes
interact_plot(mod, pred = hours_c, modx = sleep_c) # the plot
```

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- mediation</span>
A simple mediation analysis was conducted using *5,000* bootstrap samples. *Study hours* significantly predicted *self-efficacy* (*a* = *0.57*, *p* &lt; *.001*), and *self-efficacy* significantly predicted *achievement* while controlling for *study hours* (*b* = *0.33*, *p* &lt; *.001*). The indirect effect was significant, *ab* = *0.19*, 95% bootstrap CI [*0.10*, *0.29*], accounting for *68%* of the total effect. The direct effect became non-significant (*c&prime;* = *0.09*, *p* = *.233*), indicating full mediation.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- moderation</span>
Moderated regression was conducted with centred predictors. The interaction between *study hours* and *sleep quality* was significant, *b* = *0.21*, *p* = *.012*, &Delta;*R&sup2;* = *.04*. Simple slopes analysis showed that *study hours* predicted *achievement* for students with high sleep quality (+1 *SD*: *b* = *0.48*, *p* &lt; *.001*) but not for those with low sleep quality (&minus;1 *SD*: *b* = *0.06*, *p* = *.61*).
</div>

## Common mistakes

- **Calling an interaction "mediation."** The most common confusion in this lesson.
- **Testing mediation with cross-sectional data and claiming a mechanism.** M must plausibly occur after X. Measuring all three at once cannot establish that order.
- **Relying on Baron and Kenny's four steps alone.** Superseded; report the bootstrapped indirect effect.
- **Not centring before building the product term.**
- **Reporting a significant interaction without simple slopes or a plot.** The coefficient alone does not say what happens.
- **Interpreting main effects normally when the interaction is significant.** b&#8321; is now conditional on W = 0.

## Practice

**1.** "The effect of training on performance is stronger for younger employees." Mediation or moderation? Name the variables.

<details markdown="1">
<summary>Show the answer</summary>

**Moderation.**

The word that settles it is **"stronger for"** -- it says the size of an effect *depends on* another variable. That is a *when/for whom* question.

- **X (predictor):** training
- **Y (outcome):** performance
- **W (moderator):** age

The model: `performance = b0 + b1(training) + b2(age) + b3(training x age)`

**b&#8323; is the test.** If significant, the training-performance relationship differs by age. Then compute simple slopes at younger (&minus;1 SD) and older (+1 SD) ages and plot the two lines.

**Contrast with the mediation version of a similar sentence:** *"Training improves performance by increasing confidence."* That is *how*, so confidence is a mediator, not a moderator.
</details>

**2.** A mediation analysis gives a = 0.45 (p < .001), b = 0.02 (p = .71), c = 0.40 (p < .001). What do you conclude?

<details markdown="1">
<summary>Show the worked answer</summary>

```
ab = 0.45 x 0.02 = 0.009
```

**No mediation.** The *b* path is essentially zero and not significant -- the proposed mediator does not predict the outcome once X is controlled.

Reading each path:

- **a = 0.45, significant** -- X does predict M. That part of the theory holds.
- **b = 0.02, p = .71** -- but M does **not** predict Y. The chain is broken at the second link.
- **c = 0.40, significant** -- X still predicts Y, but through some other route.
- **ab = 0.009**, and a bootstrapped CI would certainly include zero.

**What to report:**

> The indirect effect through *M* was not significant, *ab* = 0.01, 95% CI [&minus;0.04, 0.06]. Although *X* predicted *M* (*a* = 0.45, *p* < .001), *M* did not predict *Y* when controlling for *X* (*b* = 0.02, *p* = .71). The proposed mediation was not supported.

**What this means substantively:** X affects Y through something you did not measure. That is a finding worth reporting and a clear direction for the Recommendations.
</details>

**3.** Why must you centre variables before creating an interaction term?

<details markdown="1">
<summary>Show the answer</summary>

**Two reasons, one statistical and one interpretive.**

**1. It removes artificial multicollinearity.** If X ranges from 20 to 60, then X and X&times;W are strongly correlated purely because both grow with X. That inflates standard errors, can flip signs, and makes the lower-order coefficients unstable. Centring breaks that correlation.

**2. It makes b&#8321; and b&#8322; interpretable.** In any model with an interaction, b&#8321; is the effect of X **when W equals zero**. Uncentred, "W = 0" may be impossible -- an age of zero, an IQ of zero. The coefficient then describes a case that cannot exist.

After centring, W = 0 means **W at its mean**, so b&#8321; is the effect of X for an average person. That is a value worth reporting.

**What centring does NOT change:**

- b&#8323;, the interaction coefficient itself
- The model's R-squared or overall fit
- The significance of the interaction

So centring costs nothing and buys interpretability. Do it every time. Note you centre only the **continuous** predictors; categorical ones are handled by coding.
</details>

## Before you move on

- [ ] I can state the mediation/moderation distinction in one sentence
- [ ] I can draw the a, b, c and c' paths and say what each means
- [ ] I can verify that c' + ab = c
- [ ] I know to report a bootstrapped CI for the indirect effect, not just Sobel
- [ ] I centre continuous predictors before building an interaction term
- [ ] I follow a significant interaction with simple slopes and a plot

Next: putting the whole course together into a defence you can walk into with confidence.""",
    [{"question": "\"The effect of training on performance is stronger for younger employees.\" This describes:",
      "choices": ["Mediation", "Moderation", "Correlation", "Confounding"], "correct": 1},
     {"question": "In mediation, the total effect c decomposes as:",
      "choices": ["c = a + b", "c = c' + ab", "c = ab - c'", "c = a x c'"], "correct": 1}],
)


# ===========================================================================
L(
    "Preparing for Your Statistics Defense",
    """## What you will be able to do

Walk into the defence able to answer the statistics questions without hesitating, because you prepared the seven that are always asked and rehearsed the three sentences that matter most.

## What a panel is actually testing

<div class="callout callout-key" markdown="1">
<span class="callout-label">The real question behind every question</span>
Not *"do you know statistics?"* but **"do you understand what YOU did?"**

A panel member may know less about your topic than you do. What they can always assess is whether you can explain your own choices. Every question below is a version of that.
</div>

## The seven questions, with model answers

### 1. "Why did you use this test?"

**What they are checking:** whether the test follows from the design, or was chosen at random.

**Model answer structure:** design &rarr; measurement level &rarr; number of groups &rarr; test.

> *"I compared two independent groups on a continuous outcome. The posttest score is ratio-level, the two sections contain different students, so an independent-samples t-test was appropriate. I verified normality within each group with Shapiro-Wilk and homogeneity of variance with Levene's test before running it."*

### 2. "Did you check your assumptions?"

**Name the tests and give the numbers.**

> *"Yes. Shapiro-Wilk was non-significant in both groups, p = .999 and p = .988, and the Q-Q plots showed no departure from linearity. Levene's test was non-significant, F = 0.15, p = .704, so equal variances were assumed and the standard t-test was used."*

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Never say "yes, they were met"</span>
With no numbers, that answer reads as "I did not check." Have the values ready on a card.
</div>

### 3. "What does your p-value mean?"

**The trap question.** Get this right and the panel relaxes.

> *"A p-value of .005 means that if there were truly no difference between the two groups in the population, we would obtain a difference at least this large in about 0.5% of samples. It is not the probability that the null hypothesis is true."*

### 4. "Is the difference important, not just significant?"

> *"Cohen's d was 1.12, a large effect by conventional standards. The module group scored 6.67 points higher on a 100-item test, with a 95% confidence interval from 2.22 to 11.12 points."*

### 5. "Why this sample size?"

> *"An a-priori power analysis in G*Power indicated 24 per group for a large effect at 80% power. I obtained 15 per group because that was the section size. A sensitivity analysis shows this detects effects of d = 1.06 or larger, so the study was powered for large effects only. This is stated as a limitation."*

### 6. "Can you claim your intervention caused the improvement?"

> *"No. I used intact sections rather than random assignment, so this is quasi-experimental. Pre-existing differences between the sections cannot be ruled out. I therefore report that the module group scored significantly higher, not that the module caused the difference. I collected pretest scores and could run ANCOVA to adjust for baseline differences."*

<div class="callout callout-key" markdown="1">
<span class="callout-label">Saying "no" is a strong answer</span>
Panels respect a candidate who knows the limits of their own design far more than one who overclaims. Attempting to defend a causal claim from a non-random design is how defences go wrong.
</div>

### 7. "What are your limitations?"

Have four ready, each with the reason:

> *"First, quasi-experimental design without random assignment, so causal inference is limited. Second, a single school, so results may not generalise beyond this population. Third, a sample powered only for large effects. Fourth, a researcher-made instrument; I report a KR-20 of .82, which is acceptable, but it has not been validated beyond this study."*

## The three sentences to memorise

<div class="callout callout-key" markdown="1">
<span class="callout-label">Rehearse these until they are automatic</span>

**1. Your main result, complete:**
> *"Students taught with the module (M = 78.67, SD = 6.21) scored significantly higher than those taught by lecture (M = 72.00, SD = 5.68), t(28) = 3.07, p = .005, d = 1.12."*

**2. What p means:**
> *"The probability of obtaining a difference at least this large if the null hypothesis were true."*

**3. What you may and may not conclude:**
> *"The groups differed significantly. Because assignment was not random, I describe this as an association rather than a causal effect."*
</div>

## The defence-day card

One page, in front of you, allowed in nearly every defence.

```
STUDY:  module vs lecture, posttest achievement
DESIGN: quasi-experimental, non-equivalent control group
n:      15 + 15 = 30

DESCRIPTIVES     lecture  M=72.00  SD=5.68
                 module   M=78.67  SD=6.21

ASSUMPTIONS      Shapiro-Wilk  p=.999 / .988   (per group)
                 Levene        F=0.15, p=.704

TEST             independent-samples t-test
RESULT           t(28)=3.07, p=.005
EFFECT           d=1.12 (large)
DIFFERENCE       6.67 points, 95% CI [2.22, 11.12]

POWER            a-priori 24/group needed; had 15
                 sensitivity: detects d >= 1.06
LIMITATIONS      no randomisation / one school / powered for large effects only
```

## Questions you may not be able to answer

You will be asked something you do not know. Have a response prepared.

<div class="callout callout-write" markdown="1">
<span class="callout-label">The honest answer, which works</span>
*"I am not certain about that. My understanding is [what you do know]. I would want to verify before answering definitively, and I will follow that up."*
</div>

This is far better received than guessing. A wrong confident answer invites three follow-ups; an honest one usually ends the thread.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Three answers that damage a defence</span>

- *"That is what the software gave."* Says you operated the analysis without understanding it.
- *"My adviser told me to use it."* Deflects responsibility for your own study.
- *"It is standard in this field."* Only works if you can also say **why** it is standard.
</div>

## The week before

- [ ] Every number in the text matches its table
- [ ] Defence card written and printed
- [ ] The three sentences rehearsed out loud
- [ ] Answers prepared for all seven questions
- [ ] Four limitations, each with its reason
- [ ] Software open and ready, with the dataset, in case they ask you to re-run something
- [ ] Assumption output printed as an appendix
- [ ] G*Power screenshot in the appendix
- [ ] Explained your analysis to someone outside your field and they followed it

That last item is the real test. If a non-specialist cannot follow your explanation, you do not yet understand it well enough.

## Practice

**1.** A panel member asks: "Your p-value is .005. So there is a 99.5% chance your hypothesis is correct?" Respond.

<details markdown="1">
<summary>Show the answer</summary>

**Correct the misconception without embarrassing them.**

> *"Not quite, sir. The p-value is computed **assuming the null hypothesis is true** -- it tells us how surprising our data would be under that assumption. A p of .005 means that if there were genuinely no difference between the groups, we would see a difference this large in about 5 samples in 1,000. It does not give the probability that my hypothesis is correct; that would require a Bayesian analysis with a prior."*

**Then redirect to what does support the claim:**

> *"What supports the finding more directly is the effect size, d = 1.12, and the confidence interval on the difference, 2.22 to 11.12 points. Even the smallest plausible difference is over two points."*

The tone matters: *"Not quite"* rather than *"No, you're wrong."* You are demonstrating command of the concept, not winning an argument.
</details>

**2.** "Why didn't you use ANOVA?" for a two-group study. Respond.

<details markdown="1">
<summary>Show the answer</summary>

> *"ANOVA and the independent-samples t-test are equivalent for two groups -- in fact F equals t squared. With 3.07 squared giving F = 9.41 on 1 and 28 degrees of freedom, the p-value would be identical at .005. The t-test is conventional for two groups because it reports the mean difference and its confidence interval directly, and it allows a one-tailed test if the hypothesis is directional. I would have used ANOVA if I had three or more groups."*

**Why this answer works:** it shows you know the two are the same procedure, you can state the exact relationship, and you chose on reporting grounds rather than by habit. That is exactly what the question was probing.

If you want to verify the relationship: 3.0684² = 9.415, and F(1,28) = 9.415 gives p = .00474 — the same p as the t-test.
</details>

**3.** "Your two sections might have differed before the intervention. How do you know the module caused the difference?"

<details markdown="1">
<summary>Show the answer</summary>

**Concede the point, then show what you did about it.**

> *"You are right that I cannot rule that out from this design, and I do not claim causation in my conclusions. I used intact sections, so the study is quasi-experimental rather than experimental.*
>
> *Two things partly address it. First, I collected pretest scores, and the two groups did not differ significantly at pretest, t(28) = 0.41, p = .69, which is some evidence of baseline comparability. Second, I can run ANCOVA on the posttest with pretest as a covariate, which statistically adjusts for any remaining baseline difference.*
>
> *Even with both, ANCOVA adjusts only for what I measured. Unmeasured differences between the sections remain possible, and that is why my conclusion states an association and my limitations name the absence of random assignment."*

**The structure that makes this work:**

1. Agree with the criticism immediately -- do not defend the indefensible
2. Show the evidence you did gather
3. Name the analysis that addresses it
4. State the residual limitation honestly

A panel that hears all four steps knows you understand your own design.
</details>

## Before you move on

- [ ] My defence card is written
- [ ] I can answer all seven questions without notes
- [ ] The three key sentences are memorised
- [ ] I have four limitations with reasons
- [ ] I have practised saying "I am not certain, but my understanding is..."
- [ ] Someone outside my field has followed my explanation

Next: the ethics that underlie all of it.""",
    [{"question": "A panel asks what your p-value of .005 means. Which answer is correct?",
      "choices": ["There is a 99.5% chance my hypothesis is correct",
                  "If the null were true, data at least this extreme would occur about 0.5% of the time",
                  "The effect is large", "The null hypothesis is false"], "correct": 1},
     {"question": "For two groups, the relationship between ANOVA's F and the t-test's t is:",
      "choices": ["F = t", "F = t squared", "F = 2t", "They are unrelated"], "correct": 1}],
)


# ===========================================================================
L(
    "Data Integrity and the Ethics of Statistical Practice",
    """## What you will be able to do

Recognise the four practices that turn honest research into false findings, know why each is tempting, and set up your own study so that you are never in a position to be tempted.

## Why this is a statistics lesson, not a formality

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
It is three weeks before your defence. Your main analysis returns *p* = .08.

You remove three influential cases -- they look like outliers. Now *p* = .06. You add a control variable that seems theoretically reasonable. Now *p* = .04.

You report the last analysis. Every individual step had a justification. **The reported p-value is nevertheless meaningless.**
</div>

CMO 42 lists **ethics and integrity** as one of five core competencies for a statistics graduate, and program outcome (o) is simply *"commit to the integrity of data."* This lesson is what that means when the deadline is close.

## The four practices

### 1. p-hacking

Trying analyses until one reaches significance.

The moves: dropping outliers, adding or removing covariates, splitting subgroups, switching tests, trying transformations, collecting a few more cases and re-testing.

<div class="callout callout-key" markdown="1">
<span class="callout-label">Why it works, and why that is the problem</span>
Each move is defensible **in isolation**. Combined, they are a machine for manufacturing significance.

With enough flexibility, the chance of finding *p* < .05 somewhere approaches certainty even when nothing is going on. Simulation studies put the false-positive rate for a researcher using four common flexible choices at **over 60%**, not 5%.

The reported p-value no longer describes the procedure that produced it.
</div>

### 2. HARKing

**H**ypothesising **A**fter the **R**esults are **K**nown -- presenting an exploratory finding as though it had been predicted.

You ran twelve correlations, one was significant, and Chapter 1 now states that relationship as your hypothesis. It converts a hypothesis-**generating** result into a fake confirmation, and it removes the reader's ability to judge how much searching produced it.

### 3. Selective reporting

Omitting analyses that did not work.

If you ran five tests and report the two that were significant, the reported estimates are conditioned on having been significant -- which biases them **upward**. Published effects are systematically larger than true effects largely because of this.

### 4. Optional stopping

Collecting data, testing, and continuing only if the result is not yet significant.

This guarantees eventual significance. Decide your sample size in advance (your power analysis does this) and collect all of it before testing.

## The remedies

<div class="callout callout-key" markdown="1">
<span class="callout-label">Pre-registration is the strongest protection</span>
Before collecting data, write down:

- The hypotheses, stated directionally if you have a direction
- The primary outcome variable, named
- The analysis plan, including the exact test
- Your exclusion rules, with reasons
- The sample size and how you determined it

Date the file and keep it. For a thesis this can simply be your approved Chapter 3. When a panel asks whether the analysis was decided in advance, you have the answer.
</div>

### Exploratory analysis is legitimate

The problem is never exploration. It is exploration **dressed as confirmation**.

| Confirmatory | Exploratory |
|---|---|
| Hypothesis stated before data | Pattern found in the data |
| Pre-specified analysis | Analysis chosen after looking |
| p-values interpretable | p-values are descriptive only |
| Reported as a test | Reported as *"exploratory"* |

Label it. *"An exploratory analysis, not hypothesised in advance, suggested..."* -- that sentence costs you nothing and protects your credibility entirely.

### Sensitivity analysis instead of hiding

If a result changes when you drop outliers, that is a **finding**, not a problem to conceal.

> *"The effect was significant with all cases retained, t(28) = 3.07, p = .005. Excluding the three cases beyond 1.5 x IQR, the effect remained significant, t(25) = 2.61, p = .015. The conclusion is robust to outlier treatment."*

If it had **not** remained significant, that is also reportable -- and far more useful to a reader than a single number chosen because it was the one that worked.

## Reproducibility

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The operational test of integrity</span>
**If someone with your raw data and your script cannot reproduce your table, you do not yet have a result.**

This is not about trust. Most irreproducible results come from honest mistakes -- a filter left on, a sort that misaligned columns, a version of the file that was not the final one.
</div>

Five habits that make your work reproducible:

1. **Never edit the raw data file.** Keep `data_raw.csv` untouched. Do every cleaning step in a script or a documented sequence.
2. **Document every exclusion** with its rule and its count. *"14 cases removed: 9 incomplete, 5 outside the age range."*
3. **Report n at each stage.** Collected &rarr; screened &rarr; analysed.
4. **Version your files** with dates, not `final_final_v2`.
5. **Keep the output.** Save the software output that produced each table.

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- data handling</span>
Of *45* questionnaires distributed, *38* were returned (*84.4%* response rate). *5* were excluded for incomplete responses on the primary outcome and *3* for falling outside the specified age range, leaving *30* cases for analysis. No other cases were removed. Data were cleaned using a documented script; the raw data file was retained unmodified.
</div>

## Data privacy

Research data about people is regulated in the Philippines by the **Data Privacy Act of 2012 (RA 10173)**. Ethics clearance and privacy compliance are **separate requirements** -- approval from a research ethics board does not exempt you.

The practical minimum:

- **Informed consent** that is specific about what the data will be used for
- **Data minimisation** -- collect only what the research question needs
- **Separate the identifiers.** Generate a random respondent ID at encoding; keep the linking file encrypted, separately, with restricted access
- **A retention and disposal plan.** Holding identifiable data indefinitely is what the law exists to prevent

Removing names is not anonymisation. Barangay plus age plus occupation plus sex frequently identifies exactly one person.

## Authorship and acknowledgement

- If someone ran your analysis for you, that is a **contribution** and belongs in the acknowledgements at minimum.
- Paying someone to run and interpret your statistics, then presenting it as your own work, is misrepresentation. Panels ask "why this test?" partly to detect it -- and it is the question that cannot be answered secondhand.
- Learning statistics so you can defend your own analysis is the entire point of this course.

## Common mistakes

- **Running the analysis first and writing the hypothesis after.**
- **Removing cases without a pre-specified rule.**
- **Reporting only the analyses that worked.**
- **"The data were cleaned"** with no detail. That is not a method.
- **Testing as data arrives** and stopping when it turns significant.
- **Treating ethics clearance as covering data privacy.** Different requirements.

## Practice

**1.** You planned a t-test. The data is badly skewed, so you run Mann-Whitney instead and it is significant while the t-test was not. Is this p-hacking?

<details markdown="1">
<summary>Show the answer</summary>

**It depends entirely on when you decided, and what you report.**

**Not p-hacking if:** your Chapter 3 stated a rule in advance, such as *"if normality is violated, the nonparametric equivalent will be used."* You applied a pre-specified contingency. Report both the check that triggered it and the test you ran.

**P-hacking if:** you ran the t-test, saw *p* = .08, then went looking for a test that would do better. The switch was driven by the result, not by the assumption check.

**The honest path when you have already done it:**

> *"The Shapiro-Wilk test indicated a violation of normality in the treatment group (W = .87, p = .03). A Mann-Whitney U test was therefore conducted, U = 62, p = .04. For transparency, the independent-samples t-test on the same data gave t(28) = 1.81, p = .081. The discrepancy reflects the influence of two extreme values on the mean."*

**Report both.** A reader can then judge for themselves, which is the whole point. Hiding the t-test is what turns a defensible decision into a dishonest one.
</details>

**2.** Your adviser says: "Just remove the three lowest scores, they're clearly outliers, and you'll get significance." How do you respond?

<details markdown="1">
<summary>Show the answer</summary>

**Do not simply refuse, and do not simply comply. Convert it into a defensible procedure.**

> *"I can check whether those cases are errors. If they are recording mistakes I should correct or remove them and document that. But if they are genuine scores, removing them because they are inconvenient would change what the p-value means."*

**Then offer the alternative that gets the information without the problem:**

> *"What I can do is report both. A sensitivity analysis shows the result with all cases and with those three excluded. If the conclusion holds either way, that is stronger than either analysis alone. If it does not hold, the reader needs to know that."*

**What makes this work:**

- You are not accusing anyone of misconduct. Advisers often suggest this without thinking it through.
- You are proposing **more** analysis, not less.
- A sensitivity analysis is standard practice and looks rigorous to a panel.

**The line that must not be crossed:** removing genuine data specifically because it changes a p-value is falsification, regardless of who suggested it. If pressed further, the correct escalation is to ask that the decision and its justification be documented in writing.
</details>

**3.** A student reports: "The data were cleaned and 30 cases were analysed." What is missing?

<details markdown="1">
<summary>Show the answer</summary>

**Almost everything a reader needs to evaluate the sample.**

Missing:

1. **How many were collected originally.** 30 out of 32 is a very different study from 30 out of 200.
2. **How many were excluded, and why.** Each exclusion rule, with its count.
3. **Whether the rules were set in advance.** Post-hoc exclusion rules are a p-hacking route.
4. **What "cleaned" means.** Corrected typos? Recoded reversed items? Imputed missing values? Each has different implications.
5. **Whether excluded cases differed systematically** from retained ones. If the excluded respondents were mostly from one group, the comparison is compromised.

**The version that answers all five:**

> *"Of 45 questionnaires distributed, 38 were returned (84.4% response rate). Following the exclusion criteria specified in the research plan, 5 were removed for incomplete responses on the primary outcome and 3 for falling outside the 16-18 age range, leaving 30 cases. Excluded cases did not differ significantly from retained cases on sex or section, χ²(1) = 0.42, p = .52. Data cleaning consisted of reverse-scoring items 4, 7 and 12 and correcting two transcription errors verified against the original forms; the raw data file was retained unmodified."*

Longer, and it closes every question a panel could ask about the sample.
</details>

## Before you move on

- [ ] I can name p-hacking, HARKing, selective reporting and optional stopping
- [ ] My analysis plan was written before I saw the results
- [ ] My exclusion rules were specified in advance, with counts reported
- [ ] I label exploratory analysis as exploratory
- [ ] I report sensitivity analyses rather than choosing the version that worked
- [ ] My raw data file is unmodified and my cleaning is documented
- [ ] My identifiers are stored separately from the analysis dataset

Next: where to go to keep learning.""",
    [{"question": "Presenting an exploratory finding as though it had been predicted in advance is called:",
      "choices": ["p-hacking", "HARKing", "Optional stopping", "Sensitivity analysis"], "correct": 1},
     {"question": "Your result changes when outliers are excluded. The defensible response is to:",
      "choices": ["Report only the version that reaches significance",
                  "Report both as a sensitivity analysis",
                  "Delete the outliers permanently",
                  "Switch to a nonparametric test without saying so"], "correct": 1}],
)


# ===========================================================================
L(
    "Further Reading (Free & Open)",
    """## How to use this page

Everything listed is free. Work one source properly rather than sampling several.

## For choosing and running the right test

- **Andy Field, *Discovering Statistics Using IBM SPSS Statistics***. Not free, but in nearly every Philippine university library, and the clearest treatment of assumptions and their remedies in print. His **statisticshell.com** hosts free chapters and datasets.
- **Laerd Statistics** -- statistics.laerd.com. Step-by-step SPSS guides for every test in this course, with annotated screenshots. Some content is paid, much is open.
- **jamovi user guide** -- jamovi.org/user-manual.html. Free, and the software is free.

## For power analysis

- **G*Power**, free from Heinrich Heine University Düsseldorf. The tool panels recognise. The bundled manual contains worked examples for every test.
- **Cohen, J. (1992). A power primer.** *Psychological Bulletin, 112*(1), 155-159. Four pages, and still the clearest statement of effect-size conventions. Widely available as a PDF.

## For mediation and moderation

- **Andrew Hayes -- processmacro.org.** PROCESS for SPSS and SAS, free, plus documentation and the templates for all 90-plus models.
- **Hayes, A. F. -- *Introduction to Mediation, Moderation, and Conditional Process Analysis***. The standard reference. Chapter 1 is free on the site.
- The **medmod** module inside jamovi does simple mediation and moderation free, with bootstrapping.

## For research integrity

- **The Center for Open Science** -- cos.io. Free pre-registration templates and the OSF platform.
- **Simmons, Nelson and Simonsohn (2011), "False-Positive Psychology."** The paper that put p-hacking on the map, and readable in one sitting.
- **National Privacy Commission** -- privacy.gov.ph. The RA 10173 implementing rules, advisories, and templates for consent and breach notification.

## Philippine sources

- **PSA OpenSTAT** -- openstat.psa.gov.ph. Official statistics, downloadable.
- **PSA Data Archive** -- microdata from the Labour Force Survey and FIES, free for research use on request.
- **Philippine Statistical Association** -- psai.ph. Training, conferences, and the professional body CMO 42 names.

## Free software

| Tool | Best for | Note |
|---|---|---|
| **jamovi** | Everything in this course | Free, APA output, easiest route out of SPSS |
| **JASP** | Same, plus Bayesian analysis | Free |
| **G*Power** | Power analysis | Free, what panels expect to see |
| **R + RStudio** | Anything, eventually | Free, steepest curve, most capable |
| **PSPP** | If your adviser insists on SPSS-like output | Free |

## Keeping the skill

1. **Re-derive rather than re-read.** Close the page and reproduce the pooled-variance calculation.
2. **Run your own data.** Motivation carries you through the tedious parts.
3. **Explain it to a non-specialist.** If they cannot follow you, you are not ready for the panel.

## Where to go next in this catalogue

| If you want to... | Take |
|---|---|
| Design the study properly from the start | **Foundations of Research Methodology** |
| Learn regression and its diagnostics | **Intermediate Statistics: Building Real Models** |
| Handle ordinal or non-normal data | **Nonparametric Statistics** |
| Run a real experiment with randomisation | **Design & Analysis of Experiments** |
| Understand the theory beneath all of it | **Probability & Mathematical Statistics** |
| Do SEM, PLS-SEM or survival analysis | **Advanced Statistics** |""",
)


# ===========================================================================
def main():
    Base.metadata.create_all(bind=engine)
    sync_columns()
    db = SessionLocal()
    try:
        course = db.query(models.Course).filter(models.Course.slug == COURSE_SLUG).first()
        if course is None:
            print(f"[error] no course with slug {COURSE_SLUG!r}. Run seed_courses.py first.")
            return
        existing = {l.title: l for l in course.lessons}
        added = rewritten = 0
        for order, spec in enumerate(LESSONS):
            lesson = existing.get(spec["title"])
            if lesson is None:
                lesson = models.Lesson(course_id=course.id, title=spec["title"])
                db.add(lesson)
                added += 1
            else:
                rewritten += 1
            lesson.content = spec["content"]
            lesson.order = order
            lesson.is_preview = spec["preview"]
            lesson.quiz_json = json.dumps(spec["quiz"]) if spec["quiz"] else ""
        db.commit()
        chars = sum(len(s["content"]) for s in LESSONS)
        stale = [t for t in existing if t not in {s["title"] for s in LESSONS}]
        print(f"[{course.title}]")
        print(f"  {added} added, {rewritten} rewritten, {len(LESSONS)} total")
        print(f"  {chars:,} characters ({chars // len(LESSONS):,} average)")
        if stale:
            print(f"  untouched: {', '.join(stale)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
