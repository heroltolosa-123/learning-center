"""
Rewrites Design & Analysis of Experiments at teaching depth.

Every ANOVA table below was computed with statsmodels/scipy before it was
written into a lesson, and the lessons were checked back against this list.

  CRD  4 treatments x 5 reps
    A 21,19,22,20,23 (105, 21.0)   B 26,28,25,27,24 (130, 26.0)
    C 31,29,33,30,32 (155, 31.0)   D 24,22,25,23,26 (120, 24.0)
    G = 510, N = 20, CF = 13005, sum of squares = 13310
    TSS 305, SS(treat) 265, SSE 40
    MST 88.3333, MSE 2.5, F(3,16) = 35.3333, p = 2.75e-07
    eta-squared .8689, omega-squared .8374, CV = 6.20%
    LSD(.05) = 2.1199, Tukey HSD = 2.8638
    Tukey: A-B .0007, A-C <.0001, A-D .0382, B-C .0007, B-D .2288, C-D <.0001

  RCBD  4 treatments x 4 blocks
    rows = blocks: [23,27,34,24] [19,27,29,24] [25,31,34,28] [20,26,33,23]
    treatment totals 87/111/130/99 -> means 21.75/27.75/32.50/24.75
    block totals 108/99/118/102
    G = 427, CF = 11395.5625, sum of squares = 11717
    TSS 321.4375, SS(treat) 252.1875, SS(block) 52.6875, SSE 16.5625
    MSE 1.8403 (df 9), F(treat) = 45.6792 p = 9.03e-06
    F(block) = 9.5434 p = .0037, relative efficiency vs CRD = 2.709
    CV 5.08%, LSD 2.1699, Tukey HSD 2.9946
    Same data analysed as a CRD: SSE 69.25 (df 12), MSE 5.7708,
      F = 14.5668 p = .000265  -- the cost of ignoring the blocks

  LATIN SQUARE  4x4
    [[23,31,36,28],[29,35,28,19],[34,27,20,30],[28,19,30,35]]
    G = 452, CF = 12769, sum of squares = 13236
    treatment means A 20.25, B 30.00, C 35.00, D 27.75
    TSS 467, SS(row) 8.5, SS(col) 1.0, SS(treat) 451.5, SSE 6.0 (df 6)
    MSE 1.0, F(treat) = 150.5 p < .0001
    F(row) = 2.8333 p = .1285, F(col) = 0.3333 p = .8022
    LSD 1.7302, CV 3.54%

  2x3 FACTORIAL  n = 4 per cell
    cell means      M1     M2     M3
      Low         13.0   19.0   23.0
      High        21.0   24.0   25.0
    A marginal 18.3333 / 23.3333;  B marginal 17.0 / 21.5 / 24.0
    G = 500, N = 24, CF = 10416.6667, TSS 399.3333
    SS(A) 150 F(1,18) = 225;  SS(B) 201.3333 F(2,18) = 151
    SS(AxB) 36 F(2,18) = 27 p = 3.81e-06;  SSE 12, MSE 0.6667
    partial eta-squared: A .926, B .944, AxB .750

  SPLIT-PLOT  2 irrigation (whole) x 3 variety (sub) x 4 blocks
    G = 869.6, N = 24, CF = 31508.5067, TSS 582.5133
    SS(block) 42.89, SS(irr) 238.14, SS(error A) 21.49
    SS(var) 252.2433, SS(irr x var) 14.43, SS(error B) 13.32
    MS(error A) 7.1633 (df 3), MS(error B) 1.11 (df 12)
    F(irr) = 33.2443 df(1,3) p = .0104   <- against error A
    F(var) = 113.6231 df(2,12) p < .0001 <- against error B
    F(irr x var) = 6.50 df(2,12) p = .0122
    Pooling the two errors (wrong) gives MS 2.3207 and F(irr) = 102.62
    SE of a whole-plot mean difference 1.0927; of a sub-plot difference .5268

  ANCOVA  3 methods, pretest covariate
    M1 xbar 43.8333 ybar 57.3333;  M2 43.50 / 61.6667;  M3 43.6667 / 70.1667
    grand x 43.6667, grand y 63.0556
    plain ANOVA on y: F(2,15) = 6.9301 p = .0074, MSE 36.90
    slope homogeneity: F(2,12) = 2.6243 p = .1134  (slopes parallel, OK)
    ANCOVA: F(2,14) = 35.4497 p = 3.0e-06, MSE 7.3902
    pooled within-group slope b = 1.3819, t = 7.804
    adjusted means 57.1030 / 61.8970 / 70.1667
    partial eta-squared for method = .8351

Safe to re-run. Lessons are matched by title and replaced in place.

Usage:
    python3 seed_deep_doe.py
"""
import json
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal, sync_columns
from app import models

COURSE_SLUG = "design-analysis-experiments"
LESSONS = []


def L(title, content, quiz=None, preview=False):
    LESSONS.append({"title": title, "content": content, "quiz": quiz, "preview": preview})


# ===========================================================================
L(
    "The Three Principles of Experimentation",
    """## What you will be able to do

Explain -- and defend to a panel -- why an experiment needs randomisation, replication and local control, and recognise when a study that calls itself an experiment is actually none of the three.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
A candidate wants to test whether a new teaching method raises scores. She teaches Method A to her 7 a.m. section and Method B to her 1 p.m. section, then compares the two means with a t-test. Method B wins, *p* = .03.

The panel asks: "Is that the method, or is it the time of day?"

She cannot answer, and no statistical technique can rescue her. The design, not the analysis, is what failed.
</div>

This is **confounding**: the method and the time slot change together, so their effects cannot be separated. The three principles in this lesson exist to prevent exactly this.

## Principle 1: Randomisation

**Assign treatments to experimental units by a chance mechanism, not by judgement, convenience, or order of arrival.**

### Why it works

There are two reasons, and the second is the one students usually miss.

**It balances what you did not measure.** Suppose motivation affects scores and you cannot measure it. If you assign treatments at random, highly motivated students have an equal chance of landing in either group, so motivation is spread across groups up to chance. It balances *every* lurking variable at once -- including the ones you have never thought of. No amount of statistical control can do that, because you can only control for variables you measured.

**It is what makes the *p*-value mean anything.** This is the deeper point. A *p*-value is the probability of a result this extreme *if the treatment did nothing*. That probability is computed over the set of assignments that *could* have happened. If assignment was not random, there is no such set, and the reference distribution the *p*-value is computed against does not exist.

<div class="callout callout-note" markdown="1">
<span class="callout-label">The sentence worth memorising</span>
**Randomisation does not make the groups equal. It makes the *differences between them* behave like chance -- which is precisely what every statistical test assumes.**

With *n* = 10 per group, a single random assignment may well leave one group more able than the other. Randomisation does not prevent that. What it guarantees is that the imbalance is random rather than systematic, so the sampling distribution your test refers to is the right one.
</div>

### How to actually do it

**Not** this: alternating A, B, A, B as students walk in. Not drawing names from a hat you can feel through. Not "I'll put the weaker students in the treatment group so they benefit."

Do this:

```r
# 20 units, 4 treatments, 5 replications each
set.seed(2026)
assign <- sample(rep(c("A","B","C","D"), each = 5))
data.frame(unit = 1:20, treatment = assign)
```

In Excel: put `=RAND()` beside each unit, sort by that column, then assign the first 5 to A, the next 5 to B, and so on. Copy the random numbers as values first, or sorting will re-randomise them under you.

**Record the seed or keep the assignment sheet.** A panel can and does ask to see it.

## Principle 2: Replication

**Each treatment must be applied to more than one independent experimental unit.**

### What replication buys you

Without it you cannot estimate experimental error, and without that you have no denominator for any *F* or *t* statistic. One plot per treatment gives you four numbers and no way to know whether a difference of 3 units is large or trivial.

### The distinction that sinks theses: replication vs repeated measurement

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Pseudoreplication</span>
A researcher has **one** tank of fish per treatment, with 20 fish in each tank, and analyses *n* = 20 per treatment.

Her *n* is **1**, not 20. The treatment was applied to the tank, so the tank is the experimental unit. The 20 fish are *subsamples* of one unit -- repeated measurements, not replicates. Analysing them as 20 independent observations treats within-tank variation as if it were between-tank variation, which understates the standard error dramatically and inflates every *F*.

The test: **ask what the treatment was applied to.** That thing is the experimental unit, and the number of those is your *n*. One tank per treatment means one replicate per treatment, and the experiment cannot be analysed.
</div>

The same error in education research: one class per method, 40 students per class, analysed as *n* = 40. The method was assigned to the *class*. Students within a class share a teacher, a timetable and each other. The honest *n* is the number of classes.

### How much replication?

Power analysis answers this, and it needs three inputs: the smallest effect worth detecting, the error variance (from a pilot or from published work), and your target power (conventionally .80).

```r
# detecting an effect of size f = 0.40 across 4 groups, power .80
pwr::pwr.anova.test(k = 4, f = 0.40, sig.level = 0.05, power = 0.80)
#  n = 18.04 per group
```

A rough field rule for agricultural and educational trials: aim for at least **10-12 error degrees of freedom**. Below that, *F* critical values climb steeply and the experiment is unlikely to detect anything. Our CRD example in the next lesson has 16 error df -- comfortable. The Latin square has 6 -- tight.

## Principle 3: Local control (blocking)

**Group the experimental units into blocks that are internally similar, then randomise treatments within each block.**

### Why it works

Error variance is what your *F* test divides by. Anything you can remove from it makes the test more sensitive.

Suppose a field slopes, so the lower end is wetter. In a completely randomised design that moisture gradient goes straight into experimental error. Block the field into four strips across the slope, each internally uniform, and the strip-to-strip variation is pulled out as a separate source. What remains in the error term is only within-strip noise.

### The proof, from real numbers

The next two lessons use a dataset of 4 treatments in 4 blocks. Here is what blocking did to it:

| Analysis | SSE | df | MSE | F(treatment) | p |
|---|---|---|---|---|---|
| As a blocked design (RCBD) | 16.56 | 9 | **1.84** | **45.68** | .0000090 |
| Same data, blocks ignored (CRD) | 69.25 | 12 | **5.77** | **14.57** | .00027 |

Ignoring the blocks leaves 52.69 units of block-to-block variation sitting inside the error term. The MSE triples, and *F* falls from 45.68 to 14.57.

Both analyses reject here, because the treatment effect is large. With a smaller effect, the CRD analysis would have missed it entirely. **Blocking is free power.**

The formal measure is **relative efficiency**:

<div class="formula" markdown="1">
**RE = [ (b&minus;1)MS&#8342; + b(t&minus;1)MSE ] / [ (bt&minus;1) MSE ]**
<span class="formula-note">how many CRD replications it would take to match this blocked design</span>
</div>

For this data RE = **2.709**. The blocked experiment with 4 replications is worth about 10.8 CRD replications. You bought nearly three times the experiment for the cost of recording which strip each plot was in.

<div class="callout callout-note" markdown="1">
<span class="callout-label">Block what varies, randomise what you cannot block</span>
That phrase is the whole design philosophy.

**Block** the nuisance factors you can identify and group by: field position, day of testing, batch of material, operator, litter, school. The requirement is that units within a block are similar *and* that every treatment appears in every block.

**Randomise** within blocks, which handles everything you did not or could not block.

Those two together are why a well-designed experiment supports causal claims that no observational study can.
</div>

## Putting the three together: fixing the scenario

The candidate's study fails all three.

| Principle | Status | Fix |
|---|---|---|
| Randomisation | None -- method assigned by class schedule | Randomise students to method within each time slot |
| Replication | *n* = 1 per method (one class each) | Run several sections per method, or randomise individuals |
| Local control | None -- time of day confounded with method | **Block on time slot**; both methods in every slot |

The repaired design: within the 7 a.m. section, randomly assign half the students to each method; do the same at 1 p.m. Time slot becomes a block, both methods appear in both blocks, and assignment within each is random. Now the method effect is estimable, the time-of-day effect is removed from error, and the *p*-value refers to a real reference distribution.

## The vocabulary, precisely

| Term | Definition | In the scenario |
|---|---|---|
| **Experimental unit** | The smallest thing a treatment is independently applied to | A student (after the fix); the class (before) |
| **Observational unit** | The thing measured | A student |
| **Treatment** | A specific condition applied | Method A or Method B |
| **Factor** | A variable whose levels are the treatments | Teaching method |
| **Level** | One value of a factor | Method A |
| **Response** | What you measure | Test score |
| **Block** | A group of similar units | Time slot |
| **Experimental error** | Variation among units receiving the same treatment | Student-to-student differences within a method |

**The experimental unit and the observational unit are the same thing only sometimes.** When they differ -- one tank, twenty fish; one class, forty students -- the analysis must be at the level of the experimental unit, or you have pseudoreplication.

## Doing it in software

**Randomisation in R:**

```r
set.seed(2026)

# CRD: 4 treatments, 5 reps
sample(rep(LETTERS[1:4], each = 5))

# RCBD: randomise within each block
blocks <- 4
do.call(rbind, lapply(1:blocks, function(b)
  data.frame(block = b, plot = 1:4,
             treatment = sample(LETTERS[1:4]))))

# the agricolae package generates and prints field layouts
library(agricolae)
design.crd(trt = c("A","B","C","D"), r = 5, seed = 2026)$book
design.rcbd(trt = c("A","B","C","D"), r = 4, seed = 2026)$book
design.lsd(trt = c("A","B","C","D"), seed = 2026)$book
```

`agricolae` is the package for this whole course -- it generates designs, prints field books, and runs the matching ANOVA with LSD, Duncan, Tukey and Scheffe comparisons.

**Power in R or Jamovi:**

```r
pwr::pwr.anova.test(k = 4, f = 0.40, sig.level = .05, power = .80)
```

Jamovi: install the **jpower** module, then Analyses -> jpower -> Independent Samples T-Test for the two-group case. For ANOVA power, use R via the Rj module, or G*Power (free, gpower.hhu.de).

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Methods paragraph that satisfies a panel</span>
"The experiment used a randomised complete block design with four treatments and four blocks (*n* = 16 plots). Blocks were defined by position along the field's moisture gradient, with each block comprising four adjacent plots of uniform elevation. Treatments were allocated to plots within each block using a pseudo-random number generator (R 4.4.1, `sample()`, seed 2026); the allocation sheet is in Appendix C. The plot was the experimental unit. Sample size was set to give 9 error degrees of freedom, sufficient to detect a treatment difference of 3 units at alpha = .05 with power .80 given the error variance of 2.1 reported by [pilot study]."
</div>

Four things that paragraph does, each of which a panel will look for: it names the design, defines the blocks and says why, states the randomisation mechanism reproducibly, and identifies the experimental unit.

## Common mistakes

1. **Assigning treatments by convenience and calling it an experiment.** Without randomisation there is no causal claim and no valid *p*-value.
2. **Pseudoreplication.** Counting subsamples as replicates. Ask what the treatment was applied to.
3. **Blocking on something that does not vary.** If blocks are no more homogeneous than the whole field, you have spent error degrees of freedom for nothing.
4. **Blocking on a variable you want to study.** If time of day is of interest, it is a factor, not a block -- and then you need a factorial design.
5. **Incomplete blocks without the right design.** Every treatment must appear in every block for an RCBD. If it cannot, you need a balanced incomplete block design, which is a different analysis.
6. **Too few error degrees of freedom.** Below about 10, critical *F* values are so large that only huge effects are detectable.
7. **Randomising once and reusing the layout.** Each experiment gets a fresh randomisation.

## Practice

<details markdown="1">
<summary>1. A researcher applies three fertiliser rates to three greenhouses, one rate per greenhouse, and measures 30 plants in each. What is n, and what can be concluded?</summary>

*n* = **1 per treatment**. The fertiliser was applied to the greenhouse, so the greenhouse is the experimental unit. The 30 plants are subsamples.

With one unit per treatment there are **zero error degrees of freedom** -- no replication means no estimate of experimental error, and therefore no valid *F* test. Any greenhouse difference (temperature, light, a leak) is completely confounded with its fertiliser rate.

Nothing can be concluded about fertiliser. The analysis cannot be fixed; the design must be.

**The repair:** apply each rate to several greenhouses (at least 3-4 each, giving 6-9 error df), or -- if only three greenhouses exist -- randomise rates to *benches within* each greenhouse and block on greenhouse. The second option is usually feasible and turns a dead experiment into a sound RCBD.
</details>

<details markdown="1">
<summary>2. Why does randomisation matter even when you have measured and can adjust for every covariate you care about?</summary>

Because you can only adjust for what you measured, and the variables that matter most are often the ones you did not think of.

Suppose you randomise and also measure pretest score, motivation and attendance. Adjusting for those (see the ANCOVA lesson) increases precision -- good. But randomisation is what protects you from the covariate nobody recorded: a family crisis, a change in sleep, prior exposure to the material.

There is also the inferential point. Even with perfect covariate balance, a non-randomised comparison has no reference distribution for the *p*-value. Randomisation generates it. This is why the randomisation test -- shuffling the treatment labels and recomputing the statistic -- is the logical foundation of the *F* test, and why that foundation is simply absent when assignment was not random.
</details>

<details markdown="1">
<summary>3. Your blocking variable turns out to have F(block) = 0.42, p = .74. Did you waste the blocking?</summary>

You spent degrees of freedom for little return, but the answer is more nuanced than "yes".

**What happened:** the blocks were not more homogeneous than the field as a whole. With 4 blocks you moved 3 df from error to blocks and got almost no sum of squares in exchange, so MSE is slightly *higher* than a CRD's would have been and your test is marginally less powerful.

**Why it is not a real mistake:** you did not know in advance. Blocking is insurance. A non-significant block effect means the premium was wasted on this occasion; it does not mean buying insurance was wrong.

**What NOT to do:** drop the block term and re-analyse as a CRD. You randomised *within* blocks, so the randomisation structure includes them. Removing the term misrepresents how the experiment was run, and it is a form of analysing until you like the answer. Report the design you ran. One sentence -- "the block effect was not significant, *F*(3, 9) = 0.42, *p* = .74" -- is the honest treatment.

**What to do next time:** block on something that actually varies. Pick the blocking variable from pilot data or from knowledge of the site, not from habit.
</details>

<details markdown="1">
<summary>4. A relative efficiency of 2.71 — what does that mean in practical terms?</summary>

It means this blocked design with 4 replications gives the same precision as a completely randomised design with about **4 x 2.71 = 10.8 replications**.

Concretely: to match this experiment with a CRD you would need roughly 11 plots per treatment instead of 4 -- 44 plots rather than 16. Blocking bought you 28 plots' worth of information for the cost of recording a strip number.

That is why RE is worth computing and reporting. It converts an abstract design choice into a number the reader can price. It is also the argument to make when a supervisor says blocking is a needless complication.
</details>

## Before you move on

- [ ] I can state the two reasons randomisation matters, including the one about the reference distribution.
- [ ] I can identify the experimental unit by asking what the treatment was applied to.
- [ ] I can recognise pseudoreplication in a described study.
- [ ] I can explain blocking as removing identified variation from the error term.
- [ ] I can compute and interpret relative efficiency.
- [ ] I know why you do not drop a non-significant block term.
- [ ] I can write a methods paragraph that names the design, the blocks, the randomisation mechanism and the experimental unit.""",
    quiz={
        "question": "Three diets are each fed to one pen of 25 pigs, and the researcher analyses n = 25 per diet. What is wrong?",
        "options": [
            "Nothing; 25 pigs per diet is adequate replication",
            "The diet was applied to the pen, so n = 1 per treatment — the 25 pigs are subsamples and there are no error degrees of freedom",
            "The sample size is too large for ANOVA",
            "The pigs should have been blocked by weight",
        ],
        "answer": 1,
        "explanation": "The experimental unit is whatever the treatment was independently applied to — here the pen. With one pen per diet there is no replication, no estimate of experimental error, and pen effects are fully confounded with diet. This is pseudoreplication.",
    },
    preview=True,
)


# ===========================================================================
L(
    "Completely Randomized Design",
    """## What you will be able to do

Build a one-way ANOVA table by hand from raw data -- correction factor, total, treatment and error sums of squares -- get the same numbers your software gets, check the assumptions on the residuals, and follow it with the right mean comparison.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
Twenty uniform plots in a flat, homogeneous field. Four fertiliser treatments, five plots each, assigned completely at random. Yield in kg:

| Treatment | Observations | Total | Mean |
|---|---|---|---|
| A | 21, 19, 22, 20, 23 | 105 | 21.0 |
| B | 26, 28, 25, 27, 24 | 130 | 26.0 |
| C | 31, 29, 33, 30, 32 | 155 | 31.0 |
| D | 24, 22, 25, 23, 26 | 120 | 24.0 |
| **Grand** | | **510** | **25.5** |

The field is uniform, so there is nothing to block on. A CRD is the right design -- the simplest one, and the one every other design in this course is built from.
</div>

## When a CRD is the right choice

| Use a CRD when | Use something else when |
|---|---|
| Units are homogeneous | A known gradient or grouping exists (&rarr; RCBD) |
| Two nuisance factors cross (&rarr; Latin square) |
| You want maximum error df for a given *n* | Units differ in a way you can measure (&rarr; ANCOVA) |
| Unequal replication is unavoidable | |

The CRD's two real advantages: it tolerates **unequal replication** without any complication, and it gives the **most error degrees of freedom** of any design for a given number of units -- because it spends none on blocks. Its one disadvantage is the whole reason the other designs exist: every bit of unit-to-unit variation lands in the error term.

## The model

<div class="formula" markdown="1">
**Y&#7522;&#11388; = &mu; + &tau;&#7522; + &epsilon;&#7522;&#11388;**
<span class="formula-note">observation = grand mean + effect of treatment i + random error</span>
</div>

Every observation is decomposed into three pieces. ANOVA estimates how much of the total variation each piece accounts for, then asks whether the treatment piece is big relative to the error piece.

- **&mu;** -- the overall mean, 25.5 here.
- **&tau;&#7522;** -- how far treatment *i* pushes the response away from &mu;. For treatment A, 21.0 &minus; 25.5 = &minus;4.5.
- **&epsilon;&#7522;&#11388;** -- what is left over for unit *j*: assumed independent, normal, mean zero, and with the **same variance in every treatment**.

The null hypothesis is &tau;&#8321; = &tau;&#8322; = &tau;&#8323; = &tau;&#8324; = 0.

## Working the ANOVA table by hand

The whole computation runs on three quantities: the grand total, the treatment totals, and the sum of every squared observation.

**Step 1. The correction factor.**

<div class="formula" markdown="1">
**CF = G&#178; / N**
<span class="formula-note">G = grand total, N = total number of observations</span>
</div>

```
CF = 510^2 / 20 = 260100/20 = 13005
```

The correction factor is what converts "sum of squares about zero" into "sum of squares about the mean". Every sum of squares below subtracts it.

**Step 2. Total sum of squares.**

```
sum of all squared observations:
  A: 441 + 361 + 484 + 400 + 529 = 2215
  B: 676 + 784 + 625 + 729 + 576 = 3390
  C: 961 + 841 + 1089 + 900 + 1024 = 4815
  D: 576 + 484 + 625 + 529 + 676 = 2890
                            total = 13310

TSS = 13310 - 13005 = 305
```

**Step 3. Treatment sum of squares.**

<div class="formula" markdown="1">
**SS(treatment) = &Sigma;(T&#7522;&#178; / n&#7522;) &minus; CF**
<span class="formula-note">T&#7522; = total for treatment i, n&#7522; = its replication; works with unequal n&#7522;</span>
</div>

```
SS(treat) = 105^2/5 + 130^2/5 + 155^2/5 + 120^2/5 - 13005
          = 11025/5 + 16900/5 + 24025/5 + 14400/5 - 13005
          = 2205 + 3380 + 4805 + 2880 - 13005
          = 13270 - 13005
          = 265
```

**Step 4. Error sum of squares, by subtraction.**

```
SSE = TSS - SS(treat) = 305 - 265 = 40
```

Subtraction is how it is done in practice, but it is worth knowing SSE is also the direct sum of squared deviations within each treatment. Check treatment A: deviations from 21.0 are 0, &minus;2, 1, &minus;1, 2, so squares are 0 + 4 + 1 + 1 + 4 = 10. Each treatment here contributes exactly 10, so SSE = 40. &#10003;

**Step 5. The ANOVA table.**

| Source | SS | df | MS | F | p |
|---|---|---|---|---|---|
| Treatment | 265 | 3 | 88.3333 | **35.3333** | **2.75e-07** |
| Error | 40 | 16 | 2.5000 | | |
| **Total** | **305** | **19** | | | |

Degrees of freedom: treatment = *k* &minus; 1 = 3; total = *N* &minus; 1 = 19; error = *N* &minus; *k* = 16, or by subtraction 19 &minus; 3.

```
MS(treat) = 265/3 = 88.3333
MSE       = 40/16 = 2.5
F         = 88.3333/2.5 = 35.3333
```

Critical *F*(3, 16) at alpha = .05 is 3.24. Our 35.33 is ten times that. **Reject H&#8320;.**

<div class="callout callout-note" markdown="1">
<span class="callout-label">What F actually compares</span>
MSE estimates the error variance, always -- whether or not the treatments differ.

MS(treatment) estimates the error variance **plus** a term for the spread of the true treatment effects. Under H&#8320; that extra term is zero, so both mean squares estimate the same thing and *F* should be near 1.

So *F* = 35.33 says the treatment mean square is 35 times larger than error alone can explain. That is the entire logic of the *F* test, and it is why the test is one-tailed: only *large* values of *F* are evidence against the null.
</div>

## Effect size and the quality check every field report carries

**Eta-squared** -- proportion of total variation attributable to treatment:

```
eta-squared = SS(treat)/TSS = 265/305 = .8689
```

**Omega-squared** -- a less biased version, which is why journals increasingly ask for it:

<div class="formula" markdown="1">
**omega&#178; = [ SS(treat) &minus; (k&minus;1)MSE ] / [ TSS + MSE ]**
</div>

```
omega-squared = (265 - 3 x 2.5) / (305 + 2.5)
              = (265 - 7.5) / 307.5
              = 257.5/307.5
              = .8374
```

Eta-squared always overestimates; the gap closes as *n* grows. At *n* = 20 it is .8689 against .8374.

**Coefficient of variation** -- the standard quality check in agricultural and industrial reports:

<div class="formula" markdown="1">
**CV% = 100 x &radic;MSE / grand mean**
</div>

```
CV% = 100 x sqrt(2.5)/25.5 = 100 x 1.5811/25.5 = 6.20%
```

Rough guidance for field trials: under 10% is good control, 10-20% acceptable, above 20% means something went wrong in execution. A journal in agronomy will expect to see this number.

## Checking the assumptions -- on the residuals

ANOVA assumes the errors are independent, normally distributed, and equal in variance across treatments. All three are checked on the **residuals**, which here are simply each observation minus its own treatment mean.

| Treatment | Residuals |
|---|---|
| A | 0, &minus;2, 1, &minus;1, 2 |
| B | 0, 2, &minus;1, 1, &minus;2 |
| C | 0, &minus;2, 2, &minus;1, 1 |
| D | 0, &minus;2, 1, &minus;1, 2 |

**Normality.** Shapiro-Wilk on all 20 residuals, plus a Q-Q plot. Do *not* test the raw data -- four groups with different means pooled together will look non-normal even when every group is perfectly normal.

**Equal variance.** Levene's test, or Bartlett's if you are confident of normality. Here each treatment has the identical residual set, so the variances are equal by construction.

**Independence.** Guaranteed by the randomisation, if you actually randomised. If the data were collected in a spatial or temporal order, plot the residuals against that order and run a runs test.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">What to do when an assumption fails</span>
| Problem | Remedy |
|---|---|
| Variance rises with the mean (counts) | &radic;*Y* transform, or a Poisson GLM |
| Variance rises with the mean (proportions) | arcsine &radic;*p*, or a binomial GLM |
| Variance proportional to the mean squared | log(*Y*) transform |
| Unequal variance, no pattern | Welch's ANOVA |
| Non-normal with outliers | Kruskal-Wallis (see **Nonparametric Statistics**) |

ANOVA is robust to moderate non-normality, especially with equal replication. It is **much less robust to unequal variance when replication is unequal** -- that combination is the one that genuinely breaks the test.
</div>

## Mean comparisons: which treatments differ?

A significant *F* says "not all equal". With four treatments there are six pairs to consider.

**LSD (Fisher's least significant difference)** -- the most powerful and least protected:

<div class="formula" markdown="1">
**LSD = t&#8338;&#8321;&#8342;&#8342;&#8342;&#8342;&#8342;&#8342;&#8342;&#8342;&#8342;&#8342;&#8342;&#8342;&#8342;&#8342;&#8342;&#8342;&#8342;&#8342; x &radic;(2 MSE / n)**
<span class="formula-note">t at alpha/2 with error df; any two means differing by more than LSD are declared different</span>
</div>

```
t(.975, 16) = 2.1199

LSD = 2.1199 x sqrt(2 x 2.5/5)
    = 2.1199 x sqrt(1)
    = 2.1199
```

**Tukey's HSD** -- controls the error rate across all six comparisons simultaneously:

<div class="formula" markdown="1">
**HSD = q&#8338;(k, df) x &radic;(MSE / n)**
<span class="formula-note">q from the studentised range distribution; q(.05, 4, 16) = 4.05</span>
</div>

```
HSD = 4.05 x sqrt(2.5/5) = 4.05 x 0.7071 = 2.8638
```

Tukey's threshold (2.86) is larger than LSD's (2.12) -- that is the price of protecting against six chances at a false positive.

**The comparisons, using Tukey:**

| Pair | Difference | > 2.8638? | Tukey p |
|---|---|---|---|
| C vs A | 10.0 | yes | &lt; .0001 |
| C vs D | 7.0 | yes | &lt; .0001 |
| C vs B | 5.0 | yes | .0007 |
| B vs A | 5.0 | yes | .0007 |
| D vs A | 3.0 | yes | .0382 |
| B vs D | 2.0 | **no** | .2288 |

Reported with the standard letter notation, means sharing a letter are not significantly different:

```
C  31.0  a
B  26.0  b
D  24.0  b
A  21.0  c
```

So: C is best, A is worst, and **B and D cannot be distinguished**. Note that under LSD (threshold 2.12) the B-vs-D difference of 2.0 would also be non-significant -- the two procedures agree here, but on a difference of 2.5 they would not.

<div class="callout callout-note" markdown="1">
<span class="callout-label">Choosing a comparison procedure</span>
| Procedure | Protection | Use when |
|---|---|---|
| **LSD** | None beyond the *F* test | Few planned comparisons, decided in advance |
| **Tukey HSD** | All pairwise, exact | **The default for "which pairs differ"** |
| **Duncan** | Weak | Common in older agronomy papers; avoid in new work |
| **Bonferroni** | Any set, conservative | A small number of specific comparisons |
| **Dunnett** | All vs one control | **The right choice when one treatment is a control** |
| **Scheffe** | Any contrast at all | Comparisons chosen after seeing the data |

Two practical notes. If your design has a control and you only care about treatment-vs-control, **Dunnett** is strictly better than Tukey -- fewer comparisons, more power. And if you decided your comparisons before collecting data, say so; planned contrasts need less correction than a fishing expedition.
</div>

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span>
**Analyses -> ANOVA -> One-Way ANOVA** for the quick version, or **Analyses -> ANOVA -> ANOVA** for the full one with everything.
Dependent: yield. Fixed factor: treatment.
Under *Effect size* tick **eta-squared** and **omega-squared**.
Under *Assumption Checks* tick **Homogeneity test**, **Normality test** and **Q-Q plot of residuals**.
Under *Post Hoc Tests* move treatment across and choose **Tukey**; tick *Mean difference*, *Test results (t and df)* and *Flag significant comparisons*.
Under *Estimated Marginal Means* add treatment to get a plot with confidence intervals.
</div>

**SPSS.** `Analyze -> Compare Means -> One-Way ANOVA`. Put yield in *Dependent List*, treatment in *Factor*. Then:

- *Post Hoc* -> tick **Tukey** (and **LSD** if you want to compare, **Dunnett** if you have a control).
- *Options* -> tick **Descriptive**, **Homogeneity of variance test**, **Means plot**.

For omega-squared and residual plots use `Analyze -> General Linear Model -> Univariate` instead, which also prints partial eta-squared and offers residual diagnostics under *Save*.

**Excel.** This one Excel does properly. Enable the Analysis ToolPak (File -> Options -> Add-ins -> Analysis ToolPak -> Go -> tick it), then:

`Data -> Data Analysis -> Anova: Single Factor`, input range = all four columns, grouped by columns, labels in first row.

The output is the exact table above: SS 265 / 40 / 305, df 3 / 16 / 19, MS 88.3333 / 2.5, *F* 35.3333, *P-value* 2.75E-07, *F crit* 3.2389.

Excel does **not** do post-hoc tests, so compute LSD by hand:

```
H1:  =T.INV.2T(0.05,16)*SQRT(2*2.5/5)        ' LSD = 2.1199
```

For Tukey you need the *q* value, which Excel has no function for -- look it up (*q*(.05, 4, 16) = 4.05) and compute `=4.05*SQRT(2.5/5)`.

**R.**

```r
d <- data.frame(
  trt   = rep(c("A","B","C","D"), each = 5),
  yield = c(21,19,22,20,23, 26,28,25,27,24, 31,29,33,30,32, 24,22,25,23,26))

m <- aov(yield ~ trt, data = d)
summary(m)
#             Df Sum Sq Mean Sq F value   Pr(>F)
# trt          3    265   88.33   35.33 2.75e-07 ***
# Residuals   16     40    2.50

# assumptions, on the residuals
shapiro.test(residuals(m))
car::leveneTest(yield ~ trt, data = d)
par(mfrow = c(2,2)); plot(m)

# effect size
effectsize::eta_squared(m)       # 0.869
effectsize::omega_squared(m)     # 0.837

# post hoc
TukeyHSD(m)
agricolae::LSD.test(m, "trt", console = TRUE)      # with letter grouping
agricolae::HSD.test(m, "trt", console = TRUE)
DescTools::DunnettTest(yield ~ trt, data = d, control = "A")
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Use `aov`, not `anova(lm(...))`, for designed experiments</span>
Both give the same table for a balanced one-way design. But `aov` carries the design structure, which `TukeyHSD`, `agricolae` and the split-plot `Error()` syntax all depend on. Build the habit now; it matters from the RCBD lesson onward.
</div>

## Reading the output

Jamovi's assumption-check panel for this data:

| Test | Statistic | p |
|---|---|---|
| Shapiro-Wilk (residuals) | 0.936 | .203 |
| Levene's | 0.000 | 1.000 |

Both pass. Levene's is exactly zero because the four residual sets are identical -- an artefact of this teaching dataset, not something you will see in the field.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">APA / agronomy report</span>
"A one-way ANOVA on a completely randomised design with four fertiliser treatments and five replications showed a significant treatment effect on yield, *F*(3, 16) = 35.33, *p* &lt; .001, omega&#178; = .84. The coefficient of variation was 6.2%, indicating good experimental control. Residuals were normally distributed (Shapiro-Wilk *W* = .94, *p* = .20) with homogeneous variances (Levene's *F*(3, 16) = 0.00, *p* = 1.00).

Tukey's HSD (critical difference 2.86 kg) ranked the treatments C (31.0 kg) &gt; B (26.0) = D (24.0) &gt; A (21.0). Treatment C out-yielded the control by 10.0 kg, 95% CI [7.14, 12.86]. Treatments B and D did not differ significantly (*p* = .229)."
</div>

That paragraph contains everything a reader needs to evaluate the experiment: the design, the *F* test, an unbiased effect size, the CV as a quality check, the assumption checks, the ranking with its critical difference, and a confidence interval on the comparison that matters. Nothing is asserted that is not shown.

## Common mistakes

1. **Testing normality on the raw data instead of the residuals.** Several groups with different means look non-normal when pooled.
2. **Running *t*-tests on every pair instead of ANOVA.** Six *t*-tests at alpha = .05 give about a 26% chance of at least one false positive.
3. **Reporting post-hoc results when *F* is not significant.** Fisher's protected LSD specifically requires a significant *F* first.
4. **Using Duncan's test.** Weak error-rate control; it persists in agronomy by habit. Tukey or Dunnett.
5. **Reporting eta-squared as if it were unbiased.** Give omega-squared too, especially at small *n*.
6. **Ignoring the CV.** A CV of 35% means the experiment was poorly executed, whatever the *p*-value says.
7. **Using a CRD when the field has an obvious gradient.** You are putting known variation into the error term for no reason. Block it.
8. **Forgetting that unequal variance plus unequal replication is the dangerous combination.** Either alone is survivable; together they break the test.

## Practice

<details markdown="1">
<summary>1. Three treatments with totals 60, 75, 90 and n = 4 each. Sum of all squared observations is 4,200. Build the ANOVA table.</summary>

```
G = 60 + 75 + 90 = 225
N = 12
CF = 225^2/12 = 50625/12 = 4218.75
```

TSS = 4200 &minus; 4218.75 = **&minus;18.75**.

A negative total sum of squares is impossible, so one of the given numbers is wrong -- and that is the point of the exercise. TSS = &Sigma;*Y*&#178; &minus; CF can never be negative, because &Sigma;*Y*&#178; &ge; *G*&#178;/*N* by the Cauchy-Schwarz inequality.

Here the sum of squared observations must be at least 4218.75. With totals of 60, 75 and 90 (means 15, 18.75, 22.5), the minimum possible &Sigma;*Y*&#178; -- achieved when every observation within a treatment is identical -- is 4(225) + 4(351.5625) + 4(506.25) = 4331.25.

**The lesson: compute CF first and compare it to &Sigma;*Y*&#178; before going further.** It is a free validity check on your data entry, and it catches transcription errors immediately.
</details>

<details markdown="1">
<summary>2. Redo it with the sum of squared observations equal to 4,400.</summary>

```
CF  = 4218.75
TSS = 4400 - 4218.75 = 181.25

SS(treat) = 60^2/4 + 75^2/4 + 90^2/4 - 4218.75
          = 900 + 1406.25 + 2025 - 4218.75
          = 4331.25 - 4218.75
          = 112.5

SSE = 181.25 - 112.5 = 68.75
```

| Source | SS | df | MS | F |
|---|---|---|---|---|
| Treatment | 112.50 | 2 | 56.250 | **7.364** |
| Error | 68.75 | 9 | 7.639 | |
| Total | 181.25 | 11 | | |

*F*(2, 9) = 7.364. Critical value at .05 is 4.26, so reject. The *p*-value is .0128.

```
eta-squared = 112.5/181.25 = .6207
CV% = 100 x sqrt(7.639)/18.75 = 14.74%
LSD = t(.975, 9) x sqrt(2 x 7.639/4) = 2.262 x 1.9544 = 4.421
```

Means are 15.0, 18.75 and 22.5. Adjacent differences are 3.75 -- **less than the LSD of 4.42** -- while the extreme difference of 7.5 exceeds it. So treatments 1 and 3 differ and neither can be separated from treatment 2. The familiar pattern from the Kruskal-Wallis lesson: enough power for the extremes, not for the neighbours.
</details>

<details markdown="1">
<summary>3. Why is Tukey's threshold (2.86) larger than LSD's (2.12) on the same data?</summary>

Because they control different error rates.

LSD controls the error rate **per comparison**. Each of the six pairwise tests has its own 5% chance of a false positive, so the chance of at least one across all six is roughly 1 &minus; .95&#8310; = 26%.

Tukey controls the error rate **across the whole family**. The probability of *any* false positive among all six comparisons is 5%. To achieve that, the threshold must be higher -- 2.86 instead of 2.12, about 35% larger.

The mechanism is the studentised range distribution. Instead of asking "how far apart can two randomly chosen means be?", Tukey asks "how far apart can the *largest and smallest* of four means be?" The maximum of several differences is naturally bigger than a typical one, so the critical value is bigger.

**When each is right:** LSD for a small number of comparisons you specified before collecting data (and only after a significant *F*). Tukey when you are looking at all pairs, which is almost always.
</details>

<details markdown="1">
<summary>4. Your CV comes out at 28%. F is significant. Is the result usable?</summary>

Treat it as a warning, not a verdict.

A CV of 28% means the within-treatment standard deviation is 28% of the mean -- experimental error is large relative to the signal. Three things follow.

**The significant result is probably real.** A large effect detected despite high noise is, if anything, more impressive. *F* already accounts for the error; it did not get a free pass.

**But your precision is poor.** Confidence intervals on the treatment means will be wide, and you will not detect smaller differences. Adjacent treatments will be indistinguishable.

**And something may have gone wrong in execution.** This is the part worth investigating. Common causes: units less uniform than assumed (a gradient you failed to block), inconsistent application of the treatment, measurement error, or a few plots damaged by pests, flooding or equipment. Plot the residuals and look for outliers -- a single bad plot can inflate the CV substantially, and if you can document a physical reason it may legitimately be excluded (with the exclusion reported).

**What to do:** report the CV honestly, state that it limits precision, name any identified cause, and for the next experiment either block on whatever you discover or increase replication. A high CV reported openly is a limitation; a high CV omitted is a reviewer's finding.
</details>

## Before you move on

- [ ] I can compute CF, TSS, SS(treatment) and SSE by hand and verify them.
- [ ] I check &Sigma;*Y*&#178; &ge; CF before doing anything else.
- [ ] I know *F* compares treatment variation against error variation and why its expected value is 1 under the null.
- [ ] I compute and report omega-squared, not only eta-squared.
- [ ] I report CV% as a quality check.
- [ ] I test assumptions on the residuals, never on the raw data.
- [ ] I can choose between LSD, Tukey and Dunnett for a reason.
- [ ] I know unequal variance combined with unequal replication is the dangerous case.""",
    quiz={
        "question": "In a CRD with 4 treatments and 5 reps, MSE = 2.5 and MS(treatment) = 88.33. What does F = 35.33 mean?",
        "options": [
            "The treatment means differ by 35.33 units on average",
            "The treatment mean square is 35 times larger than random error alone can account for, so the treatment effect is real",
            "35.33% of the variation is explained by treatment",
            "There is a 35.33% chance the null hypothesis is false",
        ],
        "answer": 1,
        "explanation": "MSE estimates error variance whether or not treatments differ. MS(treatment) estimates error variance plus a treatment component. Under the null both estimate the same thing and F is near 1, so F = 35.33 is strong evidence against it. The proportion of variation explained is eta-squared = .87, a separate quantity.",
    },
)


# ===========================================================================
L(
    "Randomized Complete Block Design",
    """## What you will be able to do

Partition the total sum of squares into treatment, block and error; demonstrate with real numbers what blocking buys you; compute relative efficiency; and recognise the two situations that break an RCBD.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
The same four fertilisers, but now the field slopes. Soil moisture rises from the top of the slope to the bottom, so plots are **not** uniform.

Four strips are laid out across the slope, each internally uniform. Each strip is a block and receives all four treatments, randomised within it.

| Block | A | B | C | D | Block total |
|---|---|---|---|---|---|
| 1 | 23 | 27 | 34 | 24 | 108 |
| 2 | 19 | 27 | 29 | 24 | 99 |
| 3 | 25 | 31 | 34 | 28 | 118 |
| 4 | 20 | 26 | 33 | 23 | 102 |
| **Treatment total** | **87** | **111** | **130** | **99** | **427** |
| **Treatment mean** | 21.75 | 27.75 | 32.50 | 24.75 | **26.6875** |
</div>

Block 3 totals 118 and block 2 totals 99 -- a 19-unit spread that has nothing to do with treatment. In a CRD that spread would sit inside the error term. Here it comes out as a named source.

## The two requirements

An RCBD is "complete" because **every treatment appears in every block, exactly once**. That is not a convention; the analysis depends on it.

| Requirement | Why | What breaks it |
|---|---|---|
| Every treatment in every block | Treatment effects are estimated free of block effects | More treatments than units per block |
| Treatments randomised **within** each block | Position inside a block is not confounded with treatment | Using the same order in each block |

If you have more treatments than will fit in a homogeneous block, you need a **balanced incomplete block design** -- a different and harder analysis. Do not just drop treatments from some blocks.

## The model

<div class="formula" markdown="1">
**Y&#7522;&#11388; = &mu; + &tau;&#7522; + &beta;&#11388; + &epsilon;&#7522;&#11388;**
<span class="formula-note">one new term: &beta;&#11388;, the effect of block j</span>
</div>

There is no interaction term, and that is an assumption, not an oversight: the RCBD assumes treatments behave the **same way in every block**. If treatment C is best in block 1 but worst in block 4, that assumption fails and the error term absorbs the inconsistency, inflating MSE.

With one observation per treatment-block cell, treatment x block interaction and error are inseparable. The error term *is* the interaction. This is why the RCBD's error line is sometimes written "treatment x block".

## Working it by hand

**Step 1. The constants.**

```
G = 427, N = 16, t = 4 treatments, b = 4 blocks
CF = 427^2/16 = 182329/16 = 11395.5625
```

**Step 2. Total sum of squares.**

```
sum of all squared observations:
  block 1: 529 + 729 + 1156 + 576 = 2990
  block 2: 361 + 729 +  841 + 576 = 2507
  block 3: 625 + 961 + 1156 + 784 = 3526
  block 4: 400 + 676 + 1089 + 529 = 2694
                            total = 11717

TSS = 11717 - 11395.5625 = 321.4375
```

**Step 3. Treatment sum of squares -- divide by the number of *blocks*, since each treatment total is over *b* observations.**

```
SS(treat) = (87^2 + 111^2 + 130^2 + 99^2)/4 - 11395.5625
          = (7569 + 12321 + 16900 + 9801)/4 - 11395.5625
          = 46591/4 - 11395.5625
          = 11647.75 - 11395.5625
          = 252.1875
```

**Step 4. Block sum of squares -- divide by the number of *treatments*.**

```
SS(block) = (108^2 + 99^2 + 118^2 + 102^2)/4 - 11395.5625
          = (11664 + 9801 + 13924 + 10404)/4 - 11395.5625
          = 45793/4 - 11395.5625
          = 11448.25 - 11395.5625
          = 52.6875
```

**Step 5. Error by subtraction.**

```
SSE = TSS - SS(treat) - SS(block)
    = 321.4375 - 252.1875 - 52.6875
    = 16.5625
```

**Step 6. The ANOVA table.**

| Source | SS | df | MS | F | p |
|---|---|---|---|---|---|
| Block | 52.6875 | 3 | 17.5625 | **9.5434** | **.0037** |
| Treatment | 252.1875 | 3 | 84.0625 | **45.6792** | **9.03e-06** |
| Error | 16.5625 | 9 | 1.8403 | | |
| **Total** | **321.4375** | **15** | | | |

Error df = (*t* &minus; 1)(*b* &minus; 1) = 3 x 3 = **9**. Note what you paid: the CRD on 16 units would have had 12 error df. Blocking cost 3 df.

```
MSE = 16.5625/9 = 1.8403
F(treat) = 84.0625/1.8403 = 45.6792
F(block) = 17.5625/1.8403 = 9.5434
CV% = 100 x sqrt(1.8403)/26.6875 = 5.08%
```

Both are significant. The treatments differ, **and** the blocking was worth doing.

## What blocking actually bought: the same data, analysed both ways

This is the most instructive calculation in the lesson. Take the identical 16 observations and ignore the blocks.

```
As a CRD:  SSE = TSS - SS(treat)
               = 321.4375 - 252.1875
               = 69.25     (df = 16 - 4 = 12)
           MSE = 69.25/12 = 5.7708
           F   = 84.0625/5.7708 = 14.5668   p = .000265
```

Side by side:

| | SSE | df | MSE | F(treatment) | p |
|---|---|---|---|---|---|
| **RCBD** | 16.56 | 9 | **1.8403** | **45.68** | .0000090 |
| **CRD (blocks ignored)** | 69.25 | 12 | **5.7708** | **14.57** | .00027 |

The 52.69 units of block variation moved from the error term into its own line. MSE fell by a factor of 3.14 and *F* more than tripled -- **even though blocking cost 3 error degrees of freedom**.

Both analyses reject, because the treatment effect is enormous. But imagine the effect were a third as large. The RCBD's *F* would be about 5.1 (significant at 9 df, where the critical value is 3.86) while the CRD's would be about 1.6 (nowhere near the 3.49 needed at 12 df). The blocked design would find it; the unblocked one would not.

## Relative efficiency: pricing the gain

<div class="formula" markdown="1">
**RE = [ (b&minus;1)MS&#8342; + b(t&minus;1)MSE ] / [ (bt&minus;1) MSE ]**
<span class="formula-note">MS&#8342; = block mean square; the result is how many CRD reps equal one RCBD rep</span>
</div>

```
RE = [ 3 x 17.5625 + 4 x 3 x 1.8403 ] / [ 15 x 1.8403 ]
   = [ 52.6875 + 22.0833 ] / 27.6042
   = 74.7708 / 27.6042
   = 2.709
```

**This 4-block experiment is worth about 10.8 CRD replications** (4 x 2.709). To match it without blocking you would need roughly 11 plots per treatment -- 44 plots instead of 16.

An RE below 1 would mean blocking cost more in degrees of freedom than it saved in error, which happens when the blocks are no more homogeneous than the field as a whole.

## Mean comparisons

Same procedures as the CRD, with *b* in place of *n* and the RCBD's error df:

```
LSD = t(.975, 9) x sqrt(2 MSE / b)
    = 2.2622 x sqrt(2 x 1.8403/4)
    = 2.2622 x 0.9593
    = 2.1699

Tukey HSD = q(.05, 4, 9) x sqrt(MSE/b)
          = 4.415 x sqrt(1.8403/4)
          = 4.415 x 0.6783
          = 2.9946
```

Treatment means: C 32.50, B 27.75, D 24.75, A 21.75.

| Pair | Difference | > HSD 2.9946? |
|---|---|---|
| C vs A | 10.75 | yes |
| C vs D | 7.75 | yes |
| C vs B | 4.75 | yes |
| B vs A | 6.00 | yes |
| B vs D | 3.00 | yes (just) |
| D vs A | 3.00 | yes (just) |

```
C  32.50  a
B  27.75  b
D  24.75  c
A  21.75  d
```

All four treatments separate. Compare with the CRD lesson, where B and D could not be distinguished -- same treatments, same effect sizes, but the smaller MSE here resolves a 3-unit difference that the CRD could not. That is the power of blocking made concrete.

<div class="callout callout-note" markdown="1">
<span class="callout-label">Why blocks get no mean comparisons</span>
You will see an *F* test for blocks but never a Tukey test on block means. Blocks are a nuisance factor -- you are not interested in which strip of field yielded more, only in removing that variation.

Report *F*(block) because it tells the reader whether blocking was justified. Do not interpret it as a finding, and do not compare block means. If you *are* interested in the differences, it is not a block; it is a factor, and you want the factorial design in a later lesson.
</div>

## Missing data: the one real headache

An RCBD with a missing plot is no longer balanced, and the hand formulas above stop working. Three options:

**Estimate the missing value** (the classical approach):

<div class="formula" markdown="1">
**Y&#770; = (t T&#8242; + b B&#8242; &minus; G&#8242;) / [ (t&minus;1)(b&minus;1) ]**
<span class="formula-note">T&#8242;, B&#8242;, G&#8242; = totals of the treatment, block and whole experiment *excluding* the missing unit</span>
</div>

Then analyse as complete, but **subtract one degree of freedom from error** -- you estimated a value, you did not observe one. Forgetting that step overstates your precision.

**Fit the model by least squares** instead. `lm()` or `aov()` in R, and SPSS's GLM, handle unbalanced data correctly with no estimation step. This is the modern answer, and you should prefer it. One caution: with unbalanced data, Type I and Type III sums of squares differ, so state which you report (Type III is standard for unbalanced designs).

**Analyse as a CRD**, losing the blocking. Acceptable only if the block effect was negligible, which here it is not.

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span>
**Analyses -> ANOVA -> ANOVA.**
Dependent: yield. Fixed Factors: **treatment and block** -- both go in.
Under *Model*, open the Model Terms box and make sure only the two **main effects** are included. Jamovi adds `treatment * block` by default; remove the interaction term, or you will have zero error df and no *F* tests at all.
Under *Post Hoc Tests*, move **treatment only** across and choose Tukey.
</div>

**SPSS.** `Analyze -> General Linear Model -> Univariate`. Dependent: yield. Fixed Factor(s): treatment and block. Then click **Model**, choose *Custom*, move `treatment` and `block` into *Model* as **Main effects** (not the interaction), and set *Sum of squares* to Type III. Post hoc on treatment only.

Same trap as Jamovi: the default *Full factorial* model includes the interaction, which consumes every error degree of freedom.

**Excel.** The ToolPak does this one directly: `Data -> Data Analysis -> Anova: Two-Factor Without Replication`.

Lay the data out as a 4 x 4 grid with block labels down the left and treatment labels across the top. The output gives:

```
Source    SS        df   MS        F        P-value
Rows      52.6875    3   17.5625   9.5434   0.00371
Columns  252.1875    3   84.0625  45.6792   0.0000090
Error     16.5625    9    1.8403
Total    321.4375   15
```

"Rows" is blocks and "Columns" is treatments in this layout. The name "Two-Factor Without Replication" **is** the RCBD -- Excel just does not call it that. No post-hoc tests, so compute LSD by hand:

```
=T.INV.2T(0.05,9)*SQRT(2*1.8403/4)       ' 2.1699
```

**R.**

```r
d <- data.frame(
  block = factor(rep(1:4, each = 4)),
  trt   = factor(rep(c("A","B","C","D"), 4)),
  yield = c(23,27,34,24, 19,27,29,24, 25,31,34,28, 20,26,33,23))

m <- aov(yield ~ block + trt, data = d)
summary(m)
#             Df Sum Sq Mean Sq F value   Pr(>F)
# block        3  52.69  17.563   9.543  0.00371 **
# trt          3 252.19  84.063  45.679 9.03e-06 ***
# Residuals    9  16.56   1.840

TukeyHSD(m, "trt")
agricolae::LSD.test(m, "trt", console = TRUE)

# the comparison that makes the case for blocking
summary(aov(yield ~ trt, data = d))      # F = 14.57, MSE = 5.77

# relative efficiency, computed directly
a  <- summary(m)[[1]]
msb <- a["block  ", "Mean Sq"]; mse <- a["Residuals", "Mean Sq"]
(3*msb + 4*3*mse) / (15*mse)             # 2.709
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Block must be a factor</span>
If `block` is stored as the numbers 1, 2, 3, 4 and you do not wrap it in `factor()`, R fits it as a **linear covariate with 1 df** instead of 4 levels with 3 df. The block line will show `Df 1`, the error df will be wrong, and every *F* in the table will be wrong.

Check the `Df` column against what you expect before reading anything else. `Df 1` on a 4-level block is the signature of this error.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Agronomy / APA report</span>
"Yield was analysed as a randomised complete block design with four fertiliser treatments and four blocks defined by position along the field's moisture gradient. The treatment effect was significant, *F*(3, 9) = 45.68, *p* &lt; .001, as was the block effect, *F*(3, 9) = 9.54, *p* = .004, confirming that blocking was warranted. The coefficient of variation was 5.1%.

Tukey's HSD (critical difference 2.99 kg) separated all four treatments: C (32.50 kg) &gt; B (27.75) &gt; D (24.75) &gt; A (21.75). Relative efficiency of the blocked design against a completely randomised design was 2.71, indicating that the four blocks provided precision equivalent to approximately eleven unblocked replications."
</div>

The relative-efficiency sentence is the one most student write-ups omit and the one a methods-minded examiner most appreciates. It justifies the design choice with a number.

## Common mistakes

1. **Leaving the treatment x block interaction in the model.** With one observation per cell it consumes all the error df and you get no tests. Remove it in both Jamovi and SPSS.
2. **Not wrapping block in `factor()` in R.** Silently fits a 1-df linear trend instead of a 4-level factor.
3. **Running Tukey on block means.** Blocks are a nuisance factor.
4. **Dropping the block term because *F*(block) is non-significant.** You randomised within blocks; the analysis must reflect the design.
5. **Dividing treatment totals by the wrong count.** Treatment totals are over *b* observations, block totals over *t*. Mixing them up is the most common hand-calculation error here.
6. **Using an incomplete block design and analysing it as complete.** Every treatment must appear in every block.
7. **Forgetting to subtract an error df after estimating a missing value.**
8. **Using the same treatment order in every block.** Randomise within each block separately, or position is confounded with treatment.

## Practice

<details markdown="1">
<summary>1. An RCBD has 5 treatments and 3 blocks. How many error degrees of freedom, and what is the problem?</summary>

```
error df = (t-1)(b-1) = (5-1)(3-1) = 4 x 2 = 8
total df = 15 - 1 = 14
```

Eight error df is **workable but tight**. Critical *F*(4, 8) at .05 is 3.84, against 2.93 for *F*(4, 16). You need a substantially larger effect to reach significance.

The practical consequence is in the mean comparisons: *t*(.975, 8) = 2.306 and the LSD multiplier &radic;(2/3) = 0.816, so LSD = 1.882&radic;MSE. Compare with 5 blocks, where it would be 1.482&radic;MSE -- a 27% narrower critical difference.

**The fix is more blocks, not more treatments.** Going from 3 to 5 blocks takes error df from 8 to 16 and roughly halves the critical *F*. Blocks are usually the cheaper thing to add, since a block is just another strip of field or another day of testing.
</details>

<details markdown="1">
<summary>2. F(block) = 1.2, p = .36, and relative efficiency computes to 0.93. Interpret.</summary>

RE below 1 means **blocking made the experiment slightly worse**.

The blocks captured almost no variation (hence the non-significant *F*), but you still paid 3 degrees of freedom for them. Those df came out of error, so MSE is marginally higher than a CRD's would have been. RE = 0.93 says the blocked experiment is worth about 93% of an unblocked one of the same size -- a 7% loss.

**What you should do:** nothing to the analysis. Report the design as run, including the non-significant block effect. Do not re-analyse as a CRD, and do not present the CRD result as your primary analysis.

**What you learn for next time:** the blocking variable you chose does not drive variation in this response. Either find the variable that does -- look at a map of the residuals, which often shows the real gradient -- or accept that the units are genuinely homogeneous and use a CRD, which will then give you the extra df.

Worth keeping in proportion: a 7% loss is cheap insurance against the alternative outcome, where an unblocked design buries a real effect under gradient variation.
</details>

<details markdown="1">
<summary>3. Why does the RCBD have no interaction term, and what happens if treatments really do behave differently in different blocks?</summary>

**Why there is no term:** with one observation per treatment-block cell there are *tb* observations and *tb* parameters needed to describe all the cell means. Nothing is left to estimate error from. Treatment x block interaction and error are mathematically the same sum of squares, so the design can fit one or the other, not both.

**What happens when the interaction is real:** it goes into the error term. MSE is inflated, *F*(treatment) is deflated, and the test loses power. You will not see a warning; you will just have a weaker experiment and possibly a missed effect.

**How to detect it:** plot treatment means by block -- an interaction plot. Parallel lines mean no interaction. Lines that cross, or fan out sharply, mean the treatment effect depends on the block. Tukey's one-degree-of-freedom test for non-additivity gives a formal check.

**What to do about it:** if the interaction is substantial, it is itself a finding -- "treatment C works in wet soil but not dry" is more useful than an average effect that applies nowhere. To estimate it you need **replication within blocks**: put each treatment in each block two or more times. That turns the design into a factorial with blocks and lets you test the interaction properly, at the cost of more units.
</details>

<details markdown="1">
<summary>4. Compute the missing value for an RCBD with t = 4, b = 4, where one plot is lost. The treatment total excluding it is 66, the block total excluding it is 78, and the grand total excluding it is 400.</summary>

```
Yhat = (t T' + b B' - G') / [(t-1)(b-1)]
     = (4 x 66 + 4 x 78 - 400) / (3 x 3)
     = (264 + 312 - 400) / 9
     = 176/9
     = 19.56
```

Then analyse the completed 16-value dataset as a normal RCBD, **but with error df = 9 &minus; 1 = 8**, not 9.

The df adjustment is the step people forget, and it matters: you supplied that value from the other observations, so it carries no independent information. Keeping 9 df would make MSE too small and every *F* too large.

The formula itself is just the value that makes the residual for that cell exactly zero under the additive model -- in other words, the value the model predicts. That is also why it adds no information: it is a fitted value, not data.

**In practice, use least squares instead.** `aov(yield ~ block + trt)` on the 15 real observations handles the imbalance correctly, gets the df right automatically, and does not require you to remember the formula. Report Type III sums of squares.
</details>

## Before you move on

- [ ] I can partition TSS into treatment, block and error by hand.
- [ ] I divide treatment totals by *b* and block totals by *t*, and I know which is which.
- [ ] I can compute error df as (*t*&minus;1)(*b*&minus;1) and say what blocking cost me.
- [ ] I can re-analyse the same data as a CRD to show what blocking bought.
- [ ] I can compute relative efficiency and state it as "equivalent to N unblocked reps".
- [ ] I remove the interaction term in Jamovi and SPSS, and wrap block in `factor()` in R.
- [ ] I report *F*(block) but never compare block means.
- [ ] I know what to do when a plot is missing, including the df adjustment.""",
    quiz={
        "question": "The same 16 observations give MSE = 1.84 as an RCBD and MSE = 5.77 analysed as a CRD, even though the RCBD has fewer error degrees of freedom. Why?",
        "options": [
            "The RCBD uses a different formula for the error sum of squares",
            "Blocking moved 52.69 units of block-to-block variation out of the error term into its own line, and that gain outweighed the 3 degrees of freedom it cost",
            "The CRD analysis is incorrect and should not be computed",
            "Fewer degrees of freedom always produce a smaller mean square",
        ],
        "answer": 1,
        "explanation": "SSE fell from 69.25 to 16.56 because the block sum of squares was extracted from it. Dividing a much smaller SS by a slightly smaller df still gives a much smaller MSE. Relative efficiency of 2.71 prices the net gain.",
    },
)
