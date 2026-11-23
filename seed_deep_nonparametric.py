"""
Rewrites Nonparametric Statistics at teaching depth.

Every number below was computed with scipy before it was written into a lesson,
and the lessons were then checked back against this list.

  SIGN TEST  12 pain scores vs hypothesised median 5
    [7,8,6,9,4,7,8,5,9,6,8,7]; one tie dropped -> n=11, 10 plus / 1 minus
    exact two-sided p = .0117

  WILCOXON SIGNED-RANK  10 students pre/post
    pre  [52,48,61,55,43,58,50,47,63,54]
    post [58,55,64,60,49,57,56,53,68,59]
    d = [6,7,3,5,6,-1,6,6,5,5]; W+ = 54, W- = 1, W+ + W- = 55 = n(n+1)/2
    exact p = .0039;  z = -2.7011, normal-approx p = .0069,  r = .854

  MANN-WHITNEY U  two groups of 8 ordinal scores
    A [3,4,4,5,5,6,7,8]  B [1,2,2,3,3,4,5,6]
    R1 = 87.5, R2 = 48.5; U1 = 51.5, U2 = 12.5, U1 + U2 = 64 = n1*n2
    exact p = .0438; tie-corrected z = 2.0693, p = .0385
    rank-biserial r = .609; common-language = .805

  KRUSKAL-WALLIS  3 groups of 6
    R = 21 / 57 / 93;  H = 15.1579, df 2, p = .000511
    epsilon-squared = .8916,  eta-squared_H = .8772
    Dunn SE = 3.0822; g1-g3 z = -3.8933 p = .0001 (Bonferroni .0003)
    g1-g2 and g2-g3 both z = -1.9467 p = .0516 (Bonferroni .1547)

  FRIEDMAN  8 judges x 3 methods, column rank sums 22 / 15 / 11
    Q = 7.75, df 2, p = .0208;  Kendall W = .4844

  SPEARMAN / KENDALL  10 pairs
    sum d-squared = 8 -> rho = .9515 (scipy p = .0000228)
    Pearson on the same data = .9472
    41 concordant, 4 discordant of 45 pairs -> tau = .8222, p = .000358

  RUNS TEST  20 readings, median 50.5, perfectly alternating
    n1 = n2 = 10, runs = 20; mu = 11, sd = 2.1764, z = 4.1352, p = .00004

  CHI-SQUARE GOODNESS OF FIT  [42,35,28,20,25], n = 150
    chi-square = 9.9333, df 4, p = .0416

  KS ONE-SAMPLE  15 values, mean 75.8, sd 8.4701
    D = .0962, p = .997;  Shapiro W = .9833, p = .987

  CHI-SQUARE INDEPENDENCE  3x2 [[45,15],[30,30],[25,35]], n = 180
    chi-square = 14.625, df 2, p = .000667, Cramer's V = .285
    adjusted residuals: STEM +3.71, ABM -1.06, HUMSS -2.65

  2x2 [[18,7],[9,16]]
    uncorrected chi-square = 6.5217 p = .0107; Yates = 5.1530 p = .0232
    Fisher p = .0222; OR = 4.571, 95% CI [1.383, 15.109]; phi = .3612

Safe to re-run. Lessons are matched by title and replaced in place.

Usage:
    python3 seed_deep_nonparametric.py
"""
import json
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal, sync_columns
from app import models

COURSE_SLUG = "nonparametric-statistics"
LESSONS = []


def L(title, content, quiz=None, preview=False):
    LESSONS.append({"title": title, "content": content, "quiz": quiz, "preview": preview})


# ===========================================================================
L(
    "When Parametric Assumptions Fail",
    """## What you will be able to do

Decide, from the data in front of you rather than from habit, whether a t-test or ANOVA is defensible -- and know exactly which rank-based test replaces it when it is not. You will also be able to explain what you give up by switching, because the switch is never free.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
A candidate surveys 24 teachers on a five-point agreement scale and runs an independent-samples t-test comparing public and private schools. The panel asks one question: *"Is the mean of a five-point scale a meaningful number?"*

The candidate has no answer, because there isn't a good one. The gap between "agree" and "strongly agree" is not knowably the same size as the gap between "neutral" and "agree". The arithmetic mean assumes it is.
</div>

This is the most common reason to go nonparametric in education and social-science research, and it has nothing to do with normality. The measurement itself is ordinal.

## The four assumptions a t-test actually makes

Students are usually taught one and ignore three.

| Assumption | What it means | What breaks it |
|---|---|---|
| **Interval measurement** | Equal distances between adjacent values | Likert items, ranks, "mild/moderate/severe" |
| **Normality of the sampling distribution** | Not of the raw data -- of the mean | Heavy skew at small *n*; outliers |
| **Homogeneity of variance** | Groups spread similarly | One group far more variable than another |
| **Independence** | One observation tells you nothing about another | Repeated measures, clustered classes, pairs |

Only the last one is fatal in both worlds. A nonparametric test does not rescue you from dependence -- you need the *matched* version of the test instead.

## The idea before any formula

Replace the numbers with their positions.

Take any set of values. Sort them. Give the smallest the number 1, the next 2, and so on. Every rank-based test in this course then works on those positions and ignores the original values entirely.

Two consequences follow immediately, and together they are the whole trade:

1. **An outlier loses its leverage.** Change the largest value from 56 to 5,600 and its rank is still *n*. The mean would lurch; the median would not move at all.
2. **You throw away the spacing.** Ranks 1, 2, 3 say nothing about whether the gaps were 1 unit or 100. If the spacing was real information, you have discarded it.

<div class="callout callout-note" markdown="1">
<span class="callout-label">The honest framing</span>
Nonparametric tests are not "assumption-free". They assume less about the *shape* of the distribution. Most of them still assume independence, and many assume the groups have similar shape even if not similar location. "Distribution-free" means free of a *named* distribution, not free of assumptions.
</div>

## Your decision table

Keep this where you can see it. Every row is a test that appears later in this course.

| If your parametric plan was... | And it fails because... | Use |
|---|---|---|
| One-sample t-test | Ordinal, or skewed small sample | **Sign test** or **Wilcoxon signed-rank** |
| Paired t-test | Ordinal, or skewed differences | **Wilcoxon signed-rank** |
| Independent t-test | Ordinal, or very unequal spread | **Mann-Whitney U** |
| One-way ANOVA | Ordinal, or non-normal with outliers | **Kruskal-Wallis H** |
| Repeated-measures ANOVA | Ordinal, or sphericity violated badly | **Friedman** |
| Pearson *r* | Ordinal, or a curved but monotone relation | **Spearman rho** or **Kendall tau** |
| -- | Both variables are categories | **Chi-square** or **Fisher exact** |

## How to decide, step by step

**Step 1. Look at the measurement, not the data.**
Is the variable ordinal by construction? A single Likert item, a rank, a stage, a severity grade -- yes. If so, stop here; you are nonparametric regardless of what the normality test says.

A *summed scale* of several Likert items (say the mean of ten agreement items) is a different matter. Most methodologists treat that as approximately interval, and parametric tests on it are routinely published. One item is ordinal; a ten-item composite is usually not treated that way.

**Step 2. Plot the data.** Histogram, then boxplot, per group.
You are looking for three things: a long tail, points sitting far outside the whiskers, and groups with visibly different box heights.

**Step 3. Test normality -- but read it correctly.**

Run Shapiro-Wilk on each group's residuals.

```r
shapiro.test(scores[group == "A"])
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Where almost everyone misreads this</span>
Shapiro-Wilk is a test of a *null* of normality. At *n* = 20 it has so little power that it will pass data that is visibly skewed. At *n* = 2,000 it will reject data that is normal enough for any practical purpose.

So: **small sample, non-significant Shapiro means very little**; **large sample, significant Shapiro means very little**. At large *n* the Central Limit Theorem has already done the work -- that is the point of the theorem. Use the plot to decide, and the test only to confirm what the plot already showed.
</div>

**Step 4. Check spread.** Levene's test on the group variances.

```r
car::leveneTest(score ~ group)
```

If variances differ sharply and the design is two independent groups, Welch's t-test is often the better answer than Mann-Whitney. Welch keeps the mean as the parameter of interest and simply stops pooling the variances. Mann-Whitney changes the question from means to stochastic dominance.

**Step 5. Decide, and say why in writing.** One sentence in your methods chapter, naming the specific reason.

## A worked decision, start to finish

Fifteen measurements of a reading-comprehension score, taken from a hosted test:

`62, 65, 68, 70, 71, 72, 73, 75, 76, 78, 80, 82, 85, 88, 92`

Mean = 75.80, SD = 8.4701.

Shapiro-Wilk: **W = .9833, p = .987.**
Kolmogorov-Smirnov against *N*(75.80, 8.4701): **D = .0962, p = .997.**

Both say the same thing -- nothing here contradicts normality. The variable is a total score out of 100, which is at least quasi-interval. **Verdict: a one-sample t-test is defensible.** We do not go nonparametric here, and saying so is as much a result as going the other way.

Now change one value. Replace 92 with 192 (a data-entry slip that got past cleaning):

Mean jumps to 82.47. Median moves from 75 to 75 -- not at all. Shapiro-Wilk now rejects. The t-test on the corrupted data would be testing a mean that no single student is near. A rank-based test would have been almost untouched.

That contrast is the entire argument for robust methods in one example.

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span> (free, and the one to learn first)
Normality: **Analyses -> Exploration -> Descriptives**, tick *Shapiro-Wilk*, *Q-Q plot*, *Box plot*. Split by your grouping variable.
Nonparametric tests live under **Analyses -> T-Tests** (tick *Mann-Whitney U* or *Wilcoxon rank*) and **Analyses -> ANOVA -> One-Way ANOVA (Non-parametric)**.
</div>

**SPSS.** `Analyze -> Descriptive Statistics -> Explore`, then *Plots -> Normality plots with tests*. Tests: `Analyze -> Nonparametric Tests -> Independent Samples` (or *Related Samples*). SPSS's "Legacy Dialogs" submenu has the classic one-test-at-a-time versions, which print more of the working.

**Excel.** Shapiro-Wilk is not built in. You can get a skewness value with `=SKEW(range)` and kurtosis with `=KURT(range)`; absolute skew above about 2 is a real warning sign. Excel cannot run Mann-Whitney or Wilcoxon without an add-in -- this is where Excel genuinely runs out, and it is a good reason to install Jamovi.

**R.**

```r
shapiro.test(x)                      # normality
car::leveneTest(y ~ g)               # equal variance
wilcox.test(y ~ g)                   # Mann-Whitney
wilcox.test(pre, post, paired = TRUE)# Wilcoxon signed-rank
kruskal.test(y ~ g)                  # Kruskal-Wallis
```

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Methods, when you go nonparametric</span>
"Because teacher agreement was measured on a single five-point ordinal item, group differences were tested with the Mann-Whitney *U* test rather than an independent-samples *t*-test. Effect size is reported as the rank-biserial correlation."
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Methods, when you stay parametric</span>
"Reading-comprehension totals were approximately normally distributed in both groups (Shapiro-Wilk *W* = .98, *p* = .99 and *W* = .97, *p* = .84) and variances were homogeneous (Levene's *F*(1, 28) = 0.42, *p* = .52), so an independent-samples *t*-test was used."
</div>

Write the second one too. A panel that sees only the first wonders whether you checked.

## Common mistakes

1. **Choosing nonparametric because *n* is small.** Small *n* is not a reason by itself; small *n* with visible skew is. And nonparametric tests have their own small-sample limits -- the sign test on *n* = 5 can never reach *p* < .05 two-tailed no matter how one-sided the data is.
2. **Running a normality test on the whole dataset instead of within groups.** Two perfectly normal groups with different means look bimodal when pooled.
3. **Reporting "the data were not normal" with no numbers.** Give the statistic, the df where applicable, and the *p*.
4. **Assuming nonparametric means "no effect size needed".** Every test in this course has one. They are in the lessons that follow.
5. **Treating the median as the thing being tested in Mann-Whitney.** It usually isn't -- see the lesson on two independent samples.
6. **Forgetting that non-independence is fatal in both worlds.** If students are nested in classes, neither a t-test nor Mann-Whitney is right; you need the matched test or a mixed model.

## Practice

<details markdown="1">
<summary>1. A researcher has 300 responses on a 10-item attitude scale (mean of the items). Shapiro-Wilk is significant, p = .003. Should she go nonparametric?</summary>

Probably not. At *n* = 300 Shapiro-Wilk detects deviations too small to matter, and the Central Limit Theorem means the sampling distribution of the mean is near-normal anyway. A 10-item composite is also usually treated as interval.

The correct move is to **plot it**. If the histogram is mildly non-normal with no extreme outliers, a t-test or ANOVA is fine and the large *n* protects her. If there are genuine outliers or the skew is severe, she should report both analyses and note that they agree -- a *sensitivity analysis*, which is more convincing than either alone.
</details>

<details markdown="1">
<summary>2. Pain is recorded as none / mild / moderate / severe for 40 patients in two treatment arms. Which test?</summary>

**Mann-Whitney U.** The variable has four ordered categories, so it is ordinal -- the distance from "none" to "mild" is not knowably the distance from "moderate" to "severe".

An alternative worth knowing: with only four categories and a reasonable *n*, an **ordinal logistic regression** (proportional-odds model) gives you an odds ratio you can interpret, and it extends to covariates. Mann-Whitney is the simpler report; ordinal regression is the more informative one.
</details>

<details markdown="1">
<summary>3. Two groups, n = 15 each. Both normal. But group A's SD is 3.1 and group B's is 11.8. Mann-Whitney?</summary>

**No -- use Welch's t-test.** The problem is unequal variance, not non-normality, and Welch's test exists precisely for that. It adjusts the degrees of freedom and does not pool the variances.

Mann-Whitney also assumes similar shape when you want to interpret it as a location shift. With SDs differing nearly four-fold, the shapes differ, so Mann-Whitney's interpretation gets murky too. Welch is both more powerful here and easier to explain.
</details>

<details markdown="1">
<summary>4. Why can't you just rank the data yourself and run a t-test on the ranks?</summary>

You almost can, and that is a real insight -- this is called the **rank transform**, and for the two-group case a t-test on ranks gives a *p*-value very close to Mann-Whitney's.

But it breaks down in two places. For factorial designs the rank transform produces interaction tests that are simply wrong (the ranks are not additive the way the raw scores were). And for small samples the purpose-built exact tests give you the exact permutation *p*-value, where the t-test on ranks only gives an approximation. Use the real test.
</details>

## Before you move on

- [ ] I can name the four assumptions of a t-test, not just normality.
- [ ] I know why a significant Shapiro-Wilk at *n* = 1,000 is usually not a reason to switch tests.
- [ ] I can state the trade I make when I replace values with ranks.
- [ ] I can find the right nonparametric test for any of the six parametric tests in the decision table.
- [ ] I know that Welch's t-test, not Mann-Whitney, is the usual answer to unequal variances.""",
    quiz={
        "question": "At n = 1,200, Shapiro-Wilk on a summed attitude scale returns p = .004. What does this most likely mean?",
        "options": [
            "The data are badly non-normal and a nonparametric test is required",
            "Shapiro-Wilk has detected a deviation too small to matter at this sample size; plot the data and decide from that",
            "The sample is too large for any valid test",
            "The scale must be re-measured on an interval basis",
        ],
        "answer": 1,
        "explanation": "Shapiro-Wilk's power grows with n, so at large n it rejects trivial departures. The CLT also makes the sampling distribution of the mean near-normal. Decide from the histogram and from whether outliers are present, not from the p-value alone.",
    },
    preview=True,
)


# ===========================================================================
L(
    "One Sample: Sign and Wilcoxon Signed-Rank Tests",
    """## What you will be able to do

Test a claim about a single median -- by hand, with exact probabilities, and in software -- using the two tests that replace the one-sample t-test. You will also know why the Wilcoxon test is almost always the better of the two, and the one case where the sign test wins.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
A clinic claims its standard protocol leaves patients at a median pain score of 5 on a 0-10 scale. Twelve patients are assessed after the protocol:

`7, 8, 6, 9, 4, 7, 8, 5, 9, 6, 8, 7`

Is the median really 5, or is it higher? The scale is a subjective 0-10 rating -- ordinal -- so a t-test on the mean is hard to defend.
</div>

## The sign test: the idea before the formula

Forget magnitude entirely. Ask only one thing of each observation: **is it above the hypothesised median, or below it?**

If the true median really is 5, then each patient is a coin flip -- equally likely to land above or below. So the number of "aboves" should follow a binomial distribution with *p* = .5.

That is the whole test. It is the most assumption-light test in all of statistics: it needs only that the observations are independent and that the variable is at least ordinal. It does not care about shape, spread, or outliers.

**Ties go in the bin.** An observation exactly equal to the hypothesised median is neither above nor below, so it is dropped and *n* shrinks. This is not a trick -- it is forced on you by the logic of the test.

## Working the sign test by hand

**Step 1. Classify every observation.**

| Patient | Score | vs median 5 | Sign |
|---|---|---|---|
| 1 | 7 | above | + |
| 2 | 8 | above | + |
| 3 | 6 | above | + |
| 4 | 9 | above | + |
| 5 | 4 | below | &minus; |
| 6 | 7 | above | + |
| 7 | 8 | above | + |
| 8 | 5 | **equal** | drop |
| 9 | 9 | above | + |
| 10 | 6 | above | + |
| 11 | 8 | above | + |
| 12 | 7 | above | + |

**Step 2. Count.** Plus signs = 10. Minus signs = 1. Ties dropped = 1.

**Step 3. Set the effective sample size.** *n* = 10 + 1 = **11**. The twelfth patient is gone.

**Step 4. Compute the exact binomial probability.**

Under H&#8320;, the count of plus signs *X* follows Binomial(*n* = 11, *p* = .5). We observed 10. The two-sided *p*-value is the probability of a result at least this lopsided *in either direction*:

<div class="formula" markdown="1">
**p = 2 x P(X &ge; 10) = 2 x [ P(X = 10) + P(X = 11) ]**
<span class="formula-note">X ~ Binomial(n = 11, p = .5) under the null</span>
</div>

```
P(X = 10) = C(11,10) x (0.5)^11 = 11 x 1/2048 = 11/2048
P(X = 11) = C(11,11) x (0.5)^11 =  1 x 1/2048 =  1/2048
                                              ----------
                                      total  = 12/2048

p = 2 x 12/2048 = 24/2048 = .0117
```

**Decision: reject H&#8320; at alpha = .05.** The median is not 5; the sample median is 7.

<div class="callout callout-note" markdown="1">
<span class="callout-label">Why the exact probability and not a z-score</span>
With *n* = 11 the normal approximation is unreliable. The binomial is discrete and skewed at the tail, and *p* = .0117 from the exact calculation is the right answer. Only use the normal approximation when *n* is above roughly 25, and then with a continuity correction.
</div>

## The sign test's weakness, shown with one number

Our data had differences from the median of +2, +3, +1, +4, &minus;1, +2, +3, +4, +1, +3, +2.

The sign test saw: + + + + &minus; + + + + + +.

It could not tell the difference between a patient who scored 6 (one point above) and one who scored 9 (four points above). Both were just "+". That is a lot of discarded information, and it costs power.

The Wilcoxon signed-rank test keeps that information.

## The Wilcoxon signed-rank test: the idea

Two steps instead of one:

1. **Rank the differences by size, ignoring sign.** Smallest absolute difference gets rank 1.
2. **Put the signs back, and add up the ranks that carry a plus.**

If the median is really what you claim, the positive ranks and negative ranks should be balanced -- large differences should fall on both sides about equally. If all the *big* differences are positive, the sum of positive ranks will be large, and the test notices.

So Wilcoxon uses both the direction *and* the relative size of each difference. It is roughly 95% as powerful as the t-test when the data really are normal, and more powerful than the t-test when they are heavy-tailed. There is almost never a reason to prefer the sign test when both apply.

## Working Wilcoxon by hand: a paired design

The same test handles the much more common paired case. Ten students take a pre-test and a post-test:

| Student | Pre | Post | *d* = Post &minus; Pre | &#124;*d*&#124; | Rank of &#124;*d*&#124; | Signed rank |
|---|---|---|---|---|---|---|
| 1 | 52 | 58 | +6 | 6 | 7.5 | +7.5 |
| 2 | 48 | 55 | +7 | 7 | 10 | +10 |
| 3 | 61 | 64 | +3 | 3 | 2 | +2 |
| 4 | 55 | 60 | +5 | 5 | 4 | +4 |
| 5 | 43 | 49 | +6 | 6 | 7.5 | +7.5 |
| 6 | 58 | 57 | **&minus;1** | 1 | 1 | **&minus;1** |
| 7 | 50 | 56 | +6 | 6 | 7.5 | +7.5 |
| 8 | 47 | 53 | +6 | 6 | 7.5 | +7.5 |
| 9 | 63 | 68 | +5 | 5 | 4 | +4 |
| 10 | 54 | 59 | +5 | 5 | 4 | +4 |

**Step 1. Compute every difference.** Fix a direction and never change it. Here Post &minus; Pre, so a positive *d* means improvement.

**Step 2. Take absolute values and rank them.**
Sorted: 1, 3, 5, 5, 5, 6, 6, 6, 6, 7.

Now handle ties. The three 5s occupy positions 3, 4, 5, so each gets the average: (3+4+5)/3 = **4**. The four 6s occupy positions 6, 7, 8, 9, so each gets (6+7+8+9)/4 = **7.5**. The 1 gets rank 1, the 3 gets rank 2, the 7 gets rank 10.

**Step 3. Reattach the signs and sum each side.**

```
W+ = 7.5 + 10 + 2 + 4 + 7.5 + 7.5 + 7.5 + 4 + 4 = 54
W- = 1
```

**Step 4. Check your arithmetic -- this step catches most hand-calculation errors.**

```
W+ + W-     = 54 + 1      = 55
n(n+1)/2    = (10 x 11)/2 = 55     <- they match, so the ranks are right
```

If those two numbers disagree, you have mis-ranked something. Go back before you go forward.

**Step 5. The test statistic is the smaller of the two.** *W* = min(54, 1) = **1**.

**Step 6. Exact *p*-value.** For *n* = 10, scipy's exact calculation gives **p = .0039**.

Why so small? Because out of the full rank sum of 55, only 1 point sits on the negative side. Nine of ten students improved, and the one who declined declined by the smallest amount in the dataset -- so it earned rank 1, the lightest possible weight. The data are about as one-sided as ten observations can be.

## The normal approximation, for when *n* is larger

For *n* above about 20, *W* is near-normal with:

<div class="formula" markdown="1">
**mean of W = n(n+1)/4&nbsp;&nbsp;&nbsp;&nbsp;SD of W = &radic;[ n(n+1)(2n+1) / 24 ]**
<span class="formula-note">valid once n is above about 20</span>
</div>

For our data (*n* = 10 -- too small in practice, but worth seeing the machinery):

```
mean of W = (10 x 11) / 4 = 110 / 4 = 27.5

SD of W   = sqrt( (10 x 11 x 21) / 24 )
          = sqrt( 2310 / 24 )
          = sqrt( 96.25 )
          = 9.8107

z = (W - mean) / SD = (1 - 27.5) / 9.8107 = -2.7011
```

Two-sided *p* from the normal: **.0069**. Compare with the exact **.0039**. They agree in conclusion but not in value -- another reason to use the exact test when your software offers it.

## Effect size

A *p*-value does not tell you how big the shift is. Report one of these:

**Matched-pairs rank-biserial correlation.**

```
r = |z| / sqrt(n) = 2.7011 / sqrt(10) = 2.7011 / 3.1623 = .854
```

Interpret like any correlation: .1 small, .3 medium, .5 large. So .85 is a very large effect.

**The Hodges-Lehmann estimator -- the one your reader actually wants.**
Take all *n*(*n*+1)/2 = 55 pairwise averages of the differences (the Walsh averages) and report their median. For this data it is **+5.5 points**, with a distribution-free 95% confidence interval you can read off the same set.

That sentence -- "the median improvement was 5.5 points" -- means more to a reader than *r* = .85 does. Give both.

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span>
**Paired:** Analyses -> T-Tests -> Paired Samples T-Test. Move Pre and Post into the box, then tick **Wilcoxon rank** under *Tests*. Tick *Effect size* and *Descriptives*.
**One sample:** Analyses -> T-Tests -> One Sample T-Test, tick **Wilcoxon rank**, and set *Test value* to your hypothesised median (5, in our clinic example).
</div>

**SPSS.**
`Analyze -> Nonparametric Tests -> Related Samples`. Under *Fields* pair Pre and Post; under *Settings -> Customize tests* tick **Wilcoxon matched-pair signed-rank** and **Sign**. Double-click the output table to get the ranks and the exact *p*.

**Excel.** No built-in function. You can do it manually in six columns -- difference, absolute difference, `=RANK.AVG(C2,$C$2:$C$11,1)` for mid-ranks, then `=SUMIF` on the sign -- and get *W*. For the exact *p* you then need a table. The binomial part of the sign test, though, is one cell:

```
=2*(1-BINOM.DIST(9,11,0.5,TRUE))
```

which returns 0.011719 -- exactly the sign-test *p* we computed by hand.

**R.**

```r
# Sign test via the binomial
binom.test(10, 11, p = 0.5)                 # p = .01172

# Wilcoxon, exact, with the Hodges-Lehmann estimate and CI
wilcox.test(post, pre, paired = TRUE, exact = TRUE,
            conf.int = TRUE)
#  V = 54, p-value = 0.003906
#  difference in location  5.5
#  95 percent CI: 3.5  6.5

# effect size
rstatix::wilcox_effsize(long_df, value ~ time, paired = TRUE)
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">A reporting trap</span>
R reports *V* = 54 -- the sum of the *positive* ranks. SPSS and most textbooks report *W* = 1, the smaller of the two. Both give the same *p*. Say which convention you used, or your number will look wrong to a reader checking it against a table.
</div>

## Reading the output

Jamovi's paired table for our data:

| | Statistic | p | Effect size |
|---|---|---|---|
| Student's t | 5.33 | .0005 | 1.686 (Cohen's d) |
| Wilcoxon W | 54.0 | .0039 | 0.964 (rank-biserial) |

Three things to notice.

The **t-test p is smaller** (.0005 vs .0039). That is the usual cost of going nonparametric -- you give up a little power when the data would have supported the parametric test.

The **conclusion is identical**. Both reject decisively. When the two agree, say so; it is reassuring.

Jamovi's **rank-biserial here is .964**, not the .854 we computed. Jamovi uses (*W*&#8314; &minus; *W*&#8315;)/(*W*&#8314; + *W*&#8315;) = 53/55 = .964, while the *z*/&radic;*n* route gives .854. Both are called "rank-biserial" in the literature. Report the formula alongside the number.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">APA, Wilcoxon signed-rank (paired)</span>
"A Wilcoxon signed-rank test showed that post-test scores (*Mdn* = 57.5) were significantly higher than pre-test scores (*Mdn* = 53.0), *W* = 1.00, *p* = .004, *r* = .85. The Hodges-Lehmann estimate of the median improvement was 5.5 points, 95% CI [3.5, 6.5]. Nine of the ten students improved."
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">APA, sign test (one sample)</span>
"A sign test indicated that post-protocol pain scores (*Mdn* = 7.0) were significantly above the claimed median of 5, with 10 of 11 non-tied observations above the hypothesised value, exact *p* = .012."
</div>

Note what both of these do: they give the medians, the statistic, the exact *p*, an effect size or an interpretable estimate, and -- in the sign test -- the count of ties dropped. A reader can reconstruct the analysis from the sentence.

## Common mistakes

1. **Forgetting to report dropped ties.** Going from *n* = 12 to *n* = 11 changes the *p*-value. Say it happened.
2. **Ranking the signed differences instead of the absolute differences.** The ranking is on magnitude; the signs come back afterwards.
3. **Breaking ties by rank order instead of averaging.** Three tied values at positions 3, 4, 5 all get 4, not 3, 4, 5 in arbitrary order.
4. **Skipping the *W*&#8314; + *W*&#8315; = *n*(*n*+1)/2 check.** It is free and it catches almost every ranking error.
5. **Reporting *W* without saying which *W*.** The smaller of the two, or the positive-rank sum? They differ.
6. **Using the normal approximation at *n* = 8.** Use the exact test. Every modern package has it.
7. **Flipping the direction of the difference halfway through.** Decide Post &minus; Pre or Pre &minus; Post once, and keep it. The *p* is the same; the sign of the effect is not.

## Practice

<details markdown="1">
<summary>1. Six patients, differences: +4, +6, +2, +5, +7, +3. Run the Wilcoxon signed-rank test by hand.</summary>

Absolute values sorted: 2, 3, 4, 5, 6, 7 -- no ties, so ranks are 1, 2, 3, 4, 5, 6.

Every difference is positive, so every rank is positive:
*W*&#8314; = 1+2+3+4+5+6 = **21**, *W*&#8315; = **0**.

Check: 21 + 0 = 21, and *n*(*n*+1)/2 = 6(7)/2 = 21. &#10003;

*W* = min(21, 0) = **0** -- the most extreme value possible with *n* = 6.

The exact two-sided *p* for *W* = 0 at *n* = 6 is 2/64 = **.031**. Reject at alpha = .05.

Notice the limit: with *n* = 6 the smallest possible two-sided *p* is .031. With *n* = 5 it would be 2/32 = .063, and you could never reach significance two-tailed no matter how perfect the data. That is the small-sample floor.
</details>

<details markdown="1">
<summary>2. In the clinic data, why did we use n = 11 rather than n = 12 — and what would happen if the tie were kept as a plus?</summary>

Patient 8 scored exactly 5, the hypothesised median. The sign test asks "above or below?" and that patient is neither, so the logic of the test has nothing to assign. Dropping it is the standard treatment and it reduces *n* to 11.

If you cheated and called it a plus, you would have 11 plus signs out of 12, giving exact *p* = 2 x P(*X* &ge; 11 | *n* = 12) = 2(13/4096) = **.0063** -- a smaller *p* than the honest .0117. Keeping ties as support for your hypothesis inflates significance. That is why the convention exists.
</details>

<details markdown="1">
<summary>3. Your supervisor says "just run a paired t-test, Wilcoxon loses power." Is she right?</summary>

Partly, and the honest answer has two halves.

**When the differences really are normal**, Wilcoxon's asymptotic relative efficiency against the t-test is 3/pi &asymp; **.955**. So you need about 5% more participants for the same power. That is a real but modest cost -- and we saw it in our own data: *p* = .0005 vs *p* = .0039.

**When the differences are heavy-tailed or contain an outlier**, the comparison reverses and Wilcoxon can be *far* more powerful, because the t-test's standard error is inflated by the outlier while Wilcoxon only sees its rank.

So: if the differences pass a normality check, use the t-test. If they do not, or if the measurement is ordinal, use Wilcoxon and accept the 5%. Best practice at small *n* is to report both and note that they agree.
</details>

<details markdown="1">
<summary>4. Why does the Wilcoxon test beat the sign test, in terms of what each one looks at?</summary>

The sign test reduces each observation to one bit -- above or below. Wilcoxon keeps the *ordering of the magnitudes* as well.

In our pre/post data, nine students improved and one declined. The sign test sees 9 plus, 1 minus, and returns exact *p* = 2 x P(*X* &ge; 9 | *n* = 10) = **.0215**.

Wilcoxon sees the same 9-to-1 split, but *also* notices that the single decline was &minus;1 point -- the smallest absolute change in the whole dataset, so rank 1 of 10 -- while the improvements were 3 to 7 points, carrying ranks 2 through 10. It returns **p = .0039**, five times smaller.

The extra information was: the one piece of contrary evidence was the weakest piece of evidence in the set. The sign test could not see that. Asymptotic relative efficiency of the sign test against Wilcoxon under normality is only about .67.
</details>

<details markdown="1">
<summary>5. Compute the Hodges-Lehmann estimate for the small set of differences +2, +4, +6.</summary>

Take all pairwise averages *including* each value with itself -- there are *n*(*n*+1)/2 = 3(4)/2 = 6 of them (the Walsh averages):

(2+2)/2 = 2
(2+4)/2 = 3
(2+6)/2 = 4
(4+4)/2 = 4
(4+6)/2 = 5
(6+6)/2 = 6

Sorted: 2, 3, 4, 4, 5, 6. The median of six values is the average of the 3rd and 4th: (4+4)/2 = **4**.

So the Hodges-Lehmann estimate of the median shift is **+4**. Here it happens to equal the median of the raw differences, but in general it does not -- and it is the estimator that pairs correctly with the Wilcoxon test's confidence interval.
</details>

## Before you move on

- [ ] I can run a sign test by hand, including dropping ties and getting the exact binomial *p*.
- [ ] I can rank absolute differences with correct mid-ranks for ties.
- [ ] I always check *W*&#8314; + *W*&#8315; = *n*(*n*+1)/2 before trusting my ranks.
- [ ] I know *W* means the smaller sum in SPSS but the positive sum in R.
- [ ] I can report a Hodges-Lehmann estimate and say why it is more useful than *r*.
- [ ] I can explain the 5% power cost of Wilcoxon under normality, and when it reverses.""",
    quiz={
        "question": "You rank the absolute differences and get W+ = 48 and W- = 9 for n = 10. What should you conclude first?",
        "options": [
            "The test is significant because W- is small",
            "There is a ranking error: W+ + W- must equal 55, not 57",
            "W = 9 and you can proceed to the table",
            "The sample is too small for Wilcoxon",
        ],
        "answer": 1,
        "explanation": "For n = 10 the two rank sums must add to n(n+1)/2 = 55. Getting 57 means a mis-ranked tie or a dropped observation. Always run this check before interpreting anything.",
    },
)


# ===========================================================================
L(
    "Two Samples: Related and Independent",
    """## What you will be able to do

Run the Mann-Whitney *U* test by hand from the ranks up, get the same number your software gets (including the tie correction), report an effect size a reader can actually use, and -- the part most courses skip -- state correctly what the test is and is not testing.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
Sixteen clients rate a service on a 1-9 satisfaction scale. Eight used the new workflow, eight the old one.

**New (A):** 3, 4, 4, 5, 5, 6, 7, 8
**Old (B):** 1, 2, 2, 3, 3, 4, 5, 6

The scale is a single ordinal item and *n* is 8 per group. A t-test on the means of a 1-9 rating with 8 cases per cell is hard to defend. Mann-Whitney it is.
</div>

## First: which two-sample test?

The two cases are completely different and mixing them up is the single most common error in this part of statistics.

| Design | What makes it this | Test |
|---|---|---|
| **Related / paired** | Each value in group 1 is tied to one specific value in group 2 -- same person twice, matched pairs, twins, left/right | **Wilcoxon signed-rank** (previous lesson) |
| **Independent** | Nobody appears in both groups; the two samples could be different sizes | **Mann-Whitney U** |

The quick check: **can you draw a line connecting each observation in group 1 to exactly one in group 2?** If yes, it is paired, and you must use the paired test -- the pairing is information, and ignoring it throws away power. If no, it is independent.

A trap: *n*&#8321; = *n*&#8322; does **not** make a design paired. Two independent groups of 8 are still independent.

## The idea before the formula

Pool both groups. Rank everything from smallest to largest, ignoring which group it came from. Then add up the ranks belonging to group A.

If the new workflow is no better than the old, the two groups' values should be shuffled through each other, and group A's rank sum should land near the middle. If A really is higher, A's values crowd into the high ranks and A's rank sum will be large.

That is the test. *U* is just a rescaling of that rank sum so the smallest possible value is 0 rather than *n*(*n*+1)/2.

<div class="callout callout-note" markdown="1">
<span class="callout-label">What Mann-Whitney actually tests</span>
Not "are the medians equal". The null hypothesis is **P(a random value from A exceeds a random value from B) = .5** -- in words, that neither group stochastically dominates the other.

It becomes a test of medians *only* if you add an assumption: that the two distributions have the **same shape** and differ only by a shift in location. With that assumption, equal distributions means equal medians, and the test is a location test.

Without that assumption it is still a perfectly valid test -- it just answers the dominance question instead. Two distributions can have identical medians and still produce a significant *U*, if one is far more spread out than the other. Say which version you are claiming.
</div>

## Working it by hand

**Step 1. Pool and sort, keeping track of the source.**

| Value | 1 | 2 | 2 | 3 | 3 | 3 | 4 | 4 | 4 | 5 | 5 | 5 | 6 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| From | B | B | B | A | B | B | A | A | B | A | A | B | A | B | A | A |
| Position | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 |

**Step 2. Convert positions to mid-ranks, because there are ties.**

- One value of 1 at position 1 &rarr; rank **1**
- Two 2s at positions 2-3 &rarr; (2+3)/2 = **2.5** each
- Three 3s at positions 4-6 &rarr; (4+5+6)/3 = **5** each
- Three 4s at positions 7-9 &rarr; (7+8+9)/3 = **8** each
- Three 5s at positions 10-12 &rarr; (10+11+12)/3 = **11** each
- Two 6s at positions 13-14 &rarr; (13+14)/2 = **13.5** each
- One 7 at position 15 &rarr; rank **15**
- One 8 at position 16 &rarr; rank **16**

**Step 3. Sum the ranks within each group.**

Group A values 3, 4, 4, 5, 5, 6, 7, 8 take ranks 5, 8, 8, 11, 11, 13.5, 15, 16:

```
R1 = 5 + 8 + 8 + 11 + 11 + 13.5 + 15 + 16 = 87.5
```

Group B values 1, 2, 2, 3, 3, 4, 5, 6 take ranks 1, 2.5, 2.5, 5, 5, 8, 11, 13.5:

```
R2 = 1 + 2.5 + 2.5 + 5 + 5 + 8 + 11 + 13.5 = 48.5
```

**Step 4. The check that catches ranking errors.**

```
R1 + R2    = 87.5 + 48.5  = 136
N(N+1)/2   = (16 x 17)/2  = 136     <- match, ranks are correct
```

**Step 5. Convert rank sums to U.**

<div class="formula" markdown="1">
**U&#8321; = R&#8321; &minus; n&#8321;(n&#8321;+1)/2&nbsp;&nbsp;&nbsp;&nbsp;U&#8322; = R&#8322; &minus; n&#8322;(n&#8322;+1)/2**
<span class="formula-note">subtracting the smallest rank sum the group could possibly have</span>
</div>

```
U1 = 87.5 - (8 x 9)/2 = 87.5 - 36 = 51.5
U2 = 48.5 - (8 x 9)/2 = 48.5 - 36 = 12.5

check: U1 + U2 = 51.5 + 12.5 = 64 = n1 x n2 = 8 x 8    <- match
```

**Step 6. Interpret *U* directly -- this is the part worth memorising.**

*U*&#8321; = 51.5 counts the number of A-vs-B pairs in which the A value wins, with ties counting half. There are 8 x 8 = 64 such pairs. So A beat B in 51.5 of 64 head-to-head comparisons.

**Step 7. Get a *p*-value.** The exact two-sided *p* from scipy is **.0438**. Reject at alpha = .05.

## The normal approximation -- and why the tie correction matters

For larger samples:

<div class="formula" markdown="1">
**mean of U = n&#8321;n&#8322;/2**
<span class="formula-note">and with no ties, SD of U = &radic;[ n&#8321;n&#8322;(N+1)/12 ]</span>
</div>

```
mean of U = (8 x 8)/2 = 32
```

With no ties the SD would be:

```
SD = sqrt( 8 x 8 x 17 / 12 ) = sqrt( 1088/12 ) = sqrt(90.667) = 9.5219
```

But this data is full of ties -- counts of 1, 2, 3, 3, 3, 2, 1, 1 across the eight distinct values. The tie-corrected formula is:

<div class="formula" markdown="1">
**SD of U = &radic;[ (n&#8321;n&#8322; / (N(N&minus;1))) x ( (N&#179; &minus; N &minus; T) / 12 ) ]&nbsp;&nbsp;where T = &Sigma;(t&#179; &minus; t)**
<span class="formula-note">t is the number of observations in each tied group</span>
</div>

```
tie groups: 1x1, 2x2, 3x3, 3x4, 3x5, 2x6, 1x7, 1x8
T = (1-1) + (8-2) + (27-3) + (27-3) + (27-3) + (8-2) + (1-1) + (1-1)
  = 0 + 6 + 24 + 24 + 24 + 6 + 0 + 0
  = 84

SD = sqrt( (64 / (16 x 15)) x ((4096 - 16 - 84)/12) )
   = sqrt( (64/240) x (3996/12) )
   = sqrt( 0.26667 x 333 )
   = sqrt( 88.80 )
   = 9.4234

z = (U1 - mean)/SD = (51.5 - 32)/9.4234 = 19.5/9.4234 = 2.0693

two-sided p = .0385
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Why you cannot skip the tie correction</span>
Ties shrink the variance of the rank sum. Ignoring them uses too large an SD, which shrinks *z* and inflates *p* -- your test becomes conservative and you lose real findings. Here it is the difference between SD 9.5219 and 9.4234, which is small. On a 5-point Likert item with *n* = 200, where every value is tied dozens of times, the gap is large. Every serious package applies the correction automatically; check that yours says so.
</div>

## Effect size -- report one of these, always

**Rank-biserial correlation** (the standard choice):

<div class="formula" markdown="1">
**r = (U&#8321; &minus; U&#8322;) / (n&#8321; x n&#8322;)**
<span class="formula-note">runs from &minus;1 to +1, like any correlation</span>
</div>

```
r = (51.5 - 12.5) / 64 = 39/64 = .609
```

A large effect.

**Common-language effect size** (the one to put in front of a non-statistical reader):

```
P(a random A beats a random B) = U1 / (n1 x n2) = 51.5/64 = .805
```

"If you pick one client from each group at random, the new-workflow client reports higher satisfaction about 80% of the time." That sentence does more work in a defence than *r* = .609 does.

**What not to report:** Cohen's *d*. It is built from means and pooled SDs, which is exactly what you decided not to trust when you chose this test.

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span>
**Analyses -> T-Tests -> Independent Samples T-Test.**
Dependent variable: satisfaction. Grouping variable: workflow.
Under *Tests* tick **Mann-Whitney U**. Under *Additional Statistics* tick **Effect size** (gives rank-biserial) and **Descriptives**.
Jamovi reports *U*, the *p*, and the rank-biserial in one row.
</div>

**SPSS.**
`Analyze -> Nonparametric Tests -> Independent Samples`. Under *Fields* put satisfaction in *Test Fields* and workflow in *Groups*; under *Settings -> Customize tests* tick **Mann-Whitney U (2 samples)**. Double-click the result to open the Model Viewer, which shows the population pyramid of ranks and both the exact and asymptotic *p*.

SPSS's output labels the asymptotic *p* as "Asymp. Sig. (2-tailed)" and the exact one as "Exact Sig. [2*(1-tailed Sig.)]". **Report the exact one when n is under about 20 per group.**

**Excel.** Workable but manual. Pool both groups in one column with a group label beside it, then:

```
B2:  =RANK.AVG(A2,$A$2:$A$17,1)          ' mid-ranks, ascending
D1:  =SUMIF($C$2:$C$17,"A",$B$2:$B$17)   ' R1  -> 87.5
D2:  =D1-8*9/2                            ' U1  -> 51.5
D3:  =2*(1-NORM.S.DIST((D2-32)/9.4234,TRUE))  ' approximate p -> .0385
```

`RANK.AVG` is the function that makes this possible -- it gives mid-ranks for ties. The older `RANK` does not, and using it will give you wrong rank sums.

**R.**

```r
A <- c(3,4,4,5,5,6,7,8)
B <- c(1,2,2,3,3,4,5,6)

wilcox.test(A, B)                      # W = 51.5, p = .04377
wilcox.test(A, B, conf.int = TRUE)     # + Hodges-Lehmann shift and CI

# effect size
rstatix::wilcox_effsize(df, score ~ group)   # r = 0.609

# exact permutation p, no normal approximation at all
coin::wilcox_test(score ~ factor(group), data = df, distribution = "exact")
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">R's W is Mann-Whitney's U</span>
`wilcox.test` prints `W = 51.5`. That is *U*&#8321;, not the Wilcoxon signed-rank *W* from the previous lesson. R uses one function for both tests and one letter for both statistics. When you write it up, call it *U* if the design was independent and *W* if it was paired -- and R will also warn "cannot compute exact p-value with ties", which is simply telling you it fell back to the corrected normal approximation.
</div>

## Reading the output

Jamovi, for our data:

| | Statistic | p | Effect size |
|---|---|---|---|
| Student's t | 2.84 | .013 | 1.42 (Cohen's d) |
| Mann-Whitney U | 51.5 | .044 | 0.609 (rank-biserial) |

Group medians: A = 5.0, B = 3.0.

The t-test gives a smaller *p* again -- the usual power cost. Both reject. The conclusion is the same, and that agreement is worth one sentence in the write-up.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">APA, Mann-Whitney U</span>
"A Mann-Whitney *U* test showed that clients using the new workflow reported significantly higher satisfaction (*Mdn* = 5.0) than clients using the old workflow (*Mdn* = 3.0), *U* = 51.5, *z* = 2.07, *p* = .044, *r* = .61. A randomly chosen new-workflow client rated the service higher than a randomly chosen old-workflow client in approximately 80% of comparisons."
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Methods sentence that pre-empts the obvious question</span>
"Satisfaction was recorded on a single nine-point ordinal item with eight cases per group, so the Mann-Whitney *U* test was used in place of an independent-samples *t*-test. Exact *p*-values are reported; because of tied ranks the normal approximation with the tie correction is also given."
</div>

## Common mistakes

1. **Running Mann-Whitney on paired data.** If each person contributes to both columns, you need Wilcoxon signed-rank. Mann-Whitney treats the pairing as nonexistent and loses most of the power the design bought you.
2. **Using `RANK` instead of `RANK.AVG` in Excel.** Integer ranks for tied values give wrong rank sums and a wrong *U*.
3. **Reporting it as a test of medians without stating the equal-shape assumption.** It is a dominance test unless you add that assumption.
4. **Skipping the tie correction** on Likert data, where ties are the norm. It makes the test conservative.
5. **Reporting Cohen's *d* beside *U*.** You rejected the mean when you chose the test; do not reintroduce it in the effect size.
6. **Reporting the asymptotic *p* at *n* = 6 per group.** Use the exact one.
7. **Not saying which *U* you reported.** *U*&#8321; = 51.5 and *U*&#8322; = 12.5 both appear in textbooks. Many report min(*U*&#8321;, *U*&#8322;). Name it.

## Practice

<details markdown="1">
<summary>1. Two groups: A = 10, 14, 19 and B = 11, 12, 15. Work U1 and U2 by hand.</summary>

Pooled and sorted: 10(A), 11(B), 12(B), 14(A), 15(B), 19(A).
Ranks: 1, 2, 3, 4, 5, 6 -- no ties.

A holds ranks 1, 4, 6 &rarr; *R*&#8321; = 11.
B holds ranks 2, 3, 5 &rarr; *R*&#8322; = 10.

Check: 11 + 10 = 21, and *N*(*N*+1)/2 = 6(7)/2 = 21. &#10003;

```
U1 = 11 - (3 x 4)/2 = 11 - 6 = 5
U2 = 10 - (3 x 4)/2 = 10 - 6 = 4
check: 5 + 4 = 9 = 3 x 3   OK
```

*U*&#8321; = 5 of 9 pairs won by A -- almost exactly even. The exact two-sided *p* is **1.00**. Three per group can essentially never detect anything; the smallest achievable two-sided *p* with *n* = 3 and *n* = 3 is .10.
</details>

<details markdown="1">
<summary>2. In our worked example, why is R1 + R2 = 136 a useful check rather than a formality?</summary>

Because the sum of all ranks from 1 to *N* is fixed at *N*(*N*+1)/2 no matter how the data are distributed -- and mid-ranking preserves that total (the three 3s summing to 5+5+5 = 15 is exactly 4+5+6).

So if your two rank sums do not add to 136, you have made one of exactly three errors: miscounted a tie group, assigned a value to the wrong group, or dropped an observation. The check cannot tell you which, but it tells you to stop. Most hand-calculation marks are lost here.
</details>

<details markdown="1">
<summary>3. Group A has median 50 and group B has median 50, but A ranges 48-52 and B ranges 10-90. Could Mann-Whitney be significant?</summary>

Yes, and this is the clearest illustration of what the test really does.

With identical medians but wildly different spread, B contributes most of the lowest *and* most of the highest ranks. Depending on the exact values, B's rank sum can be pushed away from its expected value and *U* can reach significance -- even though neither group dominates in location.

What the test has detected is a **difference in distribution**, not a difference in median. This is why "Mann-Whitney tests medians" is only true under the equal-shape assumption. If your boxplots show very different spreads, say in the write-up that the test is detecting a distributional difference, and consider reporting the quantiles of both groups so the reader can see what kind.
</details>

<details markdown="1">
<summary>4. Compute the common-language effect size for U1 = 51.5, n1 = n2 = 8 — and sanity-check it against the raw data.</summary>

```
CL = U1 / (n1 x n2) = 51.5/64 = .805
```

Sanity check by brute force. Take the smallest A value, 3. Against B's 1, 2, 2, 3, 3, 4, 5, 6 it wins 3 (vs 1, 2, 2), ties 2 (vs 3, 3), loses 3 (vs 4, 5, 6). That is 3 + 0.5(2) = 4 of 8.

Take A's largest, 8. It beats all 8 B values &rarr; 8 of 8.

Doing all eight A values this way sums to 51.5 out of 64, which is *U*&#8321; -- confirming that *U* literally **is** the count of pairwise wins with ties at half. That identity is the most useful thing to know about the Mann-Whitney test, and it is what makes the common-language effect size exact rather than approximate.
</details>

<details markdown="1">
<summary>5. Your groups are n1 = 40 and n2 = 12. Is the big imbalance a problem?</summary>

Not for the validity of Mann-Whitney -- unlike the t-test, there is no pooled variance to be distorted by unequal *n*, and the formulas handle *n*&#8321; &ne; *n*&#8322; directly.

It costs you **power**, because power is driven by the harmonic mean of the group sizes. For 40 and 12 that is 2(40)(12)/52 = 18.5, so the pair behaves roughly like two groups of 18 or 19 rather than two groups of 26. Recruiting 12 more into the small group would buy far more power than 12 more into the large one.

The other thing to watch: with *n*&#8322; = 12 you should prefer the exact *p*-value, and check that your software is not silently falling back to the approximation because of ties.
</details>

## Before you move on

- [ ] I can tell a paired design from an independent one in one question.
- [ ] I can mid-rank a pooled sample with ties and verify *R*&#8321; + *R*&#8322; = *N*(*N*+1)/2.
- [ ] I can convert rank sums to *U* and check *U*&#8321; + *U*&#8322; = *n*&#8321;*n*&#8322;.
- [ ] I know *U* counts pairwise wins, ties at half.
- [ ] I can apply the tie correction and explain why omitting it is conservative.
- [ ] I report rank-biserial *r* and the common-language effect size, never Cohen's *d*.
- [ ] I know R prints `W` for what is actually *U*.""",
    quiz={
        "question": "n1 = n2 = 8 and you compute U1 = 51.5. What does 51.5 literally count?",
        "options": [
            "The sum of the ranks in group A",
            "The number of A-versus-B pairs, out of 64, in which the A value is larger, counting ties as one half",
            "The difference between the two medians scaled to the rank metric",
            "The number of observations in A above the pooled median",
        ],
        "answer": 1,
        "explanation": "U is the count of pairwise wins among all n1 x n2 = 64 comparisons, with each tie contributing 0.5. Dividing by 64 gives the common-language effect size, .805.",
    },
)


# ===========================================================================
L(
    "k Samples: Kruskal-Wallis and Friedman",
    """## What you will be able to do

Extend the two-sample logic to three or more groups: run Kruskal-Wallis *H* by hand, follow it with Dunn's post-hoc test and the right multiplicity correction, and run Friedman's test for the repeated-measures case -- plus report the effect sizes that go with each.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario A -- independent groups</span>
Eighteen plots of land, six under each of three fertiliser treatments. Yield in kilograms:

**T1:** 12, 15, 14, 18, 13, 16
**T2:** 22, 25, 19, 24, 21, 23
**T3:** 31, 28, 35, 30, 33, 29

Six per group is too few to trust a normality check. Kruskal-Wallis.
</div>

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario B -- repeated measures</span>
Eight judges each rank three teaching methods from best (1) to worst (3). Every judge sees all three methods, so the three columns are not independent -- they come from the same eight people. Friedman.
</div>

These two scenarios map onto one-way ANOVA and repeated-measures ANOVA respectively, and choosing the wrong one is the main error in this lesson.

## Kruskal-Wallis: the idea before the formula

It is Mann-Whitney generalised. Pool all *N* observations, rank them 1 to *N*, and compute each group's mean rank.

If all groups came from the same distribution, every group's mean rank should land near the overall mean rank, which is (*N*+1)/2. If one group's values are systematically higher, its mean rank will be pulled up and the others pushed down.

*H* measures how far the group mean ranks spread out from (*N*+1)/2. Large spread, large *H*. Under the null, *H* follows a chi-square distribution with *k* &minus; 1 degrees of freedom.

<div class="formula" markdown="1">
**H = [ 12 / (N(N+1)) ] x &Sigma;(R&#7522;&#178; / n&#7522;) &nbsp;&minus;&nbsp; 3(N+1)**
<span class="formula-note">R&#7522; is the rank sum of group i, n&#7522; its size, N the total; compare to chi-square with k&minus;1 df</span>
</div>

**Reading the formula term by term.**

- **&Sigma;(R&#7522;&#178;/n&#7522;)** -- the engine. Squaring each rank sum punishes imbalance: a group whose ranks are all high contributes a lot.
- **12/(N(N+1))** -- a scaling constant chosen so that the result follows chi-square. It is not arbitrary; 12 falls out of the variance of a discrete uniform distribution over 1..*N*.
- **&minus;3(N+1)** -- subtracts off the value &Sigma;(R&#7522;&#178;/n&#7522;) would take if every group had exactly the average rank sum. So *H* = 0 when the groups are perfectly balanced.

## Working Kruskal-Wallis by hand

**Step 1. Pool all 18 values and rank them.**

Here the groups happen not to overlap at all, which makes the ranking easy to follow:

| Group | Values | Ranks |
|---|---|---|
| T1 | 12, 15, 14, 18, 13, 16 | 1, 4, 3, 6, 2, 5 |
| T2 | 22, 25, 19, 24, 21, 23 | 9, 12, 7, 11, 8, 10 |
| T3 | 31, 28, 35, 30, 33, 29 | 16, 13, 18, 15, 17, 14 |

T1 took ranks 1-6, T2 took 7-12, T3 took 13-18. No ties, so no tie correction needed.

**Step 2. Rank sums and mean ranks.**

```
R1 = 1 + 4 + 3 + 6 + 2 + 5    = 21     mean rank = 21/6  =  3.5
R2 = 9 + 12 + 7 + 11 + 8 + 10 = 57     mean rank = 57/6  =  9.5
R3 = 16 + 13 + 18 + 15 + 17 + 14 = 93  mean rank = 93/6  = 15.5

check: 21 + 57 + 93 = 171
       N(N+1)/2 = (18 x 19)/2 = 171     <- match
```

The overall mean rank is (18+1)/2 = 9.5. T2 sits exactly on it; T1 is 6 below, T3 is 6 above. That symmetry is a hint that this is a clean monotone effect.

**Step 3. Plug into the formula.**

```
sum(Ri^2 / ni) = 21^2/6 + 57^2/6 + 93^2/6
               = 441/6 + 3249/6 + 8649/6
               = 73.5 + 541.5 + 1441.5
               = 2056.5

12 / (N(N+1)) = 12 / (18 x 19) = 12/342 = 0.035088

H = 0.035088 x 2056.5 - 3(19)
  = 72.1579 - 57
  = 15.1579
```

**Step 4. Degrees of freedom and *p*.**

df = *k* &minus; 1 = 3 &minus; 1 = **2**. From the chi-square distribution:

```
H = 15.1579, df = 2  ->  p = .000511
```

Reject H&#8320; decisively. The three fertilisers do not produce the same yield distribution.

<div class="callout callout-note" markdown="1">
<span class="callout-label">The small-sample caveat</span>
The chi-square approximation is good when each group has at least 5 observations. With six per group we are just inside that. If any group had 3 or 4, you would want the exact permutation test (R's `coin::kruskal_test(..., distribution = "approximate")` with many resamples, or SPSS's Monte Carlo option) rather than the chi-square *p*.
</div>

## Effect size for Kruskal-Wallis

*H* itself is not an effect size -- it grows with *N*. Two standard conversions:

<div class="formula" markdown="1">
**epsilon&#178; = H / (N &minus; 1)&nbsp;&nbsp;&nbsp;&nbsp;eta&#178;&#8341; = (H &minus; k + 1) / (N &minus; k)**
<span class="formula-note">both read as "proportion of rank variance explained"; epsilon&#178; is the more common report</span>
</div>

```
epsilon^2 = 15.1579 / 17 = .8916
eta^2_H   = (15.1579 - 2) / (18 - 3) = 13.1579/15 = .8772
```

Either way, roughly 88% of the variability in ranks is attributable to treatment group. Very large -- unsurprising given that the three groups did not overlap at all.

Benchmarks: .01 small, .06 medium, .14 large.

## Post-hoc: Dunn's test

A significant *H* says "not all groups are alike". It does not say which pairs differ. For that you need pairwise comparisons on the **pooled ranks you already computed** -- not fresh Mann-Whitney tests on each pair.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Why not just run three Mann-Whitney tests?</span>
Two reasons, and both are real.

First, **multiplicity**. Three tests at alpha = .05 give roughly a 14% chance of at least one false positive.

Second, and more subtly, **re-ranking changes the ranks**. A pairwise Mann-Whitney on T1 vs T2 re-ranks just those 12 values, discarding the information that T3 exists. Dunn's test keeps the original pooled ranking, which is the ranking the omnibus test used. The two approaches can disagree.
</div>

<div class="formula" markdown="1">
**z&#7522;&#11388; = (mean rank&#7522; &minus; mean rank&#11388;) / &radic;[ (N(N+1)/12) x (1/n&#7522; + 1/n&#11388;) ]**
<span class="formula-note">Dunn's statistic; multiply each p by the number of comparisons for Bonferroni</span>
</div>

**Step 1. The standard error is the same for every pair here, because the groups are equal-sized.**

```
SE = sqrt( (18 x 19 / 12) x (1/6 + 1/6) )
   = sqrt( 28.5 x 0.33333 )
   = sqrt( 9.5 )
   = 3.0822
```

**Step 2. Each comparison.**

| Comparison | Mean rank difference | z | raw p | Bonferroni p (x3) |
|---|---|---|---|---|
| T1 vs T2 | 3.5 &minus; 9.5 = &minus;6.0 | &minus;1.9467 | .0516 | **.1547** |
| T1 vs T3 | 3.5 &minus; 15.5 = &minus;12.0 | &minus;3.8933 | .0001 | **.0003** |
| T2 vs T3 | 9.5 &minus; 15.5 = &minus;6.0 | &minus;1.9467 | .0516 | **.1547** |

Worked for the middle row:

```
z = -12.0 / 3.0822 = -3.8933
two-sided p = 2 x P(Z < -3.8933) = .0001
Bonferroni:  .0001 x 3 = .0003
```

**Step 3. Read the result honestly.**

Only **T1 vs T3** survives correction. T1 vs T2 and T2 vs T3 are each at *p* = .052 raw, which Bonferroni pushes to .155.

This is the common and slightly uncomfortable outcome: a hugely significant omnibus test (*p* = .0005, epsilon&#178; = .89) where only the extreme pair is significant pairwise. It is not a contradiction. The omnibus test uses all 18 observations against one null; each pairwise test effectively uses 12 and then pays a multiplicity tax. **Six per group is simply not enough to separate adjacent groups.**

<div class="callout callout-note" markdown="1">
<span class="callout-label">Bonferroni or something gentler?</span>
Bonferroni is the most conservative correction and the easiest to defend. With three comparisons it is fine.

With many comparisons it becomes punishing, and **Holm's step-down** method is strictly better -- same guarantee, more power. Holm sorts the raw *p*-values ascending and multiplies the smallest by *m*, the next by *m*&minus;1, and so on, stopping at the first non-significant one. For our data Holm gives .0003, .1032, .1032 -- the same decision here, but it will differ in closer cases. Most packages offer Holm; prefer it, and say which you used.
</div>

## Friedman's test: the repeated-measures case

Now Scenario B. Eight judges, three methods, every judge sees all three.

**The key difference: ranking happens *within* each row, not across the whole table.** Judge 1's ranks of the three methods are independent of judge 2's. This is what removes the between-judge variation -- the same thing blocking does in a randomised complete block design.

| Judge | Method A | Method B | Method C |
|---|---|---|---|
| 1 | 3 | 2 | 1 |
| 2 | 3 | 1 | 2 |
| 3 | 2 | 3 | 1 |
| 4 | 3 | 2 | 1 |
| 5 | 3 | 1 | 2 |
| 6 | 2 | 3 | 1 |
| 7 | 3 | 2 | 1 |
| 8 | 3 | 1 | 2 |
| **Rank sum** | **22** | **15** | **11** |

(Here the judges supplied ranks directly. If they had given scores, you would rank each judge's three scores 1-2-3 yourself before summing columns.)

Check: 22 + 15 + 11 = 48, and *n* x *k*(*k*+1)/2 = 8 x 6 = 48. &#10003;

<div class="formula" markdown="1">
**Q = [ 12 / (n k (k+1)) ] x &Sigma;R&#11388;&#178; &nbsp;&minus;&nbsp; 3n(k+1)**
<span class="formula-note">n = blocks (judges), k = treatments; compare to chi-square with k&minus;1 df</span>
</div>

```
sum of squared column sums = 22^2 + 15^2 + 11^2
                           = 484 + 225 + 121
                           = 830

12 / (n k (k+1)) = 12 / (8 x 3 x 4) = 12/96 = 0.125

Q = 0.125 x 830 - 3 x 8 x 4
  = 103.75 - 96
  = 7.75

df = k - 1 = 2  ->  p = .0208
```

Reject. The three methods are not ranked equally.

**Effect size: Kendall's W (the coefficient of concordance).**

<div class="formula" markdown="1">
**W = Q / [ n(k &minus; 1) ]**
<span class="formula-note">0 = judges completely disagree, 1 = judges agree perfectly</span>
</div>

```
W = 7.75 / (8 x 2) = 7.75/16 = .4844
```

Moderate agreement. The judges broadly agree that A is worst and C is best, but they are not unanimous -- rows 3 and 6 put B last, and rows 2, 5 and 8 put C second.

That interpretation is worth the extra sentence. *W* answers a question *Q* cannot: not just "do the methods differ" but "how much do the raters agree about how they differ".

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span>
**Kruskal-Wallis:** Analyses -> ANOVA -> **One-Way ANOVA (Non-parametric)** -- Kruskal-Wallis. Put yield in *Dependent Variables*, treatment in *Grouping Variable*, and tick **Pairwise comparisons (Dunn's)** and **Effect size**.
**Friedman:** Analyses -> ANOVA -> **Repeated Measures ANOVA (Non-parametric)** -- Friedman. Move all three method columns into *Measures*, then tick **Pairwise comparisons** and **Kendall's W**.
</div>

**SPSS.**
Kruskal-Wallis: `Analyze -> Nonparametric Tests -> Independent Samples`, tick *Kruskal-Wallis 1-way ANOVA (k samples)*. Then in *Settings -> Multiple comparisons* choose **All pairwise** -- that is Dunn's test with a Bonferroni adjustment, and SPSS reports both the raw and adjusted *p*.

Friedman: `Analyze -> Nonparametric Tests -> Related Samples`, tick *Friedman's two-way ANOVA by ranks (k samples)*, and again set *Multiple comparisons* to All pairwise.

**Excel.** Kruskal-Wallis is assembleable: `RANK.AVG` over the pooled column, `SUMIF` per group, then the *H* formula in one cell and `=CHISQ.DIST.RT(H, 2)` for the *p*. Dunn's post-hoc needs `NORM.S.DIST`. Friedman is easier -- rank within rows with `RANK.AVG` across three cells, sum the columns, apply *Q*. It works, but at this point Jamovi is a ten-minute install that does all of it with effect sizes.

**R.**

```r
# Kruskal-Wallis
kruskal.test(yield ~ treatment, data = d)
#  chi-squared = 15.158, df = 2, p-value = 0.000511

# effect size
rstatix::kruskal_effsize(d, yield ~ treatment)      # eta2[H] = 0.877

# Dunn post-hoc, Holm-adjusted
dunn.test::dunn.test(d$yield, d$treatment, method = "holm")
# or
rstatix::dunn_test(d, yield ~ treatment, p.adjust.method = "holm")

# Friedman: needs a matrix of blocks x treatments
friedman.test(as.matrix(ranks))
#  Friedman chi-squared = 7.75, df = 2, p-value = 0.02075

rstatix::friedman_effsize(long, rank ~ method | judge)   # Kendall W = 0.484
PMCMRplus::frdAllPairsNemenyiTest(as.matrix(ranks))      # post-hoc
```

## Reading the output

SPSS's Kruskal-Wallis pairwise table for our data looks like this:

| Sample 1 - Sample 2 | Test Statistic | Std. Error | Std. Test Statistic | Sig. | Adj. Sig. |
|---|---|---|---|---|---|
| T1 - T2 | &minus;6.000 | 3.082 | &minus;1.947 | .052 | .155 |
| T1 - T3 | &minus;12.000 | 3.082 | &minus;3.893 | .000 | .000 |
| T2 - T3 | &minus;6.000 | 3.082 | &minus;1.947 | .052 | .155 |

"Test Statistic" is the **mean rank difference** -- the same &minus;6, &minus;12, &minus;6 we computed. "Std. Test Statistic" is Dunn's *z*. "Adj. Sig." is Bonferroni-corrected. Report **Adj. Sig.**, and never read the unadjusted column as if it were the result.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">APA, Kruskal-Wallis with post-hoc</span>
"A Kruskal-Wallis test showed a significant difference in yield across the three fertiliser treatments, *H*(2) = 15.16, *p* &lt; .001, epsilon&#178; = .89. Mean ranks were 3.50 (T1), 9.50 (T2) and 15.50 (T3). Dunn's post-hoc comparisons with Holm adjustment found T3 significantly higher than T1 (*z* = 3.89, *p*&#8322;&#8339;&#11388; &lt; .001); the T1-T2 and T2-T3 comparisons did not reach significance after adjustment (both *z* = 1.95, *p*&#8322;&#8339;&#11388; = .103). With six plots per treatment, adjacent-group differences of this size were underpowered."
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">APA, Friedman</span>
"A Friedman test indicated that the three teaching methods were not ranked equally, chi-square(2) = 7.75, *p* = .021. Rank sums were 22 (Method A), 15 (Method B) and 11 (Method C), with Method C ranked best most often. Kendall's *W* = .48 indicated moderate agreement among the eight judges."
</div>

That last clause -- the honest note about being underpowered for adjacent groups -- is what separates a defensible write-up from one that overclaims. Say it before the panel does.

## Common mistakes

1. **Using Kruskal-Wallis on repeated measures.** If the same subjects appear in every group, you need Friedman. Kruskal-Wallis assumes independence across all *N* observations.
2. **Ranking across the whole table in Friedman.** Friedman ranks *within each block*. Ranking globally destroys the blocking and gives a meaningless *Q*.
3. **Running pairwise Mann-Whitney tests instead of Dunn's.** It re-ranks each pair and ignores multiplicity.
4. **Reading the unadjusted post-hoc *p*.** The whole point of the correction is that you must read the adjusted column.
5. **Reporting *H* as an effect size.** *H* scales with *N*. Convert to epsilon&#178; or eta&#178;&#8341;.
6. **Concluding "no differences" when the omnibus is significant but no pair survives.** The correct conclusion is "the groups differ overall, but this sample cannot localise which pairs". Those are different statements.
7. **Forgetting the rank-sum check.** &Sigma;*R*&#7522; must equal *N*(*N*+1)/2 for Kruskal-Wallis and *nk*(*k*+1)/2 for Friedman.

## Practice

<details markdown="1">
<summary>1. Three groups with n = 4, 5, 6 and rank sums 20, 40, 60. N = 15. Compute H.</summary>

```
sum(Ri^2/ni) = 400/4 + 1600/5 + 3600/6
             = 100 + 320 + 600
             = 1020

12/(N(N+1)) = 12/(15 x 16) = 12/240 = 0.05

H = 0.05 x 1020 - 3(16)
  = 51 - 48
  = 3.00

df = 2  ->  p = .223
```

Do not reject. And check the rank sums first: 20 + 40 + 60 = 120, and *N*(*N*+1)/2 = 15(16)/2 = 120. &#10003;

Note how unequal *n* is handled automatically -- dividing *R*&#7522;&#178; by *n*&#7522; is what makes the formula work for unbalanced designs with no extra step.
</details>

<details markdown="1">
<summary>2. Our omnibus test gave p = .0005 but two of three pairs were non-significant after correction. Explain this to a panel member who thinks it is a contradiction.</summary>

It is not a contradiction, and here is the structure of the answer.

The omnibus test asks one question of all 18 observations: *is the treatment variable related to yield at all?* It has the full sample behind it and spends its alpha once. The answer is a very clear yes, and epsilon&#178; = .89 says the relationship is strong.

Each pairwise test asks a narrower question using only 12 observations, and then pays a threefold multiplicity tax. T1 vs T2 has a mean-rank gap of 6 and a standard error of 3.08, giving *z* = 1.95 -- just under the 1.96 threshold even *before* correction.

So the data clearly support "fertiliser matters" and simply do not have the resolution to certify "T2 beats T1" at this sample size. The fix is more plots per treatment, not a different test. Reporting the mean ranks (3.5 / 9.5 / 15.5) lets the reader see the monotone pattern even where the pairwise tests cannot certify it.
</details>

<details markdown="1">
<summary>3. Four judges rank 3 items and all four give the identical ordering 1, 2, 3. Compute Q and Kendall's W.</summary>

Column rank sums: 4, 8, 12. Check: 4 + 8 + 12 = 24 = *nk*(*k*+1)/2 = 4(3)(4)/2 = 24. &#10003;

```
sum of squares = 16 + 64 + 144 = 224
12/(n k (k+1)) = 12/(4 x 3 x 4) = 12/48 = 0.25

Q = 0.25 x 224 - 3(4)(4)
  = 56 - 48
  = 8.00

df = 2  ->  p = .0183

W = Q / (n(k-1)) = 8/(4 x 2) = 1.00
```

*W* = 1.00 is **perfect agreement**, as it must be when every judge gives the same ordering -- a useful check that you have the formula right.

Worth noticing: *Q* = 8.00 with *p* = .018 even though the agreement is total. With only 4 judges and 3 items, perfect unanimity is the most extreme result available and it still only reaches *p* = .018. That is the small-sample ceiling for Friedman.
</details>

<details markdown="1">
<summary>4. Why does Friedman rank within blocks, and what would be lost by ranking across the whole table?</summary>

Because the blocks are the nuisance. Judge 3 may be harsh across the board and judge 7 generous; those are judge effects, not method effects, and the design exists to remove them.

Ranking within a row re-expresses each judge's data as "which method did *this* judge prefer", which is free of that judge's personal level. Summing those within-row ranks down a column then isolates the method effect.

Rank globally instead and judge 7's generous scores would all receive high ranks regardless of method, so the column sums would be contaminated by who rated what. In the extreme case where every judge prefers C but judges differ hugely in severity, global ranking can completely mask the method effect -- exactly the failure that blocking is designed to prevent. Friedman is the nonparametric analogue of a randomised complete block design, and the within-row ranking *is* the blocking.
</details>

<details markdown="1">
<summary>5. You have 5 groups. How many pairwise comparisons, and what does Bonferroni do to your alpha?</summary>

Pairs = C(5,2) = 5 x 4/2 = **10**.

Bonferroni divides alpha by 10, so each comparison is tested at **.005** -- or equivalently each *p* is multiplied by 10. A raw *p* of .03, comfortably significant on its own, becomes .30.

This is where Bonferroni starts to hurt, and where **Holm** is worth the small extra effort. Holm multiplies the smallest *p* by 10, the second by 9, the third by 8, and so on, stopping at the first that fails. The family-wise error guarantee is identical, but the later comparisons face a much lower bar. With 10 comparisons Holm will typically recover one or two findings Bonferroni discards.

A third option, if you are willing to control the *false discovery rate* rather than the family-wise error rate, is Benjamini-Hochberg -- much more powerful, but a weaker guarantee. Choose before you look at the results, and state the choice in your methods.
</details>

## Before you move on

- [ ] I can tell a Kruskal-Wallis design from a Friedman design.
- [ ] I can compute *H* by hand and verify &Sigma;*R*&#7522; = *N*(*N*+1)/2.
- [ ] I can compute Dunn's *z* for a pair and apply Bonferroni or Holm.
- [ ] I know Friedman ranks within blocks, and why.
- [ ] I can compute and interpret Kendall's *W*.
- [ ] I can explain a significant omnibus with no significant pairs without calling it a contradiction.""",
    quiz={
        "question": "Kruskal-Wallis gives H(2) = 15.16, p < .001, but after Bonferroni no pairwise comparison except the extremes is significant. What is the correct conclusion?",
        "options": [
            "The Kruskal-Wallis result must be a false positive",
            "The groups differ overall, but with six per group the sample cannot localise which adjacent pairs differ",
            "Report the unadjusted pairwise p-values instead",
            "Switch to one-way ANOVA, which will have more power",
        ],
        "answer": 1,
        "explanation": "The omnibus test uses all N observations against a single null; each pairwise test uses a subset and pays a multiplicity tax. Both results are correct. Report the mean ranks so the pattern is visible, and note the power limitation.",
    },
)


# ===========================================================================
L(
    "Measures of Association: Spearman and Kendall",
    """## What you will be able to do

Compute Spearman's rho from the rank-difference shortcut and Kendall's tau from concordant and discordant pairs, by hand, and choose between them for a reason rather than by habit.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
Ten students' weekly study hours and their final grades:

| Hours | 12 | 15 | 18 | 20 | 22 | 25 | 28 | 30 | 35 | 40 |
|---|---|---|---|---|---|---|---|---|---|---|
| Grade | 20 | 24 | 21 | 30 | 28 | 35 | 33 | 40 | 38 | 45 |

Is there a relationship? Pearson's *r* would answer "is it linear". But we may only care whether more hours go with higher grades -- a monotone question, not a linear one.
</div>

## Two different questions

| Coefficient | What it measures | When to prefer it |
|---|---|---|
| **Pearson r** | Strength of the *linear* relationship between the values | Both variables interval, relationship straight, no extreme outliers |
| **Spearman rho** | Strength of the *monotone* relationship between the ranks | Ordinal data, curved-but-monotone relationships, outliers present |
| **Kendall tau** | Probability that a randomly chosen pair is ordered the same way in both variables | Small *n*, many ties, or when you need an interpretable probability |

Spearman is literally **Pearson computed on the ranks**. That is not an analogy -- it is the definition, and it is why a curved monotone relationship that gives Pearson *r* = .85 can give Spearman rho = 1.00.

## Spearman: the idea before the formula

Rank each variable separately. Then ask: do the two rank orders agree?

If student A is 1st in hours and 1st in grades, 2nd and 2nd, and so on all the way down, the rank orders agree perfectly and rho = 1. If they are exactly reversed, rho = &minus;1. If the orders are unrelated, rho sits near 0.

<div class="formula" markdown="1">
**rho = 1 &minus; [ 6 x &Sigma;d&#7522;&#178; ] / [ n(n&#178; &minus; 1) ]**
<span class="formula-note">d&#7522; = rank of x&#7522; minus rank of y&#7522;; valid only when there are no ties</span>
</div>

**Reading it term by term.**

- **d&#7522;** is the disagreement for one case. Perfect agreement gives every *d* = 0.
- **&Sigma;d&#7522;&#178;** aggregates disagreement, squaring so that direction does not cancel.
- **n(n&#178;&minus;1)** is the largest &Sigma;d&#178; could be divided by 6 -- a normalising constant that forces the result into [&minus;1, 1].
- The **1 &minus; ...** makes large disagreement give a small rho.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The shortcut formula fails with ties</span>
That formula is exact only when neither variable has tied values. With ties you must fall back to computing Pearson's *r* on the mid-ranks, which is what every software package does anyway. If you use the shortcut on tied data you will get a number that is close but wrong -- and on heavily tied data like a 5-point Likert item, badly wrong.
</div>

## Working Spearman by hand

**Step 1. Rank each variable separately, smallest = 1.**

| Student | Hours | Rank X | Grade | Rank Y | d | d&#178; |
|---|---|---|---|---|---|---|
| 1 | 12 | 1 | 20 | 1 | 0 | 0 |
| 2 | 15 | 2 | 24 | 3 | &minus;1 | 1 |
| 3 | 18 | 3 | 21 | 2 | +1 | 1 |
| 4 | 20 | 4 | 30 | 5 | &minus;1 | 1 |
| 5 | 22 | 5 | 28 | 4 | +1 | 1 |
| 6 | 25 | 6 | 35 | 7 | &minus;1 | 1 |
| 7 | 28 | 7 | 33 | 6 | +1 | 1 |
| 8 | 30 | 8 | 40 | 9 | &minus;1 | 1 |
| 9 | 35 | 9 | 38 | 8 | +1 | 1 |
| 10 | 40 | 10 | 45 | 10 | 0 | 0 |

Hours were already in ascending order, so Rank X is 1 to 10. Grades were not, so Rank Y has to be worked out: the smallest grade is 20 (rank 1), then 21 (rank 2), then 24 (rank 3), 28 (rank 4), 30 (rank 5), 33 (rank 6), 35 (rank 7), 38 (rank 8), 40 (rank 9), 45 (rank 10).

**Step 2. A check before you continue.** &Sigma;*d* must be 0: (0 &minus;1 +1 &minus;1 +1 &minus;1 +1 &minus;1 +1 +0) = 0. &#10003;

This always holds, because both rank columns sum to *n*(*n*+1)/2. If your *d* column does not sum to zero, you have mis-ranked.

**Step 3. Sum the squares.**

```
sum of d^2 = 0 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 0 = 8
```

**Step 4. Apply the formula.**

```
rho = 1 - (6 x 8) / (10 x (100 - 1))
    = 1 - 48 / (10 x 99)
    = 1 - 48/990
    = 1 - 0.048485
    = .9515
```

**Step 5. The *p*-value.** For *n* = 10, scipy gives **p = .0000228**. Reject H&#8320;: rho = 0 decisively.

**Step 6. Compare with Pearson on the same data: *r* = .9472.**

Spearman is slightly *higher* here. The eight rank disagreements are all adjacent swaps -- 2 with 3, 4 with 5, 6 with 7, 8 with 9 -- so in rank terms the relationship is almost perfectly monotone, while in value terms the grade of 21 sitting between 20 and 24 pulls the straight line slightly off.

## Kendall's tau: a different and more interpretable idea

Forget rank differences. Take every possible **pair** of students and ask one question of each: *do the two variables agree about which student is higher?*

- **Concordant** -- student A has more hours *and* a higher grade than student B. The pair agrees.
- **Discordant** -- A has more hours but a *lower* grade. The pair disagrees.

<div class="formula" markdown="1">
**tau = (C &minus; D) / [ n(n &minus; 1)/2 ]**
<span class="formula-note">C = concordant pairs, D = discordant pairs; the denominator is the total number of pairs</span>
</div>

## Working Kendall by hand

**Step 1. Count the pairs.** With *n* = 10 there are 10 x 9/2 = **45** pairs.

**Step 2. Classify each one.** Because Hours is already sorted ascending, every pair is concordant unless the grades are out of order. So we only need to count the **inversions** in the grade column.

Grade order as listed: 20, 24, 21, 30, 28, 35, 33, 40, 38, 45.

Reading left to right, count how many later values are *smaller* than each value:

| Value | Later values smaller than it | Inversions |
|---|---|---|
| 20 | none | 0 |
| 24 | 21 | 1 |
| 21 | none | 0 |
| 30 | 28 | 1 |
| 28 | none | 0 |
| 35 | 33 | 1 |
| 33 | none | 0 |
| 40 | 38 | 1 |
| 38 | none | 0 |
| 45 | none | 0 |
| | **Total D** | **4** |

So **D = 4** and **C = 45 &minus; 4 = 41**.

**Step 3. Apply the formula.**

```
tau = (41 - 4) / 45 = 37/45 = .8222
```

**Step 4. The *p*-value.** scipy gives **p = .000358**.

**Step 5. The large-sample *z*, for when *n* is big enough.**

<div class="formula" markdown="1">
**z = 3(C &minus; D) / &radic;[ n(n&minus;1)(2n+5) / 2 ]**
<span class="formula-note">normal approximation; reliable from about n = 10 upward</span>
</div>

```
z = 3(41 - 4) / sqrt( 10 x 9 x 25 / 2 )
  = 111 / sqrt(1125)
  = 111 / 33.5410
  = 3.3094
```

## Why tau is smaller than rho, and why that is not a problem

For this data: rho = **.9515**, tau = **.8222**.

Tau is almost always smaller in absolute value than rho on the same data -- typically around two-thirds of it for moderate associations. They are on **different scales measuring different things**, so comparing their magnitudes is a category error.

Tau's scale has a meaning rho's does not:

```
tau = .8222  means  P(concordant) - P(discordant) = .8222

and since P(C) + P(D) = 1 (no ties),
  P(concordant) = (1 + .8222)/2 = .911
```

**"Pick two students at random: 91% of the time the one who studied more also scored higher."** You can say that sentence to a non-statistician and they will understand it exactly. There is no comparable sentence for rho = .9515.

<div class="callout callout-note" markdown="1">
<span class="callout-label">Choosing between them</span>
**Use tau when:** *n* is small (its sampling distribution approaches normality faster), there are many ties (tau-b handles them cleanly), or your reader needs an interpretable number.

**Use rho when:** you want the familiar correlation scale, you plan to compare against published Pearson or Spearman values, or you need rho&#178; as a rough variance-explained analogue.

**In practice** they almost never disagree about significance. Report whichever your field expects -- education and psychology mostly use Spearman; econometrics and some medical fields prefer Kendall. If you have no constraint, Kendall's interpretability is a real advantage.
</div>

## Handling ties: tau-a, tau-b, tau-c

With tied values, some pairs are neither concordant nor discordant. Three variants exist:

| Variant | Denominator | Use for |
|---|---|---|
| **tau-a** | *n*(*n*&minus;1)/2 | No ties at all |
| **tau-b** | Geometric mean of the tie-adjusted pair counts | Ties present, square table |
| **tau-c** | Adjusted for table shape | Rectangular tables (e.g. 3 x 5) |

**tau-b is the default in every package and the right choice in almost every real analysis.** It is what scipy's `kendalltau` and SPSS's "Kendall's tau-b" report. For our tie-free data all three coincide at .8222.

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span>
**Analyses -> Regression -> Correlation Matrix.** Move both variables in, then under *Correlation Coefficients* tick **Spearman** and **Kendall's tau-b** (and Pearson, to compare). Tick *Confidence intervals* and the scatterplot under *Plot*.
Running all three at once and looking at the gap between them is genuinely informative: a Pearson far below a Spearman means the relationship is monotone but curved.
</div>

**SPSS.**
`Analyze -> Correlate -> Bivariate`. Tick **Spearman** and **Kendall's tau-b** in the *Correlation Coefficients* box. SPSS reports the coefficient, the two-tailed *p* and *N* in one table.

**Excel.** Spearman has a neat trick -- rank both columns with `RANK.AVG`, then run `CORREL` on the rank columns:

```
C2:  =RANK.AVG(A2,$A$2:$A$11,1)     ' rank of hours
D2:  =RANK.AVG(B2,$B$2:$B$11,1)     ' rank of grades
F1:  =CORREL(C2:C11,D2:D11)          ' -> 0.951515  = Spearman rho
F2:  =CORREL(A2:A11,B2:B11)          ' -> 0.947195  = Pearson r
```

That first formula is the definition of Spearman made visible: Pearson on the ranks. And because `CORREL` handles mid-ranks correctly, this approach stays valid with ties where the 6&Sigma;*d*&#178; shortcut does not.

Kendall's tau is not available in Excel without an add-in.

**R.**

```r
hours  <- c(12,15,18,20,22,25,28,30,35,40)
grades <- c(20,24,21,30,28,35,33,40,38,45)

cor(hours, grades, method = "spearman")   # 0.9515152
cor(hours, grades, method = "kendall")     # 0.8222222
cor(hours, grades, method = "pearson")     # 0.9471945

cor.test(hours, grades, method = "spearman")
#  S = 8, p-value = 2.28e-05        <- note: S is the sum of d-squared
cor.test(hours, grades, method = "kendall")
#  T = 41, p-value = 0.0003577      <- T is the concordant count

# the identity, demonstrated
cor(rank(hours), rank(grades))             # 0.9515152, same as Spearman
```

<div class="callout callout-note" markdown="1">
<span class="callout-label">R prints your hand-computed intermediates</span>
`cor.test(..., method = "spearman")` reports **S = 8** -- that is exactly our &Sigma;*d*&#178;. And the Kendall version reports **T = 41**, our concordant count. Your hand calculation and the software are not just agreeing on the final answer; they are agreeing step by step. That is the cheapest possible way to verify you understood the method.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">APA, Spearman</span>
"Weekly study hours were strongly and positively associated with final grades, *r*&#8347; = .95, *p* &lt; .001, *n* = 10. Kendall's tau-b gave the same conclusion, tau = .82, *p* &lt; .001; in 91% of randomly selected student pairs, the student who studied more also scored higher."
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Methods, justifying the choice</span>
"Because the relationship between study hours and grades was expected to be monotone rather than strictly linear, and because *n* was small, association was quantified with Spearman's rho and Kendall's tau-b rather than Pearson's *r*. Pearson's *r* is reported alongside for comparison."
</div>

## Common mistakes

1. **Using the 6&Sigma;*d*&#178; shortcut when there are ties.** Use Pearson-on-mid-ranks instead -- or just use `CORREL` on the rank columns, which does it correctly.
2. **Comparing rho and tau as if they were on the same scale.** Tau is systematically smaller. The gap is not a discrepancy.
3. **Reporting tau-a on tied data.** tau-b is the default for a reason.
4. **Forgetting to check &Sigma;*d* = 0.** Free error detection.
5. **Claiming causation.** "Students who study more get higher grades" is the finding. "Studying more causes higher grades" is not -- able students may both study more and score higher.
6. **Squaring tau and calling it variance explained.** rho&#178; has a loose variance-explained reading; tau&#178; has none.
7. **Reporting only the coefficient.** Give the *p*, the *n*, and ideally the scatterplot. A rho of .95 at *n* = 5 is not the same finding as a rho of .95 at *n* = 500.

## Practice

<details markdown="1">
<summary>1. Five cases, rank X = 1,2,3,4,5 and rank Y = 5,4,3,2,1. Compute rho.</summary>

```
d  = 1-5, 2-4, 3-3, 4-2, 5-1 = -4, -2, 0, 2, 4
check: sum d = 0  OK
d^2 = 16, 4, 0, 4, 16        sum = 40

rho = 1 - (6 x 40)/(5 x (25-1))
    = 1 - 240/120
    = 1 - 2
    = -1.00
```

Perfect negative association, as it must be for an exactly reversed ordering. This is also a good way to remember the formula's scaling: &Sigma;*d*&#178; = 40 is the maximum possible for *n* = 5, and the formula maps that maximum exactly to &minus;1.
</details>

<details markdown="1">
<summary>2. Same five cases. Compute Kendall's tau.</summary>

Every one of the C(5,2) = 10 pairs is discordant, because whenever X increases Y decreases.

```
tau = (0 - 10)/10 = -1.00
```

So rho and tau both hit &minus;1 at perfect reversal. They agree at the extremes (&minus;1, 0, +1) and diverge in between -- which is precisely why their intermediate values cannot be compared directly.
</details>

<details markdown="1">
<summary>3. Pearson r = .62 but Spearman rho = .94 on the same data. What is going on, and which do you report?</summary>

The relationship is **strongly monotone but not linear** -- almost certainly curved. A classic case is exponential growth: as X rises, Y rises every time (so the ranks agree almost perfectly, giving rho = .94) but the increments get larger and larger, so no straight line fits well (*r* = .62).

A single high-leverage outlier can also produce this gap, in either direction.

**What to do:** plot it. The scatterplot will immediately show whether it is a curve or an outlier.

- **Curve:** report Spearman, and say the relationship is monotone but nonlinear. Consider whether log(Y) would straighten it, in which case Pearson on the transformed variable becomes meaningful.
- **Outlier:** investigate the case. If it is a data error, fix it. If it is real, report both coefficients and note the sensitivity.

Never report only the larger of the two without explaining the gap.
</details>

<details markdown="1">
<summary>4. Both variables are 5-point Likert items, n = 200. Spearman or Kendall?</summary>

**Kendall's tau-b**, and the reason is ties.

With 200 cases spread over 5 x 5 = 25 possible combinations, there will be dozens of tied values in every category. Spearman handles this by mid-ranking, which works, but the resulting rho is hard to interpret and is attenuated by the heavy tying in a way that is not transparent.

tau-b was designed for exactly this situation: its denominator explicitly adjusts for the tied pairs, so the coefficient keeps its "excess of concordant over discordant pairs" meaning even on a coarse scale.

A further option worth knowing for two ordinal variables with few categories: **polychoric correlation**, which models an underlying continuous variable beneath each ordinal item and estimates the correlation between those latents. It is standard in scale development and in SEM, and typically returns a larger value than either rho or tau because it undoes the attenuation that coarse categories cause.
</details>

<details markdown="1">
<summary>5. Convert tau = .60 into a statement about pairs.</summary>

```
P(concordant) - P(discordant) = .60
P(concordant) + P(discordant) = 1        (assuming no ties)

Adding:  2 x P(concordant) = 1.60
         P(concordant) = .80
```

**"In 80% of randomly chosen pairs, the two variables agree about which case is higher."**

That is the sentence to put in a results section for a non-technical reader. Note the assumption in the second line -- with ties present, P(C) + P(D) is less than 1 and the conversion is only approximate.
</details>

## Before you move on

- [ ] I can compute rho from &Sigma;*d*&#178; and verify &Sigma;*d* = 0 first.
- [ ] I know the shortcut formula is invalid with ties, and what to use instead.
- [ ] I can count concordant and discordant pairs and compute tau.
- [ ] I can explain why tau is smaller than rho without calling it a discrepancy.
- [ ] I can convert tau into a probability statement about pairs.
- [ ] I know tau-b is the default variant and why.
- [ ] I know Spearman is literally Pearson on the ranks, and can demonstrate it in Excel.""",
    quiz={
        "question": "On the same dataset you get Pearson r = .58 and Spearman rho = .96. What is the most likely explanation?",
        "options": [
            "One of the two was computed incorrectly",
            "The relationship is strongly monotone but curved, or a single outlier is distorting the linear fit",
            "Spearman always exceeds Pearson, so the gap means nothing",
            "The sample is too small for Pearson to be valid",
        ],
        "answer": 1,
        "explanation": "Spearman only needs the rank orders to agree; Pearson needs a straight line. A large gap points to curvature or an influential outlier. Plot the data to tell which, then report accordingly.",
    },
)


# ===========================================================================
L(
    "Tests for Randomness and Goodness of Fit",
    """## What you will be able to do

Test whether a sequence is random using the runs test, and whether a sample came from a claimed distribution using chi-square goodness of fit and the Kolmogorov-Smirnov test -- and know which of those three answers the question you actually have.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario A -- is the sequence random?</span>
A quality inspector records 20 consecutive fill weights from a bottling machine:

`48, 52, 47, 53, 46, 54, 45, 55, 44, 56, 49, 51, 50, 52, 48, 53, 47, 54, 46, 55`

The mean is near target and the standard deviation is acceptable. Both of the usual checks pass. But the inspector has a feeling something is wrong.
</div>

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario B -- does the distribution fit?</span>
A survey offers five response options and the researcher claims respondents chose at random. Observed counts, *n* = 150:

`42, 35, 28, 20, 25`

If choice were random, each option should attract about 30.
</div>

## The runs test: the idea before the formula

A **run** is a maximal streak of consecutive observations on the same side of some reference point -- usually the median.

Convert every observation to "above" (A) or "below" (B), then count the streaks.

Two failure modes exist, and this is the crucial point most treatments bury:

- **Too few runs** means clustering -- a trend, a drift, a shift in the process. `AAAAABBBBB` is 2 runs in 10 observations.
- **Too many runs** means over-alternation -- negative autocorrelation, often an over-correcting controller. `ABABABABAB` is 10 runs in 10.

Both are non-random. The test is two-sided and catches both.

## Working the runs test on Scenario A

**Step 1. Find the median.**

Sorted: 44, 45, 46, 46, 47, 47, 48, 48, 49, 50, 51, 52, 52, 53, 53, 54, 54, 55, 55, 56.

With *n* = 20, the median is the average of the 10th and 11th values: (50 + 51)/2 = **50.5**.

**Step 2. Code each observation.**

| 48 | 52 | 47 | 53 | 46 | 54 | 45 | 55 | 44 | 56 | 49 | 51 | 50 | 52 | 48 | 53 | 47 | 54 | 46 | 55 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| B | A | B | A | B | A | B | A | B | A | B | A | B | A | B | A | B | A | B | A |

**Step 3. Count runs and group sizes.**

The sequence is `BABABABABABABABABABA` -- it changes side at every single step.

```
n1 (above median) = 10
n2 (below median) = 10
runs = 20
```

Twenty observations, twenty runs. Every run is length 1.

**Step 4. Expected runs under randomness.**

<div class="formula" markdown="1">
**mean number of runs = 2n&#8321;n&#8322;/(n&#8321;+n&#8322;) + 1**
<span class="formula-note">variance = 2n&#8321;n&#8322;(2n&#8321;n&#8322; &minus; n&#8321; &minus; n&#8322;) / [ (n&#8321;+n&#8322;)&#178;(n&#8321;+n&#8322;&minus;1) ]</span>
</div>

```
mean = 2(10)(10)/20 + 1 = 200/20 + 1 = 10 + 1 = 11

variance = 2(10)(10) x (2(10)(10) - 10 - 10) / (20^2 x 19)
         = 200 x (200 - 20) / (400 x 19)
         = 200 x 180 / 7600
         = 36000/7600
         = 4.7368

SD = sqrt(4.7368) = 2.1764
```

**Step 5. The z-test.**

```
z = (observed runs - mean) / SD
  = (20 - 11) / 2.1764
  = 9 / 2.1764
  = 4.1352

two-sided p = .00004
```

**Step 6. Interpret -- and notice the direction.**

Reject H&#8320; emphatically. But read *which way*: we observed **more** runs than expected (20 against 11), not fewer.

This is not drift. It is over-alternation: every reading that lands high is followed by one that lands low. The physical story is a feedback controller over-correcting -- it sees a heavy fill, cuts the next one too far, sees a light fill, overshoots again. The mean and SD looked fine precisely because the errors cancel pairwise. **Only the runs test could see this.**

<div class="callout callout-note" markdown="1">
<span class="callout-label">Why this example matters</span>
A quality chart of mean and standard deviation would have passed this machine. The data has the right centre and the right spread. What it does not have is independence -- and independence is an assumption of nearly every test in this course and every control chart in the factory.

The runs test is one of the few tools that tests independence directly. Run it on residuals, on time-ordered data, on anything where the order of collection is meaningful.
</div>

## A second runs example: the too-few case

Suppose instead the readings had been:

`44, 45, 46, 46, 47, 47, 48, 48, 49, 50, 51, 52, 52, 53, 53, 54, 54, 55, 55, 56`

Same values, same median 50.5, same mean, same SD. Coded: `BBBBBBBBBBAAAAAAAAAA`.

```
n1 = 10, n2 = 10, runs = 2
mean = 11, SD = 2.1764
z = (2 - 11)/2.1764 = -4.1352
p = .00004
```

Identical *p*, opposite sign. This is a pure upward drift -- the machine is slowly creeping. Again invisible to mean and SD, caught by the runs test.

Two datasets with identical descriptive statistics and opposite pathologies. That is the lesson.

## Chi-square goodness of fit: the idea

You have counts in *k* categories and a claim about what the proportions should be. Compare observed to expected.

<div class="formula" markdown="1">
**chi-square = &Sigma; (O &minus; E)&#178; / E&nbsp;&nbsp;&nbsp;&nbsp;df = k &minus; 1 &minus; (parameters estimated)**
<span class="formula-note">O = observed count, E = expected count under the claimed distribution</span>
</div>

**Why divide by E?** Because a discrepancy of 10 means something different against an expected 20 than against an expected 2,000. Dividing by *E* converts the raw gap into a relative one. This is the single most important thing to understand about the statistic.

## Working Scenario B

**Step 1. Expected counts.** If all five options are equally likely:

```
E = n/k = 150/5 = 30 for each category
```

**Step 2. The cell-by-cell table -- always show this.**

| Option | O | E | O &minus; E | (O&minus;E)&#178;/E |
|---|---|---|---|---|
| 1 | 42 | 30 | +12 | 144/30 = 4.800 |
| 2 | 35 | 30 | +5 | 25/30 = 0.833 |
| 3 | 28 | 30 | &minus;2 | 4/30 = 0.133 |
| 4 | 20 | 30 | &minus;10 | 100/30 = 3.333 |
| 5 | 25 | 30 | &minus;5 | 25/30 = 0.833 |
| **Total** | **150** | **150** | **0** | **9.933** |

Two checks: the O column and the E column must both sum to *n*, and the (O&minus;E) column must sum to 0. &#10003;

**Step 3. Degrees of freedom.** No parameters were estimated from the data -- the "all equal" hypothesis was specified in advance. So df = *k* &minus; 1 = **4**.

**Step 4. The *p*-value.**

```
chi-square = 9.933, df = 4  ->  p = .0416
```

Reject at alpha = .05. The responses are not uniformly distributed.

**Step 5. Say where the misfit is.** This is the step people skip.

The cell contributions are 4.800, 0.833, 0.133, 3.333, 0.833. Options 1 and 4 together contribute 8.13 of the 9.93 total -- **82% of the entire statistic**. Option 1 is over-chosen and option 4 under-chosen; options 2, 3 and 5 are close to expectation.

That is a finding. "Responses were not uniform" is not; it is the preamble to one. In a real survey this often points to the position of the options on the page, or wording that makes one option read as the safe choice.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The expected-count rule</span>
Chi-square's approximation needs **all expected counts at least 5** (a stricter version says all at least 1 with no more than 20% below 5). Expected, not observed -- an observed zero is fine if its expected count is 8.

When the rule fails: collapse adjacent categories if they are substantively similar, or use an exact multinomial test. Do **not** just run it anyway; the *p*-value will be wrong, usually too small.
</div>

## Degrees of freedom when you estimate parameters

This is where the goodness-of-fit df formula earns its extra term.

Testing whether counts fit a **Poisson** distribution means estimating lambda from the data. That costs one df:

```
df = k - 1 - 1 = k - 2
```

Testing fit to a **normal** distribution means estimating both the mean and the SD, costing two:

```
df = k - 1 - 2 = k - 3
```

Forgetting this inflates df, which inflates the critical value, which makes the test too conservative -- you will fail to reject distributions that genuinely do not fit.

## Kolmogorov-Smirnov: a different kind of fit test

Chi-square needs you to bin continuous data into categories, and the result depends on how you chose the bins. KS does not bin at all.

It compares the **empirical cumulative distribution function** -- the step function that rises by 1/*n* at each data point -- against the theoretical CDF, and takes the largest vertical gap.

<div class="formula" markdown="1">
**D = max &#124; F&#8345;(x) &minus; F&#8320;(x) &#124;**
<span class="formula-note">F&#8345; is the empirical CDF, F&#8320; the hypothesised one; large D means poor fit</span>
</div>

Our 15 reading scores from the first lesson:

`62, 65, 68, 70, 71, 72, 73, 75, 76, 78, 80, 82, 85, 88, 92`

mean = 75.80, SD = 8.4701.

```
D = .0962,  p = .997
```

Excellent fit to a normal distribution. Shapiro-Wilk on the same data gives *W* = .9833, *p* = .987 -- the same verdict by a different route.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The KS trap almost everyone falls into</span>
The standard KS test assumes the hypothesised distribution is **fully specified in advance** -- you must know the mean and SD, not estimate them from the same data.

Estimating them makes the test **too liberal in the direction of accepting fit**: the fitted normal is pulled toward your data, so the gap *D* comes out artificially small and the *p*-value artificially large. You end up concluding "normal" more often than you should.

The corrected version is the **Lilliefors test**, which uses the same *D* with a different null distribution. For testing normality specifically, **Shapiro-Wilk is more powerful than either** and is what you should use. Use KS for comparing against a genuinely known distribution, or in its two-sample form.
</div>

**The two-sample KS test** is the version worth remembering. It compares two empirical CDFs with no distributional assumption at all, and it is sensitive to differences in *shape*, not just location -- which makes it a useful complement to Mann-Whitney when you suspect the groups differ in spread rather than centre.

## Which test for which question

| Your question | Test |
|---|---|
| Is this sequence independent / in random order? | **Runs test** |
| Do these category counts match claimed proportions? | **Chi-square goodness of fit** |
| Does this continuous sample come from a specified distribution? | **KS one-sample** (specified) or **Lilliefors** (estimated) |
| Is this continuous sample normal? | **Shapiro-Wilk** |
| Do these two continuous samples have the same distribution? | **KS two-sample** |
| Are these two categorical variables related? | **Chi-square independence** (next lesson) |

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span>
**Goodness of fit:** Analyses -> Frequencies -> **N Outcomes (chi-square Goodness of fit)**. Put your category variable in *Variable*; under *Expected Proportions* tick the box and type the ratios (leave them equal for a uniform null). The output gives chi-square, df, *p*, and an observed-vs-expected table.
**Normality:** Analyses -> Exploration -> Descriptives, tick *Shapiro-Wilk* and *Q-Q*.
The runs test is not in base Jamovi -- use the **Rj** module to call R's `randtests::runs.test`, or compute it by hand as above.
</div>

**SPSS.**
Runs test: `Analyze -> Nonparametric Tests -> One Sample`, then *Settings -> Customize tests -> Test for change in sequence (runs)*. You can set the cut point to the median, mean, mode or a custom value -- median is the default and usually the right choice.
Goodness of fit: same menu, tick *Compare observed probabilities to hypothesized (chi-square test)* and set the expected proportions.
KS: same menu, tick *Test observed distribution against hypothesized (Kolmogorov-Smirnov)* and choose Normal, Uniform, Poisson or Exponential.

**Excel.** The goodness-of-fit test is genuinely easy here:

```
C2:  =$E$1/5                              ' expected = 150/5 = 30
D2:  =(B2-C2)^2/C2                        ' cell contribution
D7:  =SUM(D2:D6)                          ' chi-square = 9.9333
D8:  =CHISQ.DIST.RT(D7,4)                 ' p = .041566

' or in one step
D9:  =CHISQ.TEST(B2:B6,C2:C6)             ' p = .041566
```

`CHISQ.TEST` returns the *p*-value directly and infers df from the range size. For the runs test, code the observations with `=IF(A2>MEDIAN($A$2:$A$21),"A","B")`, count changes with `=SUMPRODUCT(--(C3:C21<>C2:C20))+1`, then apply the mean and SD formulas.

**R.**

```r
# runs test
randtests::runs.test(x)
#  Runs Test
#  statistic = 4.1352, runs = 20, n1 = 10, n2 = 10, n = 20, p-value = 3.55e-05

# chi-square goodness of fit
chisq.test(c(42,35,28,20,25))
#  X-squared = 9.9333, df = 4, p-value = 0.04157

ch <- chisq.test(c(42,35,28,20,25))
ch$expected     # 30 30 30 30 30
ch$residuals    # per-cell standardised residuals -> where the misfit is

# with unequal expected proportions
chisq.test(obs, p = c(.4,.3,.15,.1,.05))

# KS and Shapiro
ks.test(y, "pnorm", mean = 75.8, sd = 8.4701)   # D = .0962, p = .997
shapiro.test(y)                                  # W = .9833, p = .987
nortest::lillie.test(y)                          # the corrected KS
ks.test(sample1, sample2)                        # two-sample, no assumptions
```

<div class="callout callout-note" markdown="1">
<span class="callout-label">`ch$residuals` is the line to remember</span>
It gives (O &minus; E)/&radic;E for every cell. Squaring those gives the per-cell contributions we tabulated by hand. Any residual beyond about &plusmn;2 marks a cell that is driving the result -- which is how you turn "the fit is poor" into "the fit is poor *because* option 1 is over-chosen".
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">APA, runs test</span>
"A runs test on the 20 sequential fill weights, dichotomised at the median (50.5), found significantly more runs than expected under randomness (20 observed, 11 expected), *z* = 4.14, *p* &lt; .001. The pattern indicates negative serial dependence -- consistent with an over-correcting controller -- despite the mean and standard deviation falling within specification."
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">APA, goodness of fit</span>
"Response choices were not uniformly distributed across the five options, chi-square(4) = 9.93, *p* = .042. Inspection of the standardised residuals showed option 1 over-selected (O = 42, E = 30) and option 4 under-selected (O = 20, E = 30); these two cells accounted for 82% of the test statistic. The remaining three options were close to expectation."
</div>

Both of these name the *direction* and the *source* of the misfit. A goodness-of-fit result reported without that information is only half a finding.

## Common mistakes

1. **Reporting a significant runs test without saying which direction.** Too few runs and too many runs mean opposite physical problems.
2. **Running the runs test on data whose order is meaningless.** It tests the sequence *as recorded*. Sorted or alphabetically ordered data gives a meaningless result.
3. **Checking observed counts against the "at least 5" rule instead of expected counts.** The rule is about *E*.
4. **Forgetting to subtract df for estimated parameters** in goodness of fit.
5. **Stopping at the omnibus chi-square.** Report the residuals and name the cells.
6. **Using KS with parameters estimated from the data** and treating the *p*-value as valid. Use Lilliefors, or Shapiro-Wilk for normality.
7. **Running chi-square on percentages.** The test needs raw counts. Feeding it percentages that sum to 100 silently sets *n* = 100 and the *p*-value is then wrong.

## Practice

<details markdown="1">
<summary>1. A sequence of 12 observations gives n1 = 6, n2 = 6, and 3 runs. Test for randomness.</summary>

```
mean = 2(6)(6)/12 + 1 = 72/12 + 1 = 6 + 1 = 7

variance = 2(6)(6) x (2(6)(6) - 6 - 6) / (12^2 x 11)
         = 72 x (72 - 12) / (144 x 11)
         = 72 x 60 / 1584
         = 4320/1584
         = 2.7273

SD = 1.6514

z = (3 - 7)/1.6514 = -2.4223
p = .0154
```

Reject at alpha = .05. **Too few** runs -- the data cluster, suggesting a trend or a shift partway through.

With only 12 observations the normal approximation is marginal; the exact runs distribution would be preferable. The conclusion would not change here, but the exact *p* would differ in the third decimal.
</details>

<details markdown="1">
<summary>2. Observed 15, 20, 25, 40 against a claimed 1:2:3:4 ratio. Test the fit.</summary>

*n* = 100. The ratio 1:2:3:4 sums to 10 parts, so expected counts are 10, 20, 30, 40.

| O | E | O&minus;E | (O&minus;E)&#178;/E |
|---|---|---|---|
| 15 | 10 | +5 | 25/10 = 2.500 |
| 20 | 20 | 0 | 0.000 |
| 25 | 30 | &minus;5 | 25/30 = 0.833 |
| 40 | 40 | 0 | 0.000 |
| | | **0** | **3.333** |

```
chi-square = 3.333, df = 4 - 1 = 3  ->  p = .343
```

Do not reject. The data are consistent with the 1:2:3:4 ratio. Note the whole statistic comes from the first two categories -- category 1 is over-represented and category 3 under-represented by the same 5 cases, which at these expected counts is well within chance.
</details>

<details markdown="1">
<summary>3. You test 200 observations for fit to a Poisson distribution using 6 count categories. What is df?</summary>

```
df = k - 1 - (parameters estimated)
   = 6 - 1 - 1
   = 4
```

Six categories minus one for the fixed total, minus one more for lambda, which you estimated as the sample mean.

If you wrongly used df = 5, the critical value at alpha = .05 would be 11.07 instead of 9.49. A chi-square of 10.2 would then be declared non-significant when it is actually significant -- you would accept a Poisson fit the data reject. The error is conservative but it is still an error, and it is a common one.
</details>

<details markdown="1">
<summary>4. Why is Shapiro-Wilk preferred to KS for testing normality?</summary>

Three reasons, in order of importance.

**Power.** Shapiro-Wilk was built specifically for the normal alternative and uses the ordered values against their expected normal order statistics. KS is a general-purpose test that will detect any departure, which means its power is spread thin. Across the simulation literature Shapiro-Wilk detects non-normality at smaller sample sizes and smaller departures.

**The estimated-parameter problem.** KS assumes a fully specified null. Testing normality means estimating the mean and SD from the same data, which biases *D* downward and makes the test accept normality too readily. Shapiro-Wilk has no such problem -- it was designed with estimation built in.

**Where it looks.** KS's *D* is a maximum vertical gap, which is most sensitive near the centre of the distribution. Non-normality usually shows up in the **tails** -- skew and heavy tails are what break a t-test. Shapiro-Wilk's construction weights the tails properly.

Use KS for its real strengths: a genuinely known null distribution, or the two-sample version.
</details>

<details markdown="1">
<summary>5. Our fill-weight data had an acceptable mean and SD. What exactly did the runs test add?</summary>

It tested **independence**, which the mean and SD cannot see.

Mean and SD are functions of the multiset of values -- reorder the data any way you like and both are unchanged. The runs test is a function of the *order*, so it detects everything the summary statistics are blind to: drift, cycles, shifts, autocorrelation, over-correction.

That matters because independence is an assumption of nearly every procedure in statistics. A t-test on autocorrelated data has a standard error that is wrong -- too small under positive autocorrelation, so the *p*-values are too small and you reject too often. A control chart on over-corrected data looks perfectly in control while the process is in fact unstable.

The practical habit: whenever your data have a meaningful collection order, plot the values against that order and run a runs test on the residuals. It costs a minute and it catches a class of problem no other check in this course will find.
</details>

## Before you move on

- [ ] I can run a runs test by hand and read the direction, not just the *p*.
- [ ] I know too few runs means clustering and too many means over-alternation.
- [ ] I can build the O / E / (O&minus;E)&#178;/E table and verify both totals.
- [ ] I know why the statistic divides by *E*.
- [ ] I can get df right when parameters are estimated.
- [ ] I know the expected-count rule applies to *E*, not *O*.
- [ ] I use Shapiro-Wilk for normality, and know why KS with estimated parameters is too liberal.
- [ ] I always name the cells driving a significant goodness-of-fit result.""",
    quiz={
        "question": "Twenty sequential measurements give 20 runs when 11 are expected (z = 4.14, p < .001). What does this indicate?",
        "options": [
            "A gradual upward drift in the process",
            "Over-alternation — negative serial dependence, such as a controller over-correcting after each reading",
            "The measurements are random; 20 runs in 20 observations is the expected result",
            "The median was chosen incorrectly as the cut point",
        ],
        "answer": 1,
        "explanation": "More runs than expected means the sequence flips sides too often. Fewer than expected would mean clustering or drift. The mean and SD cannot detect either, because they ignore the order of the data.",
    },
)


# ===========================================================================
L(
    "Chi-Square Tests of Independence",
    """## What you will be able to do

Test whether two categorical variables are related, compute expected counts and adjusted residuals by hand, choose correctly between the uncorrected chi-square, Yates' correction and Fisher's exact test, and report an effect size and an odds ratio with a confidence interval.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
A college records senior-high strand against whether the student later enrolled in a STEM degree, for 180 students:

| Strand | Enrolled in STEM | Did not | Row total |
|---|---|---|---|
| STEM | 45 | 15 | 60 |
| ABM | 30 | 30 | 60 |
| HUMSS | 25 | 35 | 60 |
| **Column total** | **100** | **80** | **180** |

Is strand related to STEM enrolment?
</div>

## Independence, and what the expected counts mean

Two variables are independent when knowing one tells you nothing about the other. In probability terms, P(A and B) = P(A) x P(B).

Turn that into counts. Overall, 100 of 180 students enrolled in STEM -- a rate of 100/180 = .5556. If strand were irrelevant, **every** strand should enrol at that same .5556 rate. With 60 students per strand, that is 60 x .5556 = 33.33 expected enrolments in each row.

<div class="formula" markdown="1">
**E&#7522;&#11388; = (row i total x column j total) / grand total**
<span class="formula-note">the count you would expect in that cell if the two variables were independent</span>
</div>

This formula is not a rule to memorise -- it is P(row) x P(column) x *n* with the denominators cancelled. Writing it out once makes it stick:

```
E = n x P(row i) x P(col j)
  = n x (row_i / n) x (col_j / n)
  = (row_i x col_j) / n
```

## Working it by hand

**Step 1. Expected counts for all six cells.**

```
E(STEM, enrolled)   = (60 x 100)/180 = 6000/180 = 33.3333
E(STEM, not)        = (60 x  80)/180 = 4800/180 = 26.6667
E(ABM, enrolled)    = (60 x 100)/180 = 33.3333
E(ABM, not)         = (60 x  80)/180 = 26.6667
E(HUMSS, enrolled)  = (60 x 100)/180 = 33.3333
E(HUMSS, not)       = (60 x  80)/180 = 26.6667
```

Identical down each column, because the three row totals happen to be equal at 60. That will not be true in general.

**Check:** every expected row total and column total must match the observed ones. Row 1: 33.3333 + 26.6667 = 60. &#10003; Column 1: 33.3333 x 3 = 100. &#10003;

**Step 2. The cell-by-cell table.**

| Cell | O | E | O&minus;E | (O&minus;E)&#178;/E |
|---|---|---|---|---|
| STEM, enrolled | 45 | 33.3333 | +11.6667 | 136.111/33.3333 = 4.0833 |
| STEM, not | 15 | 26.6667 | &minus;11.6667 | 136.111/26.6667 = 5.1042 |
| ABM, enrolled | 30 | 33.3333 | &minus;3.3333 | 11.111/33.3333 = 0.3333 |
| ABM, not | 30 | 26.6667 | +3.3333 | 11.111/26.6667 = 0.4167 |
| HUMSS, enrolled | 25 | 33.3333 | &minus;8.3333 | 69.444/33.3333 = 2.0833 |
| HUMSS, not | 35 | 26.6667 | +8.3333 | 69.444/26.6667 = 2.6042 |
| | **180** | **180** | **0** | **14.625** |

**Step 3. Degrees of freedom.**

<div class="formula" markdown="1">
**df = (rows &minus; 1) x (columns &minus; 1)**
<span class="formula-note">here (3&minus;1)(2&minus;1) = 2</span>
</div>

Why that product? Because the margins are fixed. Once you know two of the three enrolment counts, the third is forced by the column total of 100. Only 2 of the 6 cells are free to vary.

**Step 4. The *p*-value.**

```
chi-square = 14.625, df = 2  ->  p = .000667
```

Reject H&#8320;. Strand and STEM enrolment are related.

## Effect size: Cramer's V

Chi-square grows with *n*. Double every cell and chi-square doubles while the pattern is unchanged. So it cannot be an effect size.

<div class="formula" markdown="1">
**Cramer's V = &radic;[ chi-square / (n x min(r&minus;1, c&minus;1)) ]**
<span class="formula-note">0 to 1; for a 2x2 table it equals phi, the absolute correlation between the two binary variables</span>
</div>

```
min(r-1, c-1) = min(2, 1) = 1

V = sqrt( 14.625 / (180 x 1) )
  = sqrt( 0.08125 )
  = .285
```

Benchmarks for df = 1: .10 small, .30 medium, .50 large. So .285 is a medium association -- real and worth acting on, not overwhelming.

## Adjusted residuals: where the association actually lives

A significant chi-square on a 3 x 2 table says "strand matters" but not which strand. The answer is in the residuals.

The raw standardised residual is (O &minus; E)/&radic;*E*. It is useful but its variance is not quite 1, so comparing residuals across cells with different margins is unfair. The **adjusted** residual fixes that:

<div class="formula" markdown="1">
**adjusted residual = (O &minus; E) / &radic;[ E x (1 &minus; row total/n) x (1 &minus; column total/n) ]**
<span class="formula-note">approximately standard normal, so values beyond &plusmn;1.96 are notable and beyond &plusmn;2.58 strong</span>
</div>

Worked for the STEM-enrolled cell:

```
O - E = 45 - 33.3333 = 11.6667
row proportion    = 60/180  = .3333   ->  1 - .3333 = .6667
column proportion = 100/180 = .5556   ->  1 - .5556 = .4444

denominator = sqrt( 33.3333 x .6667 x .4444 )
            = sqrt( 9.8765 )
            = 3.1427

adjusted residual = 11.6667 / 3.1427 = 3.7123
```

All six, computed the same way:

| Strand | Enrolled | Did not |
|---|---|---|
| STEM | **+3.71** | **&minus;3.71** |
| ABM | &minus;1.06 | +1.06 |
| HUMSS | **&minus;2.65** | **+2.65** |

**Now you have a finding.** STEM-strand students enrol in STEM degrees far more than independence predicts (+3.71). HUMSS students far less (&minus;2.65). ABM students are indistinguishable from the overall rate (&minus;1.06, well inside &plusmn;1.96).

In a 2-column table the residuals are mirror images by construction -- the two columns in each row must sum to the row total, so a positive in one forces a negative in the other. Report one column and say so.

## The 2 x 2 case: three tests and a real disagreement

Smaller table, 50 cases:

| | Outcome yes | Outcome no | Total |
|---|---|---|---|
| Treated | 18 | 7 | 25 |
| Control | 9 | 16 | 25 |
| **Total** | **27** | **23** | **50** |

Expected counts: E(treated, yes) = 25 x 27/50 = 13.5, E(treated, no) = 25 x 23/50 = 11.5, and the same for the control row.

All expected counts are above 5, so chi-square is applicable. Three tests:

| Test | Statistic | p |
|---|---|---|
| Pearson chi-square, uncorrected | 6.5217 | **.0107** |
| Yates' continuity-corrected | 5.1530 | **.0232** |
| Fisher's exact | -- | **.0222** |

All three reject, but the *p* more than doubles from the first to the second.

**Yates' correction** subtracts 0.5 from each &#124;O &minus; E&#124; before squaring:

```
corrected chi-square = sum over cells of (|O - E| - 0.5)^2 / E
                     = (4.5 - 0.5)^2/13.5 + (4.5-0.5)^2/11.5
                       + (4.5-0.5)^2/13.5 + (4.5-0.5)^2/11.5
                     = 16/13.5 + 16/11.5 + 16/13.5 + 16/11.5
                     = 1.1852 + 1.3913 + 1.1852 + 1.3913
                     = 5.1530
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The current advice on Yates</span>
Yates' correction exists because chi-square is a continuous approximation to a discrete distribution. But the modern consensus is that it **over-corrects** -- it is too conservative, and it was designed for a world without computers.

Practical guidance:

- **Expected counts all &ge; 5:** use the **uncorrected** chi-square. Report *p* = .011.
- **Any expected count &lt; 5:** use **Fisher's exact test**, which needs no approximation at all.
- **Never a reason to prefer Yates** when Fisher is one click away.

SPSS prints Yates as "Continuity Correction" on every 2x2 table and many students report it by default. Notice here that Fisher's exact *p* = .0222 is close to Yates' .0232 -- Yates is approximating Fisher, and you can simply use Fisher instead.
</div>

## The odds ratio: the number a reader can act on

Chi-square tells you *whether*. The odds ratio tells you *how much*, and it is the standard effect measure in health and social research.

<div class="formula" markdown="1">
**OR = (a x d) / (b x c)**
<span class="formula-note">for a 2x2 table [[a, b], [c, d]]; OR = 1 means no association</span>
</div>

```
OR = (18 x 16) / (7 x 9) = 288/63 = 4.5714
```

**"The odds of a positive outcome are about 4.6 times higher in the treated group."**

Odds, not probability -- a distinction worth getting right. Treated: 18 yes to 7 no, odds 18/7 = 2.571. Control: 9 yes to 16 no, odds 9/16 = 0.5625. The ratio 2.571/0.5625 = 4.5714. &#10003;

**Confidence interval.** The OR is skewed, so the interval is built on the log scale and transformed back:

<div class="formula" markdown="1">
**SE(ln OR) = &radic;(1/a + 1/b + 1/c + 1/d)**
<span class="formula-note">then 95% CI = exp( ln OR &plusmn; 1.96 x SE )</span>
</div>

```
SE = sqrt(1/18 + 1/7 + 1/9 + 1/16)
   = sqrt(0.05556 + 0.14286 + 0.11111 + 0.0625)
   = sqrt(0.37202)
   = 0.6099

ln(4.5714) = 1.5198

lower = exp(1.5198 - 1.96 x 0.6099) = exp(0.3244) = 1.383
upper = exp(1.5198 + 1.96 x 0.6099) = exp(2.7152) = 15.109

95% CI for OR: [1.383, 15.109]
```

**Read that interval carefully.** It excludes 1, so the association is significant -- consistent with every *p*-value above. But it stretches from 1.4 to 15.1. The data are compatible with anything from a trivial effect to an enormous one. With 50 cases, that is the honest precision, and the interval says so where the *p*-value of .011 does not.

This is the strongest argument for reporting intervals: *p* = .011 sounds settled; [1.38, 15.11] does not. The second is the truth.

**And phi, for completeness:**

```
phi = sqrt(chi-square / n) = sqrt(6.5217/50) = sqrt(0.13043) = .3612
```

A medium association, agreeing with the OR's message that something real is happening.

## Assumptions -- the one that gets violated most

| Assumption | What it means | What breaks it |
|---|---|---|
| **Independent observations** | Each person appears in exactly one cell | Counting the same person twice; repeated measures |
| **Expected counts &ge; 5** | The approximation needs reasonable cell sizes | Sparse tables, rare categories |
| **Raw counts, not percentages** | The statistic is built on frequencies | Feeding in percentages |
| **Mutually exclusive categories** | Every case in exactly one cell | "Select all that apply" questions |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The "select all that apply" trap</span>
A question like "which subjects do you find difficult? (tick all)" produces more ticks than respondents. Cross-tabulating that against anything and running chi-square is **invalid** -- the observations are not independent, because one person contributes to several cells.

The fix: treat each option as its own binary variable and run a separate 2x2 test per option (correcting for multiplicity), or use a method built for multiple-response data. This error is extremely common in student surveys and a panel that spots it will ask you to redo the analysis.

The repeated-measures version has a proper test: **McNemar's test** for paired binary data (the same people before and after), which uses only the discordant pairs.
</div>

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span>
**Analyses -> Frequencies -> Independent Samples (chi-square test of association).**
Rows: strand. Columns: enrolled.
Under *Statistics* tick **chi-square**, **Fisher's exact test**, **Phi and Cramer's V**, and **Odds ratio** (2x2 only).
Under *Cells* tick **Expected counts** and **Row percentages**.
Jamovi does not print adjusted residuals -- for those use SPSS or R, or compute them by hand as above.
</div>

**SPSS.**
`Analyze -> Descriptive Statistics -> Crosstabs`. Rows and Columns as you expect. Then:

- *Statistics* -> tick **Chi-square**, **Phi and Cramer's V**, and **Risk** (which gives the odds ratio with its CI).
- *Cells* -> tick **Expected**, **Row percentages**, and **Adjusted standardized** residuals.

That last checkbox is the one worth remembering; it prints the +3.71 / &minus;2.65 table directly. SPSS also footnotes "0 cells (0.0%) have expected count less than 5", which is your assumption check done for you.

**Excel.** Build the expected table with a single formula you can fill across:

```
' observed in B2:C4, row totals in D, column totals in row 5
F2:  =$D2*B$5/$D$5                         ' expected, fills across and down
J2:  =(B2-F2)^2/F2                          ' cell contribution
J6:  =SUM(J2:K4)                            ' chi-square = 14.625
J7:  =CHISQ.DIST.RT(J6,2)                   ' p = .000667

' or in one step
J8:  =CHISQ.TEST(B2:C4,F2:G4)               ' p = .000667
```

The `$D2*B$5/$D$5` mixed reference is the whole trick -- row total times column total over grand total, written once. Excel has no Fisher's exact test and no adjusted residuals.

**R.**

```r
T <- matrix(c(45,15, 30,30, 25,35), nrow = 3, byrow = TRUE,
            dimnames = list(c("STEM","ABM","HUMSS"), c("Enrolled","Not")))

ch <- chisq.test(T, correct = FALSE)
ch                 # X-squared = 14.625, df = 2, p-value = 0.0006669
ch$expected        # 33.33 26.67 (x3)
ch$stdres          # ADJUSTED residuals: +3.71, -1.06, -2.65

# effect size
rcompanion::cramerV(T)          # 0.285

# the 2x2 case
T2 <- matrix(c(18,7,9,16), nrow = 2, byrow = TRUE)
chisq.test(T2, correct = FALSE)   # 6.5217, p = .0107
chisq.test(T2, correct = TRUE)    # 5.1530, p = .0232   (Yates)
fisher.test(T2)                   # p = .0222, OR = 4.571, CI [1.42, 16.19]

# paired binary data instead
mcnemar.test(paired_table)
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Two traps in R specifically</span>
`chisq.test` applies **Yates' correction by default on 2x2 tables**. You must write `correct = FALSE` to get the uncorrected statistic. Many published analyses report Yates without realising they asked for it.

And note that `ch$stdres` gives the **adjusted** residuals (the +3.71 we computed) while `ch$residuals` gives the plain (O&minus;E)/&radic;E (which is +2.02 for that cell). The names are counter-intuitive. Use `$stdres`.

Fisher's conditional MLE odds ratio in R is 4.571 with CI [1.42, 16.19], slightly different from the Woolf interval [1.38, 15.11] we computed by hand -- different estimators, same conclusion.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">APA, chi-square of independence with residuals</span>
"Senior-high strand was significantly associated with subsequent STEM enrolment, chi-square(2, *N* = 180) = 14.63, *p* &lt; .001, Cramer's *V* = .29. Adjusted residuals showed STEM-strand students enrolled in STEM degrees more often than expected under independence (*z* = 3.71) and HUMSS students less often (*z* = &minus;2.65), while ABM students did not differ from the overall rate (*z* = &minus;1.06). Enrolment rates were 75.0% (STEM), 50.0% (ABM) and 41.7% (HUMSS)."
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">APA, 2x2 with an odds ratio</span>
"A positive outcome was observed in 72.0% of treated cases and 36.0% of controls, chi-square(1, *N* = 50) = 6.52, *p* = .011, phi = .36. The odds ratio was 4.57, 95% CI [1.38, 15.11]; Fisher's exact test gave *p* = .022. The width of the interval indicates that although the association is reliable, its magnitude is estimated imprecisely at this sample size."
</div>

Both write-ups give percentages alongside the test. A reader understands "75% versus 42%" immediately; chi-square(2) = 14.63 means nothing without it.

## Common mistakes

1. **Running chi-square on percentages.** It needs counts. Percentages silently set *n* = 100.
2. **Reporting Yates by default.** With all *E* &ge; 5 use the uncorrected test; with any *E* &lt; 5 use Fisher.
3. **Stopping at the omnibus *p*.** Report adjusted residuals and name the cells.
4. **Using `$residuals` instead of `$stdres` in R.** Different numbers, and only one is on a standard-normal scale.
5. **Chi-square on "select all that apply" data.** Not independent; the test is invalid.
6. **Chi-square on paired binary data.** Use McNemar's test.
7. **Confusing odds with probability.** An OR of 4.57 does not mean the treated group is 4.57 times as likely. Report risks or percentages too.
8. **Treating a significant chi-square as evidence of causation.** Strand is self-selected; students who choose STEM strand already intend STEM degrees.

## Practice

<details markdown="1">
<summary>1. A 2x2 table has row totals 40 and 60, column totals 30 and 70, n = 100. Compute all four expected counts.</summary>

```
E(1,1) = 40 x 30/100 = 12
E(1,2) = 40 x 70/100 = 28
E(2,1) = 60 x 30/100 = 18
E(2,2) = 60 x 70/100 = 42
```

Checks: 12 + 28 = 40 &#10003;, 18 + 42 = 60 &#10003;, 12 + 18 = 30 &#10003;, 28 + 42 = 70 &#10003;, total = 100 &#10003;.

All four expected counts exceed 5, so the uncorrected chi-square is applicable. Note how the expected table depends only on the margins -- you can compute it before seeing a single observed cell, which is exactly why the margins carry no information about association.
</details>

<details markdown="1">
<summary>2. A 2x2 table is [[3, 12], [11, 4]]. Which test, and why?</summary>

Margins: rows 15 and 15, columns 14 and 16, *n* = 30.

```
E(1,1) = 15 x 14/30 = 7.0
E(1,2) = 15 x 16/30 = 8.0
E(2,1) = 15 x 14/30 = 7.0
E(2,2) = 15 x 16/30 = 8.0
```

All expected counts are 7 or 8 -- above 5. So the uncorrected chi-square is defensible.

**But** *n* = 30 is small and the cells 3 and 4 are themselves tiny. With a table this sparse, **Fisher's exact test is the safer report**, and it costs nothing: it conditions on the observed margins and enumerates every table with those margins, giving an exact *p* with no approximation whatsoever.

The habit worth forming: whenever *n* is under about 40 on a 2x2, report Fisher. It is never wrong, and it removes an avenue of criticism.
</details>

<details markdown="1">
<summary>3. An adjusted residual is +2.9. What does that mean, and what does it not mean?</summary>

**It means** that cell's observed count is 2.9 standard errors above what independence predicts. Since adjusted residuals are approximately standard normal, 2.9 corresponds to roughly *p* = .004 for that cell on its own -- a strong local departure, and a cell you should name in your write-up.

**It does not mean** the cell is "significant" in a way you can report as a standalone hypothesis test. You are looking at every cell in the table, so the multiplicity problem applies. If you want formal per-cell inference, apply a Bonferroni-style threshold: for a 3x2 table with 6 cells, use a critical value of about 2.64 (that is *z* for .05/6 two-tailed) rather than 1.96.

Under that stricter threshold, our STEM cell (3.71) still stands and the HUMSS cell (2.65) is right at the line. The usual practice is to use residuals **descriptively** -- to say where the association lives -- rather than as a set of formal tests, and to be explicit that is what you are doing.
</details>

<details markdown="1">
<summary>4. Convert OR = 4.57 into a risk ratio, given that 36% of controls had the outcome.</summary>

```
control odds = .36/(1-.36) = .36/.64 = .5625
treated odds = .5625 x 4.57 = 2.5706
treated risk = 2.5706/(1 + 2.5706) = 2.5706/3.5706 = .7199  (72.0%)

risk ratio = .720/.360 = 2.00
```

So the OR of 4.57 corresponds to a risk ratio of only **2.00**. The odds ratio is more than twice the risk ratio.

This is the general pattern: **the OR exaggerates the risk ratio whenever the outcome is common**, and the gap widens as the baseline risk approaches 50%. With a rare outcome -- say a 2% baseline -- OR and RR are nearly identical, which is why odds ratios are reported so freely in epidemiology.

With a 36% baseline they are not interchangeable. Saying "4.6 times more likely" when the OR is 4.57 is simply wrong; the correct statement is "4.6 times the *odds*", or "twice as likely". This misreading appears in published papers regularly. Report the percentages and the reader cannot be misled.
</details>

<details markdown="1">
<summary>5. Why is df = (r-1)(c-1) rather than rc - 1?</summary>

Because the margins are fixed by the data before the test begins, and each fixed margin removes freedom.

Take the 3x2 table. There are 6 cells. The grand total 180 is fixed, which costs 1 df. The three row totals are fixed at 60 each, but one of those is implied by the other two plus the grand total -- so they cost 2 more. The two column totals are fixed at 100 and 80, and one is implied by the other plus the total -- so 1 more.

```
6 cells - 1 (grand total) - 2 (rows) - 1 (columns) = 2 = (3-1)(2-1)
```

Concretely: tell me the two STEM-row cells and the ABM-enrolled cell, and I can derive the remaining three by subtraction. Only 2 of the 6 are genuinely free once you know the margins -- 45 and 30 in the enrolled column force 25, and the whole "not enrolled" column follows from the row totals.

Chi-square conditions on the margins because the margins are not what you are testing. You are testing how the counts are *distributed within* those fixed margins.
</details>

## Before you move on

- [ ] I can compute expected counts from the margins and explain why that formula is P(row) x P(col) x *n*.
- [ ] I can build the full O / E / (O&minus;E)&#178;/E table and verify the totals.
- [ ] I can compute adjusted residuals by hand and use them to name the cells.
- [ ] I know when to use the uncorrected chi-square, and that Fisher beats Yates.
- [ ] I can compute an odds ratio and its 95% CI through the log scale.
- [ ] I know the OR exaggerates the risk ratio when the outcome is common.
- [ ] I know "select all that apply" data breaks independence, and that paired binary data needs McNemar.
- [ ] I know R's `chisq.test` applies Yates by default on 2x2 tables.""",
    quiz={
        "question": "A 2x2 table has all expected counts above 5 and n = 50. SPSS prints Pearson chi-square p = .011, Continuity Correction p = .023, and Fisher's exact p = .022. Which should you report?",
        "options": [
            "The Continuity Correction, because it is the conservative choice",
            "The uncorrected Pearson chi-square, p = .011, since all expected counts exceed 5",
            "Whichever is closest to .05",
            "All three, without choosing",
        ],
        "answer": 1,
        "explanation": "Yates' correction over-corrects and was designed for pre-computer calculation. With all expected counts at or above 5, the uncorrected statistic is appropriate. Reserve Fisher's exact test for tables with an expected count below 5, where it needs no approximation at all.",
    },
)


# ===========================================================================
L(
    "Further Reading (Free & Open)",
    """## What you now know how to do

You came in with a decision table and you leave with seven tests you can run by hand and verify against software.

| Test | What it replaces | Statistic | Effect size |
|---|---|---|---|
| Sign test | One-sample t | exact binomial | proportion above |
| Wilcoxon signed-rank | Paired t | *W* | rank-biserial, Hodges-Lehmann |
| Mann-Whitney *U* | Independent t | *U* | rank-biserial, common-language |
| Kruskal-Wallis *H* | One-way ANOVA | *H* | epsilon&#178;, eta&#178;&#8341; |
| Friedman | Repeated-measures ANOVA | *Q* | Kendall's *W* |
| Spearman / Kendall | Pearson *r* | rho, tau | the coefficient itself |
| Chi-square / Fisher | -- | chi-square | Cramer's *V*, odds ratio |

Plus two tools that have no parametric counterpart and that most courses leave out: the **runs test** for independence, and **adjusted residuals** for locating an association inside a contingency table.

## The five habits that matter most

1. **Check the rank sums before you trust anything.** &Sigma;*R* = *N*(*N*+1)/2 for pooled ranks; *W*&#8314; + *W*&#8315; = *n*(*n*+1)/2 for signed ranks; *U*&#8321; + *U*&#8322; = *n*&#8321;*n*&#8322;. Three free error detectors.
2. **Never report a *p* without an effect size.** Every test above has one and the table names it.
3. **Say what the test is testing.** Mann-Whitney is a dominance test unless you add the equal-shape assumption. Be explicit which version you are claiming.
4. **Name the cells, name the pairs.** A significant omnibus result is the beginning of the analysis, not the end. Residuals for contingency tables, Dunn or Nemenyi for *k*-sample tests.
5. **Use exact *p*-values at small *n*.** Every modern package offers them. The normal approximations in this course are for understanding the machinery, not for publishing.

## Free textbooks

- **Conover, *Practical Nonparametric Statistics*** -- the standard reference. Not free, but in every university library, and the table of exact critical values in the back is the one worth photocopying.
- **OpenIntro Statistics** (openintro.org) -- free PDF, CC-licensed. Chapters on inference for categorical data are the clearest free treatment of chi-square you will find.
- **Learning Statistics with Jamovi**, Navarro & Foxcroft (learnstatswithjamovi.com) -- free, written around the software this course recommends, with a good nonparametric chapter.
- **Introduction to Modern Statistics** (openintro.org/book/ims) -- free, and strong on randomisation and permutation tests, which are where nonparametric inference is heading.
- **Handbook of Biological Statistics**, McDonald (biostathandbook.com) -- free online. Short, blunt chapters per test with a clear "when to use it" section. Written for biologists but applicable everywhere.

## Software, all free

- **Jamovi** (jamovi.org) -- install this first. Every test in this course, with effect sizes, in a point-and-click interface. Its **Rj** module lets you run R code inside it when you need something it lacks.
- **R** (r-project.org) with `rstatix` for tidy effect sizes, `coin` for exact permutation versions of every test here, `dunn.test` and `PMCMRplus` for post-hoc comparisons, `randtests` for the runs test, and `nortest` for Lilliefors.
- **PSPP** (gnu.org/software/pspp) -- free and close enough to SPSS's interface that SPSS instructions mostly transfer.
- **Python** with `scipy.stats`, which has every test in this course: `wilcoxon`, `mannwhitneyu`, `kruskal`, `friedmanchisquare`, `spearmanr`, `kendalltau`, `chi2_contingency`, `fisher_exact`, `chisquare`, `kstest`, `shapiro`. Every number in these lessons was computed with it.

## Where to go next in this catalogue

| If you want to... | Take |
|---|---|
| Choose and run the right test from scratch | **Applied Statistics for Research** |
| Firm up medians, quartiles and distributions | **Basic Statistics: A Practical Start** |
| Model relationships rather than test them | **Intermediate Statistics: Building Real Models** |
| Design the study that generates the data | **Foundations of Research Methodology** |
| Run a genuine randomised experiment | **Design & Analysis of Experiments** |
| Understand where the test distributions come from | **Probability & Mathematical Statistics** |
| Do SEM, PLS-SEM or survival analysis | **Advanced Statistics** |

## One closing idea worth carrying forward

Every test in this course is a special case of a single idea: **replace the data with something that does not depend on the distribution, then ask how unusual the result is under the null.**

Ranks are one such replacement. **Permutation** is the other, and it is more general. Instead of ranking, shuffle the group labels thousands of times, recompute your statistic each time, and see where the real value falls in that distribution. No table, no approximation, no assumption about shape -- and it works for statistics that have no named test at all, including differences in trimmed means, in medians, or in any quantity you can define.

```r
coin::wilcox_test(score ~ group, distribution = "exact")   # exact permutation
coin::oneway_test(score ~ group, distribution = approximate(nresample = 99999))
```

The exact *p*-values your software reported throughout this course are permutation *p*-values. You have been using the idea all along. Knowing that it generalises means you are never stuck when your statistic has no entry in a textbook table.""",
)


# ===========================================================================
def main():
    Base.metadata.create_all(bind=engine)
    sync_columns()
    db = SessionLocal()
    try:
        course = db.query(models.Course).filter(models.Course.slug == COURSE_SLUG).first()
        if course is None:
            print(f"[error] no course with slug {COURSE_SLUG!r}")
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
            if spec["quiz"]:
                lesson.quiz_json = json.dumps(spec["quiz"])
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
