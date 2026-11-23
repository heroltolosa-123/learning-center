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


# ===========================================================================
L(
    "Latin Square Designs",
    """## What you will be able to do

Build and analyse a Latin square -- the design that removes **two** nuisance factors at once -- partition the sum of squares four ways, and judge when the design's severe constraints make it the wrong choice.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
Four fertilisers again, but the field now varies in **two** directions: moisture increases down the slope (north to south) and soil depth increases west to east.

One set of blocks can only remove one gradient. A Latin square removes both.

Rows = moisture strips. Columns = depth strips. Each treatment appears **exactly once in every row and exactly once in every column**:

| | Col 1 | Col 2 | Col 3 | Col 4 | Row total |
|---|---|---|---|---|---|
| **Row 1** | A 23 | B 31 | C 36 | D 28 | 118 |
| **Row 2** | B 29 | C 35 | D 28 | A 19 | 111 |
| **Row 3** | C 34 | D 27 | A 20 | B 30 | 111 |
| **Row 4** | D 28 | A 19 | B 30 | C 35 | 112 |
| **Col total** | 114 | 112 | 114 | 112 | **452** |

Treatment totals: A 81, B 120, C 140, D 111. Grand total 452, grand mean 28.25.
</div>

## The defining constraint, and its cost

A Latin square must be **square**: the number of treatments, rows and columns are all equal to *p*. Four treatments force exactly 4 rows and 4 columns and exactly 16 plots. You cannot choose the replication.

<div class="formula" markdown="1">
**error df = (p &minus; 1)(p &minus; 2)**
</div>

| *p* | Units | Error df | Verdict |
|---|---|---|---|
| 3 | 9 | **2** | Unusable |
| 4 | 16 | **6** | Minimum workable |
| 5 | 25 | **12** | Comfortable |
| 6 | 36 | **20** | Good |
| 8 | 64 | **42** | Often impractically large |

This is the design's central problem. At *p* = 3 you have 2 error df and critical *F*(2,2) at .05 is 19.00 -- nothing will ever be significant. At *p* = 8 you need 64 units.

**The practical range is p = 4 to 6.** Outside it, use something else.

The fix for small *p* is **replicated Latin squares**: run two or more squares and pool. Two 4x4 squares give 32 plots and 13 error df (or more, depending on how rows and columns are treated across squares).

## Constructing a square

A standard square is built by cyclically shifting the treatment letters:

```
A B C D
B C D A
C D A B
D A B C
```

Then **randomise**: shuffle the row order, shuffle the column order, and randomly reassign treatment letters to the actual treatments. Doing only one of the three leaves a systematic pattern.

```r
agricolae::design.lsd(trt = c("A","B","C","D"), seed = 2026)$book
```

Never use the standard square as laid out above. Its diagonal structure means treatment A always sits on a diagonal, which can align with a real diagonal gradient.

## The model

<div class="formula" markdown="1">
**Y&#7522;&#11388;&#8342; = &mu; + &rho;&#7522; + &gamma;&#11388; + &tau;&#8342; + &epsilon;&#7522;&#11388;&#8342;**
<span class="formula-note">&rho; = row effect, &gamma; = column effect, &tau; = treatment effect</span>
</div>

Four sources instead of three, all assumed additive with no interactions -- a stronger assumption than the RCBD's, and worth stating when you report the design.

## Working it by hand

**Step 1. Constants.**

```
G = 452, N = 16, p = 4
CF = 452^2/16 = 204304/16 = 12769
```

**Step 2. Total.**

```
sum of all squared observations:
  row 1: 529 + 961 + 1296 + 784 = 3570
  row 2: 841 + 1225 + 784 + 361 = 3211
  row 3: 1156 + 729 + 400 + 900 = 3185
  row 4: 784 + 361 + 900 + 1225 = 3270
                          total = 13236

TSS = 13236 - 12769 = 467
```

**Step 3. Rows, columns and treatments -- all three divide by *p*.**

```
SS(row) = (118^2 + 111^2 + 111^2 + 112^2)/4 - 12769
        = (13924 + 12321 + 12321 + 12544)/4 - 12769
        = 51110/4 - 12769
        = 12777.5 - 12769
        = 8.5

SS(col) = (114^2 + 112^2 + 114^2 + 112^2)/4 - 12769
        = (12996 + 12544 + 12996 + 12544)/4 - 12769
        = 51080/4 - 12769
        = 12770 - 12769
        = 1.0

SS(trt) = (81^2 + 120^2 + 140^2 + 111^2)/4 - 12769
        = (6561 + 14400 + 19600 + 12321)/4 - 12769
        = 52882/4 - 12769
        = 13220.5 - 12769
        = 451.5
```

**Step 4. Error by subtraction.**

```
SSE = TSS - SS(row) - SS(col) - SS(trt)
    = 467 - 8.5 - 1.0 - 451.5
    = 6.0
```

**Step 5. The ANOVA table.**

| Source | SS | df | MS | F | p |
|---|---|---|---|---|---|
| Row | 8.5 | 3 | 2.8333 | 2.8333 | .1285 |
| Column | 1.0 | 3 | 0.3333 | 0.3333 | .8022 |
| Treatment | 451.5 | 3 | 150.5000 | **150.5000** | **&lt; .0001** |
| Error | 6.0 | 6 | 1.0000 | | |
| **Total** | **467.0** | **15** | | | |

```
MSE = 6.0/6 = 1.0
F(trt) = 150.5/1.0 = 150.5
CV% = 100 x sqrt(1.0)/28.25 = 3.54%
```

Treatment means: A 20.25, B 30.00, C 35.00, D 27.75.

**Step 6. Read the nuisance factors honestly.**

Rows: *F* = 2.83, *p* = .13. Columns: *F* = 0.33, *p* = .80.

**Neither gradient was real in this data.** The moisture strips captured 8.5 units and the depth strips only 1.0 -- almost nothing, out of a total of 467.

So the double blocking bought little here, and it cost 6 error degrees of freedom (3 for rows, 3 for columns). An RCBD blocking only on rows would have had 9 error df; a CRD would have had 12.

That is the honest conclusion, and it is the most useful thing this example teaches. **A Latin square is expensive insurance.** When both gradients are real it is excellent value; when neither is, you have spent half your error df for nothing.

<div class="callout callout-note" markdown="1">
<span class="callout-label">Why the design was still defensible</span>
You did not know in advance. The field visibly sloped and the soil survey showed a depth gradient. Designing for what the site showed was correct; the gradients turning out not to matter for *this* response is information you only had afterwards.

What you must not do is drop the row and column terms because their *F* values are small. You randomised under the Latin square constraint, so the analysis must honour it. Report all four lines.
</div>

## Mean comparisons

Same machinery, with *p* in place of *n* and the Latin square's error df:

```
LSD = t(.975, 6) x sqrt(2 MSE / p)
    = 2.4469 x sqrt(2 x 1.0/4)
    = 2.4469 x 0.7071
    = 1.7302

Tukey HSD = q(.05, 4, 6) x sqrt(MSE/p)
          = 4.896 x sqrt(1.0/4)
          = 4.896 x 0.5
          = 2.448
```

| Pair | Difference | > HSD 2.448? |
|---|---|---|
| C vs A | 14.75 | yes |
| C vs D | 7.25 | yes |
| C vs B | 5.00 | yes |
| B vs A | 9.75 | yes |
| B vs D | 2.25 | **no** |
| D vs A | 7.50 | yes |

```
C  35.00  a
B  30.00  b
D  27.75  b
A  20.25  c
```

B and D do not separate. Note how much larger Tukey's *q* is here -- 4.896 at 6 df against 4.415 at 9 df and 4.05 at 16 df. Few error degrees of freedom make every critical value climb.

## When a Latin square is right, and when it is not

| Use a Latin square when | Use something else when |
|---|---|
| Two identifiable nuisance factors cross | Only one nuisance factor (&rarr; RCBD) |
| Both are genuinely substantial | Neither is substantial (&rarr; CRD) |
| 4 &le; *p* &le; 6 | *p* = 2 or 3 (&rarr; replicate the square) |
| You can afford exactly *p*&#178; units | *p* &ge; 7 and units are costly |
| Treatment effects are large | You need many error df for a subtle effect |

A very common and underappreciated application: **order effects in repeated-measures studies**. Four subjects each test four products in a different order. Rows = subjects, columns = testing position, treatments = products. The square removes both subject differences and position effects (fatigue, learning, carry-over) in one design. This is the standard layout in sensory evaluation and in crossover clinical trials.

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span>
**Analyses -> ANOVA -> ANOVA.**
Dependent: yield. Fixed Factors: **row, column and treatment** -- all three.
Under *Model*, set the model terms to the **three main effects only**. Jamovi's default full factorial would include every interaction and leave no error df, so this step is not optional.
Post hoc on treatment only.
</div>

**SPSS.** `Analyze -> General Linear Model -> Univariate`. Fixed Factors: row, column, treatment. Click **Model -> Custom**, move all three in as *Main effects*, Type III sums of squares. Post hoc on treatment.

**Excel.** No direct tool exists -- the ToolPak's two-factor routines cannot handle the Latin square constraint. Compute it by hand:

```
' data in B2:E5, with row totals in F and column totals in row 6
H1:  =SUM(B2:E5)^2/16                     ' CF = 12769
H2:  =SUMSQ(B2:E5)-H1                      ' TSS = 467
H3:  =SUMSQ(F2:F5)/4-H1                    ' SS(row) = 8.5
H4:  =SUMSQ(B6:E6)/4-H1                    ' SS(col) = 1.0
H5:  =SUMSQ(J2:J5)/4-H1                    ' SS(trt) = 451.5, J holds treatment totals
H6:  =H2-H3-H4-H5                          ' SSE = 6.0
H7:  =(H5/3)/(H6/6)                        ' F(trt) = 150.5
H8:  =F.DIST.RT(H7,3,6)                    ' p
```

Getting the treatment totals requires `SUMIF` over a parallel grid of treatment letters. `SUMSQ` is the function that makes the rest compact.

**R.**

```r
d <- data.frame(
  row = factor(rep(1:4, each = 4)),
  col = factor(rep(1:4, times = 4)),
  trt = factor(c("A","B","C","D", "B","C","D","A",
                 "C","D","A","B", "D","A","B","C")),
  y   = c(23,31,36,28, 29,35,28,19, 34,27,20,30, 28,19,30,35))

m <- aov(y ~ row + col + trt, data = d)
summary(m)
#             Df Sum Sq Mean Sq F value  Pr(>F)
# row          3    8.5   2.833   2.833  0.1285
# col          3    1.0   0.333   0.333  0.8022
# trt          3  451.5 150.500 150.500 5.2e-06 ***
# Residuals    6    6.0   1.000

TukeyHSD(m, "trt")
agricolae::LSD.test(m, "trt", console = TRUE)

# generate a randomised square for your own experiment
agricolae::design.lsd(trt = c("A","B","C","D"), seed = 2026)$book
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Check the Df column, every time</span>
A correct 4x4 Latin square ANOVA shows **3, 3, 3, 6**. If you see anything else, something is wrong: row or col was not wrapped in `factor()`, the design is not a proper square (some treatment appears twice in a row), or an interaction crept into the model.

The 3-3-3-6 pattern is your checksum. Verify it before reading a single *F*.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Agronomy / APA report</span>
"A 4x4 Latin square was used to control two perpendicular field gradients: soil moisture (rows) and soil depth (columns). The treatment effect on yield was significant, *F*(3, 6) = 150.50, *p* &lt; .001, with a coefficient of variation of 3.5%. Neither nuisance factor reached significance -- rows *F*(3, 6) = 2.83, *p* = .13; columns *F*(3, 6) = 0.33, *p* = .80 -- indicating that in this field the two gradients contributed little to yield variation, so the double blocking provided limited gain for the six error degrees of freedom it required.

Tukey's HSD (critical difference 2.45 kg) ranked C (35.00 kg) &gt; B (30.00) = D (27.75) &gt; A (20.25)."
</div>

The second paragraph of that write-up -- naming what the design cost and admitting it did not pay off -- is what a methods-aware examiner will respect. Reporting the two non-significant lines without comment invites the question; answering it first does not.

## Common mistakes

1. **Using an unrandomised standard square.** Its diagonal pattern can align with a real diagonal gradient.
2. **Running a 3x3 square.** Two error df; critical *F*(2,2) = 19.00. Replicate the square or choose another design.
3. **Leaving interactions in the model.** Zero error df and no *F* tests.
4. **Not wrapping row and col in `factor()`.** Fits linear trends with 1 df each.
5. **A square that is not Latin.** Every treatment exactly once per row *and* per column. Check before analysing; the Df checksum will catch it.
6. **Comparing row or column means.** Both are nuisance factors.
7. **Dropping non-significant row or column terms.** The randomisation was constrained by them.
8. **Using a Latin square when only one gradient exists.** You pay double and gain once. Use an RCBD.

## Practice

<details markdown="1">
<summary>1. A 5x5 Latin square. How many units, and what is the error df?</summary>

```
units    = p^2 = 25
error df = (p-1)(p-2) = 4 x 3 = 12
total df = 24 = 4 (rows) + 4 (cols) + 4 (trt) + 12 (error)
```

Twelve error df is **comfortable** -- critical *F*(4, 12) at .05 is 3.26, against 4.76 for *F*(4, 6) in a 4x4. Going from *p* = 4 to *p* = 5 adds 9 units and doubles the error df, which is the best trade available in this family of designs.

If 25 units are affordable, a 5x5 is the sweet spot for a Latin square. Below that you are squeezed on df; above *p* = 6 the unit count grows faster than the benefit.
</details>

<details markdown="1">
<summary>2. Is this a valid Latin square?</summary>

```
A B C
B C A
C A B
```

Check rows: ABC, BCA, CAB -- each contains all three letters exactly once. &#10003;
Check columns: ABC, BCA, CAB -- each contains all three letters exactly once. &#10003;

**Yes, it is a valid 3x3 Latin square.** But it should not be used.

Error df = (3&minus;1)(3&minus;2) = **2**. Critical *F*(2, 2) at alpha = .05 is 19.00. To reach significance, MS(treatment) would have to be 19 times MSE -- a bar so high that only an overwhelming effect clears it, and your confidence intervals would be useless regardless.

**The fix: replicate.** Run three independent 3x3 squares (27 units). Depending on whether rows and columns are the same physical entities across squares, you get between 12 and 18 error df -- a usable experiment. `agricolae::design.lsd` will generate the squares; the analysis adds a `square` term to the model.
</details>

<details markdown="1">
<summary>3. In our analysis, rows gave F = 2.83 (p = .13) and columns F = 0.33 (p = .80). Was the Latin square a mistake?</summary>

**Not a mistake, but it did not pay off**, and those are different judgements.

The design cost 6 error degrees of freedom. An RCBD on rows alone would have had 9; a CRD would have had 12. With MSE = 1.0 either way, fewer df means larger critical values: *t*(.975, 6) = 2.447 against *t*(.975, 12) = 2.179, so the CRD's LSD would have been about 11% narrower.

**Why it was still the right decision ex ante:** the field visibly sloped and the soil survey documented a depth gradient. Designing to control two observed sources of heterogeneity is sound practice. That they turned out not to affect *this* response is a finding, not a design error -- and it is useful information for the next experiment on that field.

**What makes it a mistake:** choosing the design out of habit, without evidence that two gradients exist. Or, worse, dropping the non-significant terms afterwards and reporting a CRD. The design you ran constrains the analysis you may report.

**The practical lesson:** a Latin square is insurance with a real premium. Buy it when you have evidence of two crossing gradients and the treatment effect is large enough to survive on few error df. Otherwise an RCBD on the dominant gradient usually gives a better experiment.
</details>

<details markdown="1">
<summary>4. Describe how a Latin square handles order effects in a repeated-measures taste test.</summary>

Four panellists each taste four products, and you want the product effect free of two contaminants: panellists differ in how harshly they score, and tasting position matters (palate fatigue, the first sample anchoring the rest, carry-over flavour).

```
            Position 1   Position 2   Position 3   Position 4
Panellist 1      A            B            C            D
Panellist 2      B            C            D            A
Panellist 3      C            D            A            B
Panellist 4      D            A            B            C
```

Rows = panellists, columns = position, treatments = products.

**What this buys you:** every product is tasted exactly once in every position, so position effects cancel in the product totals. And every panellist tastes every product, so panellist severity cancels too. The product effect emerges free of both.

**Why it beats the alternatives.** Giving all panellists the same order confounds product with position completely -- product A is always first. Randomising each panellist's order independently removes the confound on average but leaves position variation in the error term; the Latin square removes it exactly.

**The limit to watch:** the design removes the *average* position effect, but it assumes no **carry-over** -- that tasting A does not change how B scores specifically. If carry-over is likely (strong flavours, lingering aftertaste), a plain Latin square is not enough; you need a **Williams design** or another balanced crossover that also balances for the immediately preceding treatment. This is exactly why crossover clinical trials build in washout periods.
</details>

## Before you move on

- [ ] I know a Latin square requires *p* treatments, *p* rows, *p* columns and *p*&#178; units.
- [ ] I can compute error df as (*p*&minus;1)(*p*&minus;2) and say why *p* = 3 is unusable.
- [ ] I partition TSS four ways, dividing every total by *p*.
- [ ] I verify the 3-3-3-6 Df checksum before reading any *F*.
- [ ] I randomise rows, columns and letter assignment, never using the standard square.
- [ ] I report row and column *F* values honestly, including when they show the blocking did not pay.
- [ ] I know the repeated-measures application and the carry-over limitation.""",
    quiz={
        "question": "Why is a 3x3 Latin square almost never usable in practice?",
        "options": [
            "Three treatments cannot be randomised properly",
            "Error df = (3-1)(3-2) = 2, and critical F(2,2) at .05 is 19.00 — only an overwhelming effect could ever reach significance",
            "Nine plots is too few for any ANOVA",
            "The standard 3x3 square has no valid randomisation",
        ],
        "answer": 1,
        "explanation": "The Latin square spends 2(p-1) degrees of freedom on its two nuisance factors, which at p = 3 leaves only 2 for error. The remedy is to replicate the square: three 3x3 squares give 27 units and enough error df to work with.",
    },
)



# ===========================================================================
L(
    "Factorial Experiments and Interaction",
    """## What you will be able to do

Analyse two factors at once, partition the treatment sum of squares into main effects and interaction, read an interaction plot correctly, and -- the decision most students get wrong -- know when a significant interaction means you must stop interpreting the main effects.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
A study tests two factors on exam scores:

- **Factor A -- prior preparation:** Low or High (2 levels)
- **Factor B -- teaching method:** M1, M2 or M3 (3 levels)

Every combination is run, four students per cell. That is a **2 x 3 factorial** with *n* = 4, so 24 students.

Cell means:

| | M1 | M2 | M3 | Row mean |
|---|---|---|---|---|
| **Low** | 13.0 | 19.0 | 23.0 | 18.3333 |
| **High** | 21.0 | 24.0 | 25.0 | 23.3333 |
| **Column mean** | 17.0 | 21.5 | 24.0 | **20.8333** |

Raw data, four observations per cell:

```
Low  M1: 12, 14, 13, 13      High M1: 20, 22, 21, 21
Low  M2: 18, 20, 19, 19      High M2: 24, 25, 23, 24
Low  M3: 22, 24, 23, 23      High M3: 25, 26, 24, 25
```
</div>

## Why run two factors together rather than two experiments

Three reasons, and the third is the one that only a factorial can give you.

**Efficiency.** Twenty-four students give you a 6-replicate comparison of preparation levels *and* a 4-replicate comparison of methods, simultaneously. Two separate experiments of 24 students each would cost twice as much for the same precision. Every observation works for both factors -- this is called **hidden replication**.

**Wider validity.** A one-factor method experiment run only on well-prepared students tells you about well-prepared students. The factorial tests methods across both preparation levels, so the conclusion generalises further.

**Interaction.** Only a factorial can detect whether the effect of one factor **depends on the level of the other**. Two separate experiments cannot answer that question at all, no matter how large they are. And it is frequently the most important question in the study.

## The model

<div class="formula" markdown="1">
**Y&#7522;&#11388;&#8342; = &mu; + &alpha;&#7522; + &beta;&#11388; + (&alpha;&beta;)&#7522;&#11388; + &epsilon;&#7522;&#11388;&#8342;**
<span class="formula-note">&alpha; = main effect of A, &beta; = main effect of B, (&alpha;&beta;) = interaction, &epsilon; = error</span>
</div>

The interaction term is what separates a factorial from an RCBD with two blocking factors. It needs **replication within cells** to be estimable -- with *n* = 1 per cell, interaction and error are inseparable, exactly as in the RCBD.

## Working the ANOVA by hand

Cell totals (each over *n* = 4):

| | M1 | M2 | M3 | Row total |
|---|---|---|---|---|
| **Low** | 52 | 76 | 92 | 220 |
| **High** | 84 | 96 | 100 | 280 |
| **Column total** | 136 | 172 | 192 | **500** |

**Step 1. Constants.**

```
G = 500, N = 24, a = 2 levels of A, b = 3 levels of B, n = 4
CF = 500^2/24 = 250000/24 = 10416.6667
```

**Step 2. Total sum of squares.**

```
sum of all squared observations = 10816
TSS = 10816 - 10416.6667 = 399.3333
```

**Step 3. Main effect of A -- divide each row total by the number of observations behind it, which is b x n = 12.**

```
SS(A) = (220^2 + 280^2)/12 - 10416.6667
      = (48400 + 78400)/12 - 10416.6667
      = 126800/12 - 10416.6667
      = 10566.6667 - 10416.6667
      = 150.0
```

**Step 4. Main effect of B -- each column total is over a x n = 8 observations.**

```
SS(B) = (136^2 + 172^2 + 192^2)/8 - 10416.6667
      = (18496 + 29584 + 36864)/8 - 10416.6667
      = 84944/8 - 10416.6667
      = 10618.0 - 10416.6667
      = 201.3333
```

**Step 5. The cell (subtotal) sum of squares, then interaction by subtraction.**

```
SS(cells) = (52^2 + 76^2 + 92^2 + 84^2 + 96^2 + 100^2)/4 - 10416.6667
          = (2704 + 5776 + 8464 + 7056 + 9216 + 10000)/4 - 10416.6667
          = 43216/4 - 10416.6667
          = 10804.0 - 10416.6667
          = 387.3333

SS(A x B) = SS(cells) - SS(A) - SS(B)
          = 387.3333 - 150.0 - 201.3333
          = 36.0
```

<div class="callout callout-note" markdown="1">
<span class="callout-label">What the interaction sum of squares is</span>

SS(cells) captures **all** the variation among the six cell means. SS(A) and SS(B) capture the part explained by the two factors acting additively.

What is left over -- 36.0 -- is the variation among cell means that **cannot** be explained by adding the two main effects. That is the interaction, defined by subtraction, which is exactly what "the effect of A depends on B" means arithmetically.
</div>

**Step 6. Error by subtraction.**

```
SSE = TSS - SS(cells) = 399.3333 - 387.3333 = 12.0
```

**Step 7. The ANOVA table.**

| Source | SS | df | MS | F | p |
|---|---|---|---|---|---|
| A (preparation) | 150.0000 | 1 | 150.0000 | **225.00** | **1.29e-11** |
| B (method) | 201.3333 | 2 | 100.6667 | **151.00** | **5.64e-12** |
| A x B | 36.0000 | 2 | 18.0000 | **27.00** | **3.81e-06** |
| Error | 12.0000 | 18 | 0.6667 | | |
| **Total** | **399.3333** | **23** | | | |

Degrees of freedom: A = *a*&minus;1 = 1; B = *b*&minus;1 = 2; A x B = (*a*&minus;1)(*b*&minus;1) = 2; error = *ab*(*n*&minus;1) = 6(3) = 18; total = *N*&minus;1 = 23.

```
MSE = 12.0/18 = 0.6667
F(A)   = 150.0000/0.6667 = 225.00
F(B)   = 100.6667/0.6667 = 151.00
F(AxB) =  18.0000/0.6667 =  27.00
```

**All three are significant**, and the interaction is the one to interpret first.

## Effect sizes

Partial eta-squared is the standard report for factorials:

<div class="formula" markdown="1">
**partial eta&#178; = SS(effect) / [ SS(effect) + SSE ]**
<span class="formula-note">the proportion of variation explained by this effect, after removing the other effects</span>
</div>

```
partial eta^2 (A)   = 150.0/(150.0 + 12.0)     = .926
partial eta^2 (B)   = 201.3333/(201.3333 + 12) = .944
partial eta^2 (AxB) =  36.0/(36.0 + 12.0)      = .750
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Partial eta-squared does not sum to 1</span>

Here the three values add to 2.62. That is not an error -- each one uses a *different* denominator, because each removes the other effects before computing its share.

If you want values that partition the total, use plain eta-squared: SS(effect)/TSS, giving .376, .504 and .090, which sum to .970 with the remaining .030 being error. Report partial eta-squared (the convention, and what SPSS prints) but never describe it as a share of total variance.
</div>

## The interaction: reading it properly

**Step 1. Compute the simple effects** -- the effect of one factor *at each level* of the other.

Effect of preparation (High &minus; Low) at each method:

```
at M1:  21.0 - 13.0 = +8.0
at M2:  24.0 - 19.0 = +5.0
at M3:  25.0 - 23.0 = +2.0
```

Effect of method within each preparation level:

```
Low:   M1 13.0 -> M2 19.0 -> M3 23.0     spread = 10.0
High:  M1 21.0 -> M2 24.0 -> M3 25.0     spread =  4.0
```

**Step 2. Describe the pattern in words.** Both factors help, but **their benefits overlap**. Preparation matters a great deal under M1 (+8) and barely at all under M3 (+2). Equivalently: method choice matters a lot for poorly prepared students (a 10-point spread) and much less for well-prepared ones (4 points).

The mechanism is a **ceiling**: M3 and High preparation each get students close to the maximum, so combining them adds little. This is the most common interaction shape in education research and it has a name -- *ordinal* (or non-crossing) interaction, because the ordering of the levels never reverses.

**Step 3. The interaction plot.** Plot cell means with one factor on the x-axis and one line per level of the other.

```
score
  26 |                                  High M3  *
  25 |                       High M2 *        o  Low M3
  24 |                                        
  23 |                                 
  22 |            High M1 *            
  21 |                                 
  20 |                        o  Low M2
  19 |                                 
     |                                 
  14 |                                 
  13 |    o  Low M1                    
     +--------------------------------------------
          M1            M2            M3

  *  High preparation     o  Low preparation
```

**Parallel lines mean no interaction.** These lines converge -- the gap narrows from 8 to 5 to 2 -- so the interaction is real, and the convergence is its signature.

<div class="callout callout-note" markdown="1">
<span class="callout-label">Two kinds of interaction, and why the distinction matters</span>

**Ordinal (converging or diverging, non-crossing).** The ranking of levels is the same at every level of the other factor -- High always beats Low, M3 always beats M1. Main effects are still *meaningful* here: "High preparation is better" is true everywhere, it just varies in size.

**Disordinal (crossing lines).** The ranking reverses. Method M1 best for prepared students, M3 best for unprepared ones. Now the main effect of method is **actively misleading** -- the average across preparation levels describes no one, and reporting it would hide the finding.

Ours is ordinal, so we may still report the main effects -- with the interaction stated alongside. If the lines had crossed, the honest report would be the simple effects only.
</div>

## Simple-effects tests: the correct follow-up

With a significant interaction, test the effect of one factor *within* each level of the other rather than averaging over it.

Effect of method within the Low group (three means, *n* = 4, using the full-model MSE = 0.6667 with its 18 df):

```
SS(B within Low) = (52^2 + 76^2 + 92^2)/4 - 220^2/12
                 = (2704 + 5776 + 8464)/4 - 48400/12
                 = 16944/4 - 4033.3333
                 = 4236.0 - 4033.3333
                 = 202.6667

MS = 202.6667/2 = 101.3333
F(2, 18) = 101.3333/0.6667 = 152.00     p < .0001
```

Effect of method within the High group:

```
SS(B within High) = (84^2 + 96^2 + 100^2)/4 - 280^2/12
                  = (7056 + 9216 + 10000)/4 - 78400/12
                  = 26272/4 - 6533.3333
                  = 6568.0 - 6533.3333
                  = 34.6667

MS = 34.6667/2 = 17.3333
F(2, 18) = 17.3333/0.6667 = 26.00       p < .0001
```

Check your work: 202.6667 + 34.6667 = 237.3333 = SS(B) + SS(AxB) = 201.3333 + 36.0. &#10003;

That identity is worth noticing -- **the two simple effects of B together contain exactly the main effect of B plus the interaction**. It is why simple effects are the right decomposition when the interaction is significant.

Both are significant, but the *F* values differ by a factor of six (152 against 26). Method matters in both groups, far more so for the unprepared.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Use the pooled MSE, and correct for multiplicity</span>

Two details that separate a correct simple-effects analysis from a wrong one.

**Pooled MSE.** Use MSE from the full model (0.6667, df 18), not a fresh one-way ANOVA within each subgroup. The full model's error estimate uses all 24 observations and has 18 df; a within-subgroup ANOVA would have only 9. Pooling assumes equal variances across all cells -- which you should check, and which is already an ANOVA assumption.

**Multiplicity.** You are running *a* = 2 simple-effects tests, so adjust. Bonferroni at alpha = .05/2 = .025 is the simple option. Both of ours survive easily, but a borderline result would not.
</div>

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span>

**Analyses -> ANOVA -> ANOVA.**
Dependent: score. Fixed Factors: prep and method.
Here you **keep** the default full factorial model -- unlike the RCBD and Latin square, the interaction is the point.
Under *Effect size* tick **partial eta-squared**.
Under *Estimated Marginal Means*, add a term containing **both** factors to get the interaction plot; tick *Observed scores* to overlay the data.
Under *Post Hoc Tests* move the interaction term across for cell-by-cell comparisons, or use **Simple Effects** in the *Estimated Marginal Means* panel.
</div>

**SPSS.** `Analyze -> General Linear Model -> Univariate`. Fixed Factors: prep and method. Leave the model as *Full factorial*. Then:

- *Options* -> tick **Descriptive statistics**, **Estimates of effect size**, **Homogeneity tests**.
- *Plots* -> put method on the *Horizontal Axis* and prep in *Separate Lines*, click Add. This is the interaction plot.
- *EM Means* -> move `prep*method` into *Display Means for*, tick **Compare main effects**, and set the confidence-interval adjustment to Bonferroni.

For proper simple-effects tests, SPSS needs syntax:

```
UNIANOVA score BY prep method
  /EMMEANS = TABLES(prep*method) COMPARE(method) ADJ(BONFERRONI)
  /PRINT = ETASQ DESCRIPTIVE
  /DESIGN = prep method prep*method.
```

The `COMPARE(method)` keyword is what produces the method comparisons *within* each preparation level.

**Excel.** The ToolPak handles balanced factorials: `Data -> Data Analysis -> Anova: Two-Factor With Replication`.

Lay the data out with factor A levels as row blocks (4 rows each) and factor B levels as columns, with labels in the first row and first column. Set *Rows per sample* to 4. The output:

```
Source         SS        df   MS        F        P-value
Sample        150.0000    1  150.0000  225.00   1.29E-11     <- factor A
Columns       201.3333    2  100.6667  151.00   5.64E-12     <- factor B
Interaction    36.0000    2   18.0000   27.00   3.81E-06
Within         12.0000   18    0.6667
Total         399.3333   23
```

"Sample" is the row factor, "Columns" the column factor, "Within" is error. Excel gives no plot and no post-hoc tests, but the table is exactly right -- and this is the one design where Excel's ToolPak genuinely does the whole analysis. Build the interaction plot manually from the cell means with a line chart.

**R.**

```r
d <- data.frame(
  prep   = factor(rep(c("Low","High"), each = 12), levels = c("Low","High")),
  method = factor(rep(rep(c("M1","M2","M3"), each = 4), 2)),
  score  = c(12,14,13,13, 18,20,19,19, 22,24,23,23,
             20,22,21,21, 24,25,23,24, 25,26,24,25))

m <- aov(score ~ prep * method, data = d)
summary(m)
#              Df Sum Sq Mean Sq F value   Pr(>F)
# prep          1  150.0  150.00     225 1.29e-11 ***
# method        2  201.3  100.67     151 5.64e-12 ***
# prep:method   2   36.0   18.00      27 3.81e-06 ***
# Residuals    18   12.0    0.67

effectsize::eta_squared(m, partial = TRUE)    # .926, .944, .750

# the interaction plot
interaction.plot(d$method, d$prep, d$score,
                 ylab = "score", xlab = "method", trace.label = "prep")

# simple effects, done properly
library(emmeans)
em <- emmeans(m, ~ method | prep)
joint_tests(m, by = "prep")       # F(2,18) = 152 for Low, 26 for High
pairs(em, adjust = "bonferroni")  # method comparisons within each prep level

emmeans(m, ~ prep | method) |> pairs()   # prep effect at each method: 8, 5, 2
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">`prep * method` versus `prep + method`</span>

In R's formula notation, `*` means "both main effects **and** their interaction"; `+` means main effects only.

Writing `score ~ prep + method` fits the additive model, which forces the 36.0 of interaction into the error term: SSE becomes 48.0 on 20 df, MSE becomes 2.40, and every *F* shrinks by a factor of 3.6. You would still find both main effects here because they are enormous, but you would miss the interaction entirely -- and the interaction is the finding.

Use `*` whenever the design has replication within cells. Use `+` only when you *cannot* estimate the interaction (RCBD, Latin square) or have a specific reason to assume additivity.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">APA, factorial with a significant interaction</span>

"A 2 x 3 between-subjects ANOVA found significant main effects of prior preparation, *F*(1, 18) = 225.00, *p* &lt; .001, partial eta&#178; = .93, and teaching method, *F*(2, 18) = 151.00, *p* &lt; .001, partial eta&#178; = .94, together with a significant interaction, *F*(2, 18) = 27.00, *p* &lt; .001, partial eta&#178; = .75.

The interaction was ordinal: the advantage of high preparation declined across methods, from 8.0 points under M1 to 5.0 under M2 and 2.0 under M3. Simple-effects tests confirmed that method mattered in both groups but far more for less-prepared students, *F*(2, 18) = 152.00, *p* &lt; .001, than for well-prepared ones, *F*(2, 18) = 26.00, *p* &lt; .001 (Bonferroni-adjusted). The pattern is consistent with a ceiling: M3 and high preparation each bring students close to the maximum attainable score, so their benefits do not accumulate.

Practically, method choice matters most where preparation is weakest -- the 10-point spread across methods in the low-preparation group narrows to 4 points in the high-preparation group."
</div>

Note the structure: the full table first, then the interaction described in plain language with its numbers, then the simple effects, then one sentence on what it means for practice. The interaction is reported *before* being interpreted, and the main effects are not abandoned because the interaction is ordinal.

## Common mistakes

1. **Interpreting main effects without checking the interaction first.** Always read the interaction line first.
2. **Reporting main effects after a *disordinal* interaction.** If the lines cross, the average effect describes nobody. Report simple effects.
3. **Fitting `+` instead of `*`.** The interaction sum of squares lands in error, inflating MSE and deflating every *F*.
4. **Claiming "no interaction" from a non-significant *F*.** With small *n*, interaction tests are badly underpowered -- interaction effects typically need around four times the sample size of main effects. Say "no interaction was detected", and report the effect size.
5. **Saying partial eta-squared values partition the variance.** Different denominators; they can sum past 1.
6. **Running separate one-way ANOVAs within each subgroup for simple effects.** Use the pooled MSE from the full model, with its larger df.
7. **Forgetting to adjust for multiplicity across simple-effects tests.**
8. **Removing the interaction term because it is not significant, then reporting the simplified model as if planned.** If you do pool it into error, say so.

## Practice

<details markdown="1">
<summary>1. A 2 x 2 factorial with n = 5 per cell. What are the four degrees of freedom in the ANOVA table?</summary>

```
A         : a - 1           = 1
B         : b - 1           = 1
A x B     : (a-1)(b-1)      = 1
Error     : ab(n-1) = 4(4)  = 16
Total     : N - 1 = 20 - 1  = 19

check: 1 + 1 + 1 + 16 = 19   OK
```

A 2 x 2 is the smallest useful factorial and it has a convenient property: every effect has 1 df, so each *F* has a corresponding *t* with *F* = *t*&#178;, and each effect is a single contrast with an unambiguous direction. No post-hoc tests are ever needed -- with two levels, a significant *F* already tells you which is higher.
</details>

<details markdown="1">
<summary>2. Cell means are A1B1 = 10, A1B2 = 20, A2B1 = 20, A2B2 = 30. Is there an interaction?</summary>

Compute the effect of B at each level of A:

```
at A1:  20 - 10 = +10
at A2:  30 - 20 = +10
```

**Identical.** No interaction -- the effect of B is +10 regardless of A.

Formally, the interaction contrast is (A1B1 &minus; A1B2) &minus; (A2B1 &minus; A2B2) = (10&minus;20) &minus; (20&minus;30) = &minus;10 &minus; (&minus;10) = **0**, so SS(AxB) = 0 exactly.

This is **perfect additivity**: the cell mean is the grand mean plus a row effect plus a column effect, with nothing left over. Plotted, the two lines are exactly parallel.

Compare with our worked example, where the effect of preparation was +8, +5, +2 -- changing across levels of method, which is what made SS(AxB) = 36.0 rather than 0.
</details>

<details markdown="1">
<summary>3. Cell means are A1B1 = 10, A1B2 = 25, A2B1 = 25, A2B2 = 10. Describe the main effects and the interaction.</summary>

Marginal means:

```
A1 = (10 + 25)/2 = 17.5        A2 = (25 + 10)/2 = 17.5
B1 = (10 + 25)/2 = 17.5        B2 = (25 + 10)/2 = 17.5
```

**Both main effects are exactly zero.** SS(A) = 0 and SS(B) = 0.

But the cell means range from 10 to 25, so there is a great deal of variation among them -- and all of it is interaction. The interaction contrast is (10&minus;25) &minus; (25&minus;10) = &minus;15 &minus; 15 = &minus;30, the largest possible given these values.

The pattern is **purely disordinal**: B2 is better than B1 at level A1 (25 vs 10), and worse at level A2 (10 vs 25). The lines cross in an X.

**The lesson, and it is the central one of this lesson:** a factorial can find a large, important effect where both main effects are zero. Had you run two separate single-factor experiments, both would have returned "no effect" and you would have concluded nothing is going on -- when in fact the combination matters enormously.

**How to report it:** the main effects are not merely uninformative, they are *actively misleading*. Report the interaction, the cell means, and the simple effects. Do not report "no effect of A" as a finding.
</details>

<details markdown="1">
<summary>4. Your interaction is F(2, 18) = 2.4, p = .12, partial eta-squared = .21. Can you conclude the factors are additive?</summary>

No. You can conclude only that **this experiment did not detect an interaction**, which is a much weaker statement.

The effect size is the reason to be careful. A partial eta-squared of .21 is a *large* effect by conventional benchmarks (.01 small, .06 medium, .14 large). You have a large estimated interaction that failed to reach significance -- which is the signature of an underpowered test, not of additivity.

**Why this happens so often.** Interaction tests are inherently less powerful than main-effect tests. A main effect in our 2 x 3 design is estimated from 12 observations per level; the interaction is a contrast of contrasts, estimated from the cell means, and its standard error is correspondingly larger. The usual rule of thumb is that detecting an interaction of a given size needs roughly **four times** the sample size needed for a main effect of that size.

**What to report:** "No significant interaction was detected, *F*(2, 18) = 2.40, *p* = .12, though the effect size was substantial (partial eta&#178; = .21), so the study was underpowered to detect an interaction of this magnitude. Main effects are therefore reported with that caveat."

**What not to do:** drop the interaction term, re-run the additive model, and present it as the planned analysis. If you do pool the interaction into error to gain degrees of freedom, state that you did and why.
</details>

<details markdown="1">
<summary>5. Why do the two simple effects of B (202.6667 and 34.6667) sum to SS(B) + SS(AxB)?</summary>

Because together they account for all the variation among the six cell means that involves B -- and that variation is exactly SS(B) + SS(AxB).

Think of it as two ways to slice the same thing. SS(cells) = 387.3333 is the total variation among cell means, and it decomposes as SS(A) + SS(B) + SS(AxB) = 150 + 201.3333 + 36.

The simple effects of B slice it differently: SS(B within Low) + SS(B within High) = 202.6667 + 34.6667 = 237.3333 captures all the within-row variation, leaving SS(A) = 150 as the between-row part. And 237.3333 = 201.3333 + 36 = SS(B) + SS(AxB). &#10003;

**Why this matters practically.** It shows that simple effects are not an extra, optional analysis bolted on after the fact -- they are an **alternative complete decomposition** of the same sums of squares. When the interaction is significant, the simple-effects slicing is the one that describes the data honestly, because it never averages an effect over conditions where that effect differs.

It is also a free arithmetic check. If your two simple-effects sums of squares do not add to SS(B) + SS(AxB), you have made an error.
</details>

## Before you move on

- [ ] I can partition SS(cells) into SS(A), SS(B) and SS(AxB), getting the interaction by subtraction.
- [ ] I divide row totals by *bn* and column totals by *an*, and I know which is which.
- [ ] I read the interaction line of the table **before** the main effects.
- [ ] I can tell an ordinal interaction from a disordinal one and know what each permits me to report.
- [ ] I can compute simple effects and verify they sum to SS(B) + SS(AxB).
- [ ] I use the pooled MSE for simple effects and adjust for multiplicity.
- [ ] I know `*` includes the interaction and `+` does not.
- [ ] I never read a non-significant interaction as proof of additivity, and I report its effect size.""",
    quiz={
        "question": "Cell means are A1B1 = 10, A1B2 = 25, A2B1 = 25, A2B2 = 10. What should you report?",
        "options": [
            "No effects, since both marginal means are 17.5 and SS(A) = SS(B) = 0",
            "A large disordinal interaction with the cell means and simple effects — the zero main effects are misleading, not a finding",
            "Only the main effects, because the interaction cannot be interpreted without more data",
            "An ordinal interaction, since all four cell means are between 10 and 25",
        ],
        "answer": 1,
        "explanation": "Both main effects are exactly zero, yet the cell means span 10 to 25 — all of that variation is interaction. B2 beats B1 at A1 and loses at A2, so the lines cross. Two separate single-factor experiments would both have reported nothing.",
    },
)


# ===========================================================================
L(
    "Split-Plot Designed Experiments",
    """## What you will be able to do

Recognise when a design has **two different experimental units** and therefore two error terms, build the split-plot ANOVA table by hand, test each effect against the correct error, and see exactly what goes wrong when the two errors are pooled.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
Two irrigation systems and three crop varieties, in four blocks.

Irrigation cannot be applied to a small plot -- the pipework serves a whole strip, and water spreads. So each block is divided into two large strips, one per irrigation system, and each strip is then divided into three small plots, one per variety.

| Block | Irrigation | V1 | V2 | V3 |
|---|---|---|---|---|
| 1 | I1 | 31.2 | 33.0 | 37.4 |
| 1 | I2 | 33.4 | 40.6 | 43.8 |
| 2 | I1 | 26.4 | 31.1 | 32.0 |
| 2 | I2 | 35.0 | 38.7 | 44.5 |
| 3 | I1 | 33.1 | 34.6 | 39.5 |
| 3 | I2 | 34.8 | 42.0 | 45.3 |
| 4 | I1 | 29.3 | 34.1 | 35.3 |
| 4 | I2 | 33.8 | 38.1 | 42.6 |

Grand total 869.6, *N* = 24, grand mean 36.2333.
</div>

**This is not a factorial with blocks.** In a factorial, every treatment combination is assigned to its own independently randomised unit. Here irrigation was randomised to **strips** and variety to **plots within strips**. Two levels of randomisation means two sizes of experimental unit, and therefore two error terms.

## The idea: two experimental units, two errors

| Level | Experimental unit | Factor assigned to it | Error term |
|---|---|---|---|
| **Whole plot** | The strip (8 of them) | Irrigation | **Error A** (block x irrigation) |
| **Sub-plot** | The small plot (24 of them) | Variety, and irrigation x variety | **Error B** (residual) |

The replication differs too. Irrigation has **4 replications** -- one strip per block. Variety has **8** -- one plot in each of the eight strips.

<div class="callout callout-note" markdown="1">
<span class="callout-label">The one sentence that makes split-plot analysis make sense</span>

**Every effect must be tested against the error term of the unit it was randomised to.**

Irrigation was randomised to strips, so it is tested against strip-to-strip error (Error A). Variety was randomised to plots within strips, so it is tested against plot-to-plot error (Error B). The interaction involves comparing varieties *within* strips, so it too belongs at the sub-plot level and is tested against Error B.

Error A has 3 df and is large. Error B has 12 df and is small. Using the wrong one does not give a slightly wrong answer -- it gives a badly wrong one, as the calculation below shows.
</div>

## Why anyone would choose this design

Rarely for statistical reasons. Usually because of a physical constraint:

- **Machinery.** A tillage implement, a sprayer, an irrigation line covers a wide strip. You cannot till one square metre.
- **Spillover.** Water, fertiliser drift, smoke, temperature -- treatments that cannot be confined to a small plot.
- **Logistics.** An oven temperature, a kiln setting, a classroom-level intervention.
- **A deliberate precision trade.** You accept low precision on the whole-plot factor in exchange for high precision on the sub-plot factor and the interaction. If variety is your real interest and irrigation is background, that trade is a win.

The cost is stated plainly: **the whole-plot factor is tested with few degrees of freedom and a large error.** If irrigation is the factor you care most about, a split-plot is the wrong design.

## The model

<div class="formula" markdown="1">
**Y&#7522;&#11388;&#8342; = &mu; + &rho;&#8342; + &alpha;&#7522; + (&rho;&alpha;)&#7522;&#8342; + &beta;&#11388; + (&alpha;&beta;)&#7522;&#11388; + &epsilon;&#7522;&#11388;&#8342;**
<span class="formula-note">&rho; = block, &alpha; = whole-plot factor, (&rho;&alpha;) = Error A, &beta; = sub-plot factor, (&alpha;&beta;) = interaction, &epsilon; = Error B</span>
</div>

The term that does the work is **(&rho;&alpha;)&#7522;&#8342;**, the block x whole-plot-factor interaction. It *is* Error A -- there is no replication of strips within a block, so that interaction and whole-plot error are the same thing.

## Working it by hand

**Step 1. Constants.**

```
G = 869.6, N = 24
b = 4 blocks, w = 2 whole-plot levels, s = 3 sub-plot levels
CF = 869.6^2/24 = 756204.16/24 = 31508.5067
TSS = 582.5133
```

**Step 2. The whole-plot analysis** -- work with the eight strip totals (each over 3 plots).

Strip totals:

```
block 1: I1 = 101.6   I2 = 117.8
block 2: I1 =  89.5   I2 = 118.2
block 3: I1 = 107.2   I2 = 122.1
block 4: I1 =  98.7   I2 = 114.5
```

```
SS(block)  = (block totals^2)/6 - CF        =  42.8900
SS(irr)    = (irrigation totals^2)/12 - CF  = 238.1400
SS(strips) = (strip totals^2)/3 - CF        = 302.5200

SS(Error A) = SS(strips) - SS(block) - SS(irr)
            = 302.5200 - 42.8900 - 238.1400
            = 21.4900
```

Error A is the variation among strips that neither block nor irrigation explains -- exactly the block x irrigation interaction.

**Step 3. The sub-plot analysis.**

```
SS(var)     = (variety totals^2)/8 - CF             = 252.2433
SS(irr x var) = (cell totals^2)/4 - CF - SS(irr) - SS(var)
              = 14.4300

SS(Error B) = TSS - SS(strips) - SS(var) - SS(irr x var)
            = 582.5133 - 302.5200 - 252.2433 - 14.4300
            = 13.3200
```

**Step 4. The ANOVA table, with the two error lines in place.**

| Source | SS | df | MS | F | p |
|---|---|---|---|---|---|
| Block | 42.8900 | 3 | 14.2967 | 1.996 | .292 |
| **Irrigation** | 238.1400 | 1 | 238.1400 | **33.244** | **.0104** |
| **Error A** (block x irr) | 21.4900 | 3 | **7.1633** | | |
| **Variety** | 252.2433 | 2 | 126.1217 | **113.623** | **&lt; .0001** |
| **Irrigation x Variety** | 14.4300 | 2 | 7.2150 | **6.500** | **.0122** |
| **Error B** | 13.3200 | 12 | **1.1100** | | |
| **Total** | **582.5133** | **23** | | | |

Degrees of freedom:

```
block        : b - 1                = 3
irrigation   : w - 1                = 1
Error A      : (b-1)(w-1)           = 3
variety      : s - 1                = 2
irr x var    : (w-1)(s-1)           = 2
Error B      : w(b-1)(s-1) = 2(3)(2)= 12
total        : N - 1                = 23

check: 3 + 1 + 3 + 2 + 2 + 12 = 23   OK
```

The *F* ratios, each against the right denominator:

```
F(irrigation)  = 238.1400 / 7.1633 = 33.244    df (1, 3)    <- Error A
F(block)       =  14.2967 / 7.1633 =  1.996    df (3, 3)    <- Error A
F(variety)     = 126.1217 / 1.1100 = 113.623   df (2, 12)   <- Error B
F(irr x var)   =   7.2150 / 1.1100 =   6.500   df (2, 12)   <- Error B
```

**Notice the two mean squares for error: 7.1633 and 1.1100.** Error A is 6.5 times larger than Error B. That is the design working as designed -- strips vary a lot more than plots within a strip, which is why irrigation had to go on the strips in the first place.

## What happens if you pool the errors

This is the calculation that justifies the whole lesson.

Suppose you ignored the structure and ran an ordinary factorial ANOVA with blocks -- one error term:

```
pooled SSE = 21.4900 + 13.3200 = 34.8100     df = 3 + 12 = 15
pooled MSE = 34.8100/15 = 2.3207

F(irrigation) = 238.1400/2.3207 = 102.62     df (1, 15)    p = 4.2e-08
```

| | MS error | df | F(irrigation) | p |
|---|---|---|---|---|
| **Correct** (Error A) | 7.1633 | 3 | **33.24** | **.0104** |
| **Pooled** (wrong) | 2.3207 | 15 | **102.62** | **.00000004** |

The *p*-value drops by more than five orders of magnitude -- from .01 to .00000004.

Both reject here, so the *conclusion* happens to survive. But the pooled analysis is **anticonservative by a factor of three in *F***, and it would manufacture significance for a whole-plot effect that the design genuinely cannot detect. Irrigation has only four replications; pretending it has 24 is not a rounding error, it is pseudoreplication at the whole-plot level.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">This is the most common serious error in agricultural and educational statistics</span>

A classroom-level intervention delivered to 6 classes of 30 students, analysed as *n* = 180. An oven temperature applied to 4 batches of 20 items, analysed as *n* = 80. A hospital-level protocol across 8 wards, analysed per patient.

Every one of these is a split-plot or a cluster design analysed as if it were fully randomised. The whole-plot factor gets tested against sub-plot error, the *F* is inflated several-fold, and the published effect is not supported by the design.

The diagnostic question is always the same: **what was each factor randomised to?** If the answer differs between factors, you have more than one error term.
</div>

## Standard errors: they differ by the comparison

Because there are two error terms, there is no single standard error. Which one you need depends on what you are comparing.

**Comparing two whole-plot (irrigation) means** -- each is an average of *b* x *s* = 12 observations, but the relevant variation is strip-to-strip:

```
SE of difference = sqrt( 2 x MS(Error A) / (b x s) )
                 = sqrt( 2 x 7.1633 / 12 )
                 = sqrt( 1.19389 )
                 = 1.0927
```

**Comparing two sub-plot (variety) means** -- each averages *b* x *w* = 8 observations, and the relevant variation is plot-to-plot:

```
SE of difference = sqrt( 2 x MS(Error B) / (b x w) )
                 = sqrt( 2 x 1.1100 / 8 )
                 = sqrt( 0.2775 )
                 = 0.5268
```

The variety comparison is roughly **twice as precise** as the irrigation comparison -- despite irrigation means being averages of more observations. That is the trade the design makes, quantified.

**Comparing two sub-plot means within the same whole plot** uses Error B. **Comparing two sub-plot means across different whole plots** needs a combination of both error terms, and the resulting *t* has no exact degrees of freedom -- Satterthwaite's approximation is used. Let software handle that one.

## Marginal means

Irrigation: I1 = 33.0833, I2 = 39.3833 (difference 6.30, SE 1.0927).

Variety: V1 = 32.1250, V2 = 36.5250, V3 = 40.0500.

Cell means:

| | V1 | V2 | V3 | Row mean |
|---|---|---|---|---|
| **I1** | 30.00 | 33.20 | 36.05 | 33.0833 |
| **I2** | 34.25 | 39.85 | 44.05 | 39.3833 |
| Difference | 4.25 | 6.65 | 8.00 | 6.30 |

The interaction (*p* = .012) is visible in that last row: the irrigation advantage **grows** from 4.25 on V1 to 8.00 on V3. The lines diverge -- an ordinal interaction, since I2 beats I1 at every variety, but the size of the gain depends on which variety you plant. V3 responds best to the better irrigation system.

That is a genuinely useful agronomic finding, and it is the kind of result only a factorial structure can produce.

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span>

Base Jamovi's ANOVA cannot fit two error terms. Two routes:

**GAMLj module** (install via the + menu) -> **Mixed Model**. Dependent: yield. Fixed: irrigation, variety, their interaction. Random effects: `Intercept | block` and `Intercept | block:irrigation`. That second random term is what creates Error A.

**Rj module** -> paste the R code below. For a design this structured, this is often the faster path.
</div>

**SPSS.** `Analyze -> General Linear Model -> Univariate`. Dependent: yield. Fixed Factors: irrigation, variety. **Random Factor(s): block.** Then *Model -> Custom* and build:

```
block
irrigation
block*irrigation        <- this becomes Error A
variety
irrigation*variety
```

SPSS computes the expected mean squares and selects the correct error term for each line automatically once `block` is declared random and `block*irrigation` is in the model. Check the output's "Expected Mean Squares" footnotes to confirm that irrigation is being tested against `block*irrigation` and not against the residual.

Alternatively `Analyze -> Mixed Models -> Linear`, which is the more modern route and handles unbalanced data.

**Excel.** Not realistically. The ToolPak has no facility for multiple error terms. You can compute the six sums of squares by hand with `SUMSQ` over the strip, block, treatment and cell totals -- which is exactly what we did above and is a worthwhile exercise -- but there is no automated path, and the *F* ratios would have to be assembled manually.

**R.**

```r
d <- expand.grid(var = c("V1","V2","V3"),
                 irr = c("I1","I2"),
                 block = factor(1:4))
d$y <- c(31.2,33.0,37.4, 33.4,40.6,43.8,
         26.4,31.1,32.0, 35.0,38.7,44.5,
         33.1,34.6,39.5, 34.8,42.0,45.3,
         29.3,34.1,35.3, 33.8,38.1,42.6)

# classical aov with an explicit error stratum
m <- aov(y ~ irr * var + Error(block/irr), data = d)
summary(m)

# Error: block
#           Df Sum Sq Mean Sq F value Pr(>F)
# Residuals  3  42.89   14.30

# Error: block:irr
#           Df Sum Sq Mean Sq F value Pr(>F)
# irr        1 238.14  238.14   33.24 0.0104 *
# Residuals  3  21.49    7.16

# Error: Within
#           Df Sum Sq Mean Sq F value   Pr(>F)
# var        2 252.24  126.12  113.62 1.06e-08 ***
# irr:var    2  14.43    7.22    6.50   0.0122 *
# Residuals 12  13.32    1.11

# the modern equivalent, which also handles unbalanced data
library(lmerTest)
m2 <- lmer(y ~ irr * var + (1|block) + (1|block:irr), data = d)
anova(m2)

library(emmeans)
emmeans(m2, ~ irr)                  # SE uses Error A
emmeans(m2, ~ var)                  # SE uses Error B
emmeans(m2, ~ var | irr) |> pairs()
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">`Error(block/irr)` is the whole design, in six characters</span>

The `/` means nesting: *irrigation strips are nested within blocks*. That one expression tells `aov` to build three strata -- block, block-within-irrigation (Error A), and within (Error B) -- and to place each effect in the correct one.

Drop it and write `aov(y ~ block + irr * var)` and you get the pooled analysis: a single residual of 2.3207 on 15 df and *F*(irrigation) = 102.62. The output looks perfectly normal. Nothing warns you. **The structure is only in the model if you put it there.**

Check the output has three `Error:` strata before reading anything else. That is your checksum for this design.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Agronomy / APA report</span>

"The experiment used a split-plot design in four randomised complete blocks. Irrigation system was assigned to whole plots (strips) because the irrigation line serves a full strip; the three varieties were assigned to sub-plots within each strip. Whole-plot and sub-plot effects were tested against their respective error terms.

Irrigation significantly affected yield, *F*(1, 3) = 33.24, *p* = .010, with I2 out-yielding I1 by 6.30 t/ha (SE 1.09). Variety was also significant, *F*(2, 12) = 113.62, *p* &lt; .001, as was the irrigation x variety interaction, *F*(2, 12) = 6.50, *p* = .012. The irrigation advantage increased across varieties, from 4.25 t/ha for V1 to 6.65 for V2 and 8.00 for V3, indicating that V3 exploits the improved irrigation system most effectively.

Error mean squares were 7.16 (whole plot, 3 df) and 1.11 (sub-plot, 12 df). Standard errors of a difference were 1.09 for irrigation means and 0.53 for variety means, reflecting the lower precision the design necessarily affords the whole-plot factor."
</div>

Three things that paragraph does which a split-plot write-up must: it says **why** the design was split (the physical constraint), it reports **both** error mean squares with their df, and it gives the two different standard errors. Without those, a reader cannot tell whether you analysed the design or just ran a factorial on it.

## Common mistakes

1. **Pooling the two error terms.** The single most consequential error here. *F* for the whole-plot factor is inflated several-fold.
2. **Reporting one standard error for all comparisons.** There are at least two, and the across-whole-plot comparison needs a third.
3. **Putting the factor you care about on the whole plot.** It gets the fewest df and the largest error. Put it on the sub-plot if the physics allows.
4. **Omitting `Error(block/irr)` in R, or `block*irrigation` in SPSS.** Both silently produce the pooled analysis.
5. **Calling it a factorial.** A split-plot is a *restricted* randomisation. The restriction is the whole point.
6. **Confusing it with a repeated-measures design.** They are structurally similar (subjects as whole plots, time as sub-plots) but repeated measures adds a correlation structure over time that a split-plot does not assume. Repeated measures needs sphericity checks; a split-plot does not.
7. **Interpreting a non-significant whole-plot factor as "no effect".** With 3 error df, critical *F*(1,3) at .05 is 10.13. The design has very little power there.

## Practice

<details markdown="1">
<summary>1. A split-plot has 3 blocks, 2 whole-plot treatments and 4 sub-plot treatments. Give the full df breakdown.</summary>

```
block        : b - 1                   =  2
whole-plot   : w - 1                   =  1
Error A      : (b-1)(w-1)              =  2
sub-plot     : s - 1                   =  3
w x s        : (w-1)(s-1)              =  3
Error B      : w(b-1)(s-1) = 2(2)(3)   = 12
                                         --
total        : N - 1 = 24 - 1          = 23
check: 2 + 1 + 2 + 3 + 3 + 12 = 23   OK
```

**Error A has 2 df**, which is close to unusable: critical *F*(1, 2) at alpha = .05 is **18.51**. The whole-plot treatment would need a mean square more than eighteen times Error A to register.

**The fix is more blocks, and only more blocks.** Error A df = (*b*&minus;1)(*w*&minus;1), so with *w* = 2 fixed it is simply *b* &minus; 1. Going to 6 blocks gives 5 error-A df and critical *F*(1,5) = 6.61; going to 9 blocks gives 8 df and *F*(1,8) = 5.32. Adding sub-plot treatments does nothing for the whole-plot test.

This is the standard planning rule for split-plots: **the number of blocks is what determines whether the whole-plot factor is testable at all.**
</details>

<details markdown="1">
<summary>2. Why is MS(Error A) = 7.16 so much larger than MS(Error B) = 1.11?</summary>

Because they measure variation at two different physical scales.

**Error B** is variation among small plots *inside the same strip*. Those plots share irrigation, soil type, drainage, slope, management and microclimate. They differ only in what the variety does and in small-scale measurement noise. Very little room for variation -- hence 1.11.

**Error A** is variation among whole strips. Strips are large, far apart, and differ in soil depth, drainage, previous cropping, edge exposure and anything else that varies over metres rather than centimetres. All of that is in Error A -- hence 7.16.

**This is not a flaw; it is the reason the design exists.** Strips vary a lot, which is precisely why you could not randomise irrigation to small plots. And because sub-plots within a strip are so uniform, variety and the interaction are tested with unusual precision.

**The ratio tells you something useful.** A ratio near 1 means strips were no more variable than plots, in which case a plain factorial would have been simpler and better. A large ratio like 6.5 confirms the split was necessary. Report both mean squares and let the reader see it.
</details>

<details markdown="1">
<summary>3. A researcher applies a reading programme to 6 classes (3 per programme) and tests 30 students per class, analysing n = 180. What is wrong and what is the correct analysis?</summary>

**The error:** the programme was applied to the *class*, so the class is the whole-plot experimental unit. There are **3 classes per programme, not 90 students**. Analysing *n* = 180 tests the programme against student-to-student error when it should be tested against class-to-class error -- exactly the pooling error from this lesson.

Students in a class share a teacher, a timetable, a peer group and a room. They are not independent. Treating them as independent replicates of the programme understates the standard error by roughly &radic;(1 + (*m*&minus;1)&rho;), where *m* = 30 and &rho; is the intraclass correlation. With a typical classroom ICC of .15, that factor is about 2.3 -- so the reported *t* is more than twice what it should be.

**The correct analyses, in increasing sophistication:**

**Aggregate.** Compute each class's mean and run a *t*-test on 6 numbers, 3 per group. Error df = 4. Low power, but valid and easy to defend.

**Split-plot / nested ANOVA.** Treat class as a random effect nested within programme. The programme is tested against the class-within-programme mean square -- the Error A analogue. Same *F* as the aggregate analysis in the balanced case, but it also lets you estimate how much variance sits at each level.

**Multilevel (mixed) model.** `lmer(score ~ programme + (1|class))`. This is the modern standard for clustered educational data. It keeps the student-level data (so student-level covariates like pretest can be included) while attributing the programme effect to the correct level, and it reports the ICC.

**What the researcher should also report:** the ICC, and the number of clusters. With 6 clusters any of these analyses has very little power -- the real problem is the design, and more classes, not more students per class, is the only fix.
</details>

<details markdown="1">
<summary>4. Your whole-plot factor gives F(1, 3) = 6.2, p = .088. Is there no effect?</summary>

You cannot say that. What you can say is that **this design had very little power to detect one**.

Critical *F*(1, 3) at alpha = .05 is **10.13**. Your 6.2 is well short of it, but 6.2 is also not a small *F* -- it corresponds to a substantial effect. With 3 error degrees of freedom the bar is simply very high.

Quantify it. The effect size is *F*/(*F* + df_error) = 6.2/9.2 = **.67** as a partial eta-squared -- large by any benchmark. So you have a large estimated effect that cannot be certified at 4 whole-plot replications.

**What to report:** "The whole-plot effect did not reach significance, *F*(1, 3) = 6.20, *p* = .088, though with only three whole-plot error degrees of freedom the design had limited power; the observed partial eta-squared of .67 suggests a substantial effect that a larger number of blocks would be needed to confirm."

**What to do next time:** more blocks. Going from 4 blocks to 8 takes Error A df from 3 to 7, dropping the critical *F*(1,7) to 5.59 -- which your observed 6.2 would clear. Note again that adding sub-plot treatments would not have helped at all.

**What not to do:** pool the errors to get more df. That is the error this lesson exists to prevent, and it would turn an honest *p* = .088 into a fabricated one.
</details>

## Before you move on

- [ ] I can tell a split-plot from a factorial by asking what each factor was randomised to.
- [ ] I can state which error term tests each effect, and why.
- [ ] I can compute SS(Error A) as SS(strips) &minus; SS(block) &minus; SS(whole-plot factor).
- [ ] I can verify the df breakdown sums to *N* &minus; 1.
- [ ] I know pooling the errors inflates the whole-plot *F* -- here from 33 to 103.
- [ ] I report both error mean squares and both standard errors of a difference.
- [ ] I know the whole-plot test's power depends on the number of blocks, not on sub-plot treatments.
- [ ] I can recognise the classroom, batch and ward versions of this design in the wild.""",
    quiz={
        "question": "In a split-plot, MS(Error A) = 7.16 on 3 df and MS(Error B) = 1.11 on 12 df. A researcher pools them to get MS = 2.32 on 15 df and reports F(irrigation) = 102.62 instead of 33.24. What has happened?",
        "options": [
            "A reasonable simplification, since both analyses reject the null",
            "The whole-plot factor is now tested against sub-plot error, so its F is inflated threefold — pseudoreplication at the whole-plot level",
            "The pooled analysis is more powerful and therefore preferable",
            "Nothing, provided the two error mean squares are not significantly different",
        ],
        "answer": 1,
        "explanation": "Irrigation was randomised to 8 strips, so it must be tested against strip-to-strip variation. Pooling tests it against plot-to-plot variation, effectively claiming 24 replications where there are 4. The p-value falls from .010 to .00000004 — anticonservative by five orders of magnitude.",
    },
)



# ===========================================================================
L(
    "Treatment Mean Comparison",
    """## What you will be able to do

Choose the right procedure for comparing treatment means, compute LSD, Tukey HSD, Dunnett and Scheffe critical differences by hand, build orthogonal contrasts for structured questions, and present the result in the letter notation every agronomy journal uses.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
The CRD from earlier in this course: four fertilisers, five plots each, MSE = 2.5 on 16 df, *F*(3, 16) = 35.33, *p* &lt; .001.

Means: A 21.0, B 26.0, C 31.0, D 24.0.

A is the untreated control. B and D are two formulations of the same nitrogen source at different rates. C is a competitor's product.

A significant *F* says the four are not all equal. It says nothing about **which**, and the structure above means there are several different questions worth asking.
</div>

## First: what kind of question do you have?

This is the decision that determines the procedure, and it comes before any formula.

| Your question | Procedure |
|---|---|
| "Which pairs differ?" -- all of them, no prior structure | **Tukey HSD** |
| "Does each treatment beat the control?" | **Dunnett** |
| "Is the nitrogen group different from the competitor?" -- planned, specific | **Orthogonal contrasts** |
| "I have a few specific pairs in mind, decided in advance" | **LSD** or **Bonferroni** |
| "Anything that looks interesting after seeing the data" | **Scheffe** |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Planned before, or chosen after?</span>

This is the distinction that matters most, and software cannot make it for you.

A comparison you specified **before collecting data** is a *planned* (a priori) comparison. You committed to one question, so you pay little or no multiplicity penalty.

A comparison you chose **after looking at the means** is *post hoc*. You implicitly considered all the others and picked the biggest, so the correction must account for every comparison you could have made. That is why Scheffe's critical value is so large.

Writing your comparisons into your proposal is not bureaucracy -- it buys you statistical power, legitimately.
</div>

## The procedures, computed

All four use the same two ingredients: MSE = 2.5, *n* = 5, error df = 16.

### LSD -- Fisher's least significant difference

<div class="formula" markdown="1">
**LSD = t&#8338;&#8338;&#8322; x &radic;(2 MSE / n)**
<span class="formula-note">no protection beyond requiring a significant F first</span>
</div>

```
t(.975, 16) = 2.1199
LSD = 2.1199 x sqrt(2 x 2.5/5) = 2.1199 x sqrt(1) = 2.1199
```

### Tukey's HSD -- honest significant difference

<div class="formula" markdown="1">
**HSD = q&#8338;(k, df) x &radic;(MSE / n)**
<span class="formula-note">q from the studentised range distribution, not from t</span>
</div>

```
q(.05, 4, 16) = 4.05
HSD = 4.05 x sqrt(2.5/5) = 4.05 x 0.7071 = 2.8638
```

### Dunnett -- every treatment against one control

<div class="formula" markdown="1">
**d = d&#8338;(k&minus;1, df) x &radic;(2 MSE / n)**
<span class="formula-note">three comparisons here, not six, so the critical value is smaller than Tukey's</span>
</div>

```
d(.05, 3, 16) = 2.59
critical difference = 2.59 x sqrt(2 x 2.5/5) = 2.59 x 1 = 2.59
```

### Scheffe -- any contrast, including ones chosen after the fact

<div class="formula" markdown="1">
**S = &radic;[ (k&minus;1) F&#8338;(k&minus;1, df) ] x &radic;(2 MSE / n)**
</div>

```
F(.05, 3, 16) = 3.2389
S = sqrt(3 x 3.2389) x 1 = sqrt(9.7167) = 3.1172
```

### The four side by side

| Procedure | Critical difference | Protects |
|---|---|---|
| **LSD** | **2.12** | Nothing beyond the *F* test |
| **Dunnett** | **2.59** | 3 treatment-vs-control comparisons |
| **Tukey** | **2.86** | All 6 pairwise comparisons |
| **Scheffe** | **3.12** | Every possible contrast |

The ordering is always this: **LSD &lt; Dunnett &lt; Tukey &lt; Scheffe.** More protection means a larger threshold means less power. There is no procedure that is both maximally protected and maximally powerful; you choose where on that line your question sits.

## Applying them

Observed differences:

| Pair | Difference | LSD 2.12 | Dunnett 2.59 | Tukey 2.86 | Scheffe 3.12 |
|---|---|---|---|---|---|
| C &minus; A | 10.0 | yes | yes | yes | yes |
| C &minus; D | 7.0 | yes | -- | yes | yes |
| C &minus; B | 5.0 | yes | -- | yes | yes |
| B &minus; A | 5.0 | yes | yes | yes | yes |
| D &minus; A | 3.0 | yes | yes | yes | **no** |
| B &minus; D | 2.0 | **no** | -- | **no** | **no** |

Dashes mark comparisons Dunnett does not make -- it only tests against the control.

Two things to notice.

**B vs D (difference 2.0) fails under every procedure.** The two nitrogen formulations cannot be distinguished at this sample size.

**D vs A (difference 3.0) is significant under LSD, Dunnett and Tukey but not Scheffe.** Your choice of procedure changes the conclusion for this comparison. That is exactly why the choice must be made and justified *before* you look -- otherwise you are picking the procedure that gives the answer you want.

## The letter notation

Agronomy and food-science journals present mean comparisons as letters. Means sharing a letter are not significantly different. Using Tukey:

```
Treatment   Mean    Group
    C       31.0      a
    B       26.0      b
    D       24.0      b
    A       21.0      c
```

**How to build it.** Sort the means descending. Give the first mean the letter 'a'. Work down: if a mean is within the critical difference of an earlier mean carrying a letter, it gets that letter too; otherwise it starts a new letter.

```
C 31.0  -> 'a'
B 26.0  -> 31.0 - 26.0 = 5.0 > 2.86, so not 'a'   -> new letter 'b'
D 24.0  -> 26.0 - 24.0 = 2.0 < 2.86, so shares 'b'
           31.0 - 24.0 = 7.0 > 2.86, so not 'a'
A 21.0  -> 24.0 - 21.0 = 3.0 > 2.86, so not 'b'   -> new letter 'c'
```

<div class="callout callout-note" markdown="1">
<span class="callout-label">Letter groupings can be genuinely ambiguous</span>

Suppose means were 31.0, 28.5, 26.0. With a critical difference of 2.86: 31.0 vs 28.5 is 2.5 (not different), 28.5 vs 26.0 is 2.5 (not different), but 31.0 vs 26.0 is 5.0 (different).

So the top two share a letter, the bottom two share a letter, and the extremes do not. The notation needs overlapping groups:

```
31.0  a
28.5  ab
26.0   b
```

This is not a flaw in the method -- it reflects a real feature of the data. "Not significantly different" is not a transitive relation, and the overlapping letters say so honestly. Do not force a clean partition that the data does not support.
</div>

## Orthogonal contrasts: the most informative option

If your treatments have structure -- and most do -- contrasts answer sharper questions than pairwise tests, with full power and no multiplicity penalty.

A contrast is a weighted sum of means where the weights sum to zero:

<div class="formula" markdown="1">
**L = &Sigma;c&#7522; y&#772;&#7522;&nbsp;&nbsp;with&nbsp;&nbsp;&Sigma;c&#7522; = 0&nbsp;&nbsp;&nbsp;&nbsp;SS(L) = n L&#178; / &Sigma;c&#7522;&#178;**
<span class="formula-note">each contrast has 1 df, so F = SS(L)/MSE</span>
</div>

Our treatment structure suggests three questions, which map onto three contrasts:

| Question | A | B | C | D |
|---|---|---|---|---|
| L1: control vs everything else | &minus;3 | +1 | +1 | +1 |
| L2: competitor (C) vs the two nitrogen products | 0 | &minus;1 | +2 | &minus;1 |
| L3: the two nitrogen rates against each other | 0 | +1 | 0 | &minus;1 |

**Check orthogonality** -- the cross-products of every pair of contrasts must sum to zero:

```
L1.L2 = (-3)(0) + (1)(-1) + (1)(2) + (1)(-1) = 0 - 1 + 2 - 1 = 0   OK
L1.L3 = (-3)(0) + (1)(1)  + (1)(0) + (1)(-1) = 0 + 1 + 0 - 1 = 0   OK
L2.L3 = (0)(0)  + (-1)(1) + (2)(0) + (-1)(-1) = 0 - 1 + 0 + 1 = 0  OK
```

All three orthogonal, so the three 1-df sums of squares will partition SS(treatment) = 265 exactly.

**Compute them.**

```
L1 = -3(21.0) + 1(26.0) + 1(31.0) + 1(24.0)
   = -63 + 81 = 18.0
   sum of c^2 = 9 + 1 + 1 + 1 = 12
   SS(L1) = 5 x 18.0^2 / 12 = 5 x 324/12 = 135.0
   F = 135.0/2.5 = 54.00        p < .0001

L2 = 0(21.0) - 1(26.0) + 2(31.0) - 1(24.0)
   = -26 + 62 - 24 = 12.0
   sum of c^2 = 0 + 1 + 4 + 1 = 6
   SS(L2) = 5 x 144/6 = 120.0
   F = 120.0/2.5 = 48.00        p < .0001

L3 = 0(21.0) + 1(26.0) + 0(31.0) - 1(24.0)
   = 2.0
   sum of c^2 = 0 + 1 + 0 + 1 = 2
   SS(L3) = 5 x 4/2 = 10.0
   F = 10.0/2.5 = 4.00          p = .0625
```

**The partition check:**

```
135.0 + 120.0 + 10.0 = 265.0 = SS(treatment)     OK
```

That identity is the hallmark of orthogonal contrasts: they carve the treatment sum of squares into independent, interpretable pieces with nothing left over. If your three contrasts do not sum to SS(treatment), they are not orthogonal.

**What the contrasts tell you that Tukey could not:**

- **L1 (*F* = 54.00):** fertilising works. Any product beats no product, decisively.
- **L2 (*F* = 48.00):** the competitor's product beats both nitrogen formulations. This is the commercially important finding, and it is a single clean test rather than two separate pairwise comparisons.
- **L3 (*F* = 4.00, *p* = .063):** the two nitrogen rates do not differ significantly. Consistent with the pairwise result, but note that *p* = .063 is much more informative than Tukey's *p* = .229 for the same comparison -- because the contrast spends no alpha on comparisons you never cared about.

Three questions, three answers, 265 units of variation fully accounted for.

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span>

**Analyses -> ANOVA -> ANOVA.** Under *Post Hoc Tests*, move the factor across and choose among **Tukey**, **Scheffe**, **Bonferroni** and **Holm**; tick *Mean difference* and *Flag significant comparisons*.
For contrasts, open *Contrasts* and choose a built-in scheme (simple, deviation, helmert, polynomial). For fully custom weights, use the **Rj** module or the GAMLj module's custom contrast facility.
</div>

**SPSS.** `Analyze -> Compare Means -> One-Way ANOVA`:

- *Post Hoc* -> tick Tukey, LSD, Scheffe, or Dunnett (and set the control category for Dunnett).
- *Contrasts* -> type the coefficients one at a time, clicking **Next** between contrasts. For L1 enter &minus;3, 1, 1, 1 in the order the factor's levels are coded. SPSS prints the contrast value, its standard error, *t*, df and two-tailed *p*, and gives both the equal-variance and Welch versions.

**Excel.** The critical differences are one formula each:

```
H1:  =T.INV.2T(0.05,16)*SQRT(2*2.5/5)              ' LSD    = 2.1199
H2:  =SQRT(3*F.INV.RT(0.05,3,16))*SQRT(2*2.5/5)    ' Scheffe = 3.1172
```

Tukey's *q* and Dunnett's *d* have no Excel functions -- look them up in a table (*q*(.05, 4, 16) = 4.05; *d*(.05, 3, 16) = 2.59) and multiply.

Contrasts are straightforward arithmetic:

```
' means in B2:B5, contrast weights in C2:C5
H4:  =SUMPRODUCT(B2:B5,C2:C5)                      ' L = 18.0
H5:  =5*H4^2/SUMSQ(C2:C5)                          ' SS(L) = 135.0
H6:  =H5/2.5                                       ' F = 54.00
H7:  =F.DIST.RT(H6,1,16)                           ' p
```

**R.**

```r
m <- aov(yield ~ trt, data = d)

TukeyHSD(m)
agricolae::LSD.test(m, "trt", console = TRUE)      # with letter groups
agricolae::HSD.test(m, "trt", console = TRUE)
agricolae::scheffe.test(m, "trt", console = TRUE)
DescTools::DunnettTest(yield ~ trt, data = d, control = "A")

# orthogonal contrasts
library(emmeans)
em <- emmeans(m, ~ trt)
contrast(em, list(
  "control vs rest"   = c(-3, 1, 1, 1)/1,
  "competitor vs N"   = c( 0,-1, 2,-1)/1,
  "N rate difference" = c( 0, 1, 0,-1)/1))

# or via the model, to see the SS partition
contrasts(d$trt) <- cbind(c(-3,1,1,1), c(0,-1,2,-1), c(0,1,0,-1))
summary.aov(aov(yield ~ trt, data = d), split =
  list(trt = list("ctrl vs rest" = 1, "comp vs N" = 2, "N rates" = 3)))
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Check the level order before entering weights</span>

Contrast weights are applied in the order the software has coded the factor's levels -- usually alphabetical, which may not be the order in your table.

Run `levels(d$trt)` in R, or check the SPSS value labels, before typing &minus;3, 1, 1, 1. Entering the right weights in the wrong order gives a perfectly valid contrast answering a question you did not ask, and nothing in the output will warn you.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Agronomy report, with planned contrasts</span>

"Treatment means were compared using three pre-planned orthogonal contrasts. Fertilised plots out-yielded the untreated control, *F*(1, 16) = 54.00, *p* &lt; .001. The competitor product C out-yielded the two nitrogen formulations, *F*(1, 16) = 48.00, *p* &lt; .001. The two nitrogen rates did not differ significantly, *F*(1, 16) = 4.00, *p* = .063. The three contrasts partition the treatment sum of squares exactly (135.0 + 120.0 + 10.0 = 265.0).

Tukey's HSD (critical difference 2.86 kg) gave the grouping C (31.0 kg) a &gt; B (26.0) b = D (24.0) b &gt; A (21.0) c; means not sharing a letter differ at alpha = .05."
</div>

Reporting both is good practice: the contrasts answer your research questions, and the letter grouping gives readers the complete pairwise picture in the format their field expects.

## Common mistakes

1. **Running post-hoc tests after a non-significant *F*.** Fisher's protected LSD specifically requires the *F* test to pass first.
2. **Choosing the procedure after seeing which one gives significance.** D vs A is significant under three procedures and not under Scheffe. Decide first.
3. **Using Duncan's multiple range test.** Weak error-rate control; it persists by habit in older agronomy literature.
4. **Using Tukey when you have a control.** Dunnett makes 3 comparisons instead of 6 and is more powerful for that question.
5. **Non-orthogonal contrasts presented as a partition.** If the cross-products are not zero, the sums of squares overlap and will not add to SS(treatment).
6. **Entering contrast weights in the wrong level order.**
7. **Forcing a clean letter partition** where the data genuinely supports overlapping groups.
8. **Reporting only the significant contrast** out of several tested. Report all the comparisons you made.

## Practice

<details markdown="1">
<summary>1. Five treatments, n = 4, MSE = 6.0, error df = 15. Compute LSD and Tukey HSD. (q(.05, 5, 15) = 4.37)</summary>

```
LSD = t(.975, 15) x sqrt(2 x 6.0/4)
    = 2.1314 x sqrt(3.0)
    = 2.1314 x 1.7321
    = 3.691

HSD = 4.37 x sqrt(6.0/4)
    = 4.37 x 1.2247
    = 5.352
```

Tukey's threshold is **45% larger** than LSD's. With five treatments there are C(5,2) = 10 pairwise comparisons, so the multiplicity penalty is substantial -- considerably more than the 35% gap we saw with four treatments and six comparisons.

The gap grows with *k*. That is the argument for contrasts: if you have specific questions, you can ask four orthogonal ones with 1 df each at full power, rather than paying for all ten pairwise comparisons you do not need.
</details>

<details markdown="1">
<summary>2. Are the contrasts (1, -1, 0, 0) and (1, 1, -1, -1) orthogonal?</summary>

Both sum to zero, so both are valid contrasts:

```
1 - 1 + 0 + 0 = 0    OK
1 + 1 - 1 - 1 = 0    OK
```

Cross-product:

```
(1)(1) + (-1)(1) + (0)(-1) + (0)(-1) = 1 - 1 + 0 + 0 = 0
```

**Yes, orthogonal.** The first compares treatments 1 and 2; the second compares the pair {1, 2} against the pair {3, 4}. The two questions are independent -- knowing the difference between 1 and 2 tells you nothing about how their average compares with the average of 3 and 4.

A third orthogonal contrast would be (0, 0, 1, &minus;1), comparing treatments 3 and 4. Those three together partition SS(treatment) completely, and with *k* = 4 treatments you can have at most *k* &minus; 1 = 3 mutually orthogonal contrasts -- exactly the treatment degrees of freedom.
</details>

<details markdown="1">
<summary>3. Our L3 contrast (B vs D) gave p = .063, but Tukey gave p = .229 for the same pair. Why the difference, and which should you report?</summary>

Same difference (2.0), same MSE, same df -- so the discrepancy is entirely about **how many comparisons each procedure is protecting against.**

The contrast is a single planned 1-df test. You committed to this one question before collecting data, so there is no multiplicity to correct and the *p*-value is the raw *F*(1, 16) = 4.00 result: *p* = .063.

Tukey's *p* is adjusted for all six pairwise comparisons. The same observed difference, viewed as "the smallest of six gaps I happened to look at", is much less surprising -- hence *p* = .229.

**Which to report depends on one thing only: did you plan it?**

If the B-vs-D comparison was written into your proposal as a research question, report the contrast: *F*(1, 16) = 4.00, *p* = .063. Neither is significant at .05, but the contrast is a far more honest reflection of the evidence for that specific question.

If you noticed B and D were close only after seeing the means, report Tukey's *p* = .229.

**What you may not do** is report whichever is smaller. The protection you are entitled to is determined by your design, not by your preferences after the fact -- and in a thesis the planned comparisons should be stated in the methods chapter, before the results, where the reader can see that you committed to them.
</details>

## Before you move on

- [ ] I choose the procedure from my question, before looking at the means.
- [ ] I can compute LSD, Tukey HSD, Dunnett and Scheffe critical differences by hand.
- [ ] I know the ordering LSD &lt; Dunnett &lt; Tukey &lt; Scheffe and why it holds.
- [ ] I use Dunnett when there is a control.
- [ ] I can build orthogonal contrasts, verify the cross-products are zero, and check they partition SS(treatment).
- [ ] I can assign letter groupings, including overlapping ones.
- [ ] I check the factor's level order before entering contrast weights.
- [ ] I report every comparison I made, not just the significant ones.""",
    quiz={
        "question": "Three contrasts give SS = 135.0, 120.0 and 10.0, and SS(treatment) = 265.0. What does the exact sum confirm?",
        "options": [
            "That all three contrasts are statistically significant",
            "That the contrasts are mutually orthogonal, so they partition the treatment sum of squares into independent 1-df pieces with nothing left over",
            "That the design was balanced",
            "That MSE was computed correctly",
        ],
        "answer": 1,
        "explanation": "Orthogonal contrasts have zero cross-products, which makes their sums of squares independent and additive. With k = 4 treatments you can have at most 3 such contrasts — exactly the treatment degrees of freedom. If they do not sum to SS(treatment), they are not orthogonal and their sums of squares overlap.",
    },
)

# ===========================================================================
L(
    "Analysis of Covariance",
    """## What you will be able to do

Use a measured covariate to strip noise out of the error term, test the one assumption that decides whether ANCOVA is even legal, compute adjusted means by hand, and know the situation in which ANCOVA is the wrong tool and will mislead you.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
Three teaching methods, six students each, with a **pretest** score recorded before the intervention. The pretest is not what you are studying -- but it predicts the post-test strongly, and students vary on it.

| Method | Pretest (x) | Post-test (y) | x&#772; | y&#772; |
|---|---|---|---|---|
| M1 | 42, 45, 38, 50, 47, 41 | 58, 56, 54, 67, 57, 52 | 43.8333 | 57.3333 |
| M2 | 44, 39, 48, 43, 46, 41 | 64, 55, 70, 58, 67, 56 | 43.5000 | 61.6667 |
| M3 | 40, 47, 43, 45, 38, 49 | 64, 76, 67, 74, 62, 78 | 43.6667 | 70.1667 |

Grand means: x&#772; = 43.6667, y&#772; = 63.0556.
</div>

Note the pretest means: 43.83, 43.50, 43.67. Randomisation worked -- the three groups started essentially equal. So why bother with ANCOVA at all?

## The idea: blocking after the fact, with a continuous variable

Blocking removes identified variation by *grouping* units. ANCOVA removes it by *regressing* it out. Same purpose, continuous instead of categorical.

Pretest scores range from 38 to 50. Some of the spread in the post-test is just that spread carried forward -- a student who began at 50 will likely finish higher than one who began at 38, regardless of method. In a plain ANOVA, all of that lands in the error term.

ANCOVA fits the pretest-post-test relationship first, then asks whether the methods differ in what is left over.

<div class="formula" markdown="1">
**Y&#7522;&#11388; = &mu; + &tau;&#7522; + &beta;(X&#7522;&#11388; &minus; X&#772;) + &epsilon;&#7522;&#11388;**
<span class="formula-note">&beta; = the pooled within-group regression slope of y on x</span>
</div>

**Reading the model.** The term &beta;(*X*&#7522;&#11388; &minus; X&#772;) says: for every point a student's pretest sits above the grand mean, predict their post-test to be &beta; points higher. Remove that, and &tau;&#7522; is the method effect on a level playing field.

The covariate must be **measured before the treatment, or at least be unaffected by it.** That requirement is not negotiable, and it is the subject of the warning at the end of this lesson.

## Step 1: the plain ANOVA, so you can see what ANCOVA buys

| Source | SS | df | MS | F | p |
|---|---|---|---|---|---|
| Method | 511.4444 | 2 | 255.7222 | **6.9301** | **.0074** |
| Error | 553.5000 | 15 | **36.9000** | | |
| Total | 1064.9444 | 17 | | | |

Significant, with MSE = **36.90**.

Hold onto that number.

## Step 2: test the assumption that decides everything

**Homogeneity of regression slopes.** ANCOVA assumes the covariate relates to the outcome **the same way in every group** -- that is, one common slope &beta;.

Test it by fitting a model that *allows* different slopes and asking whether the interaction adds anything:

| Source | SS | df | F | p |
|---|---|---|---|---|
| Method | 523.9600 | 2 | 43.6756 | &lt; .001 |
| Pretest | 450.0372 | 1 | 75.0272 | &lt; .001 |
| **Pretest x Method** | **31.4829** | **2** | **2.6243** | **.1134** |
| Error | 71.9798 | 12 | | |

**p = .113.** The interaction is not significant, so a single common slope is defensible. **ANCOVA is legal here.**

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Run this test first, always</span>

If the slope x group interaction *is* significant, ANCOVA is **invalid** -- there is no single adjustment to make, because the covariate's effect differs by group. Adjusted means would be fiction.

What to do instead:

- **Report the interaction as the finding.** "Method M3 benefits high-pretest students most" is more informative than an adjusted mean.
- **Use the Johnson-Neyman technique**, which identifies the range of covariate values over which the groups differ significantly. This is the proper tool for heterogeneous slopes.
- **Keep the separate-slopes model** and report simple slopes per group.

Most software does not run this test for you. In SPSS and Jamovi you must build the interaction model yourself, read the interaction *p*, and then remove the term. Skipping it is the most common ANCOVA error in theses.
</div>

## Step 3: the ANCOVA

| Source | SS | df | MS | F | p |
|---|---|---|---|---|---|
| **Pretest (covariate)** | 450.0372 | 1 | 450.0372 | **60.8965** | **&lt; .001** |
| **Method** | 523.9600 | 2 | 261.9800 | **35.4497** | **&lt; .001** |
| Error | 103.4628 | 14 | **7.3902** | | |
| Total | 1064.9444 | 17 | | | |

Now compare the two analyses directly:

| | MSE | error df | F(method) | p |
|---|---|---|---|---|
| **ANOVA** | 36.9000 | 15 | 6.93 | .0074 |
| **ANCOVA** | **7.3902** | 14 | **35.45** | **.0000030** |

**The error mean square fell by a factor of five** -- from 36.90 to 7.39 -- and *F* rose from 6.93 to 35.45, even though the covariate cost one degree of freedom.

What happened: 450.04 of the 553.50 error sum of squares was **pretest variation**, not method variation and not noise. ANCOVA named it and removed it. That is 81% of the original error term.

```
SSE(anova)  = 553.5000
SS(pretest) = 450.0372
             ----------
SSE(ancova) = 103.4628      (and SS(method) rose slightly, 511.44 -> 523.96)
```

Note that SS(method) also changed -- from 511.44 to 523.96. The groups were not *exactly* balanced on pretest (43.83 / 43.50 / 43.67), so adjusting for it shifts the method effect a little too. With a randomised design the shift is small; in an observational study it can be large.

**Partial eta-squared for method** = 523.96/(523.96 + 103.46) = **.835**.

## Step 4: the pooled slope and adjusted means

The regression coefficient on the pretest is the pooled within-group slope:

```
b = 1.3819     t = 7.804, p < .001
```

So each extra pretest point predicts **1.38 extra post-test points**, within any method.

<div class="formula" markdown="1">
**adjusted mean&#7522; = y&#772;&#7522; &minus; b (x&#772;&#7522; &minus; x&#772;)**
<span class="formula-note">what group i's mean would have been had its covariate mean equalled the grand mean</span>
</div>

Worked for all three:

```
M1: 57.3333 - 1.3819(43.8333 - 43.6667)
  = 57.3333 - 1.3819(0.1666)
  = 57.3333 - 0.2303
  = 57.1030

M2: 61.6667 - 1.3819(43.5000 - 43.6667)
  = 61.6667 - 1.3819(-0.1667)
  = 61.6667 + 0.2303
  = 61.8970

M3: 70.1667 - 1.3819(43.6667 - 43.6667)
  = 70.1667 - 0
  = 70.1667
```

| Method | Pretest mean | Unadjusted | **Adjusted** | Shift |
|---|---|---|---|---|
| M1 | 43.8333 | 57.3333 | **57.1030** | &minus;0.23 |
| M2 | 43.5000 | 61.6667 | **61.8970** | +0.23 |
| M3 | 43.6667 | 70.1667 | **70.1667** | 0.00 |

**The adjustments are tiny** -- about a quarter of a point -- and the direction makes sense: M1 started 0.17 points *above* the grand mean, so its mean is adjusted *down* slightly; M2 started below, so it is adjusted up; M3 started exactly at the grand mean, so it does not move at all.

<div class="callout callout-note" markdown="1">
<span class="callout-label">The two distinct benefits, and which one you got here</span>

ANCOVA does two separate things, and confusing them is common.

**It increases precision** by removing covariate variation from the error term. This happens whenever the covariate correlates with the outcome, **even with perfectly balanced groups**. That is what dominated here: MSE fell fivefold while the means barely moved.

**It corrects for covariate imbalance** between groups. This matters when groups started unequal -- common in quasi-experiments and observational studies, where randomisation was not possible.

In a properly randomised experiment you get mostly the first benefit, and it is reason enough. Measure a strong baseline predictor and include it. The payoff here was turning *p* = .0074 into *p* = .0000030 for free.
</div>

## Step 5: pairwise comparisons on the adjusted means

Use the ANCOVA MSE (7.3902, df 14), not the ANOVA one:

```
SE of a difference ~ sqrt( 2 x 7.3902/6 ) = sqrt(2.4634) = 1.5695
t(.975, 14) = 2.1448
LSD ~ 2.1448 x 1.5695 = 3.366
```

| Comparison | Adjusted difference | &gt; 3.37? |
|---|---|---|
| M3 vs M1 | 13.06 | yes |
| M3 vs M2 | 8.27 | yes |
| M2 vs M1 | 4.79 | yes |

All three separate. From the model output, the contrasts against M1 are **+4.794 (M2, t = 3.052, p = .009)** and **+13.064 (M3, t = 8.322, p &lt; .001)**.

Compare with the plain ANOVA, where MSE = 36.90 would have given an LSD of about 7.5 -- and the M2-vs-M1 difference of 4.33 would have been non-significant. **ANCOVA's precision gain resolved a comparison the ANOVA could not.**

<div class="callout callout-note" markdown="1">
<span class="callout-label">A refinement for exact work</span>

The SE formula above is an approximation. The exact standard error of an adjusted mean difference includes a term for how far apart the two groups' covariate means are:

```
SE = sqrt( MSE x [ 1/n1 + 1/n2 + (x1bar - x2bar)^2 / SSw(x) ] )
```

where SS&#8347;(*x*) is the within-group sum of squares of the covariate. When the covariate means are close -- as here, differing by at most 0.33 -- the extra term is negligible. When they differ substantially, it matters, and the interval widens. `emmeans` in R and SPSS's EMMEANS both use the exact formula.
</div>

## When ANCOVA is the wrong tool

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Never use a covariate measured after the treatment</span>

If the treatment affected the covariate, adjusting for the covariate removes part of the treatment effect itself. You are controlling for a consequence of the thing you are studying.

Example: a reading programme is tested, and the analyst adjusts for "hours spent reading during the term". But the programme *caused* more reading. Adjusting for it removes the mechanism through which the programme worked, and the treatment effect shrinks toward zero. The conclusion -- "no effect" -- is an artefact of the analysis.

This is sometimes called **over-adjustment** or conditioning on a mediator. The rule is simple: **the covariate must be measured before treatment assignment, or be something the treatment cannot possibly have changed** (age, sex, baseline score, prior year's grade).

If you genuinely want to know how much of the effect runs through a post-treatment variable, that is a mediation analysis, not an ANCOVA -- and it needs its own design and assumptions.
</div>

**The second trap: ANCOVA does not fix a broken quasi-experiment.** If intact groups differ substantially at baseline, adjusting for the baseline score does *not* make them exchangeable. It adjusts for *that one measured variable*, leaving every unmeasured difference intact. Worse, measurement error in the covariate biases the adjustment toward zero (Lord's paradox is the classic illustration). ANCOVA on non-equivalent groups is a precision tool, not a randomisation substitute, and the write-up must say so.

## All the assumptions

| Assumption | How to check | If violated |
|---|---|---|
| **Homogeneity of slopes** | covariate x group interaction | ANCOVA invalid; use Johnson-Neyman |
| **Covariate unaffected by treatment** | Design logic -- measured before? | Do not use that covariate |
| **Linear covariate-outcome relation** | Scatterplot per group | Add a quadratic term, or transform |
| **Covariate measured reliably** | Reliability coefficient | Adjustment is attenuated; use latent methods |
| **Normal residuals** | Shapiro-Wilk, Q-Q on residuals | Robust regression, or transform |
| **Equal error variances** | Levene on residuals | Heteroskedasticity-robust SEs |
| **Independence** | Design | Mixed model |

## Doing it in software

<div class="callout callout-note" markdown="1">
<span class="callout-label">Jamovi</span>

**Analyses -> ANOVA -> ANCOVA.**
Dependent: posttest. Fixed Factors: method. **Covariates: pretest.**

First, test the slopes. Open *Model*, and add the `pretest * method` interaction to the model terms. Read its *p* (.113 here). Then **remove it** and read the clean ANCOVA.

Under *Estimated Marginal Means* add method -- Jamovi reports the **adjusted** means with confidence intervals, and its plot shows them. Under *Post Hoc Tests* move method across with a Tukey or Bonferroni correction.
</div>

**SPSS.** `Analyze -> General Linear Model -> Univariate`. Dependent: posttest. Fixed Factor: method. Covariate(s): pretest.

Slope test: click **Model -> Custom**, move in `method`, `pretest`, and `pretest*method` (select both and choose the *Interaction* build type). Run it, read the interaction *p*, then rebuild the model without it.

For the clean run: *Model -> Full factorial* (with a covariate this gives method + pretest), then *Options* -> move `method` into *Display Means for*, tick **Compare main effects** with a Bonferroni adjustment, and tick **Estimates of effect size** and **Parameter estimates** (the latter gives you *b* = 1.3819).

**Excel.** Possible but awkward. ANCOVA is a regression with dummy variables, so:

```
' D = dummy for M2, E = dummy for M3, C = pretest
' then LINEST on y against C, D, E
=LINEST(B2:B19, C2:E19, TRUE, TRUE)
```

Entered as an array formula over a 5 x 4 range, `LINEST` returns the coefficients (including *b* = 1.3819 on the pretest and the two method contrasts 4.794 and 13.064), their standard errors, R&#178;, the overall *F*, and the residual SS and df. From those you can assemble the ANCOVA table by hand.

The `Regression` tool in the Analysis ToolPak gives the same thing in a readable layout with *t*-statistics and *p*-values -- which is the more practical route. Compute adjusted means with the formula above. Excel cannot test slope homogeneity automatically; add interaction columns (`=C2*D2`, `=C2*E2`) and compare the two regressions' residual sums of squares with a partial *F*.

**R.**

```r
d <- data.frame(
  g = factor(rep(c("M1","M2","M3"), each = 6)),
  x = c(42,45,38,50,47,41, 44,39,48,43,46,41, 40,47,43,45,38,49),
  y = c(58,56,54,67,57,52, 64,55,70,58,67,56, 64,76,67,74,62,78))

# 1. plain ANOVA, for comparison
anova(lm(y ~ g, data = d))            # F(2,15) = 6.93, MSE = 36.90

# 2. THE ASSUMPTION TEST -- do this first
anova(lm(y ~ x * g, data = d))        # x:g  F(2,12) = 2.624, p = .113  OK

# 3. the ANCOVA
m <- lm(y ~ x + g, data = d)
car::Anova(m, type = "III")
#        Sum Sq Df F value    Pr(>F)
# x      450.04  1  60.897 2.0e-06 ***
# g      523.96  2  35.450 3.0e-06 ***
# Residuals 103.46 14

coef(m)["x"]                          # 1.3819  = the pooled slope

# 4. adjusted means and comparisons
library(emmeans)
emmeans(m, ~ g)                       # 57.10, 61.90, 70.17
pairs(emmeans(m, ~ g), adjust = "tukey")

effectsize::eta_squared(m, partial = TRUE)   # g: .835

# 5. diagnostics
par(mfrow = c(2,2)); plot(m)
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Order matters with Type I sums of squares</span>

`anova(lm(y ~ x + g))` gives **sequential** (Type I) sums of squares: *x* is entered first, then *g* is tested after adjusting for *x*. For ANCOVA that happens to be what you want.

But `anova(lm(y ~ g + x))` reverses it -- *g* is tested first, *unadjusted*, giving the plain ANOVA's SS of 511.44 instead of 523.96. Same model, different table, different answer to "is there a method effect".

Use `car::Anova(m, type = "III")` to get order-independent sums of squares, and state in your write-up which type you report. With balanced groups and a near-balanced covariate the difference is small; with real imbalance it is not.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">APA, ANCOVA</span>

"Post-test scores were analysed by ANCOVA with teaching method as the factor and pretest score as a covariate. The homogeneity-of-slopes assumption was satisfied, *F*(2, 12) = 2.62, *p* = .113, so a common-slope model was fitted.

The covariate was a strong predictor, *F*(1, 14) = 60.90, *p* &lt; .001, *b* = 1.38, and adjusting for it reduced the error mean square from 36.90 to 7.39. Method had a significant effect on adjusted post-test scores, *F*(2, 14) = 35.45, *p* &lt; .001, partial eta&#178; = .84.

Adjusted means were 57.10 (M1), 61.90 (M2) and 70.17 (M3). All pairwise comparisons were significant after Tukey adjustment: M3 exceeded M1 by 13.06 points (*t*(14) = 8.32, *p* &lt; .001) and M2 by 8.27 points; M2 exceeded M1 by 4.79 points (*t*(14) = 3.05, *p* = .009). Because groups were randomly assigned and pretest means were closely matched (43.83, 43.50, 43.67), the adjustment altered the means by less than 0.25 points; the benefit of the covariate was almost entirely in precision rather than in correcting imbalance."
</div>

That final sentence is the mark of an author who understands the method. It tells the reader which of ANCOVA's two functions was operating, and it pre-empts the suspicion that the covariate was used to manufacture a result.

## Common mistakes

1. **Not testing slope homogeneity.** If slopes differ, adjusted means are meaningless. Test first, every time.
2. **Using a post-treatment covariate.** Removes part of the effect you are measuring.
3. **Treating ANCOVA as a fix for non-equivalent groups.** It adjusts for one measured variable and nothing else.
4. **Reporting unadjusted means beside an ANCOVA *F*.** Report the adjusted means -- they are what the test is about. Give both if space allows.
5. **Using the ANOVA MSE for post-hoc comparisons.** Use the ANCOVA MSE and its df.
6. **Adding many covariates to hunt for significance.** Each costs a degree of freedom and widens the scope for a spurious result. Choose covariates a priori on theoretical grounds.
7. **Ignoring covariate measurement error.** An unreliable covariate under-adjusts, and with unequal groups that bias has a direction.
8. **Relying on Type I sums of squares without checking the term order.**

## Practice

<details markdown="1">
<summary>1. The slope x group interaction is significant, F(2, 24) = 5.8, p = .009. What do you do?</summary>

**Do not run ANCOVA.** The covariate relates to the outcome differently in each group, so there is no single slope to adjust by and no meaningful set of adjusted means. Reporting them anyway would be reporting numbers that describe no group.

**What to do instead:**

**Report the interaction as a substantive finding.** "The relationship between pretest and post-test differed by method" is often more interesting than an average effect. It means one method suits high-baseline students and another suits low-baseline students -- directly actionable.

**Report the simple slopes.** Fit the separate-slopes model and give *b* for each group with its CI. Plot the three regression lines on one scatterplot; that figure is the result.

**Use the Johnson-Neyman technique.** It identifies the *regions of significance* -- the range of pretest values over which two methods differ significantly. The output is a statement like "M3 outperforms M1 for students with pretest above 41, and the two do not differ below that." `interactions::johnson_neyman()` in R, or PROCESS for SPSS.

**What not to do:** remove the interaction term because it is inconvenient and report the common-slope ANCOVA. If you have tested the assumption and it failed, you cannot then assume it holds.
</details>

<details markdown="1">
<summary>2. ANOVA MSE = 80, ANCOVA MSE = 76 on the same data. Was the covariate worth including?</summary>

Barely, and arguably not.

A 5% reduction in MSE for the loss of one error degree of freedom is close to a wash. The covariate correlates only weakly with the outcome -- the variance reduction is approximately *r*&#178;, so a 5% reduction implies *r* is only about .22.

**The calculation that settles it.** ANCOVA is worth it when the precision gained exceeds the df lost. A rough threshold: the covariate should reduce error variance by more than roughly 1/df_error. With, say, 20 error df, that is 5% -- so this case is exactly at the break-even point.

**The real question is whether it was pre-specified.** If you planned to adjust for the pretest, do so and report it; that is a clean analysis whatever the gain turns out to be. If you are deciding *after* seeing the results, you are choosing the model that gives the answer you prefer, which is a different and worse activity.

**What to report:** state that the covariate was weakly related to the outcome and that adjustment produced little precision gain. A null result honestly reported about your covariate costs you nothing.
</details>

<details markdown="1">
<summary>3. Our pretest means were 43.83, 43.50, 43.67 — nearly identical. So why run ANCOVA at all?</summary>

Because ANCOVA's two benefits are independent, and the one that mattered here was **precision**, not balance.

Balanced groups mean the *adjustment* to the means was trivial -- under 0.25 points, as the table shows. If that were the only thing ANCOVA did, it would indeed have been pointless.

But the error term is a different matter. Of the 553.50 error sum of squares in the plain ANOVA, **450.04 was pretest variation** -- 81% of it. Students differed on where they started, and in the plain ANOVA that difference was noise. ANCOVA identified it as pretest variation and removed it:

```
MSE:  36.90  ->  7.39     (a fivefold reduction)
F:     6.93  ->  35.45
p:    .0074  ->  .0000030
```

And it had a practical consequence: the ANOVA's LSD would have been about 7.5 points, so the M2-vs-M1 difference of 4.33 would have been **non-significant**. With ANCOVA's LSD of 3.37 it is significant at *p* = .009. A real difference that the plain ANOVA could not resolve.

**The general lesson:** in a randomised experiment, measure a strong baseline predictor of your outcome and include it as a covariate. You will almost never need it for balance, and you will almost always gain precision. It is the cheapest power available.
</details>

<details markdown="1">
<summary>4. A researcher compares two schools' exam results, adjusting for "hours of homework completed during the year". What is wrong?</summary>

The covariate is **post-treatment**, and it is almost certainly affected by the thing being compared.

If school A's culture, teaching or expectations produce more homework, then homework hours are partly a *consequence* of attending school A. Adjusting for it asks: "comparing students who did the same amount of homework, do the schools differ?" -- which removes exactly the mechanism through which school A might be better. The school effect is absorbed into the covariate and shrinks toward zero.

A researcher who then reports "no difference between schools after controlling for homework" has not controlled for a confounder; they have controlled away the effect.

**What a valid covariate would look like:** the previous year's exam results, entry test scores, age, or socioeconomic indicators recorded at enrolment -- anything fixed before the school could influence it.

**If homework is genuinely of interest**, the question is a mediation question: *how much of the school difference operates through homework?* That requires a mediation model (see **Intermediate Statistics**), explicit causal assumptions, and ideally longitudinal data. It is a different analysis with a different interpretation, and it should be framed as such rather than smuggled in as a covariate.

**The underlying rule:** a covariate is legitimate only if the treatment could not have changed it. Ask "could the treatment have affected this variable?" If yes, or if you cannot rule it out, do not adjust for it.
</details>

## Before you move on

- [ ] I test slope homogeneity **before** running any ANCOVA.
- [ ] I can compute adjusted means from y&#772;&#7522; &minus; *b*(x&#772;&#7522; &minus; x&#772;) and check the direction of each shift.
- [ ] I can state the two separate benefits of ANCOVA and say which one a given analysis got.
- [ ] I compare ANOVA MSE with ANCOVA MSE to quantify the precision gain.
- [ ] I use the ANCOVA MSE and df for post-hoc comparisons.
- [ ] I never adjust for a variable the treatment could have affected.
- [ ] I know ANCOVA does not make non-equivalent groups equivalent.
- [ ] I state which sum-of-squares type I report.""",
    quiz={
        "question": "Pretest means are 43.83, 43.50 and 43.67 across three randomly assigned groups. Adding the pretest as a covariate drops MSE from 36.90 to 7.39. What did ANCOVA mainly do here?",
        "options": [
            "It corrected for baseline imbalance between the groups",
            "It increased precision by removing pretest variation from the error term; with balanced groups the adjustment to the means was under 0.25 points",
            "Nothing useful, since the groups were already balanced",
            "It introduced bias, because the covariate was related to the outcome",
        ],
        "answer": 1,
        "explanation": "ANCOVA has two independent benefits. Correction for imbalance was negligible here because randomisation worked. The precision gain was large: 450.04 of the 553.50 error sum of squares was pretest variation, so removing it cut MSE fivefold and resolved a pairwise comparison the plain ANOVA could not.",
    },
)


# ===========================================================================
L(
    "Further Reading (Free & Open)",
    """## What you now know how to do

You came in with "run an ANOVA" and you leave with five designs you can lay out, randomise, compute by hand and defend.

| Design | Removes | Error df | Use when |
|---|---|---|---|
| **CRD** | Nothing | *N* &minus; *k* | Units homogeneous |
| **RCBD** | One nuisance factor | (*t*&minus;1)(*b*&minus;1) | One known gradient |
| **Latin square** | Two nuisance factors | (*p*&minus;1)(*p*&minus;2) | Two crossing gradients, 4 &le; *p* &le; 6 |
| **Factorial** | -- (adds interaction) | *ab*(*n*&minus;1) | Two factors, interaction of interest |
| **Split-plot** | -- (two unit sizes) | two error terms | A factor cannot go on a small plot |
| **ANCOVA** | A continuous covariate | *N* &minus; *k* &minus; 1 | A measured baseline predictor exists |

Plus the comparison machinery -- LSD, Tukey, Dunnett, Scheffe and orthogonal contrasts -- and the judgement about which belongs to which question.

## The seven habits that matter most

1. **Design first, analyse second.** Every failure in this course's scenarios was a design failure that no analysis could repair. The teaching-method study confounded with time of day; the one-tank-per-treatment fish experiment; the greenhouse trial with zero error df.

2. **Ask what each factor was randomised to.** That answers three questions at once: what the experimental unit is, what your real *n* is, and how many error terms you need. It is the single most useful question in experimental design.

3. **Check the df column before reading any *F*.** A 4x4 Latin square must show 3-3-3-6. A split-plot must show three error strata. An RCBD must not show an interaction line. The df are your checksum, and they catch the errors that silently produce plausible-looking output.

4. **Verify your sums of squares.** &Sigma;*Y*&#178; &ge; CF always. SS(treatment) + SS(block) + SSE = TSS. Orthogonal contrasts sum to SS(treatment). Simple effects of B sum to SS(B) + SS(AxB). Each of these is free error detection.

5. **Report CV% and an unbiased effect size.** The *p*-value tells a reader whether to believe you; the CV tells them whether the experiment was well executed; omega-squared or partial eta-squared tells them whether it matters.

6. **Never pool error terms across levels of randomisation.** In our split-plot that inflated *F* from 33 to 103. The classroom, batch and hospital-ward versions of this error are everywhere in the published literature.

7. **Test assumptions on the residuals, and say what you found.** Including when a block effect turned out not to matter, or when a Latin square's double blocking did not pay off. Reporting a design that did not earn its keep is more credible than silence.

## Free textbooks

- **Design and Analysis of Experiments**, Montgomery -- the standard reference. Not free, but in every engineering library. The split-plot and factorial chapters are the clearest treatments in print.
- **Statistical Procedures for Agricultural Research**, Gomez & Gomez -- free PDF widely available, and the single most practical book for field trials. Written for rice researchers at IRRI; the worked examples are all real field data, and it covers the CV conventions and relative-efficiency calculations this course uses.
- **A First Course in Design and Analysis of Experiments**, Oehlert -- **free PDF from the author** (users.stat.umn.edu/~gary/Book.html). A full graduate text, released at no cost. The best free option for this subject.
- **Design of Comparative Experiments**, Bailey -- rigorous on randomisation structure and why it determines the analysis. Strong on the split-plot logic.
- **Introduction to Modern Statistics** (openintro.org/book/ims) -- free, and the best free treatment of randomisation as the basis of inference.

## Software, all free

- **R** with **agricolae** -- the package built for this course's content. `design.crd`, `design.rcbd`, `design.lsd` and `design.split` generate randomised field books; `LSD.test`, `HSD.test`, `duncan.test` and `scheffe.test` run the comparisons with letter groupings already assembled.
- **R** with **emmeans** for adjusted means, simple effects and custom contrasts on any model; **lmerTest** for split-plot and multilevel designs; **car** for Type III sums of squares; **effectsize** for omega-squared and partial eta-squared.
- **Jamovi** (jamovi.org) -- point-and-click for CRD, RCBD, Latin square, factorial and ANCOVA. Add the **GAMLj** module for split-plot and mixed models, and **Rj** to run R code inside it.
- **PSPP** (gnu.org/software/pspp) -- free, and close enough to SPSS that its menu paths mostly transfer.
- **G*Power** (gpower.hhu.de) -- free, and the standard tool for the power calculations that set your replication before you start.
- **Python** with `statsmodels` and `scipy.stats`. Every ANOVA table in this course was computed with `statsmodels.formula.api.ols` and `anova_lm`, and every *p*-value with `scipy.stats`.

## A planning checklist for your own experiment

Work through this before you collect anything.

- [ ] **What is the response variable, and how precisely can I measure it?**
- [ ] **What are the treatments, and do they have structure?** (Structure means contrasts, which means more power.)
- [ ] **What is the experimental unit?** What will each treatment be independently applied to?
- [ ] **Is there a nuisance factor I can identify?** One &rarr; RCBD. Two crossing &rarr; Latin square. None &rarr; CRD.
- [ ] **Can every treatment be applied to every unit?** No &rarr; split-plot, and put the factor you care about on the sub-plot if the physics allows.
- [ ] **Is there a baseline variable I can measure before treatment?** Yes &rarr; ANCOVA, for free precision.
- [ ] **How many replications do I need?** Power analysis, with a floor of about 10-12 error df.
- [ ] **How will I randomise, and how will I record it?** Seed or allocation sheet, kept.
- [ ] **Which comparisons will I make?** Written down now, before the data exist.
- [ ] **What will I do if an assumption fails?** Decided now, so the decision is not driven by the result.

## Where to go next in this catalogue

| If you want to... | Take |
|---|---|
| Design the study that generates the data | **Foundations of Research Methodology** |
| Choose and run the right test from scratch | **Applied Statistics for Research** |
| Firm up means, variances and distributions | **Basic Statistics: A Practical Start** |
| Model relationships rather than compare groups | **Intermediate Statistics: Building Real Models** |
| Handle ordinal or non-normal response data | **Nonparametric Statistics** |
| Understand where *F*, *t* and chi-square come from | **Probability & Mathematical Statistics** |
| Do SEM, PLS-SEM or survival analysis | **Advanced Statistics** |

## One closing idea worth carrying forward

Every design in this course is the same model with a different set of terms:

```
CRD          y ~ treatment
RCBD         y ~ block + treatment
Latin square y ~ row + column + treatment
Factorial    y ~ A * B
ANCOVA       y ~ covariate + treatment
Split-plot   y ~ A * B + Error(block/A)
```

That is not a coincidence or a convenience of notation. They are all **linear models**, and ANOVA is what you call a linear model whose predictors are all categorical. The sums of squares you computed by hand are what least squares produces when the design matrix is made of zeros and ones.

Which means the whole subject generalises in one step. Replace the normal error with a binomial and you have logistic regression for a yes/no response. Replace it with a Poisson and you have count models for insect counts or defect counts. Add random effects and you have the mixed models that handle any nesting structure you like -- the split-plot's two error terms are the simplest case of exactly that.

```r
glmer(survived ~ treatment + (1|block), family = binomial, data = d)
glmer(count ~ treatment * variety + (1|block/treatment),
      family = poisson, data = d)
```

The designs stay the same. What changes is the distribution you assume for the response. Everything you learned about randomisation, replication and local control carries over unchanged -- because those are properties of the experiment, not of the arithmetic.""",
)

# ===========================================================================
# MAIN -- new lessons are inserted above this marker
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
            print(f"  not yet rewritten: {', '.join(stale)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
