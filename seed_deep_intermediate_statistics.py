"""
Rewrites Intermediate Statistics: Building Real Models at teaching depth.

The regression course. Twelve lessons covering the linear model, everything
that can go wrong with it, and what to do about each.

Verified numbers used throughout:

  Simple regression (same 8 pairs as Basic Statistics, so R-squared = r-squared)
    x 1,2,2,3,4,5,6,7   y 12,15,18,15,22,25,20,33
    Sxy=87, Sxx=31.5, Syy=316
    b1 = 87/31.5 = 2.7619,  b0 = 20 - 2.7619(3.75) = 9.6429
    SSR=240.286, SSE=75.714, SST=316, R2=.7604, adj R2=.7205
    MSE=12.619, SE of estimate=3.552, SE(b1)=0.6329
    t(6)=4.364, p=.0047, F(1,6)=19.042 = t squared

  Multiple regression, n=120: score ~ hours + prior
    b(hours)=1.894 SE=.157 t=12.04; b(prior)=.531 SE=.062 t=8.53
    R2=.6792, adj R2=.6737, F(2,117)=123.86, SE of estimate 4.874
    VIF both 1.02, Durbin-Watson 2.22

  Severe multicollinearity, n=100 (two measures of the same construct)
    r = .9859
    alone: b=2.369 SE=.153 t=15.47 p<.001
    both : b=0.891 SE=.906 t=0.98 p=.328 and b=10.26 SE=6.20 p=.101
    R2 .7096 -> .7175 (barely moves), VIF 35.6, SE inflated 5.9x

  Heteroskedasticity, n=120
    Breusch-Pagan LM=16.72, p<.001; b1=2.175
    OLS SE=.108  ->  HC3 robust SE=.135

  Logistic regression, n=120: pass ~ hours
    b0=-4.398, b1=0.6147, SE=.126, z=4.89, p<.001
    odds ratio = 1.849, McFadden pseudo R2 = .299
    p(pass) at 8/10/12 hours = .627 / .852 / .952

  One-way ANOVA (from Applied Statistics, 3 strands n=8)
    SSB=489, SSW=325.5, SST=814.5, MSB=244.5, MSW=15.5
    F(2,21)=15.774, p<.001, eta-squared=.600

Safe to re-run. Lessons matched by title and replaced in place.

Usage:
    python3 seed_deep_intermediate_statistics.py
"""
import json
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal, sync_columns
from app import models

COURSE_SLUG = "intermediate-statistics"
LESSONS = []


def L(title, content, quiz=None, preview=False):
    LESSONS.append({"title": title, "content": content, "quiz": quiz, "preview": preview})


# ===========================================================================
L(
    "Simple and Multiple Linear Regression",
    """## What you will be able to do

Compute a regression line by hand from a table of deviations, interpret every number in a regression output including the ones students skip, and extend the same logic to several predictors at once.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
Correlation told us review hours and quiz scores move together, *r* = .87. A panel member asks the obvious next question:

*"If a student reviews for 4 hours, what score do you predict?"*

Correlation cannot answer that. Regression can -- and it turns out to use the exact same sums.
</div>

## From correlation to prediction

We use the same eight students from Basic Statistics, so every intermediate number should look familiar.

| Student | Review hours (x) | Quiz score (y) |
|---|---:|---:|
| A | 1 | 12 |
| B | 2 | 15 |
| C | 2 | 18 |
| D | 3 | 15 |
| E | 4 | 22 |
| F | 5 | 25 |
| G | 6 | 20 |
| H | 7 | 33 |

<div class="formula" markdown="1">
**y&#770; = b&#8320; + b&#8321;x**
<span class="formula-note">y&#770; ("y-hat") is the predicted value, b&#8320; the intercept, b&#8321; the slope</span>
</div>

## Computing it by hand

### Step 1 -- the three sums

These are exactly the sums you built for the correlation:

```
mean x = 30/8  = 3.75
mean y = 160/8 = 20.00

Sxy = sum of (x - 3.75)(y - 20)   =  87.0
Sxx = sum of (x - 3.75)^2         =  31.5
Syy = sum of (y - 20)^2           = 316.0
```

### Step 2 -- the slope

<div class="formula" markdown="1">
**b&#8321; = S<sub>xy</sub> / S<sub>xx</sub>**
</div>

```
b1 = 87.0 / 31.5 = 2.7619
```

**Interpretation:** each additional hour of review is associated with an increase of about **2.76 points** on the quiz.

### Step 3 -- the intercept

The line always passes through the point (mean x, mean y), which gives the intercept immediately.

<div class="formula" markdown="1">
**b&#8320; = y&#772; &minus; b&#8321;x&#772;**
</div>

```
b0 = 20.00 - 2.7619 x 3.75
   = 20.00 - 10.3571
   = 9.6429
```

### Step 4 -- write the equation

```
predicted score = 9.64 + 2.76 x (review hours)
```

**Answering the panel's question**, at 4 hours:

```
y-hat = 9.64 + 2.76 x 4 = 9.64 + 11.05 = 20.69
```

About **21 points**.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">What the intercept does and does not mean</span>
b&#8320; = 9.64 is the predicted score at **zero** review hours.

Here that is *just about* interpretable -- a student who did not review at all. But in many models zero is impossible: predicted income at age zero, predicted blood pressure at weight zero. The intercept is then a mathematical anchor with no substantive meaning, and you should say so rather than interpret it.

**Centring** the predictor (subtracting its mean) makes the intercept the predicted value at the *average* x, which is always interpretable.
</div>

## How well does the line fit?

### Partitioning the variation

Every observation's distance from the mean splits into a part the line explains and a part it does not.

<div class="formula" markdown="1">
**SST = SSR + SSE**
<span class="formula-note">total = explained by regression + left in the residuals</span>
</div>

```
SST = Syy                    = 316.000
SSR = sum of (y-hat - ybar)^2 = 240.286
SSE = sum of (y - y-hat)^2    =  75.714

check: 240.286 + 75.714 = 316.000   correct
```

### R-squared

<div class="formula" markdown="1">
**R&sup2; = SSR / SST**
</div>

```
R2 = 240.286 / 316.000 = 0.7604
```

**76% of the variation in quiz scores is accounted for by review hours.**

<div class="callout callout-key" markdown="1">
<span class="callout-label">A connection worth noticing</span>
In Basic Statistics we found *r* = .8720 for these same data.

```
r^2 = 0.8720^2 = 0.7604 = R^2
```

**In simple regression with one predictor, R-squared is literally the square of the correlation.** They are the same quantity. This stops being true once you add a second predictor.
</div>

### Adjusted R-squared

R-squared can only go up when you add predictors, even useless ones. Adjusted R-squared penalises for the number of predictors.

<div class="formula" markdown="1">
**adj R&sup2; = 1 &minus; (1 &minus; R&sup2;) &times; (n &minus; 1)/(n &minus; k &minus; 1)**
<span class="formula-note">k = number of predictors</span>
</div>

```
adj R2 = 1 - (1 - 0.7604) x (8 - 1)/(8 - 1 - 1)
       = 1 - 0.2396 x 7/6
       = 1 - 0.2795
       = 0.7205
```

**Report adjusted R-squared whenever you have more than one predictor.** A large gap between R-squared and adjusted R-squared warns that predictors are being added without earning their place.

## Is the slope significantly different from zero?

### The standard error of the slope

```
MSE = SSE / (n - 2) = 75.714 / 6 = 12.619
SE of estimate = sqrt(12.619) = 3.552

SE(b1) = SE of estimate / sqrt(Sxx)
       = 3.552 / sqrt(31.5)
       = 3.552 / 5.612
       = 0.6329
```

### The t-test on the slope

```
t = b1 / SE(b1)
  = 2.7619 / 0.6329
  = 4.364        df = n - 2 = 6
  p = .0047
```

Significant. And note this is **exactly the t we computed for the correlation** in Basic Statistics -- testing whether the slope is zero and testing whether the correlation is zero are the same test.

### The overall F test

```
F = (SSR / k) / MSE
  = (240.286 / 1) / 12.619
  = 19.042        df = 1 and 6
  p = .0047
```

```
t^2 = 4.364^2 = 19.04 = F
```

<div class="callout callout-key" markdown="1">
<span class="callout-label">In simple regression, F = t&sup2;</span>
With one predictor the overall F test and the t-test on the slope are the same test. They must give identical p-values.

With **two or more** predictors they differ: F tests whether the model as a whole explains anything, and each t tests one predictor holding the others constant.
</div>

## Multiple regression

Adding predictors changes the interpretation of every coefficient.

<div class="formula" markdown="1">
**y&#770; = b&#8320; + b&#8321;x&#8321; + b&#8322;x&#8322; + ... + b<sub>k</sub>x<sub>k</sub>**
</div>

<div class="callout callout-case" markdown="1">
<span class="callout-label">A larger study</span>
n = 120 students. Predicting posttest **score** from **review hours** and **prior grade**.

```
                 b        SE      t       p
(Intercept)   25.495    4.455    5.72   <.001
hours          1.894    0.157   12.04   <.001
prior          0.531    0.062    8.53   <.001

R-squared = .679    adjusted R-squared = .674
F(2, 117) = 123.86,  p < .001
SE of estimate = 4.87
```
</div>

### Interpreting a multiple regression coefficient

<div class="callout callout-key" markdown="1">
<span class="callout-label">The phrase that must appear</span>
**b(hours) = 1.894** means: for each additional hour of review, the predicted score increases by 1.894 points, **holding prior grade constant**.

That last clause is not optional. Without it the coefficient is misdescribed. It is the whole reason multiple regression exists -- it isolates each predictor's contribution from the others.
</div>

Notice the slope for hours here (1.894) differs from the simple-regression slope in a single-predictor model. That is expected: they answer different questions. One is the total association; the other is the association after removing what prior grade accounts for.

### Standardised coefficients

Raw coefficients cannot be compared across predictors measured on different scales -- one hour is not comparable to one grade point. **Standardised betas** put every predictor on an SD scale so they can be ranked.

Report standardised betas when the question is *"which predictor matters most?"* and unstandardised ones when the question is *"how much does y change per unit of x?"* -- which is what you need for prediction.

## Doing it in software

### Jamovi
1. **Analyses** &rarr; **Regression** &rarr; **Linear Regression**
2. `score` into **Dependent Variable**; `hours` and `prior` into **Covariates**
3. **Model Fit**: tick **R**, **R&sup2;**, **Adjusted R&sup2;**, **Overall model test (F)**
4. **Model Coefficients**: tick **Standardized estimate** and **Confidence interval**
5. **Assumption Checks**: tick everything -- you will need it in lesson 3

### SPSS
<kbd>Analyze</kbd> &rarr; <kbd>Regression</kbd> &rarr; <kbd>Linear</kbd>. Dependent and Independent(s). Click **Statistics** and tick **Estimates**, **Confidence intervals**, **Model fit**, **Descriptives**, **Collinearity diagnostics**.

### Excel
<kbd>Data</kbd> &rarr; <kbd>Data Analysis</kbd> &rarr; **Regression** (enable the Analysis ToolPak first). Or directly:
```
=SLOPE(B2:B9, A2:A9)       -> 2.7619
=INTERCEPT(B2:B9, A2:A9)   -> 9.6429
=RSQ(B2:B9, A2:A9)         -> 0.7604
=STEYX(B2:B9, A2:A9)       -> 3.5523    SE of estimate
```

### R
```r
hours <- c(1, 2, 2, 3, 4, 5, 6, 7)
score <- c(12, 15, 18, 15, 22, 25, 20, 33)

m <- lm(score ~ hours)
summary(m)
#   (Intercept)   9.6429     2.6853   3.591  0.01149
#   hours         2.7619     0.6329   4.364  0.00475
#   Multiple R-squared: 0.7604,  Adjusted R-squared: 0.7205
#   F-statistic: 19.04 on 1 and 6 DF,  p-value: 0.004752

confint(m)              # confidence intervals for the coefficients
predict(m, data.frame(hours = 4))    # 20.69
anova(m)                # the SSR / SSE partition
```

## Reading the output

```
Model Summary
 R      R Square   Adjusted R Square   Std. Error of the Estimate
.872      .760            .721                  3.552

ANOVA
            Sum of Squares   df   Mean Square      F      Sig.
Regression      240.286       1      240.286    19.042   .005
Residual         75.714       6       12.619
Total           316.000       7

Coefficients
                 B      Std. Error   Beta      t      Sig.
(Constant)     9.643      2.685              3.591   .011
hours          2.762      0.633     .872    4.364   .005
```

Every number here is one you computed. The **Beta** column (.872) equals *r* in simple regression -- another consequence of the same identity.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- simple regression</span>
A simple linear regression was conducted to predict *quiz score* from *review hours*. A significant model emerged, *F*(*1*, *6*) = *19.04*, *p* = *.005*, accounting for *76.0%* of the variance (*R&sup2;* = *.760*, adjusted *R&sup2;* = *.721*). *Review hours* significantly predicted *quiz score*, *b* = *2.76*, *SE* = *0.63*, *t*(*6*) = *4.36*, *p* = *.005*. Each additional hour of review was associated with an increase of *2.76* points.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- multiple regression</span>
A multiple linear regression was conducted to predict *posttest score* from *review hours* and *prior grade*. The model was significant, *F*(*2*, *117*) = *123.86*, *p* &lt; *.001*, *R&sup2;* = *.679*, adjusted *R&sup2;* = *.674*. Both predictors contributed significantly: *review hours* (*b* = *1.89*, *SE* = *0.16*, *t* = *12.04*, *p* &lt; *.001*) and *prior grade* (*b* = *0.53*, *SE* = *0.06*, *t* = *8.53*, *p* &lt; *.001*), each holding the other constant.
</div>

## Common mistakes

- **Interpreting a multiple regression coefficient without "holding the others constant."**
- **Extrapolating beyond the data.** Our model was fitted on 1 to 7 hours. Predicting a score for 40 hours is not supported.
- **Interpreting the intercept when x = 0 is impossible.**
- **Reporting R-squared instead of adjusted R-squared** in a multiple regression.
- **Claiming causation.** Regression predicts; it does not establish cause.
- **Reporting coefficients with no standard errors or confidence intervals.**

## Practice

**1.** For 6 pairs: Sxy = 48, Sxx = 24, mean x = 5, mean y = 30. Find the regression equation and predict y at x = 8.

<details markdown="1">
<summary>Show the worked answer</summary>

```
b1 = Sxy / Sxx = 48 / 24 = 2.00
b0 = ybar - b1 x xbar = 30 - 2.00 x 5 = 30 - 10 = 20
```

**Equation:** y&#770; = 20 + 2.00x

**Prediction at x = 8:**
```
y-hat = 20 + 2.00 x 8 = 20 + 16 = 36
```

**Interpretation:** each one-unit increase in x is associated with a 2-point increase in y.

**A caution worth stating:** is x = 8 inside the range of the observed data? The mean is 5, but without knowing the minimum and maximum we cannot tell. If the data only ran from 2 to 7, predicting at 8 is extrapolation and the prediction is not supported by the fitted model.
</details>

**2.** A model reports R&sup2; = .82 with 12 predictors and n = 30. What should concern you?

<details markdown="1">
<summary>Show the answer</summary>

**The ratio of predictors to cases.** With 12 predictors and 30 cases you have only 2.5 cases per predictor. Common guidance asks for at least 10 to 20.

Compute the adjusted R-squared:

```
adj R2 = 1 - (1 - .82) x (30 - 1)/(30 - 12 - 1)
       = 1 - .18 x 29/17
       = 1 - .3071
       = .693
```

**R&sup2; = .82 but adjusted R&sup2; = .69.** A gap of 13 percentage points is large, and it is the warning sign: much of that .82 is the model fitting noise rather than signal.

**What this means practically:**

- The model is **overfitted**. It describes this particular sample well and would predict poorly in a new one.
- Individual coefficients will be unstable -- drop two cases and they move substantially.
- With this many predictors, some will appear significant by chance alone.

**What to do:** reduce the predictor set on theoretical grounds, collect more cases, or validate on a holdout sample. And report **adjusted** R-squared, not the raw one.
</details>

**3.** In a multiple regression, hours has b = 1.89 in the two-predictor model but b = 2.34 when it is the only predictor. Is one of them wrong?

<details markdown="1">
<summary>Show the answer</summary>

**Neither is wrong. They answer different questions.**

**b = 2.34 (simple regression)** is the **total** association between hours and score. It includes any part of the relationship that runs through prior grade -- students with higher prior grades may also review more, and that shared variation is all credited to hours when hours is the only predictor.

**b = 1.89 (multiple regression)** is the association between hours and score **holding prior grade constant**. It is the unique contribution of hours after removing what prior grade explains.

The drop from 2.34 to 1.89 tells you that **part of the apparent effect of hours was really prior grade**. That is informative, not a contradiction.

**Which to report** depends on the question:

- *"How much does score change per hour of review, for students of equal prior ability?"* &rarr; the multiple regression coefficient.
- *"How much do reviewers score above non-reviewers overall?"* &rarr; the simple one.

**A warning:** if the coefficient changes **sign** between models rather than just shrinking, that usually signals multicollinearity or a suppressor variable, and needs investigation. Lesson 10 covers it.
</details>

## Before you move on

- [ ] I can compute b&#8321; and b&#8320; from Sxy, Sxx and the two means
- [ ] I can partition SST into SSR and SSE and verify they add up
- [ ] I know that R&sup2; = r&sup2; in simple regression, and F = t&sup2;
- [ ] I always say "holding the others constant" for a multiple regression coefficient
- [ ] I report adjusted R-squared when I have more than one predictor
- [ ] I do not extrapolate beyond the observed range of x

Next: comparing three or more group means, and why it is the same machinery.""",
    [{"question": "In simple linear regression with one predictor, R-squared equals:",
      "choices": ["The slope", "The square of the correlation, r-squared",
                  "The standard error", "Adjusted R-squared"], "correct": 1},
     {"question": "b = 1.89 for hours in a model that also contains prior grade. The correct interpretation is:",
      "choices": ["Score rises 1.89 points per hour, ignoring prior grade",
                  "Score rises 1.89 points per hour, holding prior grade constant",
                  "Hours explains 1.89% of the variance",
                  "1.89 is the correlation"], "correct": 1}],
    preview=True,
)


# ===========================================================================
L(
    "ANOVA: Comparing More Than Two Groups",
    """## What you will be able to do

Build a complete ANOVA table by hand -- every sum of squares, every degree of freedom, the F and the effect size -- then run post-hoc tests and know which one to pick.

## Why not just run t-tests?

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The error rate problem</span>
Three groups means three pairwise comparisons. Each at &alpha; = .05:

```
P(at least one false positive) = 1 - (1 - .05)^3 = .1426
```

**14%, not 5%.** With four groups it is six comparisons and 26%. With five groups, ten comparisons and 40%.

ANOVA tests all groups in **one** test at &alpha; = .05, which is exactly what it exists for.
</div>

## The idea

ANOVA compares **variation between groups** with **variation within groups**.

- If the groups really differ, the between-group variation will be large relative to the within-group noise.
- If they do not, both estimate the same thing and their ratio is about 1.

<div class="formula" markdown="1">
**F = MS<sub>between</sub> / MS<sub>within</sub>**
<span class="formula-note">signal divided by noise</span>
</div>

Despite the name, ANOVA tests **means**. It does it by analysing variances.

## Worked example, computed fully

<div class="callout callout-case" markdown="1">
<span class="callout-label">Our data</span>
Achievement scores for 8 students in each of three senior-high strands.

| STEM | ABM | HUMSS |
|---:|---:|---:|
| 78 | 70 | 68 |
| 80 | 72 | 70 |
| 82 | 74 | 71 |
| 83 | 75 | 73 |
| 85 | 76 | 74 |
| 86 | 78 | 75 |
| 88 | 79 | 77 |
| 90 | 82 | 80 |
</div>

### Step 1 -- group means and the grand mean

```
STEM : sum = 672,  n = 8,  mean = 84.00
ABM  : sum = 606,  n = 8,  mean = 75.75
HUMSS: sum = 588,  n = 8,  mean = 73.50

grand total = 1866,  N = 24,  grand mean = 1866/24 = 77.75
```

### Step 2 -- sum of squares between groups

<div class="formula" markdown="1">
**SS<sub>between</sub> = &Sigma; n<sub>j</sub>(x&#772;<sub>j</sub> &minus; x&#772;<sub>grand</sub>)&sup2;**
</div>

```
STEM : 8 x (84.00 - 77.75)^2 = 8 x ( 6.25)^2 = 8 x 39.0625 = 312.50
ABM  : 8 x (75.75 - 77.75)^2 = 8 x (-2.00)^2 = 8 x  4.0000 =  32.00
HUMSS: 8 x (73.50 - 77.75)^2 = 8 x (-4.25)^2 = 8 x 18.0625 = 144.50

SSB = 312.50 + 32.00 + 144.50 = 489.00
```

### Step 3 -- sum of squares within groups

Each group's deviations from **its own** mean:

```
STEM  deviations from 84.00: -6,-4,-2,-1,1,2,4,6   squares sum to 114.00
ABM   deviations from 75.75: -5.75,-3.75,-1.75,-0.75,0.25,2.25,3.25,6.25
                                                     squares sum to 105.50
HUMSS deviations from 73.50: -5.5,-3.5,-2.5,-0.5,0.5,1.5,3.5,6.5
                                                     squares sum to 106.00

SSW = 114.00 + 105.50 + 106.00 = 325.50
```

### Step 4 -- check the partition

```
SST = SSB + SSW = 489.00 + 325.50 = 814.50
```

<div class="callout callout-key" markdown="1">
<span class="callout-label">Free check</span>
Compute SST directly as the sum of squared deviations of all 24 scores from the grand mean of 77.75. It must equal **814.50** exactly. If it does not, one of your group means is wrong.
</div>

### Step 5 -- degrees of freedom

```
df between = k - 1     = 3 - 1  =  2
df within  = N - k     = 24 - 3 = 21
df total   = N - 1     = 24 - 1 = 23    (check: 2 + 21 = 23)
```

### Step 6 -- mean squares and F

```
MSB = SSB / df_between = 489.00 / 2  = 244.50
MSW = SSW / df_within  = 325.50 / 21 =  15.50

F = MSB / MSW = 244.50 / 15.50 = 15.77
```

### Step 7 -- decide

```
critical F(.05, 2, 21) = 3.47
15.77 > 3.47          ->  reject H0
p < .001
```

### The completed ANOVA table

| Source | SS | df | MS | F | p |
|---|---:|---:|---:|---:|---:|
| Between groups | 489.00 | 2 | 244.50 | 15.77 | &lt; .001 |
| Within groups | 325.50 | 21 | 15.50 | | |
| **Total** | **814.50** | **23** | | | |

## Effect size

<div class="formula" markdown="1">
**&eta;&sup2; = SS<sub>between</sub> / SS<sub>total</sub>**
</div>

```
eta-squared = 489.00 / 814.50 = 0.600
```

**60% of the variance in achievement is accounted for by strand.**

| &eta;&sup2; | Label |
|---|---|
| .01 | Small |
| .06 | Medium |
| .14 | Large |

This is a very large effect. **Omega-squared** (&omega;&sup2; = .552) is a less biased alternative and is increasingly preferred in journals.

## Post-hoc: which groups differ?

<div class="callout callout-key" markdown="1">
<span class="callout-label">F is an omnibus test</span>
A significant F says **the three means are not all equal**. It does not say which pairs differ. Reporting "STEM scored highest" from the F alone is a conclusion the analysis did not support.
</div>

| Situation | Post-hoc test |
|---|---|
| All pairwise comparisons, equal variances | **Tukey's HSD** |
| All pairwise, unequal variances | **Games-Howell** |
| Each group vs one control | **Dunnett** |
| Few pre-planned comparisons | **Planned contrasts** (most power) |
| Conservative, general purpose | **Bonferroni** |

For our data Tukey's HSD gives:

```
STEM vs ABM    : difference 8.25,  p = .001   significant
STEM vs HUMSS  : difference 10.50, p < .001   significant
ABM  vs HUMSS  : difference 2.25,  p = .499   not significant
```

So STEM differs from both others; ABM and HUMSS do not differ from each other. **That** is the finding, and it required the post-hoc tests.

## Assumptions

| Assumption | Check | If violated |
|---|---|---|
| Independent observations | Design | Repeated-measures ANOVA |
| Normality within each group | Shapiro-Wilk, Q-Q | Kruskal-Wallis |
| Homogeneity of variance | **Levene** (want p > .05) | **Welch's ANOVA** + Games-Howell |

Our data: Levene p = .965, so variances are comparable.

## Doing it in software

### Jamovi
**Analyses** &rarr; **ANOVA** &rarr; **One-Way ANOVA** for the quick version, or **ANOVA** for the full model with effect sizes.

- Under **Variances**, choose **Assume equal (Fisher's)** or **Don't assume equal (Welch's)**
- Under **Effect Size**, tick **&eta;&sup2;** and **&omega;&sup2;**
- Under **Post-Hoc Tests**, move the factor across and choose **Tukey** or **Games-Howell**
- Under **Assumption Checks**, tick **Homogeneity test** and **Normality test**

### SPSS
<kbd>Analyze</kbd> &rarr; <kbd>Compare Means</kbd> &rarr; <kbd>One-Way ANOVA</kbd>. Click **Post Hoc** and tick **Tukey**; click **Options** and tick **Descriptive**, **Homogeneity of variance test**, **Welch**.

For effect size, use <kbd>Analyze</kbd> &rarr; <kbd>General Linear Model</kbd> &rarr; <kbd>Univariate</kbd> and tick **Estimates of effect size** under Options.

### Excel
<kbd>Data</kbd> &rarr; <kbd>Data Analysis</kbd> &rarr; **ANOVA: Single Factor**. Excel gives the ANOVA table but **no post-hoc tests and no effect size** -- compute &eta;&sup2; yourself as SSB/SST.

### R
```r
dat <- data.frame(
  score  = c(78,80,82,83,85,86,88,90, 70,72,74,75,76,78,79,82, 68,70,71,73,74,75,77,80),
  strand = rep(c("STEM","ABM","HUMSS"), each = 8)
)

m <- aov(score ~ strand, data = dat)
summary(m)
#             Df Sum Sq Mean Sq F value   Pr(>F)
# strand       2  489.0  244.50   15.77 6.57e-05
# Residuals   21  325.5   15.50

TukeyHSD(m)                              # post-hoc
car::leveneTest(score ~ strand, dat)     # p = .965
effectsize::eta_squared(m)               # .600

oneway.test(score ~ strand, dat)         # Welch's version
```

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template</span>
A one-way ANOVA was conducted to compare achievement across *three* strands. Levene's test indicated homogeneity of variance (*p* = *.965*). There was a significant effect of strand, *F*(*2*, *21*) = *15.77*, *p* &lt; *.001*, *&eta;&sup2;* = *.60*. Tukey post-hoc comparisons showed that *STEM* students (*M* = *84.00*, *SD* = *4.04*) scored significantly higher than both *ABM* (*M* = *75.75*, *SD* = *3.88*, *p* = *.001*) and *HUMSS* (*M* = *73.50*, *SD* = *3.89*, *p* &lt; *.001*) students. *ABM* and *HUMSS* did not differ significantly (*p* = *.499*).
</div>

## Common mistakes

- **Running multiple t-tests instead of ANOVA.**
- **Stopping at the F.** Always follow a significant omnibus with post-hoc tests.
- **Naming which group is highest without post-hoc support.**
- **Choosing the post-hoc test after seeing which comparisons look promising.**
- **Reporting F with only one df.** F always has two: between and within.
- **Ignoring Levene.** Unequal variances call for Welch plus Games-Howell.
- **Omitting the effect size.**

## Practice

**1.** Three groups, n = 10 each. SSB = 240, SSW = 540. Build the ANOVA table and compute &eta;&sup2;.

<details markdown="1">
<summary>Show the worked answer</summary>

```
k = 3 groups, N = 30 total

df between = k - 1 = 2
df within  = N - k = 27
df total   = N - 1 = 29

MSB = 240 / 2  = 120.00
MSW = 540 / 27 =  20.00

F = 120.00 / 20.00 = 6.00
```

| Source | SS | df | MS | F |
|---|---:|---:|---:|---:|
| Between | 240 | 2 | 120.00 | 6.00 |
| Within | 540 | 27 | 20.00 | |
| **Total** | **780** | **29** | | |

```
critical F(.05, 2, 27) = 3.35
6.00 > 3.35  ->  significant, p = .007

eta-squared = 240 / 780 = 0.308
```

**&eta;&sup2; = .31 -- a large effect**, about 31% of the variance explained.

**Next step:** post-hoc tests, because the significant F does not identify which of the three pairs differ.
</details>

**2.** Levene's test gives p = .01 for a four-group comparison. What changes?

<details markdown="1">
<summary>Show the answer</summary>

**The variances are not equal, so standard ANOVA's assumption fails.**

**Two changes:**

1. **Use Welch's ANOVA** instead of the standard F. It does not pool the variances and adjusts the denominator degrees of freedom downward, often to a non-integer value.
2. **Use Games-Howell for post-hoc**, not Tukey. Tukey assumes equal variances; Games-Howell does not.

**How to report it:**

> Levene's test indicated unequal variances, *F*(3, 76) = 3.94, *p* = .011. Welch's ANOVA was therefore used, *F*(3, 41.2) = 8.52, *p* < .001. Games-Howell post-hoc comparisons showed...

**What not to do:**

- Report the standard ANOVA with a footnote. The p-value is not trustworthy, especially when group sizes are also unequal.
- Transform the data purely to equalise variances. You may, but Welch is simpler and the interpretation does not change.
- Ignore it. Unequal variances combined with unequal group sizes can badly distort the error rate -- in either direction.
</details>

**3.** Your F is significant but no Tukey comparison is. How is that possible?

<details markdown="1">
<summary>Show the answer</summary>

**It is uncommon but entirely possible, and it is not an error.**

The two procedures test different things:

- **The F test** asks whether *any* linear combination of the group means differs from zero. It is sensitive to patterns spread across several groups.
- **Tukey** tests only the *pairwise* differences, and it applies a correction that makes each individual comparison more conservative.

So a pattern where, say, two groups are slightly above the grand mean and two slightly below can produce a significant overall F while no single pair is far enough apart to clear Tukey's adjusted threshold.

**What to do:**

1. **Report it honestly.** "The omnibus test was significant, *F*(3, 36) = 3.12, *p* = .038, but no pairwise comparison reached significance after Tukey adjustment."
2. **Consider planned contrasts** if you had a specific hypothesis -- for example, the two experimental groups combined against the two control groups. Contrasts are more powerful than all-pairs procedures because they make fewer comparisons.
3. **Check your power.** This pattern often means the study was large enough to detect an overall effect but not a specific pairwise one.

**What not to do:** report an unadjusted LSD comparison because it happens to reach .05. That discards the error-rate control the post-hoc test existed to provide.
</details>

## Before you move on

- [ ] I can compute SSB, SSW, SST and verify they add up
- [ ] I know df between = k &minus; 1 and df within = N &minus; k
- [ ] I can compute F and &eta;&sup2; by hand
- [ ] I always follow a significant F with post-hoc tests
- [ ] I choose Tukey, Games-Howell or Dunnett for the right reason
- [ ] I check Levene and switch to Welch when it rejects

Next: the assumptions that sit underneath regression and ANOVA alike.""",
    [{"question": "A one-way ANOVA has SSB = 489, SSW = 325.5, with 3 groups and 24 cases. What is F?",
      "choices": ["1.50", "15.77", "3.47", "0.60"], "correct": 1},
     {"question": "A significant omnibus F tells you:",
      "choices": ["Which specific groups differ", "That the group means are not all equal",
                  "That all groups differ from each other", "The effect size"], "correct": 1}],
)


# ===========================================================================
L(
    "Checking Your Assumptions",
    """## What you will be able to do

Check every assumption behind regression and ANOVA using plots first and tests second, and know the specific remedy for each violation.

## Why plots beat tests

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The sample-size trap</span>
Normality tests behave badly at both extremes:

- **Large n (over ~300):** Shapiro-Wilk rejects departures far too small to matter. A trivially skewed variable with n = 2,000 will "fail."
- **Small n (under ~20):** the test has almost no power and misses real departures.

The test is most likely to reject exactly when it matters least. **Use plots as primary evidence, tests as support.**
</div>

## The four regression assumptions

Remember them as **LINE**:

| Letter | Assumption | Checked with |
|---|---|---|
| **L** | **L**inearity | Residuals vs fitted plot |
| **I** | **I**ndependence of errors | Durbin-Watson; study design |
| **N** | **N**ormality of residuals | Q-Q plot, Shapiro-Wilk |
| **E** | **E**qual variance (homoskedasticity) | Residuals vs fitted; Breusch-Pagan |

<div class="callout callout-key" markdown="1">
<span class="callout-label">The most common misunderstanding</span>
Regression assumes the **residuals** are normal, **not** the predictors and **not** the outcome.

A badly skewed outcome can still produce perfectly normal residuals if the skew is explained by the predictors. Testing your raw variables for normality is answering a question regression never asked.
</div>

## The one plot that checks almost everything

**Residuals versus fitted values.** Learn to read it and you have checked linearity, equal variance and outliers in a single glance.

```
GOOD -- random scatter, constant band
   resid
     |    .  .    .   .  .
   0 |--.---.--.----.---.--.---
     | .   .   .  .    .  .
     +--------------------------- fitted


CURVED -- linearity violated
   resid
     |      . . .
   0 |--.-.---------.-.---------
     |.                  . .
     +--------------------------- fitted


FUNNEL -- unequal variance
   resid
     |  .        .      .    .
   0 |--.---.-----.---.---.--.--
     |  .        .      .    .
     +--------------------------- fitted
        narrow  ->  wide
```

## Assumption by assumption

### Linearity

**Symptom.** A curve in the residuals-vs-fitted plot.

**Remedies, in order:**
1. Add a **quadratic term** (x-squared) if the curve is a simple bend
2. **Transform** the predictor -- log, square root, reciprocal
3. Use a **non-linear model** or splines

### Independence of errors

**Symptom.** Durbin-Watson far from 2. The statistic runs 0 to 4; roughly 1.5 to 2.5 is acceptable. Below 1.5 suggests positive autocorrelation.

Our multiple regression gives **DW = 2.22** -- fine.

**Remedies.** This is usually a design problem, not a modelling one. Time-series data needs time-series methods; clustered data needs multilevel models or cluster-robust standard errors.

### Normality of residuals

**Symptom.** Points depart from the diagonal on a Q-Q plot, especially at the ends.

```
Q-Q PLOT

 sample |            .
 quant  |          .
        |        .
        |     ..
        |   ..
        | ..                 points ON the line = normal
        +------------------- theoretical quantiles
```

**Remedies.**
1. With **large n**, often ignore it -- the central limit theorem protects the coefficient tests.
2. **Transform the outcome** (log for right skew).
3. Use **bootstrapped** confidence intervals, which make no normality assumption.

### Equal variance

**Symptom.** A funnel or fan in the residuals-vs-fitted plot. Formally, the **Breusch-Pagan** test.

<div class="callout callout-case" markdown="1">
<span class="callout-label">Worked example</span>
A model with visible funnelling:

```
Breusch-Pagan LM = 16.72,  p < .001     ->  heteroskedastic

b1 = 2.175
    OLS standard error       = 0.108
    HC3 robust standard error = 0.135     24% larger
```

The **coefficient is unbiased** either way. What heteroskedasticity breaks is the **standard error**, and therefore the p-value and the confidence interval.
</div>

**Remedies, in order:**
1. **Robust (HC3) standard errors.** Keeps the model, fixes the inference. Usually the best answer.
2. **Transform the outcome.** A log transform often stabilises variance and changes the interpretation to a proportional one.
3. **Weighted least squares**, if you can model the variance.

## ANOVA assumptions

The same list, expressed differently:

| Assumption | Check | Remedy |
|---|---|---|
| Independence | Design | Repeated-measures ANOVA |
| Normality within groups | Shapiro-Wilk per group | Kruskal-Wallis |
| Homogeneity of variance | Levene (want p > .05) | Welch's ANOVA |

Test normality **within each group**, never on the pooled data -- a real group difference makes the pooled distribution bimodal and the test rejects for the wrong reason.

## Doing it in software

### Jamovi
In **Linear Regression**, open **Assumption Checks** and tick:
- **Autocorrelation test** (Durbin-Watson)
- **Collinearity statistics** (VIF, lesson 10)
- **Normality test** and **Q-Q plot of residuals**
- **Residual plots**

### SPSS
In <kbd>Regression</kbd> &rarr; <kbd>Linear</kbd> &rarr; **Plots**: put `*ZRESID` on Y and `*ZPRED` on X, and tick **Normal probability plot**. Under **Statistics**, tick **Durbin-Watson** and **Collinearity diagnostics**.

### R
```r
m <- lm(score ~ hours + prior, data = dat)

par(mfrow = c(2, 2))
plot(m)          # all four diagnostic plots at once

# 1 Residuals vs Fitted  -> linearity, equal variance
# 2 Q-Q Residuals        -> normality
# 3 Scale-Location       -> equal variance
# 4 Residuals vs Leverage -> influential cases (Cook's distance)

shapiro.test(residuals(m))               # normality of RESIDUALS
lmtest::bptest(m)                        # Breusch-Pagan: BP = 16.72, p < .001
car::durbinWatsonTest(m)                 # DW = 2.22
lmtest::coeftest(m, vcov = sandwich::vcovHC(m, type = "HC3"))   # robust SEs
```

That `plot(m)` line is the single most useful command in applied regression.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- assumptions met</span>
Regression assumptions were examined prior to interpretation. Inspection of the residuals-versus-fitted plot indicated linearity and constant variance. The Q-Q plot and Shapiro-Wilk test (*W* = *.99*, *p* = *.42*) supported normality of residuals. The Durbin-Watson statistic (*2.22*) indicated independence of errors, and all variance inflation factors were below *2*, indicating no multicollinearity concern.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- a violation, handled</span>
The Breusch-Pagan test indicated heteroskedasticity (*LM* = *16.72*, *p* &lt; *.001*), confirmed by funnelling in the residual plot. Heteroskedasticity-consistent (HC3) standard errors were therefore used. The coefficient for *x* remained significant (*b* = *2.18*, robust *SE* = *0.14*, *p* &lt; *.001*).
</div>

Reporting a violation **and its remedy** is stronger than reporting no violations at all, because it shows you actually looked.

## Common mistakes

- **Testing normality of the raw variables** instead of the residuals.
- **Testing normality on pooled data** for ANOVA.
- **Relying on a test with large n**, where it rejects trivial departures.
- **Reporting "assumptions were met" with no evidence.**
- **Deleting cases to fix a violation.**
- **Ignoring heteroskedasticity** because the coefficient "looks fine" -- it is the SE that is wrong.

## Practice

**1.** Your residuals-vs-fitted plot shows a clear U shape. Which assumption is violated, and what do you do?

<details markdown="1">
<summary>Show the answer</summary>

**Linearity.** A systematic curve means the straight-line model is misspecified -- the true relationship bends and the model is forcing a line through it.

Note what it is **not**: a U shape is not a normality problem and not a variance problem. Those have different signatures (Q-Q departure and funnelling respectively).

**Remedies in order of preference:**

1. **Add a quadratic term.** `lm(y ~ x + I(x^2))`. If the x-squared coefficient is significant, the curve is real and now modelled. This is usually the fix for a simple U.
2. **Transform the predictor.** If y rises steeply then levels off, `log(x)` often straightens it.
3. **Transform the outcome**, if the curvature comes with unequal variance -- log often fixes both at once.
4. **Splines or a non-linear model**, if the shape is complex.

**What a U shape often means substantively:** a threshold or saturation effect. Study hours may help up to a point and then stop helping, or even hurt through fatigue. That is a finding, not a nuisance -- report it.

**What not to do:** report the linear model with a note that "residuals showed some pattern." The coefficient from a misspecified model estimates the wrong quantity.
</details>

**2.** Shapiro-Wilk on residuals gives p = .002 with n = 800. Is this a problem?

<details markdown="1">
<summary>Show the answer</summary>

**Probably not, and the sample size is why.**

With n = 800, Shapiro-Wilk has enormous power and will reject for departures far too small to affect anything. Significance here tells you the residuals are *detectably* non-normal, not *meaningfully* so.

**What to do instead:**

1. **Look at the Q-Q plot.** If points track the diagonal with only slight departure at the extreme tails, the departure is trivial.
2. **Check skewness and kurtosis.** Values within &plusmn;1 and &plusmn;2 respectively are fine regardless of the test.
3. **Remember the central limit theorem.** With n = 800, the sampling distributions of the coefficients are approximately normal even if the residuals are not. The t-tests are robust.

**When it WOULD matter at n = 800:** if the Q-Q plot shows severe departure -- a long heavy tail, or an obvious S-curve. That usually signals a **misspecified model**, an omitted variable, or extreme outliers, and the fix is modelling, not a transformation.

**How to report it:**

> Although the Shapiro-Wilk test was significant (*W* = .994, *p* = .002), this reflects the sensitivity of the test at *n* = 800. Inspection of the Q-Q plot showed only minor departure in the tails, and skewness (0.21) and kurtosis (&minus;0.34) were within acceptable limits. Residuals were treated as approximately normal.
</details>

**3.** Breusch-Pagan is significant. Your coefficient is 2.18 with OLS SE 0.108 and robust SE 0.135. What changes in your conclusion?

<details markdown="1">
<summary>Show the answer</summary>

**The coefficient does not change. The precision does.**

```
OLS   : b = 2.175, SE = 0.108, t = 20.1
Robust: b = 2.175, SE = 0.135, t = 16.1
```

Both are still highly significant, so **the substantive conclusion is unchanged**. But the honest standard error is 24% larger, and so is the confidence interval.

**Why the coefficient is unaffected:** heteroskedasticity does not bias the OLS estimate of b. It biases the estimate of b's *variance*. You were getting the right answer with an overstated claim of precision.

**When this matters more:** if the OLS p-value had been .03 and the robust p-value .07, the conclusion would flip. That is exactly the situation where reporting only OLS would be misleading.

**What to report:**

> Heteroskedasticity was detected (Breusch-Pagan *LM* = 16.72, *p* < .001), so heteroskedasticity-consistent (HC3) standard errors are reported. Review hours significantly predicted score, *b* = 2.18, robust *SE* = 0.14, *t* = 16.1, *p* < .001.

**A good habit:** report robust standard errors routinely when the residual plot shows any funnelling. They are identical to OLS when variance is constant, so they cost nothing and protect you when it is not.
</details>

## Before you move on

- [ ] I remember LINE and what each letter checks
- [ ] I know regression assumes normal **residuals**, not normal variables
- [ ] I can read a residuals-vs-fitted plot for curvature and funnelling
- [ ] I use plots first and tests second
- [ ] I know the remedy for each violation, and deleting cases is not one
- [ ] I report violations and their remedies rather than claiming none

Next: what happens when your outcome is not continuous at all.""",
    [{"question": "Linear regression assumes normality of:",
      "choices": ["The predictors", "The outcome variable", "The residuals", "All variables"], "correct": 2},
     {"question": "Heteroskedasticity primarily distorts:",
      "choices": ["The coefficient estimates", "The standard errors and p-values",
                  "The R-squared", "The degrees of freedom"], "correct": 1}],
)


# ===========================================================================
L(
    "Logistic Regression for Binary Outcomes",
    """## What you will be able to do

Fit and interpret a logistic regression, convert a coefficient into an odds ratio, turn a logit back into a probability, and explain why linear regression cannot be used for a yes/no outcome.

## Why not linear regression?

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
Your outcome is **passed / failed**, coded 1 and 0. You want to predict it from review hours.

Linear regression will run. It will also predict a probability of **1.34** for a student who reviewed 15 hours, and **&minus;0.12** for one who did not review at all.

Probabilities cannot exceed 1 or fall below 0. The model is structurally wrong.
</div>

Three reasons linear regression fails here:

1. **Predictions escape [0, 1].** Nothing constrains the line.
2. **The residuals cannot be normal.** With y only ever 0 or 1, residuals take just two values for any fitted value.
3. **Variance is not constant.** For a binary variable, variance is p(1&minus;p), which changes with p by construction.

## The fix: model the log-odds

### From probability to odds to logit

```
probability  p          ranges 0 to 1
odds         p/(1-p)    ranges 0 to infinity
log-odds     ln(p/(1-p))  ranges -infinity to +infinity   <- now a line can fit
```

| p | odds | log-odds (logit) |
|---:|---:|---:|
| 0.10 | 0.11 | &minus;2.20 |
| 0.25 | 0.33 | &minus;1.10 |
| 0.50 | 1.00 | 0.00 |
| 0.75 | 3.00 | 1.10 |
| 0.90 | 9.00 | 2.20 |

Notice the logit is **symmetric around 0.50**, where the odds are 1 and the log-odds are 0.

<div class="formula" markdown="1">
**ln( p / (1 &minus; p) ) = b&#8320; + b&#8321;x**
<span class="formula-note">a straight line, but in log-odds space</span>
</div>

To get back to a probability:

<div class="formula" markdown="1">
**p = 1 / (1 + e<sup>&minus;(b&#8320; + b&#8321;x)</sup>)**
</div>

## Worked example

<div class="callout callout-case" markdown="1">
<span class="callout-label">Our data</span>
n = 120 students. Outcome: **passed** (1) or **failed** (0). Predictor: **review hours**. 92 of 120 passed.

```
                b       SE      z       p      odds ratio
(Intercept)  -4.398   0.966  -4.55   <.001
hours         0.615   0.126   4.89   <.001      1.849

McFadden pseudo R-squared = .299
```
</div>

### Step 1 -- interpret the coefficient in log-odds

**b&#8321; = 0.615** means each additional hour of review increases the **log-odds** of passing by 0.615.

True but unreadable. Nobody thinks in log-odds.

### Step 2 -- convert to an odds ratio

<div class="formula" markdown="1">
**odds ratio = e<sup>b</sup>**
</div>

```
OR = e^0.615 = 1.849
```

<div class="callout callout-key" markdown="1">
<span class="callout-label">How to say an odds ratio</span>
**OR = 1.85:** each additional hour of review multiplies the **odds** of passing by 1.85 -- an **85% increase in the odds**.

Reading the scale:

- **OR = 1** &rarr; no effect
- **OR > 1** &rarr; increases the odds
- **OR < 1** &rarr; decreases the odds. OR = 0.5 halves the odds.

**Odds ratios are multiplicative, not additive.** Two extra hours multiplies the odds by 1.85&sup2; = 3.42, not by 3.70.
</div>

### Step 3 -- convert to actual probabilities

This is what a reader actually wants.

**At 8 hours:**
```
logit = -4.398 + 0.615 x 8 = -4.398 + 4.918 = 0.520
odds  = e^0.520 = 1.682
p     = 1.682 / (1 + 1.682) = 0.627
```

**At 10 hours:**
```
logit = -4.398 + 0.615 x 10 = 1.749
p     = 1 / (1 + e^-1.749) = 0.852
```

**At 12 hours:**
```
logit = -4.398 + 0.615 x 12 = 2.979
p     = 1 / (1 + e^-2.979) = 0.952
```

| Review hours | Probability of passing |
|---:|---:|
| 8 | 62.7% |
| 10 | 85.2% |
| 12 | 95.2% |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The effect is not constant</span>
From 8 to 10 hours, probability rises **22.5 points**. From 10 to 12, only **10.0 points**.

The odds ratio is constant; the **probability change is not**. It is largest near p = 0.5 and shrinks toward the extremes. This is why you should report probabilities at meaningful values rather than a single "effect."
</div>

## Model fit

Logistic regression has no R-squared in the ordinary sense. What you get instead:

| Measure | Meaning | Note |
|---|---|---|
| **&minus;2 Log Likelihood** | Badness of fit | Lower is better |
| **McFadden pseudo R&sup2;** | Proportional improvement over an intercept-only model | .2 to .4 already indicates excellent fit |
| **Cox & Snell R&sup2;** | Similar | Cannot reach 1 |
| **Nagelkerke R&sup2;** | Cox & Snell rescaled | Can reach 1 |
| **Hosmer-Lemeshow** | Goodness of fit test | **Non**-significant is good |
| **Classification table** | % correctly predicted | Compare against the base rate |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Pseudo R-squared is not R-squared</span>
McFadden's **.299 is a strong result**, not a weak one. The conventions differ completely: values of .2 to .4 indicate excellent fit.

Do not compare a pseudo R-squared with a linear R-squared, and do not apologise for a value of .3.
</div>

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The classification-accuracy trap</span>
Our model classifies about 87% of cases correctly. Impressive?

**92 of 120 students passed -- 76.7%.** A model that predicted "pass" for everyone would score 76.7% with no predictors at all.

Always compare accuracy against that **base rate**. Better still, report **sensitivity** (share of passers correctly identified) and **specificity** (share of failers correctly identified) separately, or the **AUC**.
</div>

## Assumptions

Logistic regression drops the normality and equal-variance assumptions, but adds others:

| Assumption | Check |
|---|---|
| Binary outcome | By definition |
| Independent observations | Design |
| **Linearity of the logit** in continuous predictors | Box-Tidwell test, or add x&times;ln(x) |
| **No severe multicollinearity** | VIF |
| **Adequate sample size** | At least 10 events per predictor |
| No complete separation | Check for infinite coefficients |

<div class="callout callout-key" markdown="1">
<span class="callout-label">Events per variable</span>
The rule of thumb is **10 cases of the rarer outcome per predictor**.

With 28 failures and 3 predictors, 28/3 &asymp; 9 -- borderline. With 28 failures and 6 predictors you are overfitting badly, whatever the p-values say.

For rare outcomes, **Firth logistic regression** corrects the small-sample bias. It is covered in Advanced Statistics.
</div>

## Doing it in software

### Jamovi
**Analyses** &rarr; **Regression** &rarr; **2 Outcomes (Binomial)**.
- Set the **Reference Level** explicitly -- this decides which outcome you are modelling
- Under **Model Coefficients**, tick **Odds ratio** and **Confidence interval**
- Under **Prediction**, tick **Classification table**, **Accuracy**, **Specificity**, **Sensitivity** and **AUC**

### SPSS
<kbd>Analyze</kbd> &rarr; <kbd>Regression</kbd> &rarr; <kbd>Binary Logistic</kbd>. `Exp(B)` in the output **is** the odds ratio. Click **Options** and tick **CI for exp(B)** and **Hosmer-Lemeshow goodness-of-fit**.

### R
```r
m <- glm(passed ~ hours, data = dat, family = binomial)
summary(m)
#   (Intercept)  -4.3982     0.9663  -4.552 5.3e-06
#   hours         0.6147     0.1256   4.893 9.9e-07

exp(coef(m))            # odds ratios:  hours = 1.849
exp(confint(m))         # CI for the odds ratios

# predicted probabilities at specific values
predict(m, data.frame(hours = c(8, 10, 12)), type = "response")
#        1         2         3
# 0.6271    0.8519    0.9516

# pseudo R-squared
1 - m$deviance / m$null.deviance      # McFadden = 0.299

# AUC
pROC::roc(dat$passed, fitted(m))
```

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template</span>
A binary logistic regression was conducted to predict *passing* from *review hours*. The model was significant, *&chi;&sup2;*(*1*) = *40.2*, *p* &lt; *.001*, and explained *29.9%* of the variance (McFadden pseudo *R&sup2;*). *Review hours* significantly predicted passing, *b* = *0.61*, *SE* = *0.13*, *Wald z* = *4.89*, *p* &lt; *.001*, *OR* = *1.85*, 95% CI [*1.47*, *2.42*]. Each additional hour of review was associated with an *85%* increase in the odds of passing. Predicted probabilities ranged from *62.7%* at *8* hours to *95.2%* at *12* hours.
</div>

Always report **both** the odds ratio and predicted probabilities at meaningful values. The odds ratio is the statistic; the probabilities are what a reader understands.

## Common mistakes

- **Reporting b instead of the odds ratio.** Log-odds are not interpretable.
- **Describing an odds ratio as a risk ratio.** For common outcomes they differ substantially; OR overstates.
- **Saying "1.85 times more likely to pass."** It is 1.85 times the **odds**, not the probability.
- **Comparing pseudo R-squared with linear R-squared.**
- **Reporting classification accuracy without the base rate.**
- **Too many predictors for the number of events.**
- **Not stating the reference category.** Which outcome is being modelled?

## Practice

**1.** A logistic regression gives b = &minus;0.693 for a predictor. What is the odds ratio and what does it mean?

<details markdown="1">
<summary>Show the worked answer</summary>

```
OR = e^(-0.693) = 0.500
```

**OR = 0.50.** Each one-unit increase in the predictor **halves the odds** of the outcome.

The negative coefficient signals this immediately: b < 0 always gives OR < 1, meaning the predictor reduces the odds.

**Two equivalent ways to say it:**

- *"Each one-unit increase halved the odds of the outcome, OR = 0.50."*
- *"Each one-unit **decrease** multiplied the odds by 2.0"* -- since 1/0.50 = 2. Reversing the direction is often the more natural sentence, and it is the same finding.

**The value 0.693 is worth recognising:** ln(2) = 0.693, so a coefficient of &minus;0.693 exactly halves the odds and +0.693 exactly doubles them. Spotting that saves you reaching for a calculator.

**What you cannot say:** "the probability halved." Whether a halving of odds halves the probability depends entirely on the starting probability. From p = .50 the odds go 1.0 to 0.5, so p falls to .33 -- a drop of a third, not a half.
</details>

**2.** Your model classifies 90% of cases correctly. Your outcome occurred in 89% of cases. Evaluate.

<details markdown="1">
<summary>Show the answer</summary>

**The model is worth almost nothing, despite the impressive-sounding accuracy.**

Predicting the majority class for **every** case, with no predictors at all, would score **89%**. Your model's 90% is a one-percentage-point improvement over doing nothing.

**Why this happens:** with an imbalanced outcome, accuracy is dominated by the majority class. The model can get everything right on the 89% and everything wrong on the 11% and still look excellent.

**What to report instead:**

- **Sensitivity** -- of the cases where the outcome occurred, what share did the model catch?
- **Specificity** -- of the cases where it did not, what share did the model correctly rule out? This is where imbalanced models collapse, often to near zero.
- **AUC** -- 0.5 is chance, 0.7 acceptable, 0.8 good. Unaffected by the base rate.
- **The full classification table**, not just the headline percentage.

**What you will usually find:** specificity near zero. The model predicts "yes" almost always.

**What to do about it:** adjust the classification threshold away from 0.5, or use a method designed for imbalance. But first ask whether classification is even the goal -- if you want to understand *which* predictors matter, the odds ratios are the finding and accuracy is beside the point.
</details>

**3.** A student writes: "Students who reviewed were 1.85 times more likely to pass." What is wrong?

<details markdown="1">
<summary>Show the answer</summary>

**It confuses odds with probability, and it drops the per-unit clause.**

**Error 1 -- odds versus likelihood.** OR = 1.85 means 1.85 times the **odds**, not 1.85 times the **probability**. "More likely" reads as probability to almost every reader.

How much they differ depends on the base rate:

```
If p starts at .30:  odds = 0.429
                     new odds = 0.429 x 1.85 = 0.793
                     new p = 0.793/1.793 = .442
                     Probability ratio = .442/.30 = 1.47, not 1.85
```

For rare outcomes the two converge; for common ones the odds ratio substantially overstates the risk ratio. Our outcome occurred in 77% of cases -- very common -- so the gap is large.

**Error 2 -- the unit is missing.** The coefficient is per **additional hour**, not for "reviewed versus did not review." The sentence describes a comparison the model never made.

**Corrected:**

> Each additional hour of review was associated with an 85% increase in the odds of passing (*OR* = 1.85, 95% CI [1.47, 2.42]). In probability terms, predicted pass rates rose from 62.7% at 8 hours to 95.2% at 12 hours.

**The general rule:** if you want to say "more likely," report **predicted probabilities**. If you report an odds ratio, say "odds."
</details>

## Before you move on

- [ ] I can explain why linear regression fails for a binary outcome
- [ ] I can move between probability, odds and log-odds
- [ ] I convert coefficients to odds ratios with e^b
- [ ] I can compute a predicted probability from the logit
- [ ] I never describe an odds ratio as a probability ratio
- [ ] I compare classification accuracy against the base rate
- [ ] I check events-per-variable before adding predictors

Next: finding structure across many variables at once.""",
    [{"question": "A logistic regression coefficient of b = 0.615 corresponds to an odds ratio of:",
      "choices": ["0.615", "1.85", "6.15", "0.54"], "correct": 1},
     {"question": "Your model is 90% accurate and the outcome occurs in 89% of cases. This means:",
      "choices": ["The model is excellent", "The model barely improves on predicting the majority class",
                  "The sample is too small", "The odds ratio is 0.90"], "correct": 1}],
)


# ===========================================================================
L(
    "Introduction to Multivariate Thinking",
    """## What you will be able to do

Recognise when a research question needs several outcomes analysed together rather than one at a time, name the right multivariate method for each situation, and explain why running many univariate tests is not an acceptable substitute.

## The shift

Everything so far had **one** outcome. Multivariate methods handle **several at once**.

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
You measured five subscales of academic motivation and want to compare two teaching methods.

You could run five t-tests. Five comparisons at &alpha; = .05 gives:

```
1 - .95^5 = .2262
```

**A 23% chance of at least one false positive.** And you have learned nothing about whether the five subscales move together, which is probably the actual question.
</div>

## The map

| Situation | Method |
|---|---|
| Several DVs, compare groups | **MANOVA** |
| Several DVs, compare groups, with covariates | **MANCOVA** |
| Many variables &rarr; fewer underlying factors | **Factor analysis / PCA** |
| Predict group membership from several variables | **Discriminant analysis** |
| Group cases into natural clusters | **Cluster analysis** |
| Two sets of variables, relationship between the sets | **Canonical correlation** |
| A full theoretical model with latent variables | **SEM / PLS-SEM** (Advanced Statistics) |

## MANOVA: several outcomes at once

**What it adds.** MANOVA tests whether groups differ on a **combination** of outcomes, controlling the family-wise error rate in one test.

**Why it can beat five t-tests.** Two groups may differ only slightly on each subscale individually, yet differ clearly on the **pattern** across them. MANOVA can detect that; separate t-tests cannot.

### The output

MANOVA reports four multivariate statistics:

| Statistic | When to use |
|---|---|
| **Pillai's Trace** | Most robust; the default choice, especially with unequal n |
| **Wilks' Lambda** | Most commonly reported |
| **Hotelling's Trace** | Similar |
| **Roy's Largest Root** | Most powerful when one dimension dominates; least robust |

**Report Pillai's Trace** unless you have a reason otherwise.

### The procedure

1. **Run MANOVA.** If not significant, stop.
2. **If significant**, follow with univariate ANOVAs on each DV -- now justified, because the multivariate test protected the error rate.
3. **If a univariate ANOVA is significant** and the factor has 3+ levels, run post-hoc tests.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">MANOVA is not always better</span>
It loses power when the DVs are **uncorrelated** -- you are paying a multivariate price for no multivariate benefit.

Rough guidance: use MANOVA when the DVs correlate between about **.30 and .70**. Below that, separate tests with a Bonferroni correction are often more powerful. Above .80 the DVs are near-redundant and should probably be combined into one scale.
</div>

### Assumptions

| Assumption | Check |
|---|---|
| Multivariate normality | Mardia's test; or univariate normality per DV as a proxy |
| **Homogeneity of covariance matrices** | **Box's M** (want *p* > .001) |
| Linearity among DVs | Scatterplot matrix |
| No multicollinearity among DVs | Correlations below about .80 |
| Adequate n | More cases than DVs in every cell |

Box's M is notoriously sensitive, so **judge it at &alpha; = .001**, not .05.

## Discriminant analysis

The mirror image of MANOVA. MANOVA asks *"do the groups differ on these variables?"* Discriminant analysis asks *"can these variables tell me which group someone is in?"*

Output to report: the **discriminant function**, **Wilks' lambda**, the **structure matrix** (which variables load on the function), and the **classification accuracy** compared against the base rate.

## Cluster analysis

Unlike everything else in this course, cluster analysis is **exploratory** -- there are no groups to begin with. It finds them.

| Method | Use when |
|---|---|
| **Hierarchical** (Ward's) | Small n; you want a dendrogram; number of clusters unknown |
| **K-means** | Large n; you can specify k in advance |
| **Two-step** | Mixed categorical and continuous variables |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Cluster analysis always returns clusters</span>
Ask for three clusters and you will get three, whether or not the data contains any real grouping.

Validate them: check whether clusters differ on variables **not** used to form them, check stability by re-running on split halves, and give each cluster a substantive interpretation. An uninterpretable cluster is an artefact.
</div>

## Doing it in software

### Jamovi
- **MANOVA**: **Analyses** &rarr; **ANOVA** &rarr; **MANCOVA**. Move all DVs into **Dependent Variables**.
- **Factor analysis**: **Analyses** &rarr; **Factor** &rarr; **Exploratory Factor Analysis** or **Principal Component Analysis**
- Cluster analysis needs the **snowCluster** module from the library.

### SPSS
- **MANOVA**: <kbd>Analyze</kbd> &rarr; <kbd>General Linear Model</kbd> &rarr; <kbd>Multivariate</kbd>. Tick **Homogeneity tests** under Options for Box's M.
- **Discriminant**: <kbd>Analyze</kbd> &rarr; <kbd>Classify</kbd> &rarr; <kbd>Discriminant</kbd>
- **Cluster**: <kbd>Analyze</kbd> &rarr; <kbd>Classify</kbd> &rarr; <kbd>Hierarchical Cluster</kbd> or <kbd>K-Means Cluster</kbd>

### R
```r
# MANOVA
m <- manova(cbind(dv1, dv2, dv3) ~ group, data = dat)
summary(m, test = "Pillai")
summary.aov(m)                    # follow-up univariate ANOVAs

# Box's M
heplots::boxM(dat[, c("dv1","dv2","dv3")], dat$group)

# discriminant analysis
MASS::lda(group ~ dv1 + dv2 + dv3, data = dat)

# clustering
d  <- dist(scale(dat[, 2:6]))
hc <- hclust(d, method = "ward.D2")
plot(hc); rect.hclust(hc, k = 3)
km <- kmeans(scale(dat[, 2:6]), centers = 3, nstart = 25)
```

Note `scale()` before clustering -- distance-based methods are dominated by whichever variable has the largest units unless you standardise first.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- MANOVA</span>
A one-way MANOVA was conducted with *three* motivation subscales as dependent variables and *teaching method* as the independent variable. Box's M was non-significant (*p* = *.214*), supporting homogeneity of covariance matrices. There was a significant multivariate effect of teaching method, Pillai's Trace = *.28*, *F*(*3*, *56*) = *7.21*, *p* &lt; *.001*, partial *&eta;&sup2;* = *.28*. Follow-up univariate ANOVAs indicated significant differences on *intrinsic motivation*, *F*(*1*, *58*) = *12.4*, *p* = *.001*, but not on *extrinsic motivation* (*p* = *.18*).
</div>

## Common mistakes

- **Running many univariate tests** instead of one multivariate test.
- **Using MANOVA with uncorrelated DVs**, which costs power for nothing.
- **Judging Box's M at .05.** Use .001.
- **Reporting Roy's Largest Root** because it gave the smallest p.
- **Not standardising before clustering.**
- **Treating cluster solutions as discoveries** without validation.
- **Combining DVs that measure different constructs** just because you measured them.

## Practice

**1.** You have four correlated outcome measures and two groups. Why is MANOVA better than four t-tests?

<details markdown="1">
<summary>Show the answer</summary>

**Three reasons.**

**1. Error rate control.** Four tests at .05:
```
1 - .95^4 = .1855
```
An 18.6% chance of at least one false positive. MANOVA tests everything in one procedure at .05.

**2. It uses the correlations.** The DVs are correlated, which means they carry overlapping information. MANOVA accounts for that structure; four separate tests pretend the outcomes are unrelated and effectively count the shared information four times.

**3. It can detect pattern differences.** Groups may differ only slightly on each measure alone -- none reaching significance -- while differing clearly on the *combination*. MANOVA finds that; separate tests never can.

**The procedure that follows:** significant MANOVA &rarr; univariate ANOVAs on each DV &rarr; post-hoc if needed. The multivariate test protects the error rate for the follow-ups.

**When four t-tests with Bonferroni would actually be better:** if the four DVs were essentially uncorrelated. Then there is no multivariate structure to exploit and MANOVA just costs power.
</details>

**2.** Box's M gives p = .004. Is homogeneity violated?

<details markdown="1">
<summary>Show the answer</summary>

**At the conventional threshold for this test, no.** Box's M is judged at **&alpha; = .001**, not .05, so p = .004 does **not** indicate a violation.

**Why the unusual threshold:** Box's M is extremely sensitive to any departure from multivariate normality and to large samples. Judged at .05 it rejects almost routinely, flagging violations too small to affect the analysis. The .001 convention is standard in multivariate texts.

**What to do:**

> Box's M was non-significant at the recommended &alpha; = .001 level (*M* = 18.4, *p* = .004), supporting the assumption of homogeneity of covariance matrices.

**If it had been below .001**, two protections:

1. **Report Pillai's Trace**, which is the most robust of the four multivariate statistics to covariance heterogeneity.
2. **Check group sizes.** With roughly equal n, MANOVA is fairly robust even when Box's M rejects. With badly unequal n it is not, and the violation matters.
</details>

**3.** Your k-means analysis produces three clusters. How do you know they are real?

<details markdown="1">
<summary>Show the answer</summary>

**You do not, from the clustering alone. K-means returns exactly the number of clusters you asked for, on any dataset, including pure noise.**

**Four validation steps:**

1. **External validation.** Do the clusters differ on variables **not** used to create them? If your clusters were built from motivation items and they also differ significantly on actual achievement, that is genuine evidence.

2. **Stability.** Split the sample in half, cluster each half separately, and check whether the same structure appears. Unstable solutions are artefacts.

3. **Internal indices.** The **silhouette coefficient** measures how well each case fits its cluster versus the next nearest; above 0.5 is reasonable. The **elbow method** on within-cluster sum of squares suggests how many clusters the data supports.

4. **Interpretability.** Can you describe each cluster substantively -- "high effort, low confidence" -- in a way that makes theoretical sense? A cluster you cannot name is usually a boundary artefact.

**What to report:**

> A three-cluster solution was selected based on the elbow in the within-cluster sum of squares and a mean silhouette width of 0.58. Clusters differed significantly on end-of-term achievement, which was not used in the clustering, *F*(2, 117) = 9.4, *p* < .001, supporting external validity.

**The honest framing throughout:** cluster analysis is **exploratory**. Describe the solution as one the data supports, not as a discovery of groups that objectively exist.
</details>

## Before you move on

- [ ] I know when several outcomes need a multivariate test
- [ ] I can name the right method for each multivariate question
- [ ] I report Pillai's Trace and judge Box's M at .001
- [ ] I know MANOVA loses power when the DVs are uncorrelated
- [ ] I standardise before clustering and validate the solution

Next: the method that finds the constructs hiding behind your questionnaire items.""",
    [{"question": "Box's M should be judged at which significance level?",
      "choices": [".05", ".01", ".001", ".10"], "correct": 2},
     {"question": "MANOVA loses power relative to separate ANOVAs when the dependent variables are:",
      "choices": ["Highly correlated", "Uncorrelated", "Normally distributed", "Measured on the same scale"], "correct": 1}],
)


# ===========================================================================
L(
    "Factor Analysis: Finding Structure in Your Variables",
    """## What you will be able to do

Run an exploratory factor analysis on a questionnaire, decide how many factors to retain using three converging criteria, rotate and interpret the loadings, and report reliability -- the full procedure for validating an instrument.

## The problem it solves

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
Your questionnaire has 20 items measuring "academic motivation." Are they really measuring one thing, or three?

You cannot answer that by reading the items. Factor analysis answers it from the **pattern of correlations** among them: items that measure the same underlying construct will correlate strongly with each other and weakly with everything else.
</div>

## EFA or PCA?

They are different procedures with different purposes, and the distinction comes up in defences.

| | Exploratory Factor Analysis | Principal Component Analysis |
|---|---|---|
| Goal | Find **latent constructs** that cause the items | **Reduce** variables to fewer components |
| Assumes | Underlying factors exist | Nothing causal |
| Analyses | **Shared** variance only | **Total** variance |
| Use for | Validating a questionnaire | Data reduction before regression |

<div class="callout callout-key" markdown="1">
<span class="callout-label">Which to use</span>
**Validating a scale, or arguing that a construct exists &rarr; EFA.**
**Just compressing many variables into fewer &rarr; PCA.**

SPSS's default under "Factor Analysis" is actually PCA, which is why so many theses report PCA while calling it factor analysis. Set the extraction method deliberately.
</div>

## Before you start: is the data suitable?

Two tests, both required in any write-up.

| Test | Want | Meaning |
|---|---|---|
| **Kaiser-Meyer-Olkin (KMO)** | **&ge; .60**, ideally &ge; .80 | Enough shared variance to factor |
| **Bartlett's test of sphericity** | **Significant** (*p* < .05) | Correlations differ from zero |

Note Bartlett's is the one test in this course where you **want** significance -- a non-significant result means your correlation matrix is essentially an identity matrix and there is nothing to factor.

**Sample size.** Guidance varies; a workable rule is **at least 5 cases per item and no fewer than 100**, with 10 per item preferred. Twenty items therefore wants 200 cases.

## Deciding how many factors

Never rely on one criterion. Use three and look for convergence.

### 1. Kaiser's rule -- eigenvalues over 1

Simple and **over-extracts**. Treat as an upper bound, not an answer.

### 2. The scree plot

Plot eigenvalues in descending order and look for the elbow. Retain the factors **before** the bend.

```
eigen
  5 | *
  4 |
  3 |   *
  2 |
  1 |     *
    |        *  *  *  *  *      <- scree: flat, retain 3
    +--------------------------
      1  2  3  4  5  6  7  8
```

### 3. Parallel analysis -- the best method

Generates random data of the same size and keeps only factors whose eigenvalues exceed what random data produces. **This is the current recommendation** and both Jamovi and R offer it.

<div class="callout callout-key" markdown="1">
<span class="callout-label">Also use theory</span>
If your instrument was built to measure three constructs and the analysis suggests three, that convergence is strong evidence. If it suggests five, either the instrument is not doing what you designed it to, or you have method artefacts -- such as all the reverse-scored items loading together on their own factor.
</div>

## Rotation

Unrotated factors are mathematically optimal and usually uninterpretable. Rotation redistributes the loadings to make each item load strongly on one factor and weakly on the rest.

| Type | Rotation | Assumes |
|---|---|---|
| **Orthogonal** | Varimax, Quartimax | Factors are **uncorrelated** |
| **Oblique** | Oblimin, Promax | Factors **may correlate** |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Use oblique rotation by default</span>
In the social sciences, constructs almost always correlate. Intrinsic and extrinsic motivation are related; anxiety and depression are related.

Varimax **forces** the factors to be uncorrelated, which is usually false and distorts the loadings. Run **Oblimin**: if the factor correlations come out near zero, the solution is effectively orthogonal anyway and you have lost nothing.
</div>

## Interpreting the loadings

A loading is the correlation between an item and a factor.

| Loading | Verdict |
|---|---|
| &ge; .70 | Excellent |
| .50 to .69 | Good |
| .40 to .49 | Acceptable; borderline |
| &lt; .40 | **Drop the item** |

### Cross-loadings

An item loading &ge; .40 on **two** factors is a **cross-loading**. It is ambiguous and normally removed -- unless it is theoretically essential, in which case say so explicitly.

### Communality

The proportion of an item's variance explained by the retained factors. Below **.30** means the item shares little with the rest and is a candidate for removal.

### Worked interpretation

```
Pattern Matrix (Oblimin rotation)

Item                           F1     F2     F3    Communality
I enjoy learning new things   .82    .11   -.04       .68
Learning is satisfying        .79    .08    .12       .65
I study to get high grades    .06    .85    .09       .74
I study to please my parents  .11    .78   -.02       .63
I am confident in exams       .02    .05    .81       .67
I handle pressure well       -.08    .14    .76       .61
I sometimes feel lost         .31    .28    .22       .24   <- drop
```

Reading it: three clean factors -- **intrinsic motivation** (F1), **extrinsic motivation** (F2), **academic self-efficacy** (F3). The last item loads on nothing above .40 and has a communality of .24, so it is dropped and the analysis re-run.

## Reliability

Having established the factor structure, report internal consistency for each subscale.

| Statistic | Note |
|---|---|
| **Cronbach's alpha** | Conventional; assumes all items contribute equally |
| **McDonald's omega** | Better when loadings differ; increasingly preferred |

| Alpha | Verdict |
|---|---|
| &ge; .90 | Excellent (but check for redundant items) |
| .80 to .89 | Good |
| .70 to .79 | Acceptable |
| .60 to .69 | Questionable |
| &lt; .60 | Poor |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Alpha depends on the number of items</span>
Alpha rises with item count. A 30-item scale can reach .90 with weak items simply because it is long.

Report **mean inter-item correlation** alongside it -- .15 to .50 is the healthy range. And a very high alpha (over .95) usually signals redundant items, not an excellent scale.
</div>

## Doing it in software

### Jamovi -- the easiest and the best defaults
**Analyses** &rarr; **Factor** &rarr; **Exploratory Factor Analysis**

- **Method**: Minimum residuals or Maximum likelihood
- **Rotation**: **Oblimin**
- **Number of factors**: **Based on parallel analysis**
- Under **Check Assumptions**: tick **Bartlett's test of sphericity** and **KMO measure of sampling adequacy**
- Under **Additional Output**: tick **Factor summary**, **Model fit measures**, **Scree plot**
- For reliability: **Analyses** &rarr; **Factor** &rarr; **Reliability Analysis**, tick **Cronbach's α**, **McDonald's ω**, and **Cronbach's α if item dropped**

### SPSS
<kbd>Analyze</kbd> &rarr; <kbd>Dimension Reduction</kbd> &rarr; <kbd>Factor</kbd>.
- **Descriptives** &rarr; tick **KMO and Bartlett's test of sphericity**
- **Extraction** &rarr; set Method to **Principal axis factoring** for true EFA; tick **Scree plot**
- **Rotation** &rarr; **Direct Oblimin**
- **Options** &rarr; tick **Suppress small coefficients**, set Absolute value below to **.40**

SPSS has no parallel analysis built in; syntax macros are freely available.

### R
```r
library(psych)

KMO(items)                       # want overall MSA >= .60
cortest.bartlett(items)          # want p < .05

fa.parallel(items, fa = "fa")    # parallel analysis -> how many factors

f <- fa(items, nfactors = 3, rotate = "oblimin", fm = "minres")
print(f, cut = 0.40, sort = TRUE)   # suppress loadings below .40

omega(items, nfactors = 3)       # McDonald's omega
alpha(items[, 1:5])              # Cronbach's alpha for one subscale
```

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template</span>
Exploratory factor analysis was conducted on the *20* items using minimum residuals extraction with oblimin rotation. The data were suitable for factoring: KMO = *.87* and Bartlett's test of sphericity was significant, *&chi;&sup2;*(*190*) = *1,842.3*, *p* &lt; *.001*. Parallel analysis supported a *three*-factor solution accounting for *58.4%* of the variance. *One* item was removed for failing to load above *.40* on any factor. The resulting subscales were labelled *intrinsic motivation* (*&alpha;* = *.84*), *extrinsic motivation* (*&alpha;* = *.79*) and *academic self-efficacy* (*&alpha;* = *.81*).
</div>

## Common mistakes

- **Running PCA and calling it factor analysis.**
- **Using Varimax by default** when the constructs plainly correlate.
- **Relying on eigenvalues over 1 alone**, which over-extracts.
- **Keeping items that load below .40** because they were in the original instrument.
- **Reporting alpha without the number of items** or the mean inter-item correlation.
- **Too few cases.** Under 100, or under 5 per item, the solution is unstable.
- **Naming factors before looking at the loadings.**
- **Using EFA when the structure is already known.** That calls for **confirmatory** factor analysis.

## Practice

**1.** KMO = .54 and Bartlett's test is significant. Should you proceed?

<details markdown="1">
<summary>Show the answer</summary>

**No. KMO = .54 is below the .60 minimum.**

The two tests check different things, and you need both:

- **Bartlett's significant** means your correlation matrix is not an identity matrix -- there *are* correlations. Necessary but very weak evidence; with a large sample it is significant almost automatically.
- **KMO** measures whether the correlations are **patterned enough to factor**. It compares the size of correlations with the size of partial correlations. At .54 the items correlate, but not in the clustered way factoring requires.

Kaiser's labels: .90+ marvellous, .80+ meritorious, .70+ middling, .60+ mediocre, .50+ miserable, below .50 unacceptable.

**What to do:**

1. **Check individual MSA values** on the anti-image correlation diagonal. Items below .50 are dragging the overall value down. Remove the worst, re-run, and KMO often rises substantially.
2. **Check your sample size.** Low KMO frequently just means too few cases.
3. **Reconsider the items.** If they genuinely measure unrelated things, no factor structure exists to find -- and that is a finding about your instrument.

**What not to do:** proceed and report the factors anyway. A solution extracted from unsuitable data is unstable and will not replicate.
</details>

**2.** An item loads .52 on Factor 1 and .48 on Factor 2. What do you do?

<details markdown="1">
<summary>Show the answer</summary>

**This is a cross-loading and the item is ambiguous.** Both exceed .40, and the difference of .04 is far too small to assign it to either factor.

The usual standard: an item should load at least **.20 higher** on its primary factor than on any other.

**Options, in order:**

1. **Remove it and re-run.** The default choice. Note that removing one item changes the whole solution, so the analysis must be repeated, not patched.

2. **Keep it if theory demands it.** Some constructs genuinely overlap -- an item like "I worry about failing" may legitimately tap both anxiety and motivation. If you keep it, say so explicitly and justify it, and assign it to the factor that is theoretically primary.

3. **Reconsider the number of factors.** Several cross-loadings across many items usually means you extracted the wrong number. Re-check parallel analysis and try one more and one fewer factor.

**What to report:**

> Item 14 cross-loaded on Factors 1 (.52) and 2 (.48) and was removed. The analysis was re-run with the remaining 19 items.

**What not to do:** assign it to Factor 1 because .52 > .48 and say nothing. A reader inspecting the pattern matrix will see it immediately.
</details>

**3.** Cronbach's alpha is .94 for a 25-item scale. Is that good?

<details markdown="1">
<summary>Show the answer</summary>

**It is high, but high enough to be suspicious, and the item count is why.**

**Two separate issues:**

**1. Alpha rises with length.** Alpha is a function of both the average inter-item correlation and the number of items. A 25-item scale can reach .94 with only moderate item correlations, purely because it is long. Alpha alone therefore says little about a long scale.

**2. Above about .95 suggests redundancy.** Very high alpha often means items are near-paraphrases -- "I enjoy studying," "I like studying," "Studying is enjoyable." They inflate alpha while adding no information, and they lengthen the questionnaire for no gain.

**What to check:**

- **Mean inter-item correlation.** Healthy range is **.15 to .50**. Above .50 on a long scale points to redundancy.
- **Alpha if item deleted.** If removing items barely moves alpha, they are not contributing.
- **The factor structure.** A high alpha does **not** mean unidimensionality. A two-factor scale can still show alpha of .90.

**What to report:**

> The 25-item scale showed high internal consistency (*&alpha;* = .94, *&omega;* = .93) with a mean inter-item correlation of .38, within the recommended range.

**A practical thought:** if redundancy is confirmed, a shortened 12-item version with alpha of .88 would be a better instrument — respondents complete it, and it measures the same thing.
</details>

## Before you move on

- [ ] I can state the difference between EFA and PCA and choose deliberately
- [ ] I check KMO and Bartlett before extracting
- [ ] I use parallel analysis, not eigenvalues over 1 alone
- [ ] I use oblique rotation unless I have a reason not to
- [ ] I drop items loading below .40 and re-run
- [ ] I report alpha with the item count and mean inter-item correlation

Next: why a p-value alone never answers the question that matters.""",
    [{"question": "Which rotation should be the default when constructs are expected to correlate?",
      "choices": ["Varimax", "Oblimin", "Quartimax", "No rotation"], "correct": 1},
     {"question": "For factor analysis, Bartlett's test of sphericity should ideally be:",
      "choices": ["Non-significant", "Significant", "Exactly .05", "Above .60"], "correct": 1}],
)


# ===========================================================================
L(
    "Effect Sizes: Why p-Values Alone Aren't Enough",
    """## What you will be able to do

Compute the right effect size for every test in this course, convert between them, and interpret magnitude in the units your reader actually cares about.

## The problem with p

<div class="callout callout-case" markdown="1">
<span class="callout-label">Two studies, same p-value</span>

| | Study A | Study B |
|---|---|---|
| n per group | 20 | 2,000 |
| Mean difference | 8.4 points | 0.4 points |
| *p* | .04 | .04 |
| Cohen's *d* | **0.68** | **0.06** |

Identical p-values. Study A found a difference worth acting on; Study B found one no student would notice.

**The p-value cannot distinguish them.** The effect size can.
</div>

<div class="callout callout-key" markdown="1">
<span class="callout-label">What each one tells you</span>
**p answers:** could this be chance?
**Effect size answers:** how big is it?

A p-value confounds effect size with sample size. Make n large enough and any non-zero difference becomes significant. Effect size is **independent of n** -- which is exactly why it is comparable across studies.
</div>

## The effect size for each test

| Test | Effect size | Formula | Small / Medium / Large |
|---|---|---|---|
| One-sample *t* | Cohen's *d* | (x&#772; &minus; &mu;&#8320;) / s | .20 / .50 / .80 |
| Independent *t* | Cohen's *d* | (x&#772;&#8321; &minus; x&#772;&#8322;) / s<sub>pooled</sub> | .20 / .50 / .80 |
| Paired *t* | Cohen's *d<sub>z</sub>* | mean difference / SD of differences | .20 / .50 / .80 |
| ANOVA | &eta;&sup2; or &omega;&sup2; | SS<sub>between</sub> / SS<sub>total</sub> | .01 / .06 / .14 |
| Correlation | *r* | -- | .10 / .30 / .50 |
| Regression | *R&sup2;*, *f&sup2;* | *f&sup2;* = R&sup2;/(1&minus;R&sup2;) | .02 / .15 / .35 |
| Chi-square 2&times;2 | &phi; | &radic;(&chi;&sup2;/n) | .10 / .30 / .50 |
| Chi-square larger | Cram&eacute;r's *V* | &radic;(&chi;&sup2;/(n &times; df<sub>min</sub>)) | .10 / .30 / .50 |
| Logistic regression | Odds ratio | e<sup>b</sup> | 1.5 / 2.5 / 4.0 |
| Mann-Whitney | rank-biserial *r* | -- | .10 / .30 / .50 |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Cohen's benchmarks are conventions, not laws</span>
Cohen himself described them as a last resort, for use only when no field-specific benchmark exists.

In educational interventions, *d* = 0.40 is often treated as the threshold for practical importance -- what Hattie calls the "hinge point." A *d* of 0.30 that is routine in one field is remarkable in another.

**Always interpret in context**, and say what the effect means in the original units.
</div>

## Worked computations

### Cohen's d from our two-group study

```
Control  : M = 72.00, SD = 5.68, n = 15
Treatment: M = 78.67, SD = 6.21, n = 15

pooled SD = 5.95      (computed in Applied Statistics)

d = (78.67 - 72.00) / 5.95 = 6.67 / 5.95 = 1.12
```

**d = 1.12, a large effect.** In plain units: nearly 7 points on a 100-item test.

### Eta-squared from our ANOVA

```
SSB = 489.00,  SST = 814.50

eta-squared = 489.00 / 814.50 = 0.600
```

**60% of the variance in achievement is accounted for by strand.**

<div class="callout callout-key" markdown="1">
<span class="callout-label">Partial eta-squared is not eta-squared</span>
SPSS reports **partial** &eta;&sup2; by default in GLM:

```
eta-squared         = SS_effect / SS_total
partial eta-squared = SS_effect / (SS_effect + SS_error)
```

In a one-way design with one factor they are identical. In factorial designs **partial &eta;&sup2; is larger** -- sometimes much larger -- because the other factors' variance is removed from the denominator.

Partial values from a factorial design can sum to more than 1, which is the giveaway. **Say which you are reporting.**
</div>

### Converting between effect sizes

```
d from r :   d = 2r / sqrt(1 - r^2)
r from d :   r = d / sqrt(d^2 + 4)
f2 from R2:  f2 = R2 / (1 - R2)
```

For our correlation of *r* = .872:
```
d = 2 x 0.872 / sqrt(1 - 0.760) = 1.744 / 0.490 = 3.56
```

Useful when comparing your result with studies that reported a different statistic, and essential for meta-analysis.

## Confidence intervals on effect sizes

An effect size is an **estimate** and carries uncertainty like any other.

```
d = 1.12, 95% CI [0.34, 1.88]
```

The interval runs from a medium effect to a very large one. Reporting **d = 1.12** alone implies a precision that 15 per group cannot deliver.

**Report the interval.** Journals increasingly require it, and it pre-empts the panel question about precision.

## Practical significance

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Statistical, practical and clinical significance are three things</span>

- **Statistically significant** -- unlikely to be chance
- **Large effect size** -- big relative to the variation
- **Practically significant** -- worth the cost and effort in the real world

A *d* of 1.12 is statistically significant and large. Whether it justifies rewriting a curriculum depends on what the module costs to produce, how long it takes to deliver, and what else that time could buy. **Statistics cannot answer that.** Your Discussion chapter must.
</div>

Express the effect in units a reader understands:

- *"Nearly 7 points on a 100-item test"*
- *"The average module student scored above 87% of lecture students"* (from *d* via the common-language effect size)
- *"Equivalent to roughly one additional letter grade"*

## Doing it in software

### Jamovi
Every T-Test panel has **Effect size** with a **Confidence interval** checkbox under Additional Statistics. ANOVA offers **&eta;&sup2;**, **partial &eta;&sup2;** and **&omega;&sup2;** under Effect Size.

### SPSS
Older versions report no Cohen's *d* in the t-test dialog -- compute it from the output. Version 27 and later include it. For &eta;&sup2;, use <kbd>General Linear Model</kbd> &rarr; <kbd>Univariate</kbd> &rarr; **Options** &rarr; **Estimates of effect size** (note: this gives **partial** &eta;&sup2;).

### Excel
```
= (mean1 - mean2) / SQRT(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
```

### R
```r
library(effectsize)

cohens_d(score ~ group, data = dat)        # d with 95% CI
eta_squared(aov_model)                     # eta-squared with CI
omega_squared(aov_model)                   # less biased
cramers_v(table(x, y))                     # for chi-square

interpret_cohens_d(1.12)                   # "large"
d_to_r(1.12)                               # convert
```

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- t-test</span>
The difference was statistically significant, *t*(*28*) = *3.07*, *p* = *.005*, with a large effect size, *d* = *1.12*, 95% CI [*0.34*, *1.88*]. In practical terms, students using the module scored an average of *6.67* points higher on a *100*-item test.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- ANOVA</span>
There was a significant effect of *strand*, *F*(*2*, *21*) = *15.77*, *p* &lt; *.001*, *&eta;&sup2;* = *.60*, indicating that strand accounted for *60%* of the variance in achievement -- a large effect by Cohen's conventions.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- a non-significant result</span>
The difference was not statistically significant, *t*(*14*) = *1.81*, *p* = *.092*; however, the effect size was medium, *d* = *0.47*, 95% CI [*&minus;0.08*, *1.01*]. The confidence interval includes effects of practical importance, so this result is inconclusive rather than evidence of no effect.
</div>

That last template is the one most theses need and almost none write.

## Common mistakes

- **Reporting p with no effect size.**
- **Confusing &eta;&sup2; with partial &eta;&sup2;** without saying which.
- **Treating Cohen's benchmarks as absolute.**
- **Claiming practical importance from statistical significance alone.**
- **Reporting an effect size with no confidence interval.**
- **Using r = .50 as "50% of the variance."** That is r&sup2; = .25.
- **Computing post-hoc power instead of reporting the effect size.**

## Practice

**1.** Two groups: M&#8321; = 45, SD&#8321; = 10, n&#8321; = 50; M&#8322; = 48, SD&#8322; = 10, n&#8322; = 50. Compute d and interpret.

<details markdown="1">
<summary>Show the worked answer</summary>

```
Both SDs are 10, so the pooled SD is also 10:
s_p = sqrt([49 x 100 + 49 x 100] / 98) = sqrt(9800/98) = sqrt(100) = 10

d = (48 - 45) / 10 = 3 / 10 = 0.30
```

**d = 0.30 -- a small to medium effect** by Cohen's conventions.

The test would be significant:
```
SE = 10 x sqrt(1/50 + 1/50) = 10 x 0.2 = 2.00
t  = 3 / 2.00 = 1.50, df = 98, p = .137
```

Actually **not significant** at .05.

**The teaching point:** with n = 50 per group, a small-to-medium effect of *d* = 0.30 does not reach significance. Power for *d* = 0.30 at n = 50 per group is only about 32%.

**How to report it:**

> The difference was not statistically significant, *t*(98) = 1.50, *p* = .137, *d* = 0.30, 95% CI [&minus;0.09, 0.69]. The study had approximately 32% power to detect an effect of this size; the result is inconclusive.

Reporting *d* alongside the non-significant *p* is what makes this honest rather than a dead end.
</details>

**2.** A study of 5,000 students finds r = .04, p = .005. Is this important?

<details markdown="1">
<summary>Show the answer</summary>

**Statistically significant, practically negligible.**

```
r^2 = .04^2 = .0016
```

**0.16% of the variance** -- about one part in 625. The two variables are, for all practical purposes, unrelated.

**Why it reached significance:** with n = 5,000 the standard error of *r* is roughly 1/&radic;4997 = .014, so even .04 sits nearly three standard errors from zero. Large samples detect trivially small effects.

**What to report:**

> Although the correlation was statistically significant, *r*(4998) = .04, *p* = .005, it accounted for only 0.16% of the variance and is unlikely to be of practical importance.

**The broader lesson:** in very large datasets, almost everything is significant. Significance stops being informative and effect size becomes the only thing worth reading. This is why medical and psychological journals increasingly require effect sizes with confidence intervals and de-emphasise p entirely.

**A useful reflex:** whenever n is in the thousands, look at the effect size first and the p-value second — or not at all.
</details>

**3.** SPSS reports partial &eta;&sup2; = .18 for one factor in a two-way ANOVA. Can you report this as "18% of the variance explained"?

<details markdown="1">
<summary>Show the answer</summary>

**No. That interpretation belongs to &eta;&sup2;, not partial &eta;&sup2;.**

```
eta-squared         = SS_effect / SS_total
                      -> share of TOTAL variance

partial eta-squared = SS_effect / (SS_effect + SS_error)
                      -> share of the variance NOT explained by other factors
```

In a two-way design the other factor's variance and the interaction's variance are **removed from the denominator** of partial &eta;&sup2;. So it is always larger than &eta;&sup2; and does not describe a share of the total.

**The giveaway:** partial &eta;&sup2; values from a factorial design can sum to more than 1. Shares of total variance cannot.

**Correct reporting:**

> The main effect of teaching method was significant, *F*(1, 76) = 16.7, *p* < .001, partial *&eta;&sup2;* = .18.

Naming it "partial" is the whole requirement. If you want the share of total variance, compute &eta;&sup2; yourself from the ANOVA table: SS for the effect divided by SS total.

**Why this matters beyond pedantry:** readers and meta-analysts comparing your .18 with another study's &eta;&sup2; of .18 would be comparing different quantities. Labelling it correctly is what keeps the number usable.
</details>

## Before you move on

- [ ] I know which effect size goes with each test
- [ ] I can compute Cohen's *d* and &eta;&sup2; by hand
- [ ] I report a confidence interval with every effect size
- [ ] I know the difference between &eta;&sup2; and partial &eta;&sup2;
- [ ] I express effects in the original units as well as the standardised ones
- [ ] I distinguish statistical, practical and clinical significance

Next: how the software actually finds the coefficients it reports.""",
    [{"question": "Two studies report p = .04. Study A has d = 0.68, Study B has d = 0.06. What does this show?",
      "choices": ["The studies agree", "The p-value cannot distinguish a meaningful effect from a trivial one",
                  "Study B has better methodology", "Effect size and p measure the same thing"], "correct": 1},
     {"question": "Partial eta-squared differs from eta-squared because it:",
      "choices": ["Uses a different numerator", "Removes other factors' variance from the denominator",
                  "Is always smaller", "Applies only to t-tests"], "correct": 1}],
)


# ===========================================================================
L(
    "How Statistical Models Are Actually Fit: Maximum Likelihood Estimation",
    """## What you will be able to do

Explain what the software is doing when it "estimates" a model, compute a likelihood by hand for a small example, and read the fit statistics -- AIC, BIC, &minus;2LL -- that appear in every logistic regression, SEM and survival output.

## Two ways to fit a model

**Least squares**, which you met in linear regression, picks the line minimising the sum of squared residuals.

**Maximum likelihood** asks a different question: *of all the possible parameter values, which one makes the data I actually observed most probable?*

<div class="callout callout-key" markdown="1">
<span class="callout-label">The core idea</span>
Probability runs forwards: given a coin is fair, how likely is 7 heads in 10 flips?

**Likelihood runs backwards:** given that I observed 7 heads in 10 flips, how likely is each possible value of the coin's bias?

Maximum likelihood picks the parameter value at the peak of that curve.
</div>

For linear regression with normal errors, the two methods give **identical** answers. Everywhere else -- logistic regression, survival analysis, SEM, multilevel models -- maximum likelihood is what is running.

## Worked example, by hand

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
You flip a coin 10 times and get **7 heads**. What is the most likely probability of heads, p?
</div>

### Step 1 -- write the likelihood

For a fixed p, the probability of exactly 7 heads in 10 flips is:

<div class="formula" markdown="1">
**L(p) = C(10,7) &times; p&#8311; &times; (1 &minus; p)&sup3;**
<span class="formula-note">C(10,7) = 120, a constant that does not affect where the peak is</span>
</div>

### Step 2 -- evaluate at several candidate values

| p | p&#8311; | (1&minus;p)&sup3; | L(p) = 120 &times; p&#8311;(1&minus;p)&sup3; |
|---:|---:|---:|---:|
| 0.5 | 0.00781 | 0.1250 | 0.1172 |
| 0.6 | 0.02799 | 0.0640 | 0.2150 |
| **0.7** | **0.08235** | **0.0270** | **0.2668** |
| 0.8 | 0.20972 | 0.0080 | 0.2013 |
| 0.9 | 0.47830 | 0.0010 | 0.0574 |

### Step 3 -- read off the maximum

**p = 0.7 gives the highest likelihood.** That is the maximum likelihood estimate.

And it matches intuition exactly: 7 heads out of 10 gives p&#770; = 7/10 = 0.7. For a simple binomial the MLE is just the sample proportion.

![Diagram: Maximum likelihood finds the peak of the likelihood curve](/static/diagrams/mle-curve.svg)

<div class="callout callout-key" markdown="1">
<span class="callout-label">Why intuition and the formula agree</span>
That agreement is the point. Maximum likelihood generalises the obvious answer to situations where there is no obvious answer -- logistic regression, survival models, factor models with missing data.
</div>

## Why software uses log-likelihood

Likelihoods are products of many small probabilities. With 200 cases you are multiplying 200 numbers each below 1, and the result underflows to zero in floating-point arithmetic.

Taking logarithms turns the product into a sum:

<div class="formula" markdown="1">
**ln L = &Sigma; ln(individual likelihoods)**
</div>

The logarithm is monotonic, so **the peak does not move**. Log-likelihoods are always negative (the log of a number below 1), and **closer to zero is better**.

```
ln L(0.5) = ln(0.1172) = -2.144
ln L(0.6) = ln(0.2150) = -1.537
ln L(0.7) = ln(0.2668) = -1.321    <- highest, i.e. closest to zero
ln L(0.8) = ln(0.2013) = -1.603
```

Same answer, no underflow.

## Reading the fit statistics

### &minus;2 Log Likelihood (deviance)

Multiply the log-likelihood by &minus;2. It becomes positive and, crucially, **differences between nested models follow a chi-square distribution**. **Lower is better.**

### The likelihood ratio test

To compare a model with a simpler version nested inside it:

<div class="formula" markdown="1">
**&chi;&sup2; = (&minus;2LL<sub>simple</sub>) &minus; (&minus;2LL<sub>complex</sub>)**
<span class="formula-note">df = difference in number of parameters</span>
</div>

```
Intercept-only model : -2LL = 134.6
With hours           : -2LL =  94.4
chi-square = 134.6 - 94.4 = 40.2,  df = 1,  p < .001
```

Adding `hours` significantly improves fit. This is the "Omnibus Test of Model Coefficients" in SPSS logistic output.

### AIC and BIC

Both penalise complexity so that adding useless predictors does not look like improvement.

<div class="formula" markdown="1">
**AIC = &minus;2LL + 2k** &nbsp;&nbsp;&nbsp; **BIC = &minus;2LL + k&middot;ln(n)**
<span class="formula-note">k = number of parameters, n = sample size</span>
</div>

| | Penalty | Tends to |
|---|---|---|
| **AIC** | 2 per parameter | Select larger models; better for prediction |
| **BIC** | ln(n) per parameter -- larger once n > 8 | Select smaller models; better for finding the true model |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Rules for using AIC and BIC</span>
- **Lower is better**, and the absolute value is meaningless. Only differences matter.
- A difference of **less than 2** is negligible; **2 to 6** is positive evidence; **over 10** is strong.
- They may only be compared across models fitted to the **same data** with the **same outcome**. Dropping cases with missing values changes the dataset and invalidates the comparison.
</div>

## Properties of ML estimators

| Property | Meaning |
|---|---|
| **Consistent** | Converges to the true value as n grows |
| **Asymptotically efficient** | Smallest possible variance in large samples |
| **Asymptotically normal** | Enables the Wald tests and CIs in the output |
| **Invariant** | If p&#770; is the MLE of p, then g(p&#770;) is the MLE of g(p) |
| **Possibly biased in small samples** | The main caution |

That last row matters practically. ML is a **large-sample** method. With small samples or rare outcomes the estimates can be badly biased -- which is exactly why **Firth logistic regression** exists for rare events.

## When estimation fails

Software does not solve these equations analytically; it searches iteratively. Sometimes the search fails.

| Message | Meaning | Fix |
|---|---|---|
| "Failed to converge" | The search did not settle | More iterations; rescale variables; simplify the model |
| Coefficients in the thousands with huge SEs | **Complete separation** -- a predictor perfectly predicts the outcome | Firth regression; remove or combine the predictor |
| "Hessian is not positive definite" | The likelihood surface has no proper peak | Model is unidentified; too many parameters for the data |
| Negative variance estimate (Heywood case) | Impossible estimate | Too few cases, or a misspecified factor model |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Never report results from a model that did not converge</span>
The numbers are wherever the search stopped, not estimates of anything. Fix the model or report that it could not be fitted.
</div>

## Doing it in software

### R
```r
# every glm reports the log-likelihood and AIC
m <- glm(passed ~ hours, data = dat, family = binomial)
logLik(m)          # 'log Lik.' -47.2 (df=2)
AIC(m); BIC(m)
deviance(m)        # -2LL = 94.4

# likelihood ratio test against the null model
m0 <- glm(passed ~ 1, data = dat, family = binomial)
anova(m0, m, test = "LRT")       # chi-square = 40.2, df = 1, p < .001

# fitting an MLE by hand, to see the machinery
nll <- function(p) -sum(dbinom(7, 10, p, log = TRUE))
optimize(nll, c(0.01, 0.99))     # minimum at p = 0.700
```

### SPSS
Logistic regression output shows **&minus;2 Log likelihood** in the Model Summary and the **Omnibus Tests of Model Coefficients** table, which is the likelihood ratio test against the intercept-only model.

### Jamovi
The binomial regression panel reports **Deviance**, **AIC**, **BIC** and an **Overall Model Test** under Model Fit.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template</span>
Parameters were estimated by maximum likelihood. The model significantly improved on the intercept-only model, *&chi;&sup2;*(*1*) = *40.2*, *p* &lt; *.001*. Model fit statistics were *&minus;2LL* = *94.4*, *AIC* = *98.4*, *BIC* = *104.0*. Compared with the alternative specification (*AIC* = *103.8*), the reported model was preferred (&Delta;*AIC* = *5.4*).
</div>

## Common mistakes

- **Comparing AIC across models fitted to different datasets.**
- **Interpreting an absolute AIC value.** Only differences mean anything.
- **Reporting results from a non-converged model.**
- **Ignoring complete separation.** Coefficients of 20 with SEs of 4,000 are not findings.
- **Using ML with a very small sample** and treating the estimates as unbiased.
- **Comparing &minus;2LL between non-nested models.** Use AIC or BIC for that.

## Practice

**1.** You flip a coin 20 times and get 12 heads. What is the MLE of p, and what is the log-likelihood there?

<details markdown="1">
<summary>Show the worked answer</summary>

**The MLE is the sample proportion:**
```
p-hat = 12 / 20 = 0.60
```

**The log-likelihood at that value:**
```
L(0.6)   = C(20,12) x 0.6^12 x 0.4^8
         = 125,970 x 0.0021768 x 0.00065536
         = 0.17971

ln L(0.6) = -1.7164
```

**Verification that 0.6 is the peak** -- evaluate either side:
```
ln L(0.55) = -1.8183
ln L(0.60) = -1.7164    <- highest
ln L(0.65) = -1.8242
```

**Why the MLE is always the sample proportion here:** differentiating the log-likelihood with respect to p and setting it to zero gives x/p = (n&minus;x)/(1&minus;p), which solves to p = x/n. The algebra confirms what intuition already said.

**The wider point:** for simple problems ML reproduces the obvious estimator. Its value is that it keeps working when nothing is obvious.
</details>

**2.** Model A has AIC = 245.2; Model B has AIC = 244.8. Which do you choose?

<details markdown="1">
<summary>Show the answer</summary>

```
Delta AIC = 245.2 - 244.8 = 0.4
```

**A difference of 0.4 is negligible.** The conventional reading:

| &Delta;AIC | Evidence |
|---|---|
| 0 to 2 | Essentially equivalent |
| 2 to 6 | Positive support for the lower |
| 6 to 10 | Strong |
| Over 10 | Very strong |

At 0.4 the data does not distinguish them. **Choose on other grounds:**

1. **Parsimony.** If Model B achieves the same fit with fewer parameters, prefer B. If B is the *more* complex one, prefer A — you are paying complexity for nothing.
2. **Theory.** Which model's predictors are justified by your literature?
3. **Interpretability.** Which one can you actually explain in a defence?

**How to report it:**

> Models A and B fitted the data comparably (&Delta;*AIC* = 0.4). The more parsimonious Model A was retained.

**What not to do:** present Model B as superior because its AIC is numerically lower. A reader who knows the convention will see 0.4 and know the claim is unsupported.
</details>

**3.** Your logistic regression returns a coefficient of 18.4 with a standard error of 3,214. What happened?

<details markdown="1">
<summary>Show the answer</summary>

**Complete or quasi-complete separation.** A predictor (or combination) perfectly predicts the outcome.

**Why the numbers look like that:** if every case above some cutoff passed and every case below failed, the likelihood keeps increasing as the coefficient grows toward infinity. There is no peak. The optimiser stops at an arbitrary large value, and the standard error explodes because the likelihood surface is flat.

**How to confirm it:** cross-tabulate the suspect predictor against the outcome. You will see a cell containing zero.

```
             Failed   Passed
hours < 6      28        0      <- the giveaway
hours >= 6      0       92
```

**What to do:**

1. **Firth logistic regression** (penalised likelihood). The standard fix — it produces finite, interpretable estimates. In R: `logistf::logistf()`. Covered in Advanced Statistics.
2. **Exact logistic regression** for very small samples.
3. **Combine categories** if the separating predictor is categorical with sparse levels.
4. **Remove the predictor** and report why — sometimes it is a proxy for the outcome and should never have been in the model.

**What not to do:** report the coefficient. An odds ratio of e^18.4 = 98 million is not a finding, and a panel will ask about it.
</details>

## Before you move on

- [ ] I can explain the difference between probability and likelihood
- [ ] I can compute a likelihood for a small binomial example
- [ ] I know why software uses log-likelihood
- [ ] I can run a likelihood ratio test between nested models
- [ ] I know AIC and BIC are comparable only on the same data, and only as differences
- [ ] I recognise non-convergence and complete separation

Next: the diagnostics that tell you whether a fitted model can be trusted.""",
    [{"question": "You observe 7 heads in 10 flips. The maximum likelihood estimate of p is:",
      "choices": ["0.5", "0.7", "0.75", "Cannot be determined"], "correct": 1},
     {"question": "Model A has AIC = 245.2, Model B has AIC = 244.8. This difference indicates:",
      "choices": ["Model B is clearly better", "The models are essentially equivalent",
                  "Model A should be rejected", "The sample is too small"], "correct": 1}],
)


# ===========================================================================
L(
    "Regression Diagnostics: Outliers, Non-Normality and Heteroskedasticity",
    """## What you will be able to do

Distinguish outliers, leverage and influence -- three different things students merge into one -- identify each with the right statistic, and apply the correct remedy without deleting data.

## Three different problems

<div class="callout callout-key" markdown="1">
<span class="callout-label">The distinction that matters</span>

- **Outlier** -- unusual on **y**. Large residual. The model predicts it badly.
- **High leverage** -- unusual on **x**. Far from the mean of the predictors. *Potentially* influential.
- **Influential** -- **removing it changes the fitted model.** This is the only one that is necessarily a problem.

A point can be any one of these without being the others.
</div>

```
     y                          y                          y
     |        o  <- outlier     |                  o       |              o <- influential
     |     . .                  |     . .         (high    |     . .        (both)
     |   . .                    |   . .          leverage) |   . .
     | . .                      | . .                      | . .
     +----------- x             +----------- x             +----------- x
   large residual,           unusual x, but ON          unusual x AND off
   x is typical              the trend -> harmless      the trend -> changes b
```

## The diagnostic statistics

| What it measures | Statistic | Flag when |
|---|---|---|
| Outlier on y | **Standardised residual** | beyond &plusmn;3 |
| Outlier on y (better) | **Studentised deleted residual** | beyond &plusmn;3 |
| Leverage on x | **Hat value (h)** | > 2(k+1)/n or 3(k+1)/n |
| Influence, overall | **Cook's distance** | > 4/n, or > 1 |
| Influence on one coefficient | **DFBETA** | > 2/&radic;n |
| Influence on its own fitted value | **DFFIT** | > 2&radic;((k+1)/n) |

<div class="callout callout-key" markdown="1">
<span class="callout-label">Cook's distance is the one to report</span>
It combines residual size and leverage into a single number -- exactly the combination that defines influence.

Two thresholds are in use: **D > 1** (conservative, flags only severe cases) and **D > 4/n** (sensitive, flags more). Report which you used.
</div>

### Why studentised deleted residuals beat ordinary ones

An influential point pulls the line toward itself, which **shrinks its own residual** and hides the problem.

The studentised deleted residual refits the model **without** that case and measures how far off the prediction is. A genuinely influential point cannot hide from it.

## The procedure

**Step 1 -- plot.** `plot(model)` gives all four diagnostics at once.

**Step 2 -- identify.** Note the case numbers flagged by Cook's distance, leverage and residuals.

**Step 3 -- investigate.** Go back to the raw data for each flagged case.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The decision tree for a flagged case</span>

1. **Is it a data-entry error?** Check the original form. Correct it and document the correction.
2. **Is it from a different population?** A 45-year-old in a study of Grade 11 students does not belong. Remove it, state the criterion, report the count.
3. **Is it a genuine extreme value?** **Keep it.** Report a sensitivity analysis with and without.

**Deleting a genuine observation because it is inconvenient is falsification.** Not a style issue.
</div>

**Step 4 -- run a sensitivity analysis.**

```
With all cases      : b = 2.18, p = .004
Excluding case 47   : b = 1.94, p = .021

Conclusion holds either way -> report the full-sample model and note the check.
```

**Step 5 -- report what you did.**

## Non-normal residuals

**Diagnosis.** Q-Q plot first; Shapiro-Wilk second, with the sample-size caveat from lesson 3.

**Remedies, in order:**

1. **With large n, often do nothing.** The central limit theorem protects the coefficient tests.
2. **Transform the outcome.** Log for right skew, square root for counts, reciprocal for severe skew.
3. **Bootstrap** the confidence intervals -- no normality assumption at all.
4. **Check for a misspecified model.** Severely non-normal residuals often mean an omitted variable or an unmodelled non-linearity, not a distributional problem.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Transformations change the question</span>
After `log(income)`, your coefficient describes a **proportional** change, not an absolute one. A coefficient of 0.05 on a predictor means roughly a **5% increase** in income per unit, not 0.05 pesos.

Back-transforming the mean of logged data gives the **geometric mean**, which is closer to a median than to the arithmetic mean. Say which you are reporting.
</div>

## Heteroskedasticity

**Diagnosis.** Funnelling in the residuals-vs-fitted plot; formally, the **Breusch-Pagan** or **White** test.

<div class="callout callout-case" markdown="1">
<span class="callout-label">Worked example</span>
```
Breusch-Pagan LM = 16.72,  p < .001

b1 = 2.175
   OLS standard error       = 0.108   ->  p < .001
   HC3 robust standard error = 0.135  ->  p < .001
```

The coefficient is identical. The honest standard error is **24% larger**.
</div>

**Remedies, in order:**

1. **Robust (HC3) standard errors.** Keeps the model, fixes the inference. Usually the best answer, and identical to OLS when variance is constant -- so they cost nothing.
2. **Transform the outcome.** A log transform often stabilises variance *and* fixes right skew at the same time.
3. **Weighted least squares**, if you can model how the variance changes.

## Autocorrelation

**Diagnosis.** **Durbin-Watson**, which runs 0 to 4. About 1.5 to 2.5 is acceptable; below 1.5 indicates positive autocorrelation.

Our multiple regression: **DW = 2.22**, fine.

**Remedies.** Usually a design issue. Time-ordered data needs time-series methods; clustered data needs multilevel models or cluster-robust standard errors.

## Doing it in software

### R
```r
m <- lm(score ~ hours + prior, data = dat)

par(mfrow = c(2, 2)); plot(m)

cooks.distance(m)                    # influence
which(cooks.distance(m) > 4/nrow(dat))
hatvalues(m)                         # leverage
rstudent(m)                          # studentised deleted residuals
dfbeta(m)                            # per-coefficient influence

car::influencePlot(m)                # all three on one chart
car::outlierTest(m)                  # Bonferroni-adjusted outlier test

lmtest::bptest(m)                    # Breusch-Pagan
lmtest::coeftest(m, vcov = sandwich::vcovHC(m, type = "HC3"))   # robust SEs
car::durbinWatsonTest(m)
```

`car::influencePlot()` is the single most informative diagnostic: residual on the y-axis, leverage on the x-axis, and bubble size proportional to Cook's distance. Influential points appear as large bubbles in the corners.

### SPSS
In <kbd>Regression</kbd> &rarr; <kbd>Linear</kbd> &rarr; **Save**, tick **Cook's**, **Leverage values**, **Studentized deleted** residuals, and **Standardized DfBeta(s)**. They are written as new columns you can sort and inspect.

### Jamovi
**Linear Regression** &rarr; **Assumption Checks** &rarr; tick **Cook's distance** to get a summary table with the maximum value and a count above threshold.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- diagnostics clean</span>
Regression diagnostics were examined. No case exceeded a Cook's distance of *1* (maximum = *0.18*), and no standardised residual exceeded *&plusmn;3*. Leverage values were all below the *3(k+1)/n* threshold of *.075*. The residuals-versus-fitted plot showed no systematic pattern.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- an influential case, retained</span>
One case (ID *47*) exceeded the Cook's distance threshold (*D* = *0.34*). Verification against the original questionnaire confirmed the value as genuine rather than a recording error, and the case was retained. A sensitivity analysis excluding it produced a substantively identical result (*b* = *1.94*, *p* = *.021*, versus *b* = *2.18*, *p* = *.004*).
</div>

## Common mistakes

- **Treating every flagged point as an error.** Flagged means look, not delete.
- **Confusing leverage with influence.** A high-leverage point sitting on the trend line is harmless.
- **Using ordinary residuals** where studentised deleted residuals are needed.
- **Deleting cases and not reporting it.**
- **Ignoring heteroskedasticity** because the coefficient looks unchanged -- the SE is what breaks.
- **Transforming without changing the interpretation.**
- **Reporting "no outliers were found"** with no statistic to support it.

## Practice

**1.** A case has leverage h = .28 (threshold .075) but Cook's distance = .03. Is it a problem?

<details markdown="1">
<summary>Show the answer</summary>

**No. It is a high-leverage point that is not influential.**

The case has unusual predictor values -- it sits far from the centre of the x-space. But Cook's distance of .03 is tiny, so removing it would barely move the fitted model.

**What this means geometrically:** the point is far out along the x-axis but sits **on** the trend the rest of the data defines. It is consistent with the model; it simply extends the range.

**This is actually useful.** High-leverage points that fit the trend **increase precision** — they widen the spread of x, which shrinks SE(b&#8321;) since SE depends on 1/&radic;Sxx. Removing it would make your estimate *worse*.

**What to report:**

> One case exhibited high leverage (*h* = .28) but low influence (Cook's *D* = .03) and was retained.

**When high leverage WOULD worry you:** if Cook's distance were also large. Then the point is both unusual in x and off the trend, and it is single-handedly determining the slope. That is the dangerous combination — and it is exactly why you check both statistics rather than either alone.
</details>

**2.** Your model has three cases with Cook's D above 4/n. What is your procedure?

<details markdown="1">
<summary>Show the worked answer</summary>

**Step 1 -- note that 4/n is the sensitive threshold.** With n = 120, 4/n = .033. That flags cases quite readily; the conservative threshold of D > 1 might flag none. Check both and say which you used.

**Step 2 -- investigate each case individually.** Pull the original data:
- Is any value impossible? An age of 150, a score of 120 out of 100.
- Is any value implausible but possible? Verify against the source document.
- Does the case belong to the target population?

**Step 3 -- classify and act:**

| Finding | Action |
|---|---|
| Data-entry error, correctable | Correct it, document, re-run |
| Error, not correctable | Remove, report the count and reason |
| Not from the target population | Remove, state the criterion |
| Genuine extreme value | **Keep**, run a sensitivity analysis |

**Step 4 -- sensitivity analysis for any genuine cases:**

```
All 120 cases      : b = 1.89, SE = 0.16, p < .001
Excluding the 3    : b = 1.76, SE = 0.15, p < .001
```

**Step 5 -- report:**

> Three cases exceeded the 4/n Cook's distance threshold. Verification confirmed all three as genuine observations, and they were retained. A sensitivity analysis excluding them produced substantively identical results (*b* = 1.76 versus 1.89), indicating the findings are robust to influential cases.

**The key judgement:** if the conclusion *changed* when you removed them, that is the finding and it must be reported. Three cases out of 120 driving a result is important information about the fragility of your model.
</details>

**3.** After log-transforming income, your coefficient for education is 0.08. How do you interpret it?

<details markdown="1">
<summary>Show the answer</summary>

**Approximately an 8% increase in income per additional year of education, holding other predictors constant.**

**Why:** in a log-linear model, the coefficient approximates a proportional change. For small coefficients:

```
percentage change = (e^b - 1) x 100
                  = (e^0.08 - 1) x 100
                  = (1.0833 - 1) x 100
                  = 8.33%
```

The approximation b &times; 100 = 8% works well below about 0.20. Above that, use the exact formula — a coefficient of 0.50 means (e^0.5 &minus; 1) = 65%, not 50%.

**What you must NOT say:** "income increases by 0.08 units." The outcome is no longer in pesos; it is in log-pesos, which has no meaningful unit.

**Two further points for a defence:**

1. **Back-transforming the fitted mean gives a geometric mean**, not an arithmetic one. It approximates the **median** income, which for skewed income data is arguably the better summary anyway — but say which you are reporting.

2. **Why the log was appropriate:** income is right-skewed and its variance grows with its level. The log transform usually fixes both the skew and the heteroskedasticity at once, which is why it is the standard choice for income, and it makes the proportional interpretation natural — a 8% raise means the same thing to everyone regardless of starting salary.

**How to report:**

> Income was log-transformed to address right skew and heteroskedasticity. Each additional year of education was associated with an 8.3% increase in income (*b* = 0.08, *SE* = 0.02, *p* < .001), holding experience and sector constant.
</details>

## Before you move on

- [ ] I can distinguish outlier, leverage and influence
- [ ] I know Cook's distance combines both and is the one to report
- [ ] I investigate flagged cases before deciding anything
- [ ] I never delete a genuine observation to improve a result
- [ ] I run and report sensitivity analyses
- [ ] I use robust standard errors when variance is not constant
- [ ] I restate the interpretation after any transformation

Next: what happens when two predictors carry the same information.""",
    [{"question": "A case has high leverage but Cook's distance near zero. This means it is:",
      "choices": ["Influential and should be removed", "Unusual on x but consistent with the model's trend",
                  "A data entry error", "An outlier on y"], "correct": 1},
     {"question": "After log-transforming the outcome, a coefficient of 0.08 means approximately:",
      "choices": ["An increase of 0.08 units", "An 8% increase", "An 80% increase", "A decrease of 8%"], "correct": 1}],
)


# ===========================================================================
L(
    "Multicollinearity, Ridge Regression and Shrinkage",
    """## What you will be able to do

Detect multicollinearity with VIF, recognise its signature in your output, and choose the right remedy -- including knowing when it is not a problem at all.

## What it is

**Multicollinearity is correlation among the predictors.** It says nothing about the outcome.

<div class="callout callout-key" markdown="1">
<span class="callout-label">Why it breaks interpretation</span>
A multiple regression coefficient answers: *"what is the effect of this predictor, holding the others constant?"*

If two predictors move almost perfectly together, there is **no data** where one changes and the other does not. The question has no answer in your sample, so the model cannot give a stable one.

The fit is unaffected. The individual coefficients become meaningless.
</div>

## The signature

<div class="callout callout-case" markdown="1">
<span class="callout-label">Worked demonstration</span>
n = 100. Predicting score from **study hours per week** and **study hours per day** -- two measures of one thing, r = .986.

**With study hours per week alone:**
```
b = 2.369,  SE = 0.153,  t = 15.47,  p < .001
R-squared = .7096
```

**With both predictors:**
```
hours/week: b = 0.891,  SE = 0.906,  t = 0.98,  p = .328
hours/day : b = 10.261, SE = 6.198,  t = 1.66,  p = .101
R-squared = .7175
```
</div>

Read what happened:

- **Neither predictor is significant** -- yet together they explain 72% of the variance
- The standard error for hours/week grew from 0.153 to 0.906, a **5.9-fold inflation**
- The coefficient collapsed from 2.37 to 0.89
- **R-squared barely moved** (.7096 to .7175)

<div class="callout callout-key" markdown="1">
<span class="callout-label">The diagnostic pattern</span>
**A significant overall F with no significant individual predictors is the classic signature of multicollinearity.** The model predicts well; it just cannot apportion credit between the correlated predictors.
</div>

## Measuring it: VIF

<div class="formula" markdown="1">
**VIF<sub>j</sub> = 1 / (1 &minus; R&sup2;<sub>j</sub>)**
<span class="formula-note">R&sup2;<sub>j</sub> is from regressing predictor j on all the other predictors</span>
</div>

**What VIF means literally:** the factor by which that coefficient's **variance** is inflated by collinearity. VIF = 4 means the standard error is &radic;4 = 2 times larger than it would be with uncorrelated predictors.

| VIF | Reading |
|---|---:|
| 1 | No collinearity |
| 1 to 5 | Acceptable |
| 5 to 10 | Concerning; investigate |
| Over 10 | Serious |

**Tolerance** is just 1/VIF; a tolerance below .10 corresponds to VIF over 10.

In our demonstration, **VIF = 35.6** for both predictors -- far beyond any threshold.

```
VIF = 1/(1 - R^2_j) = 1/(1 - 0.9719) = 35.6
```

By contrast, our earlier two-predictor model (hours and prior grade) had **VIF = 1.02** for both -- essentially no collinearity.

## The remedies

### 1. Drop one predictor (usually the right answer)

If two predictors measure the same construct, keep the one that best matches your research question and drop the rest. This is a **substantive** decision, not a statistical one.

In the demonstration, hours/week and hours/day are the same variable in different units. Keeping both was never defensible.

### 2. Combine them

If several items measure one construct, build a composite -- a sum, a mean, or a factor score from lesson 6. One predictor, no collinearity, and often a more reliable measure.

### 3. Centre for interaction terms

Interaction terms are **automatically** collinear with their components. Centring the predictors (subtracting the mean) removes that artificial collinearity without changing the interaction coefficient or the model fit.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Centring fixes only the artificial kind</span>
It removes collinearity **created by** forming a product term. It does nothing for genuine correlation between the underlying variables.
</div>

### 4. Principal component regression

Replace the correlated predictors with uncorrelated components (lesson 6). Solves the instability completely at the cost of interpretability -- your coefficients now apply to components, not to variables anyone can name.

### 5. Ridge regression and shrinkage

<div class="formula" markdown="1">
**minimise: &Sigma;(y &minus; y&#770;)&sup2; + &lambda;&Sigma;b&sup2;**
<span class="formula-note">ordinary least squares plus a penalty on the size of the coefficients</span>
</div>

Ridge deliberately accepts a **little bias** in exchange for a **large reduction in variance**. Coefficients are shrunk toward zero, which stabilises them.

| Method | Penalty | Behaviour |
|---|---|---|
| **Ridge** | &lambda;&Sigma;b&sup2; | Shrinks all coefficients; keeps every predictor |
| **LASSO** | &lambda;&Sigma;&#124;b&#124; | Shrinks some to **exactly zero** -- selects variables |
| **Elastic net** | Both | Compromise; good with many correlated predictors |

&lambda; is chosen by cross-validation, not by hand.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Shrinkage is for prediction, not inference</span>
Ridge and LASSO coefficients are **biased by construction**, and standard errors and p-values are not straightforward.

Use them when the goal is **predicting well in new data**. If the goal is interpreting individual coefficients -- which it usually is in a thesis -- fix the collinearity substantively instead.
</div>

## When multicollinearity does NOT matter

<div class="callout callout-key" markdown="1">
<span class="callout-label">Three cases where you can ignore it</span>

1. **You only care about prediction.** Collinearity does not harm R-squared or predicted values. Only individual coefficients suffer.
2. **The collinear variables are control variables** you never intended to interpret.
3. **It involves only the interaction term and its components**, after centring.
</div>

## Doing it in software

### Jamovi
**Linear Regression** &rarr; **Assumption Checks** &rarr; tick **Collinearity statistics**. Gives VIF and tolerance for each predictor.

### SPSS
<kbd>Regression</kbd> &rarr; <kbd>Linear</kbd> &rarr; **Statistics** &rarr; tick **Collinearity diagnostics**. Reports VIF, tolerance, eigenvalues and condition indices. A **condition index above 30** combined with two variance proportions above .50 on the same row indicates a collinearity problem.

### R
```r
m <- lm(score ~ hours_wk + hours_day, data = dat)
car::vif(m)                 # 35.6  35.6

cor(dat[, c("hours_wk","hours_day")])    # r = .986

# ridge and lasso
library(glmnet)
X <- model.matrix(score ~ hours_wk + hours_day, dat)[, -1]
cv <- cv.glmnet(X, dat$score, alpha = 0)     # alpha = 0 ridge, 1 lasso
coef(cv, s = "lambda.min")
```

Always inspect the correlation matrix of your predictors before fitting. Most collinearity is visible there.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- no problem</span>
Multicollinearity was assessed using variance inflation factors. All VIFs were below *2* (maximum = *1.02*), and tolerance values exceeded *.98*, indicating no multicollinearity concern.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- detected and resolved</span>
Initial analysis revealed severe multicollinearity between *study hours per week* and *study hours per day* (*r* = *.99*, VIF = *35.6*), reflecting that both operationalised the same construct. *Study hours per week* was retained as the measure aligned with the research question and *study hours per day* was removed. All remaining VIFs were below *2*.
</div>

## Common mistakes

- **Checking correlations with the outcome.** Multicollinearity is among the **predictors**.
- **Panicking over VIF = 3.** That is fine.
- **Dropping a predictor on statistical grounds alone.** Decide substantively.
- **Not centring before building interaction terms.**
- **Using ridge or LASSO when you intend to interpret coefficients.**
- **Reporting a model where nothing is significant but F is**, without investigating.
- **Ignoring a sign that contradicts theory.** That often signals collinearity, not a new finding.

## Practice

**1.** Your model has VIF values of 1.2, 1.4, 8.7 and 9.1. What do you do?

<details markdown="1">
<summary>Show the answer</summary>

**Two predictors are in the concerning range (5 to 10). Investigate before deciding.**

**Step 1 -- find out what they share.** Examine the correlation matrix. VIFs of 8.7 and 9.1 appearing together almost always means those two predictors correlate strongly with each other — roughly r = .94, since VIF = 9 implies R²ⱼ = 1 − 1/9 = .89.

**Step 2 -- ask what they measure.** Are they:
- Two operationalisations of one construct? &rarr; **combine or drop one**
- Genuinely distinct but naturally related, like income and education? &rarr; **may be legitimate**
- One a component of the other, like total score and a subscale? &rarr; **drop one**, they are structurally dependent

**Step 3 -- decide by research question, not by VIF.** If both are theoretically essential and you only need the *model* rather than the individual coefficients, VIF of 9 is tolerable. If you need to interpret those two coefficients, it is not — their standard errors are &radic;9 = 3 times inflated.

**Step 4 -- report whatever you decide.**

> Two predictors showed elevated VIFs (8.7 and 9.1), reflecting their substantial correlation (*r* = .94). Because both were central to the hypothesis, both were retained; however, their individual coefficients should be interpreted with caution given the inflated standard errors.

**What not to do:** drop the one with the larger p-value. That is letting the data choose your model.
</details>

**2.** Your F test is significant (p < .001) but no predictor is significant. What is happening?

<details markdown="1">
<summary>Show the answer</summary>

**This is the textbook signature of multicollinearity.**

The two tests ask different questions:

- **The F test** asks whether the predictors **as a set** explain variance in y. With collinear predictors the set does fine.
- **Each t test** asks whether that predictor adds something **the others do not already provide**. When predictors overlap heavily, none adds unique information, so none reaches significance.

**Our demonstration showed exactly this:** R² = .7175 with F highly significant, yet p = .328 and p = .101 for the two predictors.

**What to do:**

1. **Check VIF.** Expect large values.
2. **Check the predictor correlation matrix.** The culprits are usually obvious.
3. **Fit each predictor alone.** In our demonstration, hours/week alone gave b = 2.37, t = 15.47, p < .001 — strongly significant once its twin was removed.
4. **Decide substantively** which to keep.

**Two alternative explanations worth ruling out:**

- **Small sample with many predictors.** Low power on every individual test.
- **Genuinely weak predictors** that collectively explain a little. Check whether R² is actually respectable — .72 rules this out here.

**How to report it once resolved:** do not present the collinear model at all. Present the corrected one and describe the diagnosis in your analysis section.
</details>

**3.** You add an interaction term and the VIFs for both main effects jump above 10. Is this a problem?

<details markdown="1">
<summary>Show the answer</summary>

**Almost certainly not — this is artificial collinearity and centring removes it.**

**Why it happens:** the product X&times;W is mathematically dependent on X and W. If X ranges from 20 to 60, both X and X&times;W grow together, producing correlations near .95 and VIFs in the tens. Nothing is wrong with your data; it is an artefact of how the product was constructed.

**The fix:**

```r
dat$X_c <- scale(dat$X, scale = FALSE)   # subtract the mean
dat$W_c <- scale(dat$W, scale = FALSE)
m <- lm(Y ~ X_c * W_c, data = dat)
car::vif(m)        # now typically close to 1
```

**What centring changes and does not change:**

| Changes | Does not change |
|---|---|
| VIFs for the main effects (drop sharply) | The interaction coefficient b&#8323; |
| Interpretation of b&#8321; and b&#8322; | R-squared or overall fit |
| The intercept | The interaction's significance |

After centring, b&#8321; is the effect of X **when W is at its mean** — an interpretable value. Uncentred, it was the effect of X when W = 0, which may be impossible.

**The one case where it IS a real problem:** if X and W were already strongly correlated *before* you formed the product. Centring will not fix that, because the collinearity is genuine rather than constructed. Check `cor(X, W)` on the raw variables to tell the two situations apart.
</details>

## Before you move on

- [ ] I know multicollinearity is among predictors, not with the outcome
- [ ] I can compute VIF from R&sup2;ⱼ and interpret it as variance inflation
- [ ] I recognise the significant-F-no-significant-predictors signature
- [ ] I resolve collinearity substantively, not by dropping the larger p-value
- [ ] I centre before creating interaction terms
- [ ] I know shrinkage is for prediction, not for interpreting coefficients

Next: bringing categorical predictors into the linear model.""",
    [{"question": "Your overall F is significant but no individual predictor is. The most likely cause is:",
      "choices": ["Too small a sample", "Multicollinearity among the predictors",
                  "Heteroskedasticity", "Non-normal residuals"], "correct": 1},
     {"question": "A VIF of 9 means that coefficient's standard error is inflated by a factor of about:",
      "choices": ["9", "3", "81", "1.5"], "correct": 1}],
)


# ===========================================================================
L(
    "Dummy Variables, Interaction and Comparing Models Across Groups",
    """## What you will be able to do

Bring categorical predictors into a regression correctly, interpret every coefficient against its reference category, test whether a relationship differs across groups, and report simple slopes.

## The problem

Regression needs numbers. Sex, strand, region and civil status are categories.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">What you must not do</span>
Coding strand as STEM = 1, ABM = 2, HUMSS = 3 and entering it as a continuous predictor forces the model to assume:

- The strands are **ordered**
- The gap from STEM to ABM **equals** the gap from ABM to HUMSS
- Each step has the **same** effect on the outcome

None of that is true for a nominal variable. This is the levels-of-measurement error from Basic Statistics, appearing inside a regression.
</div>

## Dummy coding

<div class="callout callout-key" markdown="1">
<span class="callout-label">The rule</span>
For a categorical variable with **k** categories, create **k &minus; 1** dummy variables, each coded 0 or 1.

The category left out is the **reference**, and every coefficient is a comparison **against it**.
</div>

### Worked example: three strands

| Strand | D1 (ABM) | D2 (HUMSS) |
|---|---:|---:|
| **STEM** (reference) | 0 | 0 |
| ABM | 1 | 0 |
| HUMSS | 0 | 1 |

Two dummies, not three. STEM is identified by having zeros on both.

```
score = b0 + b1(ABM) + b2(HUMSS)

b0 = predicted score for STEM (both dummies = 0)
b1 = difference: ABM minus STEM
b2 = difference: HUMSS minus STEM
```

Using the ANOVA data from lesson 2:
```
b0 = 84.00               STEM mean
b1 = 75.75 - 84.00 = -8.25    ABM scores 8.25 points below STEM
b2 = 73.50 - 84.00 = -10.50   HUMSS scores 10.50 points below STEM
```

<div class="callout callout-key" markdown="1">
<span class="callout-label">Regression with dummies IS ANOVA</span>
Fit that model and the overall F is **15.77 on 2 and 21 df** -- exactly the ANOVA from lesson 2, and R&sup2; = .600 = &eta;&sup2;.

They are the same procedure. ANOVA is a regression with dummy-coded predictors, which is why both sit inside the "general linear model."
</div>

### The dummy variable trap

Including **all k** dummies plus an intercept makes the model unsolvable: the dummies sum to 1 for every case, which is exactly what the intercept column already is. Software either drops one automatically or reports an error about singularity.

### Choosing the reference category

The choice does not change the model's fit, but it changes every coefficient. Choose deliberately:

- The **control** or standard condition
- The **largest** group, which gives the most stable comparisons
- The category your literature treats as the baseline

**Always state which category is the reference.** A coefficient of &minus;8.25 is uninterpretable without it.

### Other coding schemes

| Scheme | Reference | Use when |
|---|---|---|
| **Dummy (indicator)** | One chosen category | Comparing against a control -- the default |
| **Effect (deviation)** | The grand mean | Comparing each group with the overall average |
| **Contrast** | Custom | Specific planned comparisons |

## Interaction: does the relationship differ by group?

A dummy shifts the **intercept**. An interaction lets the **slope** differ.

<div class="formula" markdown="1">
**score = b&#8320; + b&#8321;(hours) + b&#8322;(group) + b&#8323;(hours &times; group)**
</div>

| Coefficient | Meaning |
|---|---|
| b&#8320; | Intercept for the **reference** group |
| b&#8321; | Slope of hours **for the reference group** |
| b&#8322; | Difference in **intercept** between groups |
| b&#8323; | Difference in **slope** between groups |

**b&#8323; is the test of whether the relationship differs across groups.** CMO 42 calls this "testing for parallelism."

```
Reference group slope        = b1
Other group slope            = b1 + b3
```

<div class="callout callout-case" markdown="1">
<span class="callout-label">Worked interpretation</span>
Predicting salary from years of experience, with a dummy for sector (public = reference).

```
b0 = 18,500   intercept for public sector
b1 =  1,200   each year of experience adds 1,200 in the PUBLIC sector
b2 =  4,300   private sector starts 4,300 higher
b3 =    850   each year adds 850 MORE in private than public

Public sector slope  = 1,200
Private sector slope = 1,200 + 850 = 2,050
```

Experience is rewarded at nearly **twice the rate** in the private sector. Reporting a single "effect of experience" would describe neither.
</div>

### Rules once an interaction is in the model

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Three things that change</span>

1. **b&#8321; is no longer a main effect.** It is the effect of hours **at the reference level** of group. Interpreting it as an overall effect is wrong.
2. **Always keep the lower-order terms.** A model with X&times;W but without X and W is almost never interpretable.
3. **Centre continuous predictors** before forming the product, or you get artificial collinearity and an uninterpretable b&#8321;.
</div>

## Simple slopes

A significant b&#8323; says slopes differ. It does not say what each slope is, or whether each is significantly different from zero.

**Simple slopes analysis** computes the effect of X at specific values of the moderator -- typically the mean and &plusmn;1 SD for a continuous moderator, or at each level of a categorical one.

```
Simple slopes for hours:
  Public sector  : b = 1,200,  SE = 180,  t = 6.67,  p < .001
  Private sector : b = 2,050,  SE = 210,  t = 9.76,  p < .001
```

Both significant, and the interaction tells you they differ from each other. **Plot it** -- two lines with visibly different gradients is far more convincing to a panel than a coefficient.

## Comparing whole models across groups

Sometimes you want to know whether the **entire** model differs -- the Chow test.

1. Fit the model separately in each group
2. Fit one pooled model with all interactions
3. Compare with an F test

If significant, the groups need separate models rather than one model with a few interactions.

## Doing it in software

### Jamovi
Enter the categorical variable as a **Factor**, not a Covariate, and Jamovi builds the dummies automatically.
- **Linear Regression** &rarr; put the grouping variable in **Factors**
- Under **Reference Levels**, choose which category is the reference
- Under **Model Builder**, add the interaction by selecting both terms and choosing the interaction arrow
- Under **Estimated Marginal Means**, tick **Marginal means plots** to get the interaction plot

### SPSS
SPSS's Linear Regression dialog does **not** create dummies for you. Either:
- Use <kbd>Transform</kbd> &rarr; <kbd>Recode into Different Variables</kbd> to build them by hand, or
- Use <kbd>Analyze</kbd> &rarr; <kbd>General Linear Model</kbd> &rarr; <kbd>Univariate</kbd>, which handles factors automatically and offers **Parameter estimates** under Options

### R
```r
dat$strand <- factor(dat$strand)
dat$strand <- relevel(dat$strand, ref = "STEM")    # set the reference

m <- lm(score ~ strand, data = dat)
summary(m)
#   strandABM     -8.25    1.968   -4.19   0.00042
#   strandHUMSS  -10.50    1.968   -5.34   0.00003
anova(m)        # identical to the one-way ANOVA: F(2,21) = 15.77

# interaction
dat$hours_c <- scale(dat$hours, scale = FALSE)
mi <- lm(salary ~ hours_c * sector, data = dat)
summary(mi)     # the hours_c:sector row is the interaction

library(interactions)
sim_slopes(mi, pred = hours_c, modx = sector)
interact_plot(mi, pred = hours_c, modx = sector)
```

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- dummy variables</span>
*Strand* was dummy-coded with *STEM* as the reference category. Relative to *STEM* students, *ABM* students scored *8.25* points lower (*b* = *&minus;8.25*, *SE* = *1.97*, *p* &lt; *.001*) and *HUMSS* students *10.50* points lower (*b* = *&minus;10.50*, *SE* = *1.97*, *p* &lt; *.001*). The model accounted for *60.0%* of the variance, *F*(*2*, *21*) = *15.77*, *p* &lt; *.001*.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- interaction</span>
The interaction between *experience* and *sector* was significant, *b* = *850*, *SE* = *276*, *t* = *3.08*, *p* = *.003*, &Delta;*R&sup2;* = *.04*. Simple slopes analysis indicated that experience predicted salary in both sectors, but more strongly in the *private* sector (*b* = *2,050*, *p* &lt; *.001*) than in the *public* sector (*b* = *1,200*, *p* &lt; *.001*).
</div>

## Common mistakes

- **Entering a nominal variable as continuous.**
- **Creating k dummies instead of k &minus; 1.**
- **Not stating the reference category.**
- **Interpreting b&#8321; as a main effect** when its interaction is in the model.
- **Removing a main effect but keeping its interaction.**
- **Not centring before forming the product term.**
- **Reporting a significant interaction with no simple slopes and no plot.**

## Practice

**1.** A variable has five categories. How many dummies, and what does each coefficient mean?

<details markdown="1">
<summary>Show the worked answer</summary>

**Four dummies** (k &minus; 1 = 5 &minus; 1 = 4), with one category left out as the reference.

```
Category    D1  D2  D3  D4
A (ref)      0   0   0   0
B            1   0   0   0
C            0   1   0   0
D            0   0   1   0
E            0   0   0   1
```

Each coefficient is the difference between **that category and the reference**:

```
b1 = mean(B) - mean(A)
b2 = mean(C) - mean(A)
b3 = mean(D) - mean(A)
b4 = mean(E) - mean(A)
```

**What the coefficients do NOT tell you:** whether B differs from C. The model never compares them directly. For that you need either a different reference category, a post-hoc test, or a planned contrast.

**Why only four:** with an intercept in the model, five dummies would be perfectly collinear — they sum to 1 for every case, which duplicates the intercept column. The model becomes unsolvable.

**Degrees of freedom:** the four dummies consume 4 df, matching the k &minus; 1 = 4 df between groups in the equivalent one-way ANOVA. The two analyses are the same procedure.
</details>

**2.** Your model has `hours`, `group` and `hours × group`. The coefficient for `hours` is 1.2 and non-significant. Does hours not matter?

<details markdown="1">
<summary>Show the answer</summary>

**You cannot conclude that. With the interaction in the model, b(hours) is not an overall effect.**

**What it actually is:** the slope of hours **for the reference group only** — the group coded 0. It says nothing about the other group, and nothing about hours overall.

**Why it might be non-significant while hours clearly matters:**

- The effect may be genuinely near zero *in the reference group* while being strong in the other. If b&#8323; = 2.8, the other group's slope is 1.2 + 2.8 = 4.0, which could be highly significant.
- With the interaction present, b&#8321; is estimated from only part of the data, so it has a larger standard error.

**What to do:**

1. **Look at b&#8323; first.** If the interaction is significant, the effect of hours differs by group and no single number describes it.
2. **Compute simple slopes** for each group, with their own standard errors and p-values.
3. **Plot it.**

**If the interaction is NOT significant**, drop it and refit. Then b&#8321; becomes a proper main effect and is interpretable as the overall effect of hours.

**How to report:**

> The interaction was significant (*b* = 2.80, *p* = .004). Simple slopes indicated that hours did not predict the outcome in the reference group (*b* = 1.20, *p* = .21) but did so strongly in the comparison group (*b* = 4.00, *p* < .001).

That is a substantive finding — the relationship exists only in one group — which the single non-significant coefficient completely hid.
</details>

**3.** Why does changing the reference category change all your coefficients but not your R-squared?

<details markdown="1">
<summary>Show the answer</summary>

**Because the coefficients are comparisons, and you changed what they are compared to. The model's fitted values never moved.**

**What changes:** every coefficient is "this category minus the reference." Switch the reference from STEM to HUMSS and the same three group means produce a different set of differences:

```
Reference STEM:            Reference HUMSS:
  b(ABM)   = -8.25           b(STEM) = +10.50
  b(HUMSS) = -10.50          b(ABM)  =  +2.25
  intercept = 84.00          intercept = 73.50
```

**What does not change:**

- The **predicted value** for any case. STEM is still predicted at 84.00 either way.
- **R-squared**, the overall F, the residuals, the standard error of the estimate.
- Which groups differ **substantively**.

**Why:** the set of dummy variables spans the same space regardless of which one you omit. You are re-describing the same fitted model in a different set of coordinates — like giving directions from a different landmark.

**Practical consequences:**

1. **Choose the reference deliberately** — the control, the largest group, or the literature's baseline.
2. **Always state it.** A coefficient of &minus;8.25 is meaningless without knowing what it is measured against.
3. **Use it deliberately.** If you need the ABM-versus-HUMSS comparison and neither is the reference, re-run with one of them as reference. That comparison then appears directly, with its own p-value — often simpler than a post-hoc test.
</details>

## Before you move on

- [ ] I create k &minus; 1 dummies and can say why not k
- [ ] I always state the reference category
- [ ] I know regression with dummies is the same procedure as ANOVA
- [ ] I interpret b&#8321; as conditional when its interaction is in the model
- [ ] I centre continuous predictors before forming interaction terms
- [ ] I follow a significant interaction with simple slopes and a plot

Next: the references, all free.""",
    [{"question": "A categorical variable has 4 categories. How many dummy variables does a model with an intercept need?",
      "choices": ["4", "3", "2", "5"], "correct": 1},
     {"question": "With an interaction term in the model, the coefficient b1 for X represents:",
      "choices": ["The overall effect of X", "The effect of X at the reference level of the moderator",
                  "The average of both groups' slopes", "The interaction itself"], "correct": 1}],
)


# ===========================================================================
L(
    "Further Reading (Free & Open)",
    """## How to use this page

Regression rewards depth over breadth. Work one book properly.

## The core references

- **Draper, N.R. and Smith, H. -- *Applied Regression Analysis*** (Wiley). Named in CMO 42 Annex B for Regression Analysis. The standard technical reference.
- **Chatterjee, S., Hadi, A.S. and Price, B. -- *Regression Analysis by Example*** (Wiley). Also named in CMO 42, and far more approachable. Every method is introduced through a worked dataset.
- **Fox, J. -- *Applied Regression Analysis and Generalized Linear Models***. The best modern treatment of diagnostics. Fox also wrote the R `car` package used throughout this course.

## Free and open

- **Introduction to Modern Statistics** -- openintro.org. Free PDF, full chapters on regression and logistic regression, with labs.
- **An Introduction to Statistical Learning (ISLR)** -- statlearning.com. **Free PDF of the whole book.** Chapters 3 (linear regression), 4 (logistic), and 6 (ridge and LASSO) are directly relevant, and it is the clearest treatment of shrinkage in print.
- **Regression and Other Stories** -- Gelman, Hill and Vehtari. Free PDF from the authors' site. Outstanding on interpretation and on what regression cannot do.
- **MIT OpenCourseWare 15.075, *Statistical Thinking and Data Analysis***. Full notes and problem sets.
- **UCLA IDRE statistical consulting** -- stats.oarc.ucla.edu. Worked examples for every method here in SPSS, R, Stata and SAS. The single most useful free site for "how do I actually run this?"

## For factor analysis

- **Costello, A.B. and Osborne, J.W. (2005). Best practices in exploratory factor analysis.** *Practical Assessment, Research and Evaluation, 10*(7). Free, short, and the paper to cite for why you used oblique rotation and parallel analysis.
- **The `psych` package documentation** by William Revelle. Free, and includes a full tutorial on EFA.

## Free software

| Tool | Best for |
|---|---|
| **jamovi** | Everything here; best defaults for EFA and the friendliest output |
| **JASP** | Same, plus Bayesian regression |
| **R + RStudio** | `car`, `psych`, `effectsize`, `glmnet`, `interactions` |
| **PSPP** | SPSS-like interface, free |
| **G*Power** | Sample size for regression and ANOVA |

## Key R packages for this course

```r
install.packages(c("car",          # VIF, diagnostics, Levene
                   "psych",        # factor analysis, reliability
                   "effectsize",   # Cohen's d, eta-squared with CIs
                   "lmtest",       # Breusch-Pagan, coeftest
                   "sandwich",     # robust standard errors
                   "interactions", # simple slopes and plots
                   "glmnet",       # ridge and LASSO
                   "performance")) # check_model(), one-line diagnostics
```

`performance::check_model(m)` produces every regression diagnostic in one annotated panel. It is the fastest way to check a model properly.

## Philippine data to practise on

- **PSA Data Archive** -- microdata from the Labour Force Survey and FIES. Real predictors, real skew, real missingness.
- **PSA OpenSTAT** -- aggregate series across every sector.
- **data.gov.ph** -- the national open data portal.

Regression on clean textbook data teaches the arithmetic. Regression on LFS microdata teaches the job.

## Keeping the skill

1. **Re-derive.** Close the page and compute b&#8321; from Sxy and Sxx.
2. **Always plot before you interpret.** `plot(m)` or `check_model(m)`.
3. **Explain a coefficient out loud**, including "holding the others constant." If you stumble, you are not ready to defend it.

## Where to go next in this catalogue

| If you want to... | Take |
|---|---|
| Run a real experiment with randomisation | **Design & Analysis of Experiments** |
| Handle ordinal or non-normal outcomes | **Nonparametric Statistics** |
| Do SEM, PLS-SEM or survival analysis | **Advanced Statistics** |
| Model data collected over time | **Time Series Analysis & Forecasting** |
| Understand the theory beneath all of it | **Probability & Mathematical Statistics** |
| Move to prediction and machine learning | **AI & Machine Learning for Practitioners** |""",
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
