"""
Rewrites Basic Statistics as a course you can actually learn from.

The previous lessons described statistics. These teach it: one dataset carried
through the whole course, every calculation shown line by line, the exact
click-path in Jamovi / SPSS / Excel / R, annotated output, a fill-in-the-blank
reporting template, and practice problems with fully worked answers.

The teaching dataset is eight Grade 11 students from one section. Every number
quoted in these lessons was computed from it and checked, including:

    scores      12, 15, 15, 18, 20, 22, 25, 33
    n = 8   sum = 160   mean = 20   median = 19   mode = 15
    sum of squared deviations = 316
    sample variance = 316/7 = 45.14     sample SD = 6.72
    Q1 = 15   Q3 = 23.5   IQR = 8.5     range = 21
    study hours 1, 2, 2, 3, 4, 5, 6, 7  ->  r = 0.872, r-squared = 0.76
    one-sample t vs 25: t = -2.105, df = 7, p = 0.073 (not significant)
    95% CI for the mean = [14.38, 25.62]
    review x passing 2x2: chi-square = 5.4545, df = 1, p = 0.0195, phi = 0.30

Safe to re-run. Lessons are matched by title and replaced in place.

Usage:
    python3 seed_deep_basic_statistics.py
    DATABASE_URL="postgresql://..." python3 seed_deep_basic_statistics.py
"""
import json
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal, sync_columns
from app import models

COURSE_SLUG = "basic-statistics"

LESSONS = []


def L(title, content, quiz=None, preview=False):
    LESSONS.append({"title": title, "content": content, "quiz": quiz, "preview": preview})


# ===========================================================================
L(
    "Levels of Measurement and Why They Decide Everything",
    """## What you will be able to do

By the end of this lesson you will be able to look at any variable in your dataset and say, out loud and with a reason, which of the four measurement levels it is -- and therefore which statistics you are allowed to compute from it. This is the first decision in every analysis, and getting it wrong invalidates everything after it.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
You are helping a classmate with her thesis. She opens her spreadsheet and shows you a column called `Region` with values 1, 2 and 3. Her analysis reports **mean Region = 1.8**. She asks whether that looks right.

It does not. But to explain *why*, you need the four levels of measurement.
</div>

## The four levels, from least to most information

Think of it as a ladder. Each rung adds one new thing you are allowed to do.

### Rung 1 -- Nominal: names only

The numbers are labels. Nothing more.

- Examples: civil status, religion, barangay, blood type, course strand
- Order is meaningless. Coding Single = 1, Married = 2 does **not** mean married is "more" than single
- **Allowed:** counts, percentages, mode
- **Not allowed:** mean, median, standard deviation, correlation

### Rung 2 -- Ordinal: order, but uneven gaps

Now the values have a sequence, but you do not know whether the steps are equal.

- Examples: Likert agreement, year level, socio-economic class, pain scale, medal placement
- 1st, 2nd and 3rd place tell you the order but not the gaps -- 1st may have beaten 2nd by a hair, and 2nd beaten 3rd by a mile
- **Allowed:** everything nominal allows, plus median, percentiles, rank correlation
- **Not allowed:** mean, standard deviation (strictly speaking)

### Rung 3 -- Interval: equal gaps, arbitrary zero

The distance between values is now meaningful and constant. But zero is a chosen point, not an absence.

- Examples: temperature in Celsius, calendar year, IQ score
- 30 C minus 20 C is the same size gap as 20 C minus 10 C -- so **subtraction works**
- But 40 C is *not* "twice as hot" as 20 C, because 0 C is not the absence of heat -- so **division does not work**
- **Allowed:** everything ordinal allows, plus mean, standard deviation, Pearson correlation
- **Not allowed:** ratio statements ("twice as much")

### Rung 4 -- Ratio: equal gaps and a true zero

Zero now means "none of it."

- Examples: age, height, weight, income, number of children, time taken, test score counted as items correct
- Zero income means no income. So income of 40,000 really is twice 20,000
- **Allowed:** everything. Every arithmetic operation is meaningful

## The decision procedure

Ask these three questions, in order. Stop at the first "no."

<div class="callout callout-key" markdown="1">
<span class="callout-label">The three questions</span>

1. **Can I put the values in a meaningful order?** No -> **Nominal.** Stop.
2. **Are the gaps between consecutive values equal and known?** No -> **Ordinal.** Stop.
3. **Does zero mean "none of this thing"?** No -> **Interval.** Yes -> **Ratio.**
</div>

Work the scenario through it:

- `Region` coded 1, 2, 3. Question 1: is Region 3 "more" than Region 1? No. -> **Nominal.** The mean of 1.8 is arithmetic performed on name tags. The correct summary is a frequency table and the mode.

## Worked examples

| Variable | Q1 order? | Q2 equal gaps? | Q3 true zero? | Level | Correct centre |
|---|---|---|---|---|---|
| Barangay | No | -- | -- | Nominal | Mode |
| Highest educational attainment | Yes | No | -- | Ordinal | Median |
| Agreement on one Likert item | Yes | No | -- | Ordinal | Median |
| Birth year | Yes | Yes | No (year 0 is a convention) | Interval | Mean |
| Monthly income in pesos | Yes | Yes | Yes | Ratio | Mean (but check skew) |
| Number of absences | Yes | Yes | Yes | Ratio | Mean |
| Quiz score out of 40 | Yes | Yes | Yes | Ratio | Mean |

## The Likert argument, settled

This comes up in almost every defence, so learn the distinction once:

- **One Likert item on its own is ordinal.** You cannot show that the psychological distance from "Neutral" to "Agree" equals the distance from "Agree" to "Strongly Agree." Report the median and the frequency distribution.
- **A summated scale -- several items added or averaged into one score -- is conventionally treated as interval.** This is an accepted convention across the social sciences, defensible in a panel, and it is what lets you run a t-test on a construct like "job satisfaction."

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The trap</span>
Software will compute anything you ask it to. Jamovi, SPSS and Excel will all happily return `mean Region = 1.8` without a single warning. **The software checks nothing.** Measurement level lives in your codebook and in your head, not in the file.
</div>

## Recording it so you do not lose it

Every dataset needs a codebook. Build it before you collect data, not after.

| Variable name | Label | Level | Values | Missing code |
|---|---|---|---|---|
| `sex` | Sex of respondent | Nominal | 1 = Male, 2 = Female | 9 |
| `strand` | SHS strand | Nominal | 1 = STEM, 2 = ABM, 3 = HUMSS | 9 |
| `satis_1` | Satisfaction item 1 | Ordinal | 1 = Strongly disagree ... 5 = Strongly agree | 9 |
| `satis_total` | Satisfaction scale | Interval | Sum of satis_1 to satis_5, range 5-25 | . |
| `score` | Quiz score | Ratio | 0-40 | . |

## Setting the level in software

Declaring the level in the software stops it offering you nonsense, and makes your output labelled correctly.

### Jamovi
Click the variable name in the **Data** tab. In the setup panel, choose **Measure type**: `Nominal`, `Ordinal`, or `Continuous`. Jamovi merges interval and ratio into `Continuous`.

### SPSS
Go to **Variable View**. The last column is **Measure**. Set it to `Nominal`, `Ordinal` or `Scale`. SPSS also merges interval and ratio into `Scale`.

### R
```r
# nominal and ordinal are both factors; ordered = TRUE keeps the sequence
dat$sex    <- factor(dat$sex, levels = c(1, 2), labels = c("Male", "Female"))
dat$attain <- factor(dat$attain,
                     levels  = c(1, 2, 3),
                     labels  = c("Elementary", "High school", "College"),
                     ordered = TRUE)
dat$score  <- as.numeric(dat$score)   # ratio
```

### Excel
Excel has no concept of measurement level at all. Keep a separate `Codebook` worksheet and treat it as the authority.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template</span>
Sex and strand were measured on a *nominal* scale and are summarised using frequencies and percentages. Satisfaction was measured using *five* five-point Likert items; the individual items are ordinal and are reported as medians, while the summated satisfaction score is treated as interval and reported as a mean with standard deviation. Quiz score is a ratio variable reported as a mean with standard deviation.
</div>

## Common mistakes

- **Reporting a mean for a nominal variable.** The classic. Always a frequency table instead.
- **Averaging a single Likert item and calling it interval.** Defensible for a summated scale, not for one item.
- **Assuming a percentage is always ratio.** A percentage score out of 100 is ratio. A percentile *rank* is ordinal -- the 90th percentile is not "twice as good" as the 45th.
- **Treating a coded ID number as a quantity.** Student number 20231045 is nominal, no matter how numeric it looks.
- **Letting the software decide.** It never does. It just computes.

## Practice

**1.** A hospital records patient triage level as 1 = Immediate, 2 = Urgent, 3 = Delayed. What level of measurement, and what is the correct measure of centre?

<details markdown="1">
<summary>Show the answer</summary>

Run the three questions:

1. *Order?* Yes -- Immediate is genuinely more urgent than Urgent, which is more urgent than Delayed.
2. *Equal gaps?* No. The clinical gap between Immediate and Urgent is not guaranteed to equal the gap between Urgent and Delayed.

Stop at question 2. **Ordinal.** Correct centre is the **median**; also report frequencies per level. A mean triage level of 1.7 would be meaningless.
</details>

**2.** Temperature is recorded in Kelvin instead of Celsius. Does the measurement level change?

<details markdown="1">
<summary>Show the answer</summary>

**Yes -- it becomes ratio.** Kelvin has a true zero: 0 K is absolute zero, the genuine absence of thermal energy. So 300 K really is twice as hot as 150 K.

The same physical property is interval in Celsius and ratio in Kelvin. The level is a property of the **scale**, not of the thing being measured. This is the cleanest illustration of the whole idea.
</details>

**3.** Your questionnaire asks for monthly income in bands: 1 = below 10k, 2 = 10k-20k, 3 = 20k-30k, 4 = above 30k. Income is ratio -- so can you compute the mean of this variable?

<details markdown="1">
<summary>Show the answer</summary>

**No.** You did not record income. You recorded a *band*, and the band codes are ordinal.

Two problems make the mean indefensible:

- The bands are not equal in width -- the top one is unbounded, so you do not know what value to assign it.
- The code 4 does not mean "4 of something."

Correct options: report the **median band** and the frequency distribution; or, if you genuinely need a mean, assign each band its midpoint (5k, 15k, 25k, and a defensible estimate for the top band) and report it as an **approximation, with the method stated**.

The real lesson: **this was a data-collection decision, not an analysis problem.** Asking for exact income would have preserved the ratio scale. Banding destroyed information you can never get back.
</details>

## Before you move on

You should be able to tick every box:

- [ ] I can name the four levels in order and say what each one adds
- [ ] I can run the three questions on any variable without looking them up
- [ ] I can explain why the mean of a nominal variable is meaningless, using the Region example
- [ ] I can state the difference between a single Likert item and a summated scale
- [ ] I have a codebook for my own data with a Level column filled in

Next lesson: the dataset we will use for the rest of the course, and how to describe where it sits.""",
    [{"question": "A variable has ordered values, but the gaps between consecutive values are not equal. What level is it?",
      "choices": ["Nominal", "Ordinal", "Interval", "Ratio"], "correct": 1},
     {"question": "Why can you say 300 K is twice as hot as 150 K, but not that 40 C is twice as hot as 20 C?",
      "choices": ["Kelvin uses larger numbers", "Kelvin has a true zero; Celsius zero is an arbitrary point",
                  "Celsius is ordinal", "The two scales measure different things"], "correct": 1}],
    preview=True,
)


# ===========================================================================
L(
    "Descriptive Statistics: Making Sense of Raw Numbers",
    """## What you will be able to do

Compute the mean, median, mode, range, variance and standard deviation **by hand**, on paper, showing every step -- and then get the same numbers out of Jamovi, SPSS, Excel and R. By the end you will know not just how to compute them but which one to report, and why.

## The dataset for this whole course

Everything from here to the end of the course uses the same eight students. Learn these numbers; they will keep coming back.

<div class="callout callout-case" markdown="1">
<span class="callout-label">Our data</span>
Eight Grade 11 students from one section took a 40-item statistics quiz. Their scores:

**12, 15, 15, 18, 20, 22, 25, 33**

We also know how many hours each spent reviewing: **1, 2, 2, 3, 4, 5, 6, 7** (in the same student order).
</div>

Small on purpose. Eight numbers you can add in your head means you can check every step against your own arithmetic instead of trusting output.

## Part 1 -- Where is the centre?

Three different answers to "what is a typical score," and they disagree. That disagreement is information.

### The mean, step by step

<div class="formula" markdown="1">
**mean = (sum of all values) / (number of values)**
<span class="formula-note">written as x&#772; ("x-bar") for a sample, &mu; ("mu") for a population</span>
</div>

**Step 1 -- add every value.**

```
12 + 15 + 15 + 18 + 20 + 22 + 25 + 33
= 27 + 15 + 18 + 20 + 22 + 25 + 33      (12 + 15)
= 42 + 18 + 20 + 22 + 25 + 33           (27 + 15)
= 60 + 20 + 22 + 25 + 33                (42 + 18)
= 80 + 22 + 25 + 33
= 102 + 25 + 33
= 127 + 33
= 160
```

**Step 2 -- count the values.** n = 8

**Step 3 -- divide.**

```
mean = 160 / 8 = 20.0
```

### The median, step by step

The median is the middle value once the data is sorted.

**Step 1 -- sort.** Already sorted: 12, 15, 15, 18, **20**, 22, 25, 33 -- wait, with 8 values there is no single middle.

**Step 2 -- find the middle position(s).** With n even, the two middle positions are n/2 and n/2 + 1, so positions **4 and 5**.

```
position:  1   2   3   4   5   6   7   8
value:    12  15  15  18  20  22  25  33
                       ^^  ^^
```

**Step 3 -- average them.**

```
median = (18 + 20) / 2 = 38 / 2 = 19.0
```

<div class="callout callout-key" markdown="1">
<span class="callout-label">Remember</span>
With **n odd**, the median is the single value at position (n + 1)/2 -- no averaging needed. With **n even**, average the two middle values.
</div>

### The mode

The most frequently occurring value. Count them:

| Score | 12 | 15 | 18 | 20 | 22 | 25 | 33 |
|---|---|---|---|---|---|---|---|
| Times it appears | 1 | **2** | 1 | 1 | 1 | 1 | 1 |

**mode = 15**

A dataset can have no mode (all values appear once), one mode, or several. The mode is the only centre you can use on **nominal** data -- which is exactly why the previous lesson came first.

### Which centre should you report?

| Situation | Report | Why |
|---|---|---|
| Roughly symmetric, no extreme values | **Mean** | Uses every value; most efficient |
| Skewed, or has outliers | **Median** | One extreme value cannot drag it |
| Nominal data | **Mode** | The only one that is meaningful |
| Ordinal data | **Median** | Respects order without assuming equal gaps |

Our mean (20.0) is **higher** than our median (19.0). That gap is the fingerprint of a right skew, caused by the 33. Lesson 3 makes this precise.

## Part 2 -- How spread out is it?

Two sections can both average 20 and be completely different classes. Spread is what tells them apart.

### The range

<div class="formula" markdown="1">
**range = highest &minus; lowest**
</div>

```
range = 33 - 12 = 21
```

Fast, but it uses only two values and ignores the six in between. One outlier controls it entirely.

### Variance and standard deviation, step by step

This is the calculation people find hardest, so here is every stage in a table. The idea: measure how far each value sits from the mean, then average those distances -- squaring first so that negatives do not cancel positives.

**Step 1 -- subtract the mean (20) from each value.**
**Step 2 -- square each result.**

| Score (x) | x &minus; mean | (x &minus; mean)&sup2; |
|---:|---:|---:|
| 12 | 12 &minus; 20 = &minus;8 | 64 |
| 15 | 15 &minus; 20 = &minus;5 | 25 |
| 15 | 15 &minus; 20 = &minus;5 | 25 |
| 18 | 18 &minus; 20 = &minus;2 | 4 |
| 20 | 20 &minus; 20 = 0 | 0 |
| 22 | 22 &minus; 20 = 2 | 4 |
| 25 | 25 &minus; 20 = 5 | 25 |
| 33 | 33 &minus; 20 = 13 | 169 |
| **Total** | **0** | **316** |

<div class="callout callout-key" markdown="1">
<span class="callout-label">A free check on your work</span>
The middle column **must** total exactly 0. The deviations from the mean always cancel out -- that is what "mean" means. If your middle column does not sum to zero, your mean is wrong. Check this every single time.
</div>

**Step 3 -- divide the sum of squares by n &minus; 1.**

```
sample variance = 316 / (8 - 1) = 316 / 7 = 45.14
```

**Step 4 -- take the square root.**

```
sample SD = sqrt(45.14) = 6.72
```

### Why n &minus; 1 and not n?

The question every panel asks. The honest answer:

Your eight scores are a **sample**. You want to estimate the spread of the whole population, but you had to use the *sample* mean (20) to compute the deviations -- and the sample mean sits closer to your own data than the true population mean does. So your squared deviations come out slightly too small, every time.

Dividing by 7 instead of 8 makes the number slightly bigger, correcting exactly for that. It is called **Bessel's correction**, and the result is an *unbiased* estimate.

Use n only when your data is the **entire population** -- all eight students in the class, and you care about nothing beyond those eight.

```
population variance = 316 / 8 = 39.50      population SD = 6.28
```

### Reading the standard deviation

SD is in the **same units as the data** -- 6.72 points on a 40-item quiz. That is its advantage over variance (45.14 "squared points," which means nothing to a reader).

Rough interpretation: a typical student sits about 6.7 points away from the class average of 20.

## Doing it in software

### Jamovi
1. Open your data in the **Data** tab.
2. Go to **Analyses** &rarr; **Exploration** &rarr; **Descriptives**.
3. Drag `score` into the **Variables** box.
4. Open the **Statistics** panel. Tick **Mean**, **Median**, **Mode**, **Std. deviation**, **Variance**, **Range**, **Minimum**, **Maximum**.

### SPSS
1. <kbd>Analyze</kbd> &rarr; <kbd>Descriptive Statistics</kbd> &rarr; <kbd>Frequencies</kbd>
2. Move `score` into the **Variable(s)** box.
3. Click **Statistics**, tick Mean, Median, Mode, Std. deviation, Variance, Range, Minimum, Maximum. **Continue** &rarr; **OK**.

(Use **Frequencies** rather than **Descriptives** -- SPSS's Descriptives dialog does not offer the mode.)

### Excel
Put the eight scores in cells `A1:A8`, then:

```
=AVERAGE(A1:A8)      -> 20
=MEDIAN(A1:A8)       -> 19
=MODE.SNGL(A1:A8)    -> 15
=STDEV.S(A1:A8)      -> 6.72     sample, divides by n-1
=STDEV.P(A1:A8)      -> 6.28     population, divides by n
=VAR.S(A1:A8)        -> 45.14
=MAX(A1:A8)-MIN(A1:A8) -> 21
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Excel trap</span>
`STDEV.S` and `STDEV.P` differ, and the old `STDEV` is an alias for `STDEV.S`. Picking the wrong one is one of the most common silent errors in student work. **Sample data -> `STDEV.S`.**
</div>

### R
```r
score <- c(12, 15, 15, 18, 20, 22, 25, 33)

mean(score)      # 20
median(score)    # 19
var(score)       # 45.14286   (R always uses n-1)
sd(score)        # 6.718827
range(score)     # 12 33
summary(score)   # Min, Q1, Median, Mean, Q3, Max in one line
```

R has no built-in `mode()` for statistics (`mode()` returns the storage type). Get it with:
```r
names(sort(table(score), decreasing = TRUE))[1]   # "15"
```

## Reading the output

Jamovi will show something like this. Confirm each number against your hand computation:

```
Descriptives
                        score
N                           8
Mean                     20.0     <- matches our 160/8
Median                   19.0     <- matches our (18+20)/2
Mode                     15.0     <- the repeated value
Standard deviation       6.72     <- matches sqrt(316/7)
Variance                 45.1     <- matches 316/7
Minimum                    12
Maximum                    33
```

If the software disagrees with your arithmetic, find out why before continuing. Usually it is a typo in data entry -- which is exactly why you check.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- fill in your own numbers</span>
The *eight* students scored a mean of *20.00* (*SD* = *6.72*) on the *40-item* quiz, with scores ranging from *12* to *33*. The median of *19.00* was slightly lower than the mean, indicating a mild positive skew.
</div>

Reporting conventions to follow:

- Report the **SD alongside every mean**, always. A mean with no SD is half a result.
- Two decimal places is the normal convention for means and SDs.
- Italicise statistical symbols in APA: *M*, *SD*, *n*, *p*.
- APA allows *M* = 20.00, *SD* = 6.72 as shorthand.

## Common mistakes

- **Reporting a mean with no measure of spread.** The single most common omission in student theses.
- **Using `STDEV.P` on sample data** in Excel, or `n` instead of `n - 1` by hand.
- **Forgetting to sort before finding the median.** The median of unsorted data is meaningless.
- **Reporting the mean when the data is clearly skewed.** If mean and median differ noticeably, say so and consider the median.
- **Rounding too early.** Carry full precision through the calculation and round only the final answer. Rounding the mean to 20 before computing deviations is fine here because it is exact, but if the mean were 19.8375 you would need to keep it.

## Practice

**1.** Seven students in another section scored: 14, 16, 16, 19, 21, 24, 30. Compute the mean, median and mode.

<details markdown="1">
<summary>Show the worked answer</summary>

**Mean.** Sum first:
```
14 + 16 = 30
30 + 16 = 46
46 + 19 = 65
65 + 21 = 86
86 + 24 = 110
110 + 30 = 140
```
n = 7, so mean = 140 / 7 = **20.00**

**Median.** n is odd, so the middle position is (7 + 1)/2 = **position 4**.
```
position:  1   2   3   4   5   6   7
value:    14  16  16  19  21  24  30
                       ^^
```
median = **19**

**Mode.** 16 appears twice, everything else once. mode = **16**

Note this section has the *same* mean as ours (20) and a different shape entirely. Mean alone never tells you enough.
</details>

**2.** Using that same section (14, 16, 16, 19, 21, 24, 30), compute the sample standard deviation. Show the deviation table.

<details markdown="1">
<summary>Show the worked answer</summary>

Mean = 20 (from question 1).

| x | x &minus; 20 | (x &minus; 20)&sup2; |
|---:|---:|---:|
| 14 | &minus;6 | 36 |
| 16 | &minus;4 | 16 |
| 16 | &minus;4 | 16 |
| 19 | &minus;1 | 1 |
| 21 | 1 | 1 |
| 24 | 4 | 16 |
| 30 | 10 | 100 |
| **Total** | **0** | **186** |

The middle column sums to 0 -- our check passes.

```
sample variance = 186 / (7 - 1) = 186 / 6 = 31.00
sample SD       = sqrt(31.00)   = 5.57
```

**Compare with our class:** same mean (20.00), but SD 5.57 versus 6.72. This section is **more consistent** -- their scores cluster more tightly around the average. A teacher would treat these two classes very differently, and the mean alone would have hidden that completely.
</details>

**3.** A student computes the deviations from the mean and gets a total of 4, not 0. What went wrong?

<details markdown="1">
<summary>Show the answer</summary>

**The mean is wrong,** or a deviation was subtracted in the wrong direction.

Deviations from the true mean always sum to exactly zero -- it is a mathematical property, not a coincidence. A non-zero total means one of:

- the mean was computed incorrectly (most likely -- recheck the sum and the division)
- the mean was rounded before subtracting (e.g. using 19.8 instead of 19.8375)
- one subtraction was done as *mean &minus; x* instead of *x &minus; mean*
- a value was copied wrongly into the table

Fix the mean before going any further. Everything downstream -- variance, SD, every test in this course -- is built on it.
</details>

## Before you move on

- [ ] I can compute a mean, median and mode by hand and say when each is the right choice
- [ ] I can build the deviation table and use the "sums to zero" check
- [ ] I can explain n &minus; 1 to a panel without reading from notes
- [ ] I know which Excel function is for sample data and which is for a population
- [ ] I can report a mean in APA format with its SD

Next: our mean is higher than our median. Lesson 3 explains exactly what that gap is telling us.""",
    [{"question": "The deviations from the mean in your table sum to 4 instead of 0. What is the most likely cause?",
      "choices": ["The data is skewed", "The mean was computed or rounded incorrectly",
                  "You should have used n-1", "There is an outlier"], "correct": 1},
     {"question": "Which Excel function computes the standard deviation of a sample?",
      "choices": ["STDEV.P", "STDEV.S", "VAR.P", "AVERAGE"], "correct": 1}],
    preview=True,
)


# ===========================================================================
L(
    "Skewness, Kurtosis and the Shape of a Distribution",
    """## What you will be able to do

Decide, with a number rather than a feeling, whether your data is symmetric enough to report a mean -- and know what to do when it is not. You will compute skewness two ways by hand, read the value software gives you, and apply the cut-offs a panel will expect.

## Why shape is the third thing you need

You already have centre (lesson 2) and spread (lesson 2). Shape is the third leg.

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
A barangay reports **mean monthly household income = &#8369;28,000**. A resident objects: "Nobody here earns that." Both are telling the truth.

The **median** is &#8369;17,500. A handful of high earners pull the mean up while leaving the median alone. Reporting only the mean misrepresents the typical household -- and reporting only the median hides the high earners. Shape is what makes you notice.
</div>

## Skew: is the distribution lopsided?

<div class="callout callout-key" markdown="1">
<span class="callout-label">The direction rule</span>
**The skew is named after the tail, not the hump.**

- **Right (positive) skew** -- long tail stretching to the *right*. Most values low, a few very high. Income, waiting times, number of children.
- **Left (negative) skew** -- long tail stretching to the *left*. Most values high, a few very low. Scores on an easy exam, age at death.
- **Symmetric** -- both tails about equal.
</div>

### The instant check: compare mean and median

The mean is dragged by extreme values; the median is not. So the gap between them tells you the direction immediately.

| If... | Then the skew is... |
|---|---|
| mean > median | **Right (positive)** |
| mean < median | **Left (negative)** |
| mean &asymp; median | Roughly symmetric |

Our class: **mean 20.0, median 19.0**. Mean is higher, so **right skew** -- caused by the 33.

This check needs no software and no formula. Use it every time you open a dataset.

### Pearson's second coefficient of skewness

Turns that gap into a number.

<div class="formula" markdown="1">
**Sk = 3(mean &minus; median) / SD**
</div>

For our class:

```
Sk = 3 x (20.0 - 19.0) / 6.72
   = 3 x 1.0 / 6.72
   = 3.0 / 6.72
   = 0.45
```

Interpretation: **mild positive skew**. The coefficient runs roughly from &minus;3 to +3.

### The moment coefficient (what software reports)

Software uses a different, more sensitive formula based on cubed deviations. Cubing preserves sign, so values far above the mean contribute large positive amounts and values far below contribute large negative amounts.

<div class="formula" markdown="1">
**g&#8321; = [ &Sigma;(x &minus; mean)&sup3; / n ] / SD&#8345;&sup3;
<span class="formula-note">where SD&#8345; is the population standard deviation (divides by n)</span>
</div>

For our class this works out to **g&#8321; = 0.79**.

Note the two methods disagree (0.45 versus 0.79) -- they are different formulas. **Report which one you used**, and do not compare a Pearson coefficient from one study with a moment coefficient from another.

## Kurtosis: how heavy are the tails?

Kurtosis is about **tail weight** -- how often extreme values occur -- not about how "peaked" the distribution looks. The peakedness description is a common textbook error.

| Excess kurtosis | Name | Means |
|---|---|---|
| &asymp; 0 | Mesokurtic | Tails like a normal distribution |
| > 0 | Leptokurtic | **Heavier** tails -- more extreme values than normal |
| < 0 | Platykurtic | **Lighter** tails -- fewer extreme values than normal |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Check which kurtosis your software reports</span>
A normal distribution has raw kurtosis **3**. Most software subtracts 3 and reports **excess kurtosis**, so normal becomes **0**.

SPSS, Jamovi, Excel and R's `psych` package all report **excess** kurtosis. If you see a value near 3 for data that looks normal, your tool is reporting raw kurtosis -- subtract 3 before interpreting.
</div>

Our class has excess kurtosis **&minus;0.23** -- essentially normal tails.

## The cut-offs to use

These are working guidelines, widely cited in social-science methods texts, not mathematical laws:

| Statistic | Acceptable as "approximately normal" |
|---|---|
| Skewness | between &minus;1 and +1 (some use &minus;2 to +2) |
| Excess kurtosis | between &minus;2 and +2 (some use &minus;7 to +7) |

A stricter, more defensible test divides the statistic by its standard error:

<div class="formula" markdown="1">
**z = skewness / SE(skewness)**
<span class="formula-note">|z| > 1.96 suggests significant skew at &alpha; = .05 -- but only trust this for n &lt; 300</span>
</div>

With large samples this z-test flags skew far too small to matter. Above roughly n = 300, judge from a histogram and the actual size of the coefficient instead.

## Doing it in software

### Jamovi
**Analyses** &rarr; **Exploration** &rarr; **Descriptives** &rarr; open **Statistics** &rarr; under *Distribution*, tick **Skewness** and **Kurtosis**. Jamovi prints each one with its standard error directly beneath.

### SPSS
<kbd>Analyze</kbd> &rarr; <kbd>Descriptive Statistics</kbd> &rarr; <kbd>Frequencies</kbd> &rarr; **Statistics** &rarr; tick **Skewness** and **Kurtosis** under *Distribution*. SPSS reports excess kurtosis with standard errors.

### Excel
```
=SKEW(A1:A8)      -> 0.79    (moment coefficient, sample-adjusted)
=KURT(A1:A8)      -> -0.23   (excess kurtosis)
```

### R
```r
score <- c(12, 15, 15, 18, 20, 22, 25, 33)

# base R has no skewness function; use the psych package
install.packages("psych")   # once
library(psych)
describe(score)             # gives mean, sd, median, skew, kurtosis in one row

# or compute the moment coefficient directly
n  <- length(score)
m  <- mean(score)
sdp <- sqrt(sum((score - m)^2) / n)      # population SD
sum((score - m)^3) / n / sdp^3            # 0.7855
```

## Reading the output

```
Descriptives
                          score
N                             8
Mean                       20.0
Median                     19.0
Std. deviation             6.72
Skewness                  0.786
Std. error of skewness    0.752     <- z = 0.786/0.752 = 1.05, not significant
Kurtosis                 -0.231
Std. error of kurtosis    1.481     <- z = -0.16, not significant
```

**Verdict:** skewness 0.79 sits inside &plusmn;1, its z is only 1.05, and kurtosis is near zero. This data is **acceptably close to normal**. The mean is a defensible summary.

## What to do when the data IS badly skewed

In order of preference:

1. **Check for errors first.** An income of &#8369;9,000,000 is more often a typo than a billionaire. Skew caused by a data-entry error is not skew.
2. **Report the median and IQR instead of the mean and SD.** Often the whole fix. Honest, simple, no transformation to explain.
3. **Transform.** A log transformation is the standard remedy for right skew. Remember the interpretation changes -- you are now modelling log-income, and the back-transformed mean is closer to a median.
4. **Use a method that does not assume normality.** Nonparametric tests (Mann-Whitney, Kruskal-Wallis) or bootstrapping.
5. **Do nothing, if n is large.** The central limit theorem means a t-test on the *mean* holds up with large samples even when the raw data is skewed. This protects tests about means; it does not make the mean a good *description*.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Never do this</span>
Deleting values to make the skew go away. If an extreme value is genuine, removing it is falsification. Investigate it, report it, and choose a method that tolerates it.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template</span>
Quiz scores were mildly positively skewed (*skewness* = *0.79*, *SE* = *0.75*) with near-normal tails (*excess kurtosis* = *&minus;0.23*, *SE* = *1.48*). Both values fall within the conventional &plusmn;1 and &plusmn;2 limits respectively, so the distribution was treated as approximately normal and parametric procedures were retained.
</div>

## Common mistakes

- **Naming the skew after the hump instead of the tail.** Right skew means the *tail* points right; the hump is on the left.
- **Reading kurtosis as peakedness.** It is tail weight.
- **Comparing a raw kurtosis to an excess kurtosis.** They differ by exactly 3.
- **Using the z-test for skewness on a large sample.** It rejects trivial departures once n is in the hundreds.
- **Trusting a coefficient over a picture.** With n under about 50 both statistics are unstable. Always look at a histogram as well.

## Practice

**1.** A dataset has mean 45, median 52. Which way is it skewed, and which measure of centre should you report?

<details markdown="1">
<summary>Show the answer</summary>

Mean (45) is **less than** median (52), so the distribution is **left (negatively) skewed** -- a long tail stretching toward the low values, with most cases bunched high.

Report the **median**. A few unusually low values are dragging the mean down and away from where most of the data actually sits. Report the IQR alongside it for spread.

A real example of this shape: scores on an exam most students found easy, where a handful failed badly.
</details>

**2.** Compute Pearson's second coefficient of skewness for a dataset with mean = 62, median = 58, SD = 12. Interpret it.

<details markdown="1">
<summary>Show the worked answer</summary>

```
Sk = 3(mean - median) / SD
   = 3(62 - 58) / 12
   = 3 x 4 / 12
   = 12 / 12
   = 1.00
```

**Sk = 1.00** -- positive, so right-skewed, and sitting right at the conventional &plusmn;1 boundary.

Interpretation: **moderate positive skew, at the edge of acceptable.** Look at the histogram before deciding. If the skew comes from a few genuine high values and n is large, the mean is still usable but should be reported with the median beside it. If n is small, prefer the median.
</details>

**3.** Your software reports kurtosis = 3.2 for a variable whose histogram looks perfectly bell-shaped. Is something wrong?

<details markdown="1">
<summary>Show the answer</summary>

**Nothing is wrong with the data -- you are reading raw kurtosis, not excess kurtosis.**

A normal distribution has raw kurtosis of exactly 3. Your value of 3.2 corresponds to an excess kurtosis of 3.2 &minus; 3 = **0.2**, which is essentially normal and entirely consistent with the bell-shaped histogram.

Before interpreting any kurtosis value, establish which version your tool reports. Most report excess (normal = 0), but not all do, and a value near 3 on normal-looking data is the tell.
</details>

## Before you move on

- [ ] I can name the skew direction from the tail, not the hump
- [ ] I can use the mean-vs-median comparison as an instant skew check
- [ ] I can compute Pearson's second coefficient by hand
- [ ] I know whether my software reports raw or excess kurtosis
- [ ] I have a plan for what to do when data is badly skewed, and deleting values is not on it

Next: skew and kurtosis are numbers. The next lesson gives you the pictures that show you *where* the skew is coming from.""",
    [{"question": "A distribution has mean 45 and median 52. How is it skewed?",
      "choices": ["Right (positive)", "Left (negative)", "Symmetric", "Cannot tell"], "correct": 1},
     {"question": "Kurtosis measures:",
      "choices": ["How peaked the distribution looks", "How heavy the tails are",
                  "How wide the range is", "Whether the mean equals the median"], "correct": 1}],
)


# ===========================================================================
L(
    "Exploratory Data Analysis: Boxplots and Stem-and-Leaf",
    """## What you will be able to do

Build a five-number summary and draw a boxplot by hand, apply the 1.5 x IQR rule to flag outliers, read a stem-and-leaf display, and decide what to do about an extreme value -- which is almost never "delete it."

## Why look before you test

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
Four sections all average 20 on the quiz. The principal concludes the sections are equivalent and moves on.

Side-by-side boxplots show Section C has a box twice as wide as the others, containing both the highest and lowest scorers in the year level. The averages were identical; the classes were not. **No summary statistic would have shown this. The picture did.**
</div>

John Tukey, who invented both displays in this lesson, put it well: the greatest value of a picture is that it forces us to notice what we never expected to see.

## The five-number summary

Five values describe a distribution without assuming any shape at all.

| | Our class |
|---|---|
| Minimum | 12 |
| Q1 (25th percentile) | 15 |
| Median (50th percentile) | 19 |
| Q3 (75th percentile) | 23.5 |
| Maximum | 33 |

### Finding the quartiles, step by step

Several methods exist and they give slightly different answers on small samples. This is the **median-of-halves** method, the one taught in most Philippine statistics courses.

**Step 1 -- sort, and find the median.**
```
12  15  15  18  |  20  22  25  33
                ^
         median = (18+20)/2 = 19
```

**Step 2 -- Q1 is the median of the lower half.** With an even n, the lower half is the values *below* the median position.
```
lower half:  12  15  15  18
             Q1 = (15 + 15)/2 = 15
```

**Step 3 -- Q3 is the median of the upper half.**
```
upper half:  20  22  25  33
             Q3 = (22 + 25)/2 = 23.5
```

**Step 4 -- the interquartile range.**
```
IQR = Q3 - Q1 = 23.5 - 15 = 8.5
```

<div class="callout callout-key" markdown="1">
<span class="callout-label">What IQR means</span>
The IQR is the width of the **middle 50%** of your data. Half of all students scored somewhere in an 8.5-point band.

Unlike the range and the SD, the IQR is **resistant** -- you could change the 33 to 3,300 and the IQR would not move at all. That is why it is the spread measure that pairs with the median.
</div>

## The 1.5 x IQR rule for outliers

<div class="formula" markdown="1">
**lower fence = Q1 &minus; 1.5 &times; IQR &nbsp;&nbsp;&nbsp; upper fence = Q3 + 1.5 &times; IQR**
</div>

For our class:

```
lower fence = 15   - 1.5 x 8.5 = 15   - 12.75 = 2.25
upper fence = 23.5 + 1.5 x 8.5 = 23.5 + 12.75 = 36.25
```

Every score lies between 2.25 and 36.25, so **no outliers** -- not even the 33, which is comfortably below 36.25. It pulls the skew without qualifying as an outlier. Those are two different things.

## Drawing the boxplot

```
      12        15    19      23.5              33
       |---------[=====|=======]-----------------|
      min       Q1   median   Q3               max
                 |<---- IQR 8.5 ---->|

       0    5   10   15   20   25   30   35   40
       |----|----|----|----|----|----|----|----|
```

How to read one:

- **The box** spans Q1 to Q3 -- the middle 50%
- **The line inside the box** is the median. Its position shows skew: nearer the bottom means right skew
- **The whiskers** reach to the most extreme values still *inside* the fences
- **Individual dots** beyond the whiskers are flagged outliers

Our median line at 19 sits left of the box centre (19.25), and the right whisker is longer than the left -- the picture of the mild right skew we measured in lesson 3.

## Stem-and-leaf: keeping the actual numbers

A boxplot summarises. A stem-and-leaf shows every individual value while still revealing shape.

Split each number: the **stem** is everything but the last digit, the **leaf** is the last digit.

```
Stem | Leaf
-----+------
   1 | 2 5 5 8
   2 | 0 2 5
   3 | 3

Key: 1 | 2 means 12
```

Read it: four students in the teens (12, 15, 15, 18), three in the twenties (20, 22, 25), one in the thirties (33).

<div class="callout callout-key" markdown="1">
<span class="callout-label">Why this display still matters</span>
Turn the page sideways and the leaves form a histogram -- but unlike a histogram, **no information is lost**. You can read every original value back out.

It is also the fastest way to spot **digit preference**: if every leaf is 0 or 5, your respondents estimated rather than measured. That is a data-quality finding a histogram would hide completely.
</div>

## Worked example with an actual outlier

Seven delivery times in minutes: **18, 22, 24, 25, 27, 29, 74**

**Step 1 -- sort.** Already sorted.

**Step 2 -- median.** n = 7, odd, so position (7+1)/2 = 4 -> **median = 25**

**Step 3 -- quartiles.** Exclude the median itself; lower half is 18, 22, 24 and upper half is 27, 29, 74.
```
Q1 = median of (18, 22, 24) = 22
Q3 = median of (27, 29, 74) = 29
IQR = 29 - 22 = 7
```

**Step 4 -- fences.**
```
lower = 22 - 1.5 x 7 = 22 - 10.5 = 11.5
upper = 29 + 1.5 x 7 = 29 + 10.5 = 39.5
```

**Step 5 -- flag.** 74 > 39.5, so **74 is an outlier**.

**Step 6 -- decide what to do.** Work through this order:

1. **Is it an error?** Check the source. A delivery logged at 74 minutes may be a typo for 24, or the rider may have had a flat tyre. *Go and look.*
2. **If it is an error you can correct,** correct it and document the correction.
3. **If it is an error you cannot correct,** remove it and report exactly how many cases were removed and why.
4. **If it is genuine,** keep it. Report the median (25) and IQR (7) rather than the mean, and mention the extreme case explicitly.

Notice the difference it makes: with 74 included the mean is 31.3 -- higher than six of the seven actual deliveries. The median of 25 describes the typical delivery far better.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The rule that matters</span>
**An outlier is flagged, not condemned.** The 1.5 x IQR rule is a convention for drawing attention, not a test for wrongness. Deleting genuine data because a rule flagged it is falsification, and a panel will ask.
</div>

## Doing it in software

### Jamovi
1. **Analyses** &rarr; **Exploration** &rarr; **Descriptives**
2. Put `score` in **Variables**
3. Open **Plots** &rarr; tick **Box plot**, and also **Data** and **Mean** to overlay the raw points
4. For group comparison, drag the grouping variable into **Split by**

Jamovi's overlaid data points are genuinely useful on small samples -- you see the actual observations, not just the summary.

### SPSS
- Five-number summary: <kbd>Analyze</kbd> &rarr; <kbd>Descriptive Statistics</kbd> &rarr; <kbd>Explore</kbd>, put `score` in **Dependent List**, **OK**
- Explore gives boxplot, stem-and-leaf, percentiles and normality tests in one run
- SPSS labels outliers with the case number on the plot, and marks extreme cases (beyond 3 x IQR) with an asterisk

### Excel
1. Select your data
2. <kbd>Insert</kbd> &rarr; <kbd>Charts</kbd> &rarr; <kbd>Statistic Chart</kbd> &rarr; **Box and Whisker** (Excel 2016 and later)

For the numbers directly:
```
=QUARTILE.INC(A1:A8, 1)    -> 15      Q1
=QUARTILE.INC(A1:A8, 3)    -> 23.5    Q3
=QUARTILE.INC(A1:A8,3)-QUARTILE.INC(A1:A8,1)   -> 8.5   IQR
```

### R
```r
score <- c(12, 15, 15, 18, 20, 22, 25, 33)

summary(score)      # Min, Q1, Median, Mean, Q3, Max
IQR(score)          # 8.5
boxplot(score, horizontal = TRUE, main = "Quiz scores")
stem(score)         # stem-and-leaf display

# which values does R flag as outliers?
boxplot.stats(score)$out    # numeric(0) -- none
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Why your Q1 may not match</span>
R, Excel and SPSS use slightly different quartile algorithms (there are nine recognised methods). On a sample of 8 they can differ by a point or two; on samples over about 50 the difference is negligible.

If your hand calculation and your software disagree on a small sample, neither is wrong. **State the method you used** and stay consistent.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template</span>
Quiz scores had a median of *19.0* (*IQR* = *8.5*, range *12*&ndash;*33*). Inspection of the boxplot revealed *no* values beyond 1.5 &times; IQR from the quartiles. The median line sat below the centre of the box, consistent with the mild positive skew reported above.
</div>

When you *do* have outliers:

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- with outliers</span>
*One* case (*2.9%*) exceeded the upper fence of *39.5* minutes. Verification against the dispatch log confirmed the value as genuine rather than a recording error, so the case was **retained** and results are reported using the median and interquartile range.
</div>

## Common mistakes

- **Deleting outliers because the boxplot drew a dot.** Investigate first. Always.
- **Reporting a boxplot with no scale.** Unlabelled axes make it unreadable.
- **Assuming a symmetric-looking box means normal data.** A boxplot cannot show bimodality -- two clear humps can produce an ordinary-looking box. Pair it with a histogram.
- **Comparing boxplots drawn on different scales.** Put group comparisons on one shared axis.
- **Reporting the mean alongside a boxplot of skewed data.** The boxplot is built on the median; be consistent.

## Practice

**1.** Nine values: 4, 6, 7, 7, 9, 11, 12, 15, 28. Build the five-number summary and test 28 with the 1.5 x IQR rule.

<details markdown="1">
<summary>Show the worked answer</summary>

**Median.** n = 9, odd. Position (9+1)/2 = **5** -> median = **9**

**Quartiles.** Exclude the median; lower half = 4, 6, 7, 7 and upper half = 11, 12, 15, 28.
```
Q1 = (6 + 7)/2   = 6.5
Q3 = (12 + 15)/2 = 13.5
IQR = 13.5 - 6.5 = 7.0
```

**Fences.**
```
lower = 6.5  - 1.5 x 7 = 6.5  - 10.5 = -4.0
upper = 13.5 + 1.5 x 7 = 13.5 + 10.5 = 24.0
```

**Five-number summary:** 4, 6.5, 9, 13.5, 28

**28 > 24.0, so 28 is flagged as an outlier.**

Next step is investigation, not deletion. And note the effect: including 28 the mean is 11.0; the median is 9. Six of the nine values sit below the mean.
</details>

**2.** Build a stem-and-leaf display for: 23, 25, 27, 31, 34, 34, 38, 42, 45, 51.

<details markdown="1">
<summary>Show the answer</summary>

```
Stem | Leaf
-----+-----------
   2 | 3 5 7
   3 | 1 4 4 8
   4 | 2 5
   5 | 1

Key: 2 | 3 means 23
```

Reading the shape: the 30s hold the most values (4), with counts tapering off in both directions and a slightly longer tail to the right. Mildly right-skewed, single-humped.

Every original value is still recoverable from the display -- that is the property a histogram gives up.
</details>

**3.** Two boxplots for the same test: Section A has a narrow box with the median in the middle; Section B has a wide box with the median near the bottom. Both medians are 75. What does this tell a teacher?

<details markdown="1">
<summary>Show the answer</summary>

**Section A** -- narrow box means a small IQR, so the middle half of students scored within a tight band. Median centred means roughly symmetric. This class is **consistent**; a single lesson pitched at 75 suits most of them.

**Section B** -- wide box means a large IQR, so scores are spread widely. Median near the bottom of the box means **right skew**: most students bunched at the lower end with a tail of high achievers pulling the upper quartile up.

**What the teacher should do:** the identical medians say the two classes are equivalent. They are not. Section B contains at least two distinct groups and needs differentiated instruction -- remediation for the cluster at the bottom, extension for the tail at the top. Teaching both sections the same way would fail half of Section B.

This is exactly the situation from the opening scenario, and exactly what a table of means hides.
</details>

## Before you move on

- [ ] I can compute Q1, Q3 and IQR by hand using the median-of-halves method
- [ ] I can apply the 1.5 x IQR rule and state the fences
- [ ] I can read skew from where the median line sits inside the box
- [ ] I can build and read a stem-and-leaf display
- [ ] I have an investigate-first procedure for outliers, and deleting is the last option

Next: we switch from describing data to reasoning about uncertainty. Probability is the language for that.""",
    [{"question": "Q1 = 20, Q3 = 32. What is the upper fence for flagging outliers?",
      "choices": ["44", "50", "38", "56"], "correct": 1},
     {"question": "A value is flagged by the 1.5 x IQR rule. What should you do first?",
      "choices": ["Delete it", "Investigate whether it is an error or genuine",
                  "Transform the variable", "Report the mean instead"], "correct": 1}],
)


# ===========================================================================
L(
    "Probability Basics You Actually Need",
    """## What you will be able to do

Compute the probability of events, know exactly when to add and when to multiply, read a two-way table for conditional probabilities, and apply Bayes' rule. You will also be able to explain why "independent" and "mutually exclusive" are almost opposites -- a distinction that trips up most students and most panels.

## Why a statistics course needs probability

Every test you will run answers the same shape of question: **"If nothing interesting were going on, how likely is data like mine?"** That "how likely" is a probability. Without this lesson, p-values are magic numbers. With it, they are arithmetic.

## The rules, from the ground up

### What a probability is

<div class="formula" markdown="1">
**P(event) = (number of ways the event can happen) / (total number of equally likely outcomes)**
</div>

Every probability sits between 0 and 1. P = 0 means impossible, P = 1 means certain. A probability greater than 1 is always an arithmetic error.

Rolling a fair die:
```
P(rolling a 4)     = 1/6 = 0.167
P(rolling even)    = 3/6 = 0.500      (2, 4, 6)
P(rolling below 7) = 6/6 = 1.000      certain
```

### The complement rule

<div class="formula" markdown="1">
**P(not A) = 1 &minus; P(A)**
</div>

Often the shortcut. "At least one" problems are far easier backwards:

```
P(at least one head in 3 coin flips)
= 1 - P(no heads at all)
= 1 - P(tails AND tails AND tails)
= 1 - (0.5 x 0.5 x 0.5)
= 1 - 0.125
= 0.875
```

Computing that directly would mean adding up the seven ways to get one, two or three heads. The complement takes one line.

### Adding: OR

<div class="callout callout-key" markdown="1">
<span class="callout-label">The addition rule</span>
**If A and B cannot both happen** (mutually exclusive):
&nbsp;&nbsp;&nbsp;&nbsp;P(A or B) = P(A) + P(B)

**If they can both happen** (the general case):
&nbsp;&nbsp;&nbsp;&nbsp;P(A or B) = P(A) + P(B) &minus; P(A and B)

The subtraction stops you counting the overlap twice.
</div>

Drawing one card from a standard deck:

```
P(King or Queen)  = 4/52 + 4/52 = 8/52 = 0.154
   A King cannot also be a Queen -- mutually exclusive, so just add.

P(King or Heart)  = 4/52 + 13/52 - 1/52 = 16/52 = 0.308
   The King of Hearts is in both groups. Without subtracting it
   you would count that one card twice and get 17/52.
```

### Multiplying: AND

<div class="callout callout-key" markdown="1">
<span class="callout-label">The multiplication rule</span>
**If A and B are independent:**
&nbsp;&nbsp;&nbsp;&nbsp;P(A and B) = P(A) &times; P(B)

**In general:**
&nbsp;&nbsp;&nbsp;&nbsp;P(A and B) = P(A) &times; P(B given A)
</div>

```
Two coin flips, both heads:      0.5 x 0.5 = 0.25
   Independent -- the coin has no memory.

Two Kings drawn WITHOUT replacement:
   P(first King) = 4/52
   P(second King GIVEN first was a King) = 3/51    <- only 3 Kings in 51 cards now
   P(both) = (4/52) x (3/51) = 12/2652 = 0.0045
```

### Mutually exclusive versus independent

This is the distinction people get wrong. They are not similar ideas; they are nearly opposites.

| | Mutually exclusive | Independent |
|---|---|---|
| Meaning | Cannot both happen | One tells you nothing about the other |
| P(A and B) | = 0 | = P(A) &times; P(B) |
| Example | Rolling a 3 *and* a 5 on one die | Rolling a 3, then rolling a 5 |
| Knowing A happened... | tells you B definitely did **not** | tells you **nothing** about B |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The consequence</span>
If two events are mutually exclusive and both have non-zero probability, they **cannot** be independent. Knowing one occurred tells you the other did not -- which is the opposite of telling you nothing.
</div>

## Conditional probability from a real table

Here is a table we will meet again in the chi-square lesson. 60 students, classified by whether they attended a review session and whether they passed:

| | Passed | Failed | **Total** |
|---|---:|---:|---:|
| **Attended review** | 18 | 12 | **30** |
| **Did not attend** | 9 | 21 | **30** |
| **Total** | **27** | **33** | **60** |

Every probability question about these students is answered by choosing the right denominator.

### Marginal probability -- denominator is everybody

```
P(passed)   = 27/60 = 0.45      45% of all students passed
P(attended) = 30/60 = 0.50      half attended the review
```

### Joint probability -- denominator is still everybody

```
P(attended AND passed) = 18/60 = 0.30
   Of all 60 students, 30% both attended and passed.
```

### Conditional probability -- denominator is the group you conditioned on

<div class="formula" markdown="1">
**P(A given B) = P(A and B) / P(B)**
</div>

```
P(passed GIVEN attended)
   = 18/30 = 0.60        <- denominator is the 30 who attended

P(passed GIVEN did not attend)
   = 9/30  = 0.30        <- denominator is the 30 who did not
```

<div class="callout callout-key" markdown="1">
<span class="callout-label">The whole lesson in one comparison</span>
60% of review-attenders passed. 30% of non-attenders passed.

**The conditional probabilities are what answer the research question.** The joint probability (30%) and the marginal probability (45%) do not. Students routinely report joint percentages and interpret them as pass rates. They are different numbers answering different questions.
</div>

### Testing independence from the table

Are attending and passing independent? If they were, P(A and B) would equal P(A) x P(B):

```
If independent:  P(attended) x P(passed) = 0.50 x 0.45 = 0.225
Actually observed: P(attended and passed) = 0.30

0.30 is not 0.225 -> NOT independent.
```

Attendance and passing are related in this sample. Whether that relationship is bigger than chance is precisely what the chi-square test will answer later in this course.

## Bayes' rule: reversing the condition

Sometimes you know P(A given B) and need P(B given A). These are **not** the same number, and confusing them is the most consequential error in applied probability.

<div class="formula" markdown="1">
**P(B given A) = [ P(A given B) &times; P(B) ] / P(A)**
</div>

From our table: we know 60% of attenders passed. Among the students who passed, what proportion attended?

```
P(attended GIVEN passed)
   = [ P(passed given attended) x P(attended) ] / P(passed)
   = [ 0.60 x 0.50 ] / 0.45
   = 0.30 / 0.45
   = 0.667
```

Check straight from the table: 18 of the 27 who passed had attended. 18/27 = 0.667. The rule agrees.

Notice: P(passed | attended) = 0.60 but P(attended | passed) = 0.667. **Reversing the condition changes the answer.**

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Why this matters beyond exams</span>
A screening test that is 99% accurate does *not* mean a positive result gives you a 99% chance of having the disease. If the disease is rare, most positives are false positives. P(positive | sick) and P(sick | positive) can differ enormously.

The same confusion underlies the most common misreading of a p-value: P(data | null true) is **not** P(null true | data).
</div>

## Doing it in software

Probability is mostly arithmetic you do yourself, but software helps with distributions and tables.

### Excel
```
=1-0.5^3                  -> 0.875    at least one head in 3 flips
=COMBIN(52,2)             -> 1326     ways to choose 2 cards from 52
=BINOM.DIST(3,10,0.5,FALSE) -> 0.1172 exactly 3 heads in 10 flips
=BINOM.DIST(3,10,0.5,TRUE)  -> 0.1719 3 or fewer heads
```

### R
```r
1 - 0.5^3                 # 0.875
choose(52, 2)             # 1326
dbinom(3, size = 10, prob = 0.5)   # 0.1171875  exactly 3
pbinom(3, size = 10, prob = 0.5)   # 0.171875   3 or fewer

# conditional probabilities straight from a table
tab <- matrix(c(18, 12, 9, 21), nrow = 2, byrow = TRUE,
              dimnames = list(c("Attended", "Did not"), c("Passed", "Failed")))
prop.table(tab)          # joint probabilities (all cells sum to 1)
prop.table(tab, 1)       # row-conditional: P(passed | attended)
prop.table(tab, 2)       # column-conditional: P(attended | passed)
```

That `prop.table` margin argument is worth memorising: **1 = rows, 2 = columns**. Choosing the wrong one gives you the wrong conditional probability with no error message.

### Jamovi / SPSS
Both give conditional percentages through crosstabs. In Jamovi: **Analyses** &rarr; **Frequencies** &rarr; **Independent Samples (&chi;&sup2; test of association)**, then under **Cells** tick **Row** or **Column** percentages. In SPSS: <kbd>Analyze</kbd> &rarr; <kbd>Descriptive Statistics</kbd> &rarr; <kbd>Crosstabs</kbd> &rarr; **Cells** &rarr; tick **Row** or **Column**.

## Common mistakes

- **Adding probabilities of overlapping events** without subtracting the intersection.
- **Multiplying without checking independence.** Drawing without replacement changes the second probability.
- **Confusing P(A|B) with P(B|A).** The single most expensive error in this lesson.
- **Treating mutually exclusive as independent.** They are close to opposites.
- **Reporting a joint percentage as a rate.** "30% of students attended and passed" is not a pass rate.
- **Getting a probability above 1.** Always an error -- usually double-counting an overlap.

## Practice

**1.** In a class of 40, 25 take Math, 18 take Physics, and 10 take both. What is P(a random student takes Math or Physics)?

<details markdown="1">
<summary>Show the worked answer</summary>

The groups overlap (10 students take both), so use the **general** addition rule:

```
P(Math or Physics) = P(Math) + P(Physics) - P(both)
                   = 25/40  + 18/40      - 10/40
                   = 33/40
                   = 0.825
```

**0.825, or 82.5%.**

Sanity check by counting people: 25 + 18 = 43, which is more than the 40 students in the class -- impossible, because the 10 double-counted students were added twice. Subtracting them once gives 33. And 40 &minus; 33 = 7 students take neither, which is a sensible number.
</details>

**2.** Using the review table above, compute P(failed GIVEN attended review) and confirm it is consistent with P(passed GIVEN attended).

<details markdown="1">
<summary>Show the worked answer</summary>

```
P(failed GIVEN attended) = 12/30 = 0.40
```

Consistency check -- conditional probabilities over all outcomes of the *same* condition must sum to 1:

```
P(passed | attended) + P(failed | attended)
  = 0.60 + 0.40
  = 1.00   correct
```

This is the complement rule applied inside a condition. Among attenders, a student either passed or failed; there is no third option. It is a free check on any conditional probability you compute from a table.
</details>

**3.** A test for a condition is 95% accurate in both directions. The condition affects 1 in 1,000 people. Someone tests positive. What is the probability they have the condition?

<details markdown="1">
<summary>Show the worked answer</summary>

Build a concrete population of 100,000 -- far easier than the formula.

```
Have the condition:        100        (1 in 1,000)
Do not have it:         99,900

Of the 100 who have it:
   test positive (95%)      95        true positives
   test negative             5

Of the 99,900 who do not:
   test positive (5%)     4,995       false positives
   test negative         94,905

Total positives = 95 + 4,995 = 5,090
```

```
P(has condition GIVEN positive) = 95 / 5,090 = 0.0187
```

**About 1.9%.** Not 95%.

Why so low: the condition is rare, so the 5% error rate applied to the huge healthy group produces far more false positives (4,995) than the test produces true positives (95). Most positive results are false.

This is exactly the P(A|B) versus P(B|A) confusion. The test's accuracy is P(positive | has condition) = 0.95. The patient wants P(has condition | positive) = 0.019. Same test, wildly different numbers, because the **base rate** matters enormously.
</details>

## Before you move on

- [ ] I know when to add and when to multiply, and what to subtract for overlap
- [ ] I can explain why mutually exclusive events cannot be independent
- [ ] I can pull marginal, joint and conditional probabilities out of a two-way table
- [ ] I can state the difference between P(A|B) and P(B|A) with an example
- [ ] I can apply Bayes' rule, or build the equivalent population table

Next: one distribution shows up more than any other, and it is the bridge from probability to every test in this course.""",
    [{"question": "P(A) = 0.4, P(B) = 0.3, and A and B can both occur with P(A and B) = 0.1. What is P(A or B)?",
      "choices": ["0.70", "0.60", "0.12", "0.80"], "correct": 1},
     {"question": "Two events are mutually exclusive and both have non-zero probability. Therefore they:",
      "choices": ["Must be independent", "Cannot be independent",
                  "Have equal probability", "Must sum to 1"], "correct": 1}],
)


# ===========================================================================
L(
    "The Normal Distribution and Why It Matters",
    """## What you will be able to do

Convert any raw score to a z-score by hand, use a z-table (or software) to get the probability, work the calculation backwards to find a score from a percentile, and state precisely what the central limit theorem does and does not promise.

## Why this one distribution

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
A national exam has **mean 75, SD 8**. Your cousin scored **91**. The school says that is "very good." How good, exactly? Better than what percentage of takers?

By the end of this lesson you can answer that in three lines of arithmetic.
</div>

The normal distribution matters for two separate reasons, and mixing them up causes most of the confusion:

1. Many natural measurements are approximately normal -- height, measurement error, many biological quantities.
2. **Far more importantly**, the distribution of a *sample mean* is approximately normal almost regardless of what the raw data looks like. This is what makes t-tests, confidence intervals and ANOVA work.

## The shape and its properties

- Symmetric and bell-shaped
- **Mean = median = mode**, all at the centre
- Defined entirely by two numbers: the mean (where it sits) and the SD (how wide it is)
- The total area underneath is exactly 1 -- it is a probability distribution
- The tails approach zero but never touch it, so extreme values are always possible, just increasingly unlikely

## The empirical rule

<div class="callout callout-key" markdown="1">
<span class="callout-label">68 &ndash; 95 &ndash; 99.7</span>
For any normal distribution:

- **68%** of values lie within **1 SD** of the mean
- **95%** of values lie within **2 SD** of the mean
- **99.7%** of values lie within **3 SD** of the mean
</div>

Applied to the national exam (mean 75, SD 8):

```
68% scored between 75 - 8  and 75 + 8   ->  67 to 83
95% scored between 75 - 16 and 75 + 16  ->  59 to 91
99.7% scored between 75 - 24 and 75 + 24 -> 51 to 99
```

Your cousin's 91 sits right at the edge of the 95% band -- only about 2.5% of takers scored above it. We can now be exact.

## The z-score: a universal ruler

A z-score says **how many standard deviations a value sits from the mean.** It strips away the original units, so scores from completely different scales become comparable.

<div class="formula" markdown="1">
**z = (x &minus; mean) / SD**
</div>

| Symbol | Means | In our exam example |
|---|---|---|
| x | the raw score you have | 91 |
| mean | the distribution's centre | 75 |
| SD | the distribution's spread | 8 |
| z | how many SDs above or below | to be computed |

### Worked example, step by step

**Step 1 -- write down the three numbers.**
```
x = 91,  mean = 75,  SD = 8
```

**Step 2 -- subtract the mean.**
```
91 - 75 = 16
```

**Step 3 -- divide by the SD.**
```
z = 16 / 8 = +2.00
```

**Step 4 -- interpret before touching a table.**
A z of +2.00 means the score is exactly 2 standard deviations above the mean. From the empirical rule, 95% of scores lie within 2 SD, so 5% lie outside -- split evenly, 2.5% above and 2.5% below. Your cousin beat about **97.5%** of takers.

**Step 5 -- get the exact figure from a z-table.**
A z-table gives the area to the **left** of z.
```
z = 2.00  ->  0.9772
```
So 97.72% of takers scored below 91, and 100 &minus; 97.72 = **2.28% scored above**.

### Reading a z-table

Rows give z to one decimal, columns give the second decimal. For z = 2.00: find row `2.0`, column `.00`, read **0.9772**.

Three question types, three procedures:

| Question | Procedure |
|---|---|
| P(below x) | Look up z. Read the table value directly. |
| P(above x) | Look up z. Compute 1 &minus; table value. |
| P(between x&#8321; and x&#8322;) | Look up both z's. Subtract the smaller table value from the larger. |

### Two more from the same exam

**What percentage scored below 67?**
```
z = (67 - 75)/8 = -8/8 = -1.00
table(-1.00) = 0.1587
-> 15.87% scored below 67
```

**What percentage scored between 67 and 83?**
```
z for 83 = (83-75)/8 = +1.00  ->  0.8413
z for 67 = (67-75)/8 = -1.00  ->  0.1587
0.8413 - 0.1587 = 0.6827
-> 68.27% scored between 67 and 83
```

That 68.27% is the empirical rule's "68%" computed exactly. The rule of thumb was a rounding of this.

## Working backwards: from percentile to score

Sometimes you need the score that cuts off a given percentage -- a passing mark, a scholarship threshold.

<div class="formula" markdown="1">
**x = mean + (z &times; SD)**
</div>

**What score is needed to be in the top 10%?**

**Step 1 -- convert to a left-tail area.** Top 10% means 90% are below, so the area to the left is 0.9000.

**Step 2 -- find the z with that area.** Search the body of the z-table for 0.9000. The closest is 0.8997 at z = 1.28. (Exact value: 1.2816.)

**Step 3 -- convert back to a raw score.**
```
x = 75 + (1.28 x 8)
  = 75 + 10.24
  = 85.24
```

A score of about **85** puts a student in the top 10%.

## The central limit theorem

This is the theorem that licenses the rest of the course.

<div class="callout callout-key" markdown="1">
<span class="callout-label">What it actually says</span>
As sample size grows, the distribution of the **sample mean** approaches a normal distribution -- **regardless of the shape of the population**, provided the population has a finite variance.

Its standard deviation, called the **standard error**, is:

&nbsp;&nbsp;&nbsp;&nbsp;**SE = SD / &radic;n**
</div>

Three consequences worth internalising:

1. **It is about the mean, not your data.** Your raw observations do not become normal. The theorem says nothing about them.
2. **Bigger samples give more precise means.** SE shrinks as n grows -- but with the square root, so quadrupling the sample only halves the standard error.
3. **"Large enough" depends on skew.** For a near-symmetric population, n = 15 may be plenty. For strongly skewed data, n = 30 is optimistic and several hundred may be needed.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The "n > 30" myth</span>
"n greater than 30 means normality" is a rule of thumb that has been promoted to a law. It is neither a theorem nor safe for skewed data. And it never claimed your *data* is normal -- only the sampling distribution of its mean.
</div>

### Standard error worked on our class

Our eight students: mean 20, SD 6.72.

```
SE = 6.72 / sqrt(8)
   = 6.72 / 2.828
   = 2.38
```

So while individual students vary by about 6.72 points, the *class average* would vary by only about 2.38 points across repeated samples of 8. This number reappears in both of the next two lessons -- it is the engine of the t-test and the confidence interval.

## Doing it in software

### Excel
```
=NORM.S.DIST(2, TRUE)          -> 0.9772   area left of z = 2
=NORM.DIST(91, 75, 8, TRUE)    -> 0.9772   same thing, no z needed
=1-NORM.DIST(91, 75, 8, TRUE)  -> 0.0228   area to the right
=NORM.S.INV(0.90)              -> 1.2816   z for the 90th percentile
=NORM.INV(0.90, 75, 8)         -> 85.25    score at the 90th percentile
=STANDARDIZE(91, 75, 8)        -> 2        the z-score itself
```

### R
```r
pnorm(2)                    # 0.9772499   area left of z = 2
pnorm(91, mean = 75, sd = 8)      # 0.9772499   direct, no z needed
pnorm(91, 75, 8, lower.tail = FALSE)  # 0.02275   area to the right
qnorm(0.90)                 # 1.281552    z for 90th percentile
qnorm(0.90, 75, 8)          # 85.25       score at 90th percentile

# a quick normality check on your own data
score <- c(12, 15, 15, 18, 20, 22, 25, 33)
shapiro.test(score)         # W = 0.9371, p = 0.583 -> no evidence against normality
qqnorm(score); qqline(score)
```

### Jamovi
For the normality of your own variable: **Analyses** &rarr; **Exploration** &rarr; **Descriptives** &rarr; **Plots** &rarr; tick **Q-Q plot**. In a Q-Q plot, points close to the diagonal line mean approximately normal.

### SPSS
<kbd>Analyze</kbd> &rarr; <kbd>Descriptive Statistics</kbd> &rarr; <kbd>Explore</kbd> &rarr; **Plots** &rarr; tick **Normality plots with tests**. This gives the Kolmogorov-Smirnov and Shapiro-Wilk tests plus a Q-Q plot.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Do not over-trust normality tests</span>
With **large** samples, Shapiro-Wilk rejects normality for departures far too small to matter. With **small** samples, it misses real departures because it has no power.

Use the Q-Q plot and the histogram as your primary evidence; treat the test as secondary.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template</span>
Quiz scores were approximately normally distributed, *Shapiro-Wilk W* = *.94*, *p* = *.58*, with visual inspection of the Q-Q plot showing no substantial departure from linearity. A score of *91* corresponds to *z* = *2.00*, placing it at approximately the *98th* percentile of the distribution.
</div>

## Common mistakes

- **Forgetting the sign of z.** A negative z means below the mean, and the table value will be under 0.5.
- **Reading the wrong tail.** Most z-tables give area to the *left*. For "above," subtract from 1.
- **Using the SD when you need the standard error.** SD describes individual variation; SE describes variation of the *mean*. Using SD where SE belongs makes intervals far too wide.
- **Claiming the CLT makes your data normal.** It makes the *sampling distribution of the mean* approximately normal.
- **Applying z when the population SD is unknown and n is small.** That is what the t-distribution is for -- next lesson.

## Practice

**1.** IQ scores are normal with mean 100, SD 15. What proportion of people score above 130?

<details markdown="1">
<summary>Show the worked answer</summary>

```
Step 1: x = 130, mean = 100, SD = 15
Step 2: 130 - 100 = 30
Step 3: z = 30 / 15 = +2.00
Step 4: table(2.00) = 0.9772  (area to the LEFT)
Step 5: we want the area to the RIGHT:
        1 - 0.9772 = 0.0228
```

**About 2.28%,** or roughly 1 person in 44.

Cross-check with the empirical rule: 130 is exactly 2 SD above the mean, 95% lie within 2 SD, leaving 5% in the two tails, so 2.5% in the upper tail. 2.28% is the exact version of that estimate.
</details>

**2.** A tricycle ride takes a mean of 18 minutes with SD 4 minutes, normally distributed. You leave 25 minutes before an appointment. What is the probability you arrive late?

<details markdown="1">
<summary>Show the worked answer</summary>

Late means the ride takes **more than** 25 minutes.

```
z = (25 - 18) / 4 = 7 / 4 = +1.75
table(1.75) = 0.9599      area to the LEFT (arriving on time)
P(late) = 1 - 0.9599 = 0.0401
```

**About 4%,** or roughly 1 trip in 25.

Follow-up worth thinking about: to cut the late risk to 1%, you need the z with 0.99 to its left, which is z = 2.33.
```
x = 18 + (2.33 x 4) = 18 + 9.32 = 27.3 minutes
```
Leaving 27 or 28 minutes early gets you to a 1% risk. Notice the cost: buying that extra safety took 2 more minutes for a 4-fold reduction in risk -- the tails fall away fast.
</details>

**3.** Someone argues: "My data is heavily skewed, so I cannot use a t-test." When is this right, and when is it wrong?

<details markdown="1">
<summary>Show the answer</summary>

**It depends entirely on the sample size, because the t-test assumes the sampling distribution of the *mean* is approximately normal -- not the data.**

**They are wrong when n is large.** With, say, 500 observations and moderate skew, the central limit theorem makes the sampling distribution of the mean approximately normal even though the raw data is not. The t-test is fine.

**They are right when n is small.** With 12 heavily skewed observations, the CLT has not had a chance to operate. The sampling distribution of the mean is still skewed and the t-test's p-value is unreliable. Use a nonparametric test (Wilcoxon or Mann-Whitney) or a bootstrap.

**A separate point, often missed:** even when the t-test is *valid* on skewed data, the mean may be a poor *description* of it. Validity of the test and appropriateness of the statistic are two different questions. You may legitimately run a t-test on the mean and still be better off reporting the median.
</details>

## Before you move on

- [ ] I can compute a z-score and say what it means in plain words
- [ ] I can find the area left of, right of, and between values using a z-table
- [ ] I can work backwards from a percentile to a raw score
- [ ] I can compute a standard error and explain how it differs from SD
- [ ] I can state what the central limit theorem promises, and what it does not

Next: we have a mean of 20 and a claim that it should be 25. Time to test it.""",
    [{"question": "Exam scores are normal with mean 75, SD 8. What is the z-score for a score of 91?",
      "choices": ["+1.50", "+2.00", "+1.14", "+16.0"], "correct": 1},
     {"question": "The central limit theorem describes the approximate normality of:",
      "choices": ["The raw data", "The sampling distribution of the mean",
                  "The population", "The standard deviation"], "correct": 1}],
)


# ===========================================================================
L(
    "Your First Hypothesis Test",
    """## What you will be able to do

Run a complete one-sample t-test by hand on our eight students, from stating the hypotheses to writing the APA sentence -- and correctly interpret a result that is **not** significant, which is the situation most theses actually face.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
The department claims the average score on this quiz is **25 out of 40**. Our eight students averaged **20.0**.

Is a five-point shortfall real evidence against the department's claim, or just the ordinary variation you would expect from a sample of eight? That is the entire question a hypothesis test answers.
</div>

## The logic, before any arithmetic

A hypothesis test is a **proof by contradiction with a probability attached.**

1. **Assume the boring thing is true.** The population mean really is 25.
2. **Ask:** if that were true, how likely is a sample mean as far from 25 as ours?
3. **If the answer is "very unlikely,"** the assumption is hard to maintain, so we reject it.
4. **If the answer is "not that unlikely,"** we have not contradicted anything, and we keep the assumption -- *without* claiming it is true.

<div class="callout callout-key" markdown="1">
<span class="callout-label">The asymmetry that matters</span>
You never **prove** the alternative. You only show the null is hard to live with.

And you never **prove** the null either. Failing to reject is like a court verdict of "not guilty" -- it means the evidence was insufficient, not that innocence was established.
</div>

## Step 1 -- State the hypotheses

<div class="formula" markdown="1">
**H&#8320;: &mu; = 25** &nbsp;&nbsp;&nbsp; the population mean is 25 (the department's claim)
<span class="formula-note">**H&#8321;: &mu; &ne; 25** &nbsp;&nbsp;&nbsp; the population mean is not 25 (two-tailed)</span>
</div>

Rules for writing hypotheses:

- They are about the **population** (&mu;), never about your sample (x&#772;). Writing H&#8320;: x&#772; = 25 is wrong -- you know the sample mean; there is nothing to test about it.
- H&#8320; always contains the equals sign.
- **Two-tailed** (&ne;) unless you have a strong, pre-registered directional theory. Two-tailed is the defensible default; choosing one-tailed after seeing the data doubles your false-positive rate.

## Step 2 -- Choose the test and the significance level

| Situation | Test |
|---|---|
| One sample against a known value, population SD **unknown** | **One-sample t-test** |
| One sample against a known value, population SD **known** | One-sample z-test (rare in practice) |
| Two independent groups | Independent-samples t-test |
| Same subjects measured twice | Paired-samples t-test |
| Three or more groups | ANOVA |

We do not know the population SD -- we estimated it from our own eight students. So: **one-sample t-test**.

Set **&alpha; = .05**, and set it *now*, before seeing results.

## Step 3 -- Check the assumptions

| Assumption | How to check | Our data |
|---|---|---|
| Independent observations | By design -- separate students, no copying | Satisfied |
| Continuous outcome | Quiz score is ratio | Satisfied |
| Approximately normal (or large n) | Shapiro-Wilk, Q-Q plot | *W* = .94, *p* = .58 -- no evidence against |

With n = 8 the normality assumption matters a lot, because the central limit theorem has barely started to work. Our check passes, so we continue.

## Step 4 -- Compute the test statistic

<div class="formula" markdown="1">
**t = (x&#772; &minus; &mu;&#8320;) / (s / &radic;n)**
<span class="formula-note">observed mean minus claimed mean, divided by the standard error</span>
</div>

| Symbol | Means | Our value |
|---|---|---|
| x&#772; | sample mean | 20.0 |
| &mu;&#8320; | the value claimed in H&#8320; | 25 |
| s | sample standard deviation | 6.72 |
| n | sample size | 8 |

**Step 4a -- compute the standard error.**
```
SE = s / sqrt(n)
   = 6.72 / sqrt(8)
   = 6.72 / 2.8284
   = 2.3755
```

**Step 4b -- compute t.**
```
t = (20.0 - 25) / 2.3755
  = -5.0 / 2.3755
  = -2.105
```

**Step 4c -- degrees of freedom.**
```
df = n - 1 = 8 - 1 = 7
```

<div class="callout callout-key" markdown="1">
<span class="callout-label">What t actually means</span>
**t = &minus;2.105** says our sample mean sits 2.105 standard errors *below* the claimed value.

That is the whole idea. t is a distance, measured in standard errors instead of points. Because it is a distance in standard units, the same table works for any study on any scale.
</div>

## Step 5 -- Find the critical value, or the p-value

### Method A -- the critical value

For a two-tailed test at &alpha; = .05 with df = 7, the critical value from a t-table is **&plusmn;2.365**.

```
Is |t| > critical?
|-2.105| = 2.105
2.105 > 2.365?   NO
```

**Do not reject H&#8320;.** Our t does not reach the critical value.

### Method B -- the p-value

```
t = -2.105, df = 7, two-tailed  ->  p = .073
```

```
Is p < alpha?
.073 < .05?   NO
```

**Do not reject H&#8320;.** The two methods always agree -- they are the same comparison seen from two directions.

## Step 6 -- State the conclusion correctly

<div class="callout callout-warn" markdown="1">
<span class="callout-label">This is where most theses go wrong</span>
Our result is **not significant** (p = .073). Here is what you may and may not say.

**Wrong:** "The average score is 25."
**Wrong:** "There is no difference between the sample mean and 25."
**Wrong:** "We proved the department's claim."
**Wrong:** "The result was almost significant" or "approaching significance."

**Right:** "There was no statistically significant difference between the sample mean and the claimed value of 25, *t*(7) = &minus;2.11, *p* = .073."

**Also right, and better:** add what the study could actually detect. With n = 8 this test had low power -- it would likely have missed even a real five-point difference. The honest reading is that the study was too small to settle the question, not that the claim is correct.
</div>

## Step 7 -- Report the effect size

A p-value tells you whether an effect is detectable. It says nothing about whether it is **big**. Cohen's d answers that.

<div class="formula" markdown="1">
**d = (x&#772; &minus; &mu;&#8320;) / s**
</div>

```
d = (20.0 - 25) / 6.72
  = -5.0 / 6.72
  = -0.744
```

| &#124;d&#124; | Conventional label |
|---|---|
| 0.2 | Small |
| 0.5 | Medium |
| 0.8 | Large |

**d = &minus;0.74 is a medium-to-large effect** -- and it was not statistically significant. That combination is the signature of an **underpowered study**: the effect looks meaningful in size, but eight students is not enough to distinguish it from noise.

This is exactly why effect sizes must be reported alongside p-values. The p-value alone would have you conclude "nothing here." The effect size says "possibly something substantial here, but this study cannot tell."

## Doing it in software

### Jamovi
1. **Analyses** &rarr; **T-Tests** &rarr; **One Sample T-Test**
2. Drag `score` into **Dependent Variables**
3. Under **Hypothesis**, set **Test value** to `25`, keep **&ne; Test value**
4. Under **Additional Statistics**, tick **Mean difference**, **Effect size (Cohen's d)**, **Descriptives**
5. Under **Assumption Checks**, tick **Normality test** and **Q-Q plot**

### SPSS
1. <kbd>Analyze</kbd> &rarr; <kbd>Compare Means</kbd> &rarr; <kbd>One-Sample T Test</kbd>
2. Move `score` into **Test Variable(s)**
3. Set **Test Value** to `25`
4. Click **Options** to confirm the confidence interval is 95%, then **OK**

### Excel
Excel has no one-sample t-test dialog. Compute it directly:
```
A1:A8 holds the scores

=AVERAGE(A1:A8)                     -> 20
=STDEV.S(A1:A8)                     -> 6.7188
=COUNT(A1:A8)                       -> 8
=(20-25)/(6.7188/SQRT(8))           -> -2.1048     the t statistic
=T.DIST.2T(ABS(-2.1048), 7)         -> 0.0733      two-tailed p
=T.INV.2T(0.05, 7)                  -> 2.3646      critical value
```

### R
```r
score <- c(12, 15, 15, 18, 20, 22, 25, 33)

t.test(score, mu = 25)
#   t = -2.1048, df = 7, p-value = 0.07333
#   95 percent confidence interval:  14.38288 25.61712
#   sample estimates: mean of x = 20

# effect size
(mean(score) - 25) / sd(score)      # -0.7441
```

## Reading the output

```
One-Sample Test                       Test Value = 25

                                                  95% CI of the Difference
            t      df   Sig.(2-tailed)  Mean Diff    Lower     Upper
score   -2.105      7        .073         -5.00      -10.62     0.62
```

Line by line:

- **t = &minus;2.105** -- our computed statistic. Negative because our mean is below 25.
- **df = 7** -- n &minus; 1.
- **Sig. (2-tailed) = .073** -- the p-value. SPSS calls it "Sig."
- **Mean Difference = &minus;5.00** -- 20 &minus; 25, in the original points.
- **95% CI of the Difference: &minus;10.62 to 0.62** -- **this interval contains zero**, which is another way of seeing the non-significant result. If a 95% CI for a difference includes 0, the two-tailed test at .05 will not reject.

<div class="callout callout-key" markdown="1">
<span class="callout-label">Three views, one answer</span>
The critical-value comparison, the p-value, and the confidence interval containing zero are **three descriptions of the same fact**. They can never disagree. If yours do, you have made an arithmetic error.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- non-significant result</span>
A one-sample *t*-test was conducted to determine whether the mean quiz score differed from the department's stated average of *25*. The sample mean of *20.00* (*SD* = *6.72*, *n* = *8*) did not differ significantly from *25*, *t*(*7*) = *&minus;2.11*, *p* = *.073*, *d* = *&minus;0.74*, 95% CI [*&minus;10.62*, *0.62*]. Although the effect size was medium to large, the small sample provided limited power to detect a difference of this magnitude.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- significant result, for when you get one</span>
A one-sample *t*-test showed that the mean *score* of *M* (*SD* = *SD*) was significantly *higher/lower* than the hypothesised value of *value*, *t*(*df*) = *t*, *p* = *p*, *d* = *d*, 95% CI [*lower*, *upper*].
</div>

APA formatting rules to follow:

- Italicise *t*, *p*, *M*, *SD*, *d*, *n*
- Degrees of freedom go in parentheses right after *t*
- Report p to three decimals; write *p* < .001 rather than *p* = .000
- Drop the leading zero on values that cannot exceed 1: write *p* = .073, not 0.073

## Common mistakes

- **Writing hypotheses about the sample.** They are always about the population.
- **"Approaching significance."** A result is significant or it is not. p = .073 is not significant at .05. Report the number and let the reader judge.
- **Accepting the null.** You fail to reject it. Never accept it.
- **Choosing one-tailed after seeing the data.** This inflates your false-positive rate and a panel will catch it.
- **Reporting p with no effect size.** Half a result.
- **Writing p = .000.** No p-value is exactly zero. Write *p* < .001.
- **Forgetting df.** *t* = &minus;2.11 means nothing without its degrees of freedom.

## Practice

**1.** A sample of 16 has mean 52 and SD 8. Test H&#8320;: &mu; = 48 at &alpha; = .05. Critical value for df = 15 is &plusmn;2.131.

<details markdown="1">
<summary>Show the worked answer</summary>

```
Step 1  H0: mu = 48,  H1: mu != 48
Step 2  SE = 8 / sqrt(16) = 8 / 4 = 2.00
Step 3  t  = (52 - 48) / 2.00 = 4 / 2 = +2.00
Step 4  df = 16 - 1 = 15
Step 5  |2.00| > 2.131?   NO
```

**Do not reject H&#8320;.** There is no statistically significant difference from 48, *t*(15) = 2.00, *p* = .064.

Effect size:
```
d = (52 - 48) / 8 = 0.50   -- a medium effect
```

Same pattern as our class: a medium effect that the sample was too small to establish. Note how close this is -- t = 2.00 against a critical value of 2.131. A slightly larger sample would very likely have reached significance, which is an argument for planning sample size *before* collecting data.
</details>

**2.** Explain to a panel member why p = .04 does not mean "there is a 4% chance the null hypothesis is true."

<details markdown="1">
<summary>Show the answer</summary>

**The p-value is computed by assuming the null is true.** It is a conditional probability in one specific direction:

```
p = P( data at least this extreme  |  H0 is true )
```

What the panel member is describing is the reverse conditional:

```
P( H0 is true  |  data )
```

These are different quantities, exactly like P(positive | sick) versus P(sick | positive) from the probability lesson. Getting from one to the other requires Bayes' rule -- and that requires a prior probability that the null is true, which frequentist testing never supplies.

**The correct sentence:** "If the null hypothesis were true, we would see a result at least this extreme about 4% of the time."

The distinction matters practically: a p of .04 on an implausible hypothesis is much weaker evidence than a p of .04 on a plausible one, and the p-value alone cannot express that.
</details>

**3.** Two studies test the same drug. Study A: n = 20, p = .04. Study B: n = 2,000, p = .04. Are they equally impressive?

<details markdown="1">
<summary>Show the answer</summary>

**No -- and Study A is likely the more impressive of the two.**

The p-value depends on both effect size and sample size. To reach p = .04 with only 20 participants, the effect must be **large**. To reach the same p with 2,000 participants, the effect can be **tiny** -- large samples detect trivial differences.

Rough reasoning: t is roughly d x sqrt(n). Holding t constant, if n grows 100-fold then d shrinks 10-fold. Study B's effect is plausibly about a tenth the size of Study A's.

**The lesson:** never compare studies by p-value. Compare **effect sizes with confidence intervals**. A statistically significant result from a huge sample may be clinically or educationally meaningless, and this is one of the most common misreadings in published research.
</details>

## Before you move on

- [ ] I can write hypotheses about the population, with H&#8320; containing the equals sign
- [ ] I can compute SE, t and df by hand and say what t means in standard errors
- [ ] I can compare against a critical value and against &alpha;, and know they always agree
- [ ] I can state a non-significant result without accepting the null or saying "approaching significance"
- [ ] I always report an effect size beside the p-value
- [ ] I can explain why p is not the probability that H&#8320; is true

Next: the same numbers, asked a better question. Instead of "is it 25 or not," we ask "what range of values is consistent with our data?"

**1.** Compute the standard error. **2.** Multiply by the critical t. **3.** Add and subtract from the mean.""",
    [{"question": "A one-sample t-test gives t(7) = -2.11, p = .073, with alpha = .05. What is the correct conclusion?",
      "choices": ["Accept the null hypothesis; the means are equal",
                  "Fail to reject the null; no significant difference was detected",
                  "Reject the null; the result is approaching significance",
                  "The null hypothesis is 7.3% likely to be true"], "correct": 1},
     {"question": "A study reports a medium effect size but a non-significant p-value. The most likely explanation is:",
      "choices": ["The effect size was computed wrongly", "The study was underpowered for that effect",
                  "The null hypothesis is true", "Alpha was set too high"], "correct": 1}],
)


# ===========================================================================
L(
    "Understanding Confidence Intervals",
    """## What you will be able to do

Build a confidence interval by hand, interpret it in words that will survive a defence, and use it to answer a hypothesis test without computing a p-value. You will also be able to explain why the sentence almost everyone says about confidence intervals is wrong.

## Why bother, when we already have a p-value

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
Last lesson ended with "no significant difference from 25, *p* = .073." A panel member asks the obvious follow-up: **"So what IS the average, then?"**

A p-value cannot answer that. A confidence interval can. It is the same arithmetic asked as a better question.
</div>

The difference in a line:

- A **hypothesis test** asks a yes/no question about one specific value.
- A **confidence interval** hands back the whole range of values your data is compatible with.

The interval contains strictly more information, which is why journals increasingly require it.

## The formula

<div class="formula" markdown="1">
**CI = x&#772; &plusmn; (t<sub>critical</sub> &times; SE)**
<span class="formula-note">where SE = s / &radic;n, and t<sub>critical</sub> comes from df = n &minus; 1</span>
</div>

The three pieces:

| Piece | What it does | Our value |
|---|---|---|
| x&#772; | where the interval is centred | 20.0 |
| t<sub>critical</sub> | how many standard errors wide, set by your confidence level | 2.365 |
| SE | one standard error | 2.3755 |

The part after the &plusmn; is called the **margin of error**.

## Building ours, step by step

**Step 1 -- compute the standard error.** (Same SE as the t-test; it always is.)
```
SE = s / sqrt(n)
   = 6.72 / sqrt(8)
   = 6.72 / 2.8284
   = 2.3755
```

**Step 2 -- find the critical t.** For 95% confidence with df = n &minus; 1 = 7:
```
t(0.025, 7) = 2.365
```
Read a t-table at df = 7 under the two-tailed .05 column. Note this is **larger** than the z of 1.96 -- the price of estimating the SD from a small sample.

**Step 3 -- compute the margin of error.**
```
ME = 2.365 x 2.3755 = 5.617
```

**Step 4 -- add and subtract.**
```
lower = 20.0 - 5.617 = 14.38
upper = 20.0 + 5.617 = 25.62
```

<div class="callout callout-key" markdown="1">
<span class="callout-label">Our result</span>
**95% CI [14.38, 25.62]**

In words: the data is compatible with a true class average anywhere from about 14 to about 26 points. That is a wide range -- eight students simply cannot pin it down more tightly.
</div>

## Saying it correctly

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The sentence that fails defences</span>
**Wrong:** "There is a 95% probability that the true mean lies between 14.38 and 25.62."

Under the frequentist framework the true mean is a **fixed constant**. It is either inside this interval or it is not. There is no probability attached to it -- the probability lives in the *procedure*, not in your one interval.

**Right:** "We are 95% confident the true mean lies between 14.38 and 25.62."

**Righter, and what "95% confident" actually means:** "If we repeated this study many times and built an interval each time this way, about 95% of those intervals would contain the true mean."
</div>

If you genuinely want to say "there is a 95% probability the parameter is in this range," that statement belongs to a **Bayesian credible interval** -- a different object, built on different assumptions, covered in Advanced Statistics.

## The interval and the test are the same statement

Look what our interval contains:

```
95% CI:  [14.38, ....... 25.62]
                          ^
                    25 is inside
```

The department's claimed value of **25 falls inside the interval**. And last lesson the test failed to reject H&#8320;: &mu; = 25.

<div class="callout callout-key" markdown="1">
<span class="callout-label">The equivalence rule</span>
**If a 95% CI contains the hypothesised value, the two-tailed test at &alpha; = .05 will NOT reject it. If the CI excludes it, the test WILL reject.**

They are the same comparison. This gives you a free check on your own work: if your CI excludes the null value but your p-value is above .05, you have made an arithmetic mistake.
</div>

You can read a hypothesis test straight off an interval, for *any* candidate value:

```
Is mu = 25 plausible?  25 is inside [14.38, 25.62]  -> yes, cannot reject
Is mu = 30 plausible?  30 is outside                -> no, would reject
Is mu = 14 plausible?  14 is outside (just)         -> no, would reject
```

One interval answers infinitely many hypothesis tests. One p-value answers exactly one.

## What makes an interval narrow

Width = 2 x t x s / &radic;n. So three levers:

| Lever | Effect on width | Under your control? |
|---|---|---|
| **Larger n** | Narrower -- but only by &radic;n | **Yes** |
| **Smaller s** | Narrower | Partly -- better measurement reduces noise |
| **Lower confidence (90% not 95%)** | Narrower | Yes, but you buy it with more error |

The square root is the important practical fact:

```
n = 8     ->  SE = 6.72/2.83  = 2.38   width about 11.2
n = 32    ->  SE = 6.72/5.66  = 1.19   width about  4.9
n = 128   ->  SE = 6.72/11.31 = 0.59   width about  2.4
```

**To halve the width you must quadruple the sample.** This is why sample-size planning belongs at the proposal stage, not after data collection.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The dishonest lever</span>
Switching from 95% to 90% confidence narrows your interval without collecting a single extra case. That is legitimate only if you decide the confidence level **before** seeing the data. Lowering it afterwards because 95% was inconveniently wide is a reporting error a careful reader will catch.
</div>

## Doing it in software

### Jamovi
Confidence intervals appear automatically in the T-Test output. **Analyses** &rarr; **T-Tests** &rarr; **One Sample T-Test**, then under **Additional Statistics** tick **Mean difference** and **Confidence interval**. Set the level (default 95%).

For a CI of the mean itself rather than the difference: **Exploration** &rarr; **Descriptives** &rarr; **Statistics** &rarr; tick **Confidence interval for mean**.

### SPSS
<kbd>Analyze</kbd> &rarr; <kbd>Descriptive Statistics</kbd> &rarr; <kbd>Explore</kbd> gives the 95% CI for the mean in the Descriptives table by default. Change the level under **Statistics**.

The One-Sample T Test dialog reports the CI **of the difference**, not of the mean. Both are useful -- just be clear which one you are quoting. Ours: CI of the mean is [14.38, 25.62]; CI of the difference from 25 is [&minus;10.62, 0.62]. Same information, shifted by 25.

### Excel
```
=CONFIDENCE.T(0.05, STDEV.S(A1:A8), COUNT(A1:A8))   -> 5.617   margin of error
=AVERAGE(A1:A8) - 5.617                              -> 14.38
=AVERAGE(A1:A8) + 5.617                              -> 25.62
```
Use `CONFIDENCE.T` when the population SD is unknown, which is nearly always. `CONFIDENCE.NORM` assumes you know it.

### R
```r
score <- c(12, 15, 15, 18, 20, 22, 25, 33)
t.test(score)$conf.int
#  [1] 14.38288 25.61712
#  attr(,"conf.level") [1] 0.95

t.test(score, conf.level = 0.99)$conf.int   # wider: 11.69 to 28.31
```

Calling `t.test` with no `mu` gives you the CI of the mean directly.

## Reading the output

```
Descriptives
                                              Statistic    Std. Error
score   Mean                                      20.00          2.376
        95% Confidence Interval   Lower Bound     14.38
        for Mean                  Upper Bound     25.62
        Median                                    19.00
        Std. Deviation                             6.719
```

Check each against your hand calculation: Std. Error 2.376 matches our 2.3755, and the bounds match 20 &plusmn; 5.617.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template</span>
The mean quiz score was *20.00* (*SD* = *6.72*), 95% CI [*14.38*, *25.62*]. The interval includes the department's stated average of *25*, indicating the data are compatible with that claim; however, the width of the interval (*11.24* points) reflects the limited precision available from a sample of *8*.
</div>

APA conventions:

- Write it as: 95% CI [14.38, 25.62] -- square brackets, comma, no units repeated
- State the confidence level explicitly every time
- Report the interval alongside the point estimate, never instead of it

## Common mistakes

- **"There is a 95% probability the mean is in this interval."** The error this lesson exists to prevent.
- **Concluding "no difference" from two overlapping intervals.** Overlapping CIs do *not* imply a non-significant difference between two groups. Test the difference directly.
- **Using z (1.96) with a small sample.** With unknown population SD and n = 8, the correct multiplier is t = 2.365, not 1.96. Using 1.96 gives a falsely narrow interval.
- **Reporting a CI with no confidence level.** [14.38, 25.62] alone is meaningless -- 95%? 99%?
- **Lowering the confidence level after seeing the data** to get a narrower interval.
- **Confusing the CI of the mean with the CI of the difference.** Both appear in SPSS output; they are not the same numbers.

## Practice

**1.** A sample of 25 has mean 68 and SD 10. Build the 95% CI. Critical t for df = 24 is 2.064.

<details markdown="1">
<summary>Show the worked answer</summary>

```
Step 1  SE = 10 / sqrt(25) = 10 / 5 = 2.00
Step 2  t(0.025, 24) = 2.064
Step 3  ME = 2.064 x 2.00 = 4.128
Step 4  lower = 68 - 4.128 = 63.87
        upper = 68 + 4.128 = 72.13
```

**95% CI [63.87, 72.13]**

Interpretation: values from about 64 to about 72 are compatible with this data. A hypothesis that the true mean is 70 could not be rejected at &alpha; = .05 (70 is inside). A hypothesis that it is 75 would be rejected (75 is outside).
</details>

**2.** A researcher reports 95% CI [2.1, 8.7] for a mean difference between two treatments. Without a p-value, is the difference significant at &alpha; = .05?

<details markdown="1">
<summary>Show the answer</summary>

**Yes, significant.**

For a *difference*, the null value is **zero** -- "no difference." The interval [2.1, 8.7] does **not** contain zero, so the two-tailed test at .05 rejects the null.

You can say more than significance, though. The entire plausible range for the difference runs from 2.1 to 8.7 in favour of one treatment, so the direction is clear and even the smallest plausible effect is 2.1 units. Whether 2.1 units is *practically* meaningful is a subject-matter question the statistics cannot answer.

This is the advantage of the interval: it told you significance, direction, and the plausible size, all from one line.
</details>

**3.** Your 95% CI is [14.38, 25.62] and your supervisor says "too wide -- narrow it." What are your options, and which are legitimate?

<details markdown="1">
<summary>Show the answer</summary>

**Legitimate:**

1. **Collect more data.** The only real fix. Width shrinks with &radic;n, so going from 8 to 32 students roughly halves it. Going to 128 halves it again.
2. **Reduce measurement error.** A more reliable instrument lowers s, which lowers SE. Genuine improvement, and it also strengthens everything else in the study.
3. **Use a stratified or otherwise more efficient sampling design**, if the study is still at the design stage.

**Not legitimate:**

4. **Dropping the confidence to 90%** after seeing the 95% interval. The interval narrows, but you chose the level to fit the result.
5. **Removing the high scorer (33)** to shrink s. Deleting genuine data to improve your numbers is falsification.

**The honest answer to a supervisor:** the width is not a flaw in the analysis -- it is an accurate report of how much eight students can tell you. Reporting a narrow interval you did not earn would be worse than reporting a wide one you did.
</details>

## Before you move on

- [ ] I can compute SE, find the critical t, and build the interval by hand
- [ ] I can state the interpretation without attaching a probability to the parameter
- [ ] I can read a hypothesis test off a confidence interval for any candidate value
- [ ] I know width shrinks with &radic;n, so quadrupling n halves the width
- [ ] I know that overlapping intervals do not prove a non-significant difference

Next: we have been looking at one variable. Time to ask whether two variables move together.""",
    [{"question": "A 95% CI for a mean difference is [2.1, 8.7]. At alpha = .05, the difference is:",
      "choices": ["Not significant, because the interval is wide",
                  "Significant, because the interval excludes zero",
                  "Impossible to judge without a p-value",
                  "Significant only if the sample is large"], "correct": 1},
     {"question": "To halve the width of a confidence interval, you must roughly:",
      "choices": ["Double the sample size", "Quadruple the sample size",
                  "Halve the sample size", "Double the confidence level"], "correct": 1}],
)


# ===========================================================================
L(
    "Correlation: What It Does and Doesn't Tell You",
    """## What you will be able to do

Compute Pearson's r by hand from a table of deviations, interpret its size and its square, choose between Pearson and Spearman, and explain -- with an example ready for a panel -- exactly why correlation does not establish causation.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
Our eight students again. This time we also know how many hours each spent reviewing:

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

Does reviewing more go with scoring higher? And if so, **how strongly**?
</div>

## What r measures

Pearson's correlation coefficient **r** measures the strength and direction of a **straight-line** relationship between two continuous variables.

- **r = +1** -- perfect positive: every point on one upward line
- **r = 0** -- no *linear* relationship
- **r = &minus;1** -- perfect negative: every point on one downward line

| &#124;r&#124; | Common label |
|---|---|
| .00 &ndash; .19 | Very weak |
| .20 &ndash; .39 | Weak |
| .40 &ndash; .59 | Moderate |
| .60 &ndash; .79 | Strong |
| .80 &ndash; 1.00 | Very strong |

These labels are conventions, and they vary by field. In physics r = .80 may be disappointing; in psychology it is remarkable.

## Computing r by hand

<div class="formula" markdown="1">
**r = &Sigma;(x &minus; x&#772;)(y &minus; y&#772;) / &radic;[ &Sigma;(x &minus; x&#772;)&sup2; &times; &Sigma;(y &minus; y&#772;)&sup2; ]**
</div>

The idea: for each student, ask whether they are above or below average on *both* variables. If above-average x tends to pair with above-average y, the products are positive and r comes out positive.

**Step 1 -- compute both means.**
```
x-bar = (1+2+2+3+4+5+6+7)/8 = 30/8 = 3.75
y-bar = (12+15+18+15+22+25+20+33)/8 = 160/8 = 20.0
```

**Step 2 -- build the deviation table.** This is the whole calculation.

| x | y | x &minus; 3.75 | y &minus; 20 | product | (x &minus; x&#772;)&sup2; | (y &minus; y&#772;)&sup2; |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 12 | &minus;2.75 | &minus;8 | 22.00 | 7.5625 | 64 |
| 2 | 15 | &minus;1.75 | &minus;5 | 8.75 | 3.0625 | 25 |
| 2 | 18 | &minus;1.75 | &minus;2 | 3.50 | 3.0625 | 4 |
| 3 | 15 | &minus;0.75 | &minus;5 | 3.75 | 0.5625 | 25 |
| 4 | 22 | 0.25 | 2 | 0.50 | 0.0625 | 4 |
| 5 | 25 | 1.25 | 5 | 6.25 | 1.5625 | 25 |
| 6 | 20 | 2.25 | 0 | 0.00 | 5.0625 | 0 |
| 7 | 33 | 3.25 | 13 | 42.25 | 10.5625 | 169 |
| | | **0** | **0** | **87.00** | **31.50** | **316** |

<div class="callout callout-key" markdown="1">
<span class="callout-label">Two free checks</span>
Both deviation columns must sum to **0**. And &Sigma;(y &minus; y&#772;)&sup2; = **316** is the same sum of squares we computed back in lesson 2 -- same eight scores, same number. If either check fails, fix it before going on.
</div>

**Step 3 -- substitute.**
```
r = 87.00 / sqrt(31.50 x 316)
  = 87.00 / sqrt(9954)
  = 87.00 / 99.77
  = 0.872
```

**r = 0.87 -- a very strong positive linear relationship.**

## The coefficient of determination

Square r and you get something more concrete.

<div class="formula" markdown="1">
**r&sup2; = proportion of variance in y explained by x**
</div>

```
r-squared = 0.872^2 = 0.760
```

**76% of the variation in quiz scores is accounted for by variation in review hours.** The remaining 24% comes from everything else -- prior knowledge, sleep, aptitude, test anxiety, luck.

r&sup2; is usually the more honest number to lead with. An r of .50 sounds like "half," but r&sup2; = .25 -- a quarter of the variance. Reporting r alone tends to overstate.

## Is it significantly different from zero?

A sample r of 0.87 might still arise by chance from an uncorrelated population, especially with n = 8.

<div class="formula" markdown="1">
**t = r &times; &radic;[ (n &minus; 2) / (1 &minus; r&sup2;) ] &nbsp;&nbsp; with df = n &minus; 2**
</div>

```
t = 0.872 x sqrt( (8-2) / (1 - 0.760) )
  = 0.872 x sqrt( 6 / 0.240 )
  = 0.872 x sqrt(25.0)
  = 0.872 x 5.00
  = 4.36

df = 8 - 2 = 6
critical t(0.025, 6) = 2.447
4.36 > 2.447  ->  significant,  p = .005
```

So: **r(6) = .87, p = .005.** Note df = n &minus; 2 here, not n &minus; 1 -- two means were estimated, one for each variable.

## Pearson or Spearman?

| Use **Pearson r** when | Use **Spearman rho** when |
|---|---|
| Both variables are interval or ratio | Either variable is **ordinal** |
| The relationship looks linear | The relationship is monotone but curved |
| No extreme outliers | Outliers are present |
| Roughly normal distributions | Distributions are badly skewed |

Spearman is simply Pearson computed on the **ranks** instead of the raw values, which is what makes it immune to outliers and usable on ordinal scales.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Correlating two Likert items</span>
A single Likert item is ordinal (lesson 1). Strictly, correlating two single items calls for **Spearman**. Pearson is defensible for summated scales built from several items.
</div>

## Plot it first. Always.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Why the number is never enough</span>
Anscombe's quartet is four datasets with **identical** means, SDs and r = 0.816. One is a clean linear relationship. One is a perfect curve. One is a straight line ruined by a single outlier. One is a vertical stack plus one distant point.

The statistics cannot tell them apart. The scatterplot separates them instantly.

Consequence: **r = 0 does not mean "no relationship."** It means no *linear* relationship. A perfect U-shape gives r near zero.
</div>

![Diagram: Fitting a line through scattered data](/static/diagrams/regression-scatter.svg)

## Correlation is not causation

Our r = .87 between review hours and scores is genuine. It still does not establish that reviewing *causes* higher scores. Four rival explanations, each of which a panel may raise:

1. **Reverse causation.** Students who already understand the material may find reviewing rewarding and do more of it. The score drives the hours.
2. **A third variable (confounding).** Conscientiousness causes both more reviewing *and* better performance. Neither causes the other.
3. **Selection.** If these eight volunteered, the motivated students are over-represented, manufacturing the association.
4. **Chance.** With n = 8, coincidences happen. p = .005 makes this unlikely but not impossible.

<div class="callout callout-key" markdown="1">
<span class="callout-label">What would establish causation</span>
**Randomly assign** students to review for a set number of hours. Randomisation breaks the link between the treatment and every unmeasured characteristic, including conscientiousness -- which is exactly what the Design & Analysis of Experiments course is about.

Without random assignment, the honest verb is "is associated with," never "causes," "affects," "improves" or "leads to."
</div>

## Doing it in software

### Jamovi
1. **Analyses** &rarr; **Regression** &rarr; **Correlation Matrix**
2. Move both variables in
3. Tick **Pearson** and/or **Spearman**, and tick **Confidence intervals**
4. Under **Plot**, tick **Correlation matrix** and **Densities for variables** to get the scatterplot

### SPSS
1. <kbd>Analyze</kbd> &rarr; <kbd>Correlate</kbd> &rarr; <kbd>Bivariate</kbd>
2. Move both variables into **Variables**
3. Tick **Pearson** (and **Spearman** if needed), keep **Two-tailed**, tick **Flag significant correlations**
4. For the scatterplot: <kbd>Graphs</kbd> &rarr; <kbd>Chart Builder</kbd> &rarr; Scatter/Dot

### Excel
```
=CORREL(A1:A8, B1:B8)      -> 0.8720
=RSQ(A1:A8, B1:B8)         -> 0.7604
=PEARSON(A1:A8, B1:B8)     -> 0.8720   (identical to CORREL)
```
Scatterplot: select both columns, <kbd>Insert</kbd> &rarr; <kbd>Scatter</kbd>. Excel has no built-in Spearman -- rank both columns with `RANK.AVG` first, then run `CORREL` on the ranks.

### R
```r
hours <- c(1, 2, 2, 3, 4, 5, 6, 7)
score <- c(12, 15, 18, 15, 22, 25, 20, 33)

cor(hours, score)                      # 0.8719
cor.test(hours, score)                 # t = 4.3637, df = 6, p = 0.004719
                                       # 95% CI: 0.4297 to 0.9765
cor(hours, score, method = "spearman") # 0.8735

plot(hours, score, pch = 19,
     xlab = "Review hours", ylab = "Quiz score")
abline(lm(score ~ hours), col = "steelblue", lwd = 2)
```

## Reading the output

```
Correlations
                              Review hours    Quiz score
Review hours   Pearson r             1              .872**
               Sig. (2-tailed)                      .005
               N                     8              8
Quiz score     Pearson r          .872**            1
               Sig. (2-tailed)     .005
               N                     8              8

** Correlation is significant at the 0.01 level (2-tailed).
```

- The diagonal is always **1** -- every variable correlates perfectly with itself
- The matrix is symmetric; the two off-diagonal cells hold the same number
- **Sig. (2-tailed) = .005** is the p-value
- The asterisks are SPSS's significance flags: one for p < .05, two for p < .01

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template</span>
A Pearson product-moment correlation was computed to assess the relationship between *review hours* and *quiz score*. There was a strong positive correlation between the two variables, *r*(*6*) = *.87*, *p* = *.005*, with review hours accounting for approximately *76%* of the variance in quiz scores. Because the design was *correlational*, no causal inference is warranted.
</div>

Note the details:

- Degrees of freedom in parentheses after *r*, and they are **n &minus; 2**
- Drop the leading zero: *r* = .87, not 0.87
- Report r&sup2; as a percentage of variance
- Close with the causal caveat when the design is not experimental

## Common mistakes

- **Claiming causation.** The error this lesson exists to prevent. Use "is associated with."
- **Not plotting the data.** Anscombe's quartet. Every time.
- **Reading r = 0 as "no relationship."** It means no *linear* relationship.
- **Using Pearson on ordinal data** without justification.
- **Using df = n &minus; 1.** Correlation uses n &minus; 2.
- **Confusing r with r&sup2;.** r = .50 is *not* "50% explained." That is r&sup2; = .25.
- **Treating a significant r from a huge sample as important.** With n = 10,000, r = .03 is significant and explains 0.09% of the variance.

## Practice

**1.** Compute r for these five pairs: x = 1, 2, 3, 4, 5 and y = 2, 4, 5, 4, 9.

<details markdown="1">
<summary>Show the worked answer</summary>

```
x-bar = 15/5 = 3.0        y-bar = 24/5 = 4.8
```

| x | y | x&minus;3 | y&minus;4.8 | product | (x&minus;x&#772;)&sup2; | (y&minus;y&#772;)&sup2; |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 2 | &minus;2 | &minus;2.8 | 5.6 | 4 | 7.84 |
| 2 | 4 | &minus;1 | &minus;0.8 | 0.8 | 1 | 0.64 |
| 3 | 5 | 0 | 0.2 | 0.0 | 0 | 0.04 |
| 4 | 4 | 1 | &minus;0.8 | &minus;0.8 | 1 | 0.64 |
| 5 | 9 | 2 | 4.2 | 8.4 | 4 | 17.64 |
| | | **0** | **0** | **14.0** | **10** | **26.8** |

```
r = 14.0 / sqrt(10 x 26.8)
  = 14.0 / sqrt(268)
  = 14.0 / 16.371
  = 0.855
```

**r = .86** -- a strong positive linear relationship. r&sup2; = .73, so about 73% of the variance in y is accounted for by x.

Both deviation columns sum to 0, so the arithmetic checks out.
</details>

**2.** A study finds r = .68 between hours of screen time and anxiety scores in teenagers. A headline reads "Screens cause teen anxiety." List three alternative explanations.

<details markdown="1">
<summary>Show the answer</summary>

1. **Reverse causation.** Anxious teenagers may retreat to screens as avoidance or self-soothing. Anxiety causes the screen time rather than the other way round -- and the correlation looks identical either way.

2. **Confounding third variable.** Poor sleep, family conflict, bullying, or low socio-economic status could independently raise both screen time and anxiety. Neither variable causes the other; both respond to something unmeasured.

3. **Selection and measurement artefacts.** If the sample was recruited through a mental-health service or an online panel, it is not representative. And if both variables were self-reported on the same questionnaire, shared method variance inflates the correlation independently of any real relationship.

**A fourth, worth adding for a panel:** even taking r = .68 at face value, r&sup2; = .46 means 54% of the variation in anxiety is *unexplained* by screen time. The headline implies a determinism the number does not support.

**What would settle it:** a randomised experiment assigning screen limits, or at minimum a longitudinal design measuring both over time to establish temporal order.
</details>

**3.** A scatterplot shows a clear upside-down U: performance rises with arousal, peaks, then falls. Pearson's r is .02. Is there no relationship?

<details markdown="1">
<summary>Show the answer</summary>

**There is a strong relationship. Pearson's r is the wrong tool for it.**

r measures **linear** association only. In an inverted U, the rising left half contributes positive products and the falling right half contributes negative ones, and they cancel almost exactly -- giving r near zero while the relationship is obvious to the eye.

This is the Yerkes-Dodson curve, a genuine and well-replicated finding in psychology. Reporting "no relationship, r = .02" would be badly wrong.

**What to do instead:**

- Plot it. Always. The plot is the finding here.
- Fit a **quadratic** model: add an arousal-squared term to a regression and test it.
- Or split at the peak and analyse the two halves separately, if theory supports a threshold.
- Report **eta-squared** from an ANOVA across arousal bands, which captures non-linear association.

This is the single best argument for the rule "always look at the scatterplot before reporting a correlation."
</details>

## Before you move on

- [ ] I can build the deviation table and compute r by hand, using the sums-to-zero check
- [ ] I can interpret r&sup2; as a percentage of variance explained
- [ ] I know df = n &minus; 2 for a correlation
- [ ] I can choose between Pearson and Spearman and justify it
- [ ] I always plot before reporting, and I can say why using Anscombe's quartet
- [ ] I can list three alternative explanations for any observed correlation

Next: both our variables have been numeric. The final test in this course handles two **categorical** variables.""",
    [{"question": "A correlation of r = .50 means what proportion of variance is explained?",
      "choices": ["50%", "25%", "70%", "5%"], "correct": 1},
     {"question": "A scatterplot shows a clear inverted-U shape but Pearson's r is .02. What does this mean?",
      "choices": ["There is no relationship", "There is a strong non-linear relationship that r cannot detect",
                  "The data has an error", "The sample is too small"], "correct": 1}],
)


# ===========================================================================
L(
    "Chi-Square Tests for Categorical Data",
    """## What you will be able to do

Build a contingency table, compute expected counts, work out chi-square cell by cell, check the assumption that decides whether the test is valid at all, report an effect size, and know when to switch to Fisher's exact test instead.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
The review table from the probability lesson, now to be tested. 60 students:

| | Passed | Failed | **Total** |
|---|---:|---:|---:|
| **Attended review** | 18 | 12 | **30** |
| **Did not attend** | 9 | 21 | **30** |
| **Total** | **27** | **33** | **60** |

We already saw 60% of attenders passed versus 30% of non-attenders. **Is that gap bigger than chance would produce?**
</div>

Neither variable here is numeric. There is no mean to compare, so t-tests are useless. Chi-square is the tool for two categorical variables.

## The logic

Chi-square compares what you **observed** against what you would **expect if the two variables were unrelated**. The bigger the mismatch, the harder independence is to believe.

<div class="formula" markdown="1">
**&chi;&sup2; = &Sigma; (O &minus; E)&sup2; / E**
<span class="formula-note">O = observed count, E = expected count, summed over every cell</span>
</div>

## Step 1 -- State the hypotheses

```
H0: Attendance and passing are independent (no association)
H1: Attendance and passing are not independent (there is an association)
```

Chi-square hypotheses are always about **independence**, and H&#8321; is never directional -- the test detects any departure, in any direction.

## Step 2 -- Compute the expected counts

<div class="formula" markdown="1">
**E = (row total &times; column total) / grand total**
</div>

Work each of the four cells:

```
Attended & Passed:    E = (30 x 27) / 60 = 810 / 60 = 13.50
Attended & Failed:    E = (30 x 33) / 60 = 990 / 60 = 16.50
Did not & Passed:     E = (30 x 27) / 60 = 810 / 60 = 13.50
Did not & Failed:     E = (30 x 33) / 60 = 990 / 60 = 16.50
```

Observed against expected:

| | Passed | Failed |
|---|---|---|
| **Attended** | O = 18, E = 13.50 | O = 12, E = 16.50 |
| **Did not attend** | O = 9, E = 13.50 | O = 21, E = 16.50 |

<div class="callout callout-key" markdown="1">
<span class="callout-label">A free check</span>
Expected counts must reproduce the **same row and column totals** as the observed table. Row 1: 13.50 + 16.50 = 30. Column 1: 13.50 + 13.50 = 27. Both correct.

Expected counts are usually decimals. That is fine -- they are not real students, they are what the average table would look like under independence.
</div>

## Step 3 -- Check the assumption before going further

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The rule that decides validity</span>
- **No expected count below 1**, and
- **No more than 20% of cells with expected count below 5**

In a 2x2 table there are only 4 cells, so 20% means **not even one cell** may drop below 5.

Our smallest expected count is 13.50. **Assumption satisfied.** If it were not, chi-square would be invalid and we would use **Fisher's exact test** instead.
</div>

Note the rule is about **expected** counts, not observed ones. Students check the wrong table constantly.

## Step 4 -- Compute chi-square, cell by cell

| Cell | O | E | O &minus; E | (O &minus; E)&sup2; | (O &minus; E)&sup2;/E |
|---|---:|---:|---:|---:|---:|
| Attended, Passed | 18 | 13.50 | 4.50 | 20.25 | 1.5000 |
| Attended, Failed | 12 | 16.50 | &minus;4.50 | 20.25 | 1.2273 |
| Did not, Passed | 9 | 13.50 | &minus;4.50 | 20.25 | 1.5000 |
| Did not, Failed | 21 | 16.50 | 4.50 | 20.25 | 1.2273 |
| | | | **0** | | **&chi;&sup2; = 5.4545** |

The O &minus; E column summing to 0 is another free check.

## Step 5 -- Degrees of freedom

<div class="formula" markdown="1">
**df = (rows &minus; 1) &times; (columns &minus; 1)**
</div>

```
df = (2 - 1) x (2 - 1) = 1 x 1 = 1
```

Unlike the t-test, df here depends on the **shape of the table**, not the sample size. A 2x2 table always has df = 1, whether you have 60 students or 6,000.

## Step 6 -- Decide

```
Critical value:  chi-square(0.05, df=1) = 3.841
Our statistic:   5.4545

5.4545 > 3.841  ->  REJECT H0

p = .0195
.0195 < .05     ->  REJECT H0
```

**There is a statistically significant association between attending the review and passing.**

## Step 7 -- Effect size

Significance says the association is detectable. It does not say it is strong.

<div class="formula" markdown="1">
**&phi; = &radic;(&chi;&sup2; / n)** &nbsp;&nbsp; for 2x2 tables
<span class="formula-note">for larger tables use Cram&eacute;r's V = &radic;[&chi;&sup2; / (n &times; (min(r,c) &minus; 1))]</span>
</div>

```
phi = sqrt(5.4545 / 60)
    = sqrt(0.0909)
    = 0.3015
```

| &phi; or V | Label |
|---|---|
| .10 | Small |
| .30 | Medium |
| .50 | Large |

**&phi; = .30 -- a medium-sized association.** Worth reporting, and worth acting on.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Why effect size is not optional here</span>
Chi-square grows directly with sample size. Multiply every cell in our table by 10 -- same percentages, same relationship -- and &chi;&sup2; becomes 54.5 with p < .0001. The association has not become stronger; the sample has become bigger.

&phi; stays at .30 either way. That is the number that describes the relationship.
</div>

## Step 8 -- Say which direction

A significant chi-square says "not independent." It does not say *how*. Get the direction from the row percentages:

```
Attended review:  18/30 = 60% passed
Did not attend:    9/30 = 30% passed
```

Attending was associated with **double** the pass rate. That sentence, not the chi-square value, is what a reader needs.

For bigger tables use **standardised residuals** -- (O &minus; E) / &radic;E -- and flag any cell beyond &plusmn;2 as a major contributor.

## When chi-square is the wrong test

| Situation | Use instead |
|---|---|
| Any expected count below 5 in a 2x2 | **Fisher's exact test** |
| Same subjects measured twice (before/after) | **McNemar's test** |
| Both variables ordinal and you want direction | **Kendall's tau-b** or **linear-by-linear** |
| More than two related measurements | **Cochran's Q** |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The independence assumption</span>
Every student must appear in **exactly one cell**. If you measured the same 30 students before and after a review programme, those are *paired* observations and chi-square is invalid -- it would treat 60 dependent observations as 60 independent ones. **McNemar's test** is the paired version.
</div>

![Diagram: Reading a contingency table](/static/diagrams/contingency-table.svg)

## Doing it in software

### Jamovi
1. **Analyses** &rarr; **Frequencies** &rarr; **Independent Samples (&chi;&sup2; test of association)**
2. Put one variable in **Rows**, the other in **Columns**
3. Under **Statistics**, tick **&chi;&sup2;**, and **Phi and Cram&eacute;r's V** for effect size
4. Under **Cells**, tick **Row** percentages and **Expected counts**

Ticking expected counts is how you verify the assumption. Do it every time.

### SPSS
1. <kbd>Analyze</kbd> &rarr; <kbd>Descriptive Statistics</kbd> &rarr; <kbd>Crosstabs</kbd>
2. Row variable and column variable into their boxes
3. **Statistics** &rarr; tick **Chi-square** and **Phi and Cramer's V**
4. **Cells** &rarr; tick **Observed**, **Expected**, and **Row** percentages
5. **OK**

SPSS prints a footnote telling you how many cells had expected count under 5 -- read it before the p-value.

### Excel
```
Observed in B2:C3, expected computed in B6:C7

B6: =($D2*B$4)/$D$4      then fill across and down
=CHISQ.TEST(B2:C3, B6:C7)    -> 0.0195    the p-value directly
=CHISQ.INV.RT(0.05, 1)       -> 3.8415    the critical value
```
`CHISQ.TEST` returns the **p-value**, not the statistic. Many students report it as chi-square by mistake.

### R
```r
tab <- matrix(c(18, 12, 9, 21), nrow = 2, byrow = TRUE,
              dimnames = list(Review = c("Attended", "Did not"),
                              Result = c("Passed", "Failed")))

chisq.test(tab, correct = FALSE)
#   X-squared = 5.4545, df = 1, p-value = 0.01952

chisq.test(tab)$expected     # check the assumption
#          Passed Failed
# Attended   13.5   16.5
# Did not    13.5   16.5

prop.table(tab, 1)           # row percentages: 0.60 vs 0.30
sqrt(5.4545 / 60)            # phi = 0.3015

fisher.test(tab)             # exact alternative: p = 0.0370
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Yates' continuity correction</span>
R applies Yates' correction to 2x2 tables **by default**, giving &chi;&sup2; = 4.31, p = .038 instead of our 5.45, p = .020. SPSS reports both, labelling the corrected one "Continuity Correction."

The correction makes the test more conservative. Modern practice generally favours the **uncorrected** value when expected counts comfortably exceed 5, and Fisher's exact test when they do not. Whichever you use, **say which**.
</div>

## Reading the output

```
Chi-Square Tests
                              Value    df   Asymp. Sig. (2-sided)
Pearson Chi-Square            5.455     1          .020
Continuity Correction(b)      4.310     1          .038
Likelihood Ratio              5.545     1          .019
Fisher's Exact Test                                             .037
N of Valid Cases                 60

b. Computed only for a 2x2 table
a. 0 cells (0.0%) have expected count less than 5.
   The minimum expected count is 13.50.
```

Read footnote **a first**. It reports the assumption check: 0 cells below 5, minimum expected 13.50. Assumption satisfied, so the Pearson row is the one to quote.

Had that footnote said "2 cells (50.0%) have expected count less than 5," you would quote **Fisher's Exact Test** instead.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template</span>
A chi-square test of independence was performed to examine the relationship between *review attendance* and *passing*. The relationship was significant, *&chi;&sup2;*(*1*, *N* = *60*) = *5.45*, *p* = *.020*, *&phi;* = *.30*. Students who attended the review session were more likely to pass (*60.0%*) than those who did not (*30.0%*). All expected cell counts exceeded 5.
</div>

The format is precise: *&chi;&sup2;*(df, *N* = sample size) = value, *p* = value. Both df **and** N go in the parentheses -- this is the one test where APA asks for the sample size there.

## Common mistakes

- **Checking observed counts instead of expected counts** against the "under 5" rule.
- **Running chi-square on paired data.** Use McNemar.
- **Reporting chi-square as proof of causation.** It shows association only.
- **Omitting the direction.** A significant chi-square with no percentages tells the reader almost nothing.
- **Omitting the effect size.** &chi;&sup2; scales with n; &phi; does not.
- **Running it on percentages instead of counts.** Chi-square requires raw frequencies. Entering percentages silently sets N = 100 and invalidates everything.
- **Using it on continuous data by chopping it into categories.** This throws away information. Use a t-test or correlation on the original values.

## Practice

**1.** Test this table. Compute expected counts, chi-square, df, and check the assumption.

| | Yes | No |
|---|---:|---:|
| **Group A** | 20 | 10 |
| **Group B** | 15 | 25 |

<details markdown="1">
<summary>Show the worked answer</summary>

**Totals.** Row A = 30, Row B = 40, Column Yes = 35, Column No = 35, N = 70.

**Expected counts.**
```
A,Yes: (30 x 35)/70 = 1050/70 = 15.0
A,No:  (30 x 35)/70 = 15.0
B,Yes: (40 x 35)/70 = 1400/70 = 20.0
B,No:  (40 x 35)/70 = 20.0
```
Smallest expected = 15.0, well above 5. **Assumption satisfied.**

**Chi-square.**

| Cell | O | E | O&minus;E | (O&minus;E)&sup2;/E |
|---|---:|---:|---:|---:|
| A,Yes | 20 | 15 | 5 | 25/15 = 1.667 |
| A,No | 10 | 15 | &minus;5 | 25/15 = 1.667 |
| B,Yes | 15 | 20 | &minus;5 | 25/20 = 1.250 |
| B,No | 25 | 20 | 5 | 25/20 = 1.250 |
| | | | **0** | **&chi;&sup2; = 5.833** |

```
df = (2-1)(2-1) = 1
critical = 3.841
5.833 > 3.841  ->  reject H0,  p = .0157
phi = sqrt(5.833/70) = sqrt(0.0833) = 0.289   -- medium
```

**Direction:** Group A 20/30 = 66.7% Yes; Group B 15/40 = 37.5% Yes.

**Report:** *&chi;&sup2;*(1, *N* = 70) = 5.83, *p* = .016, *&phi;* = .29. Group A responded Yes more often (66.7%) than Group B (37.5%).
</details>

**2.** Your 2x2 table has expected counts 3.2, 6.8, 5.1 and 10.9. Can you use chi-square?

<details markdown="1">
<summary>Show the answer</summary>

**No.**

One cell has an expected count of 3.2, which is below 5. In a 2x2 table there are only 4 cells, so a single offending cell is 25% of them -- above the 20% limit.

**Use Fisher's exact test instead.** It computes the exact probability rather than relying on an approximation that has broken down, and it has no minimum-count requirement.

Two other options, less good:

- **Collapse categories** into a coarser but still meaningful grouping, if that makes substantive sense. Never collapse just to fix the arithmetic.
- **Collect more data.** Correct but usually impractical at analysis stage.

**What not to do:** report the chi-square anyway with a footnote acknowledging the violation. Panels challenge this, and rightly -- the p-value is not trustworthy.
</details>

**3.** A researcher measures 40 patients' symptom status (improved / not improved) before and after treatment, then runs chi-square on an 80-row table. What is wrong?

<details markdown="1">
<summary>Show the answer</summary>

**The observations are not independent. The same 40 patients appear twice.**

Chi-square requires every observation to fall in exactly one cell, contributed by a different unit. Here each patient contributes two rows, so the test treats 80 dependent observations as 80 independent ones. The standard errors are understated and the p-value is too small -- the test will over-declare significance.

**Use McNemar's test.** It is built for paired binary data and focuses on exactly the cases that matter: the **discordant pairs**, those who changed status.

Set the data up as one row per patient:

| | After: Improved | After: Not improved |
|---|---:|---:|
| **Before: Improved** | a | b |
| **Before: Not improved** | c | d |

McNemar tests whether b and c differ. Cells a and d -- patients who did not change -- carry no information about whether the treatment changed anything, and the test correctly ignores them.

In R: `mcnemar.test(tab)`. In SPSS: Crosstabs &rarr; Statistics &rarr; tick **McNemar**.
</details>

## Before you move on

- [ ] I can compute expected counts from row and column totals
- [ ] I check the expected-count assumption **before** reading any p-value
- [ ] I can compute chi-square cell by cell, using the O&minus;E sums-to-zero check
- [ ] I know df = (r&minus;1)(c&minus;1) and does not depend on n
- [ ] I always report &phi; or Cram&eacute;r's V and the direction in percentages
- [ ] I know to use Fisher's exact test for sparse tables and McNemar for paired data

Next: the last lesson in the course takes you from analysing your own data to reading the official statistics everyone else publishes.""",
    [{"question": "The rule about counts below 5 in a chi-square test applies to:",
      "choices": ["Observed counts", "Expected counts", "Row totals", "The sample size"], "correct": 1},
     {"question": "A 3x4 contingency table has how many degrees of freedom?",
      "choices": ["12", "6", "7", "11"], "correct": 1}],
)


# ===========================================================================
L(
    "Rates, Ratios, Index Numbers and Official Statistics",
    """## What you will be able to do

Turn raw counts into rates that can be compared fairly across places and times, build and rebase an index number, read a Philippine official statistic without misinterpreting it, and spot the three ways these numbers are most often abused.

## Why this closes the course

Everything so far analysed **your own** data. But most numbers you will cite in a thesis came from someone else -- PSA, NEDA, the Bangko Sentral, DepEd, DOH. Those are not raw data; they are **constructed indicators**, and each carries a definition you must understand before quoting it.

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
A student writes: "Province A has a worse dengue problem than Province B -- 4,200 cases versus 1,800 last year."

Province A has 3.1 million residents. Province B has 900,000.

```
Province A: 4,200 / 3,100,000 x 100,000 = 135 per 100,000
Province B: 1,800 /   900,000 x 100,000 = 200 per 100,000
```

**The ranking reverses.** Province B has the worse problem. The raw counts were not wrong -- they were just answering a different question.
</div>

## Ratios, proportions, rates

Three related things, often confused.

| Term | Definition | Example |
|---|---|---|
| **Ratio** | one quantity divided by another; numerator need not be part of denominator | 30 boys : 20 girls = 1.5 |
| **Proportion** | a ratio where the numerator **is** part of the denominator; always 0 to 1 | 30 boys / 50 pupils = 0.60 |
| **Rate** | a proportion with a **time period** and a **population base** attached | 200 cases per 100,000 per year |

<div class="callout callout-key" markdown="1">
<span class="callout-label">The rule</span>
**A rate without its denominator and its period is a count in disguise.**

"50 cases" is uninterpretable. "50 cases per 100,000 population in 2025" can be compared with any other place or year.
</div>

### Choosing the multiplier

Rates are scaled so the result is a readable number:

```
per 100     -> a percentage; use for common events (unemployment, literacy)
per 1,000   -> use for moderately common events (births, deaths)
per 100,000 -> use for rare events (specific diseases, homicide)
```

Pick whichever gives a number between roughly 1 and 1,000. Then **state it every time**.

## Crude versus specific versus standardised rates

A crude rate lumps everyone together, which hides composition differences.

<div class="callout callout-case" markdown="1">
<span class="callout-label">The classic trap</span>
A retirement town reports a crude death rate of 25 per 1,000. A university town reports 4 per 1,000.

Is the retirement town unhealthy? **No.** It is full of elderly people, and elderly people die at higher rates everywhere. The crude rate is measuring age structure, not health.
</div>

Three fixes, in increasing sophistication:

1. **Age-specific rates.** Compute the rate separately within each age band and compare band to band. Honest and simple, but gives you many numbers instead of one.
2. **Age-standardised rates.** Apply each population's age-specific rates to one common *standard* population. This produces a single comparable number, and is what PSA and WHO publish for mortality.
3. **Regression adjustment.** Model the outcome with age as a covariate -- the ANCOVA idea from the experiments course.

### Direct standardisation, worked

Two towns, one standard population of 100,000 (60,000 young, 40,000 old):

| Age band | Town A rate | Town B rate | Standard pop |
|---|---:|---:|---:|
| Under 60 | 2 per 1,000 | 3 per 1,000 | 60,000 |
| 60 and over | 30 per 1,000 | 33 per 1,000 | 40,000 |

```
Town A expected deaths in standard population:
   (2/1000)  x 60,000 =   120
   (30/1000) x 40,000 = 1,200
   total              = 1,320
   standardised rate  = 1,320 / 100,000 x 1,000 = 13.2 per 1,000

Town B:
   (3/1000)  x 60,000 =   180
   (33/1000) x 40,000 = 1,320
   total              = 1,500
   standardised rate  = 1,500 / 100,000 x 1,000 = 15.0 per 1,000
```

**Town B is worse in every single age band, and its standardised rate is higher.** Whatever the two crude rates said, this comparison is the fair one -- both towns have now been given the same age structure.

## Index numbers

An index tracks change relative to a **base period** set to 100.

<div class="formula" markdown="1">
**Index = (value in current period / value in base period) &times; 100**
</div>

### Worked example

Rice price per kilo, base year 2020 = &#8369;42:

| Year | Price | Index (2020 = 100) | Working |
|---|---:|---:|---|
| 2020 | 42 | 100.0 | 42/42 x 100 |
| 2022 | 48 | 114.3 | 48/42 x 100 |
| 2024 | 53 | 126.2 | 53/42 x 100 |
| 2026 | 57 | 135.7 | 57/42 x 100 |

Reading it: by 2026 rice cost **35.7% more** than in 2020.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Percentage points versus percent</span>
From 2024 (126.2) to 2026 (135.7) the index rose by **9.5 index points**.

That is **not** a 9.5% increase. The percentage change is:

```
(135.7 - 126.2) / 126.2 x 100 = 7.5%
```

Confusing points with percent is the single most common index error, and it appears in newspapers constantly.
</div>

### Rebasing

Statistical agencies periodically change the base year, and you cannot compare indices on different bases. To convert a series to a new base:

<div class="formula" markdown="1">
**new index = (old index / old index in the new base year) &times; 100**
</div>

Rebasing our rice series to 2024 = 100:

```
2020: 100.0 / 126.2 x 100 =  79.2
2022: 114.3 / 126.2 x 100 =  90.6
2024: 126.2 / 126.2 x 100 = 100.0
2026: 135.7 / 126.2 x 100 = 107.5
```

The *pattern* is identical -- only the reference point moved. Note 2026 is 7.5% above 2024 on either base, which matches the percentage change computed above.

## Philippine official statistics you will actually cite

| Indicator | Agency | What it measures | The catch |
|---|---|---|---|
| **CPI / inflation rate** | PSA | Price change of a fixed basket of goods | Basket and base year are revised periodically |
| **Poverty incidence** | PSA | % of families below the poverty threshold | Threshold definition has changed over time |
| **Unemployment rate** | PSA (LFS) | % of the *labour force* without work and seeking it | Excludes discouraged workers who stopped looking |
| **Labour force participation rate** | PSA (LFS) | % of working-age population in the labour force | Falls when people give up looking -- which can make unemployment look better |
| **GDP growth** | PSA | Real change in national output | Revised several times after first release |
| **Net enrolment rate** | DepEd | % of official-age children enrolled | Different from gross enrolment, which can exceed 100% |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Unemployment: the definition that surprises people</span>
The unemployment rate's denominator is the **labour force**, not the population. Someone who gives up looking for work leaves the labour force entirely -- and the unemployment rate **falls**.

So a falling unemployment rate can mean more people found jobs, or more people stopped looking. Always read it alongside the **labour force participation rate**. This is not a flaw in PSA's statistics; it is the internationally standard ILO definition. It is a flaw in how the number gets quoted.
</div>

### Citing them properly

Always give: the **agency**, the **exact indicator name**, the **reference period**, and the **base year** if it is an index.

```
Good: Philippine Statistics Authority (2026). Consumer Price Index,
      all items, 2018 = 100, National Capital Region, January 2026.

Bad:  "Inflation was 3.2% (PSA)."
```

Check the **technical notes** on the PSA release before quoting. Definitions change, and a series break can make a year-on-year comparison meaningless.

## Doing it in software

### Excel
```
Rate per 100,000:
=cases / population * 100000

Index with base in B2:
=B3/$B$2*100                 fill down; the $ locks the base

Percentage change between periods:
=(B4-B3)/B3*100

Rebasing to a new year in B4:
=C3/$C$4*100
```

### R
```r
price <- c(42, 48, 53, 57)
year  <- c(2020, 2022, 2024, 2026)

index_2020 <- price / price[1] * 100      # 100.0 114.3 126.2 135.7
index_2024 <- price / price[3] * 100      #  79.2  90.6 100.0 107.5

# period-on-period percentage change
diff(price) / head(price, -1) * 100        # 14.29  10.42  7.55

# rate per 100,000
cases <- c(4200, 1800); pop <- c(3100000, 900000)
round(cases / pop * 100000, 1)             # 135.5  200.0
```

### Jamovi / SPSS
Both handle this with computed variables. In Jamovi, add a **Computed variable** in the Data tab with the formula `cases / population * 100000`. In SPSS, <kbd>Transform</kbd> &rarr; <kbd>Compute Variable</kbd>.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- rates</span>
Dengue incidence was *135.5* per *100,000* population in Province A and *200.0* per *100,000* in Province B for *2025*. Although Province A recorded more cases in absolute terms (*4,200* versus *1,800*), its substantially larger population yields a *lower* incidence rate.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- index numbers</span>
Using *2020* as the base year (*2020* = 100), the price index for *rice* rose to *135.7* by *2026*, representing a *35.7%* increase over the period. Between *2024* and *2026* alone the index rose *9.5* index points, a *7.5%* increase.
</div>

## Common mistakes

- **Comparing raw counts across populations of different sizes.** The opening scenario.
- **Omitting the denominator or the period.** Makes the rate uninterpretable.
- **Comparing crude rates between populations with different age structures.**
- **Confusing index points with percentage change.**
- **Comparing indices computed on different base years** without rebasing first.
- **Quoting an official statistic without its definition.** Especially unemployment and poverty incidence.
- **Treating a revised figure as final.** GDP and many PSA series are revised after first release; cite the release date.

## Practice

**1.** City X: 340 road deaths, population 2.4 million. City Y: 95 deaths, population 480,000. Which is more dangerous?

<details markdown="1">
<summary>Show the worked answer</summary>

Road deaths are relatively rare, so use per 100,000:

```
City X: 340 / 2,400,000 x 100,000 = 14.2 per 100,000
City Y:  95 /   480,000 x 100,000 = 19.8 per 100,000
```

**City Y is more dangerous**, at about 1.4 times City X's rate -- despite recording roughly a quarter of the deaths.

A caveat worth stating in a real report: resident population may be the wrong denominator for road deaths. If City X has heavy commuter inflows, its *road users* far exceed its residents, and the resident-based rate overstates its danger. For traffic statistics, deaths per 100 million vehicle-kilometres is the better measure -- when that data exists.

**The general lesson: choosing the denominator is a substantive decision, not a clerical one.**
</details>

**2.** An index (2019 = 100) reads 128 in 2024 and 140 in 2026. What is the percentage increase from 2024 to 2026?

<details markdown="1">
<summary>Show the worked answer</summary>

```
Change in index points = 140 - 128 = 12 points

Percentage change = (140 - 128) / 128 x 100
                  = 12 / 128 x 100
                  = 9.375%
```

**About 9.4%** -- not 12%.

The 12 is a change in *index points*. Converting to a percentage requires dividing by the **starting** value (128), not by the base-year value of 100.

A quick way to see the distinction: from 2019 to 2026 the index rose 40 points, which *is* a 40% increase -- but only because the starting value was exactly 100. That coincidence at the base year is what misleads people everywhere else in the series.
</details>

**3.** The unemployment rate falls from 6.2% to 5.1%. A politician claims 1.1% more people are employed. Evaluate.

<details markdown="1">
<summary>Show the answer</summary>

**Two errors, one of them substantive.**

**Error 1 -- percentage points versus percent.** The fall is 1.1 **percentage points**. As a percentage change it is (6.2 &minus; 5.1)/6.2 = 17.7%. Saying "1.1% more people are employed" confuses the two.

**Error 2 -- the definition, which is the real problem.** The unemployment rate is:

```
unemployed / labour force x 100
```

The rate can fall for two very different reasons:

- **Good:** unemployed people found jobs, so the numerator shrank.
- **Not good:** unemployed people stopped looking for work. They leave the labour force entirely, shrinking **both** numerator and denominator -- and the rate falls while nobody gained a job.

**What to check before believing the claim:**

- The **labour force participation rate**. If it fell alongside unemployment, discouraged workers are a large part of the story.
- The **absolute number of employed persons**. If employment actually rose, the good interpretation holds.
- The **underemployment rate**, which PSA publishes and which is persistently high in the Philippines. People counted as employed may be working far fewer hours than they want.

**The honest statement:** "The unemployment rate fell by 1.1 percentage points. Over the same period the labour force participation rate [rose / fell / was stable] and the number of employed persons [rose / fell] by X."

This is a good habit for every official statistic: find the denominator, and ask what else moved.
</details>

## Before you move on

- [ ] I can convert counts into rates with an explicit denominator and period
- [ ] I can explain why crude rates mislead, and compute a directly standardised rate
- [ ] I can build an index, rebase it, and distinguish index points from percentage change
- [ ] I know what the unemployment rate's denominator is and why that matters
- [ ] I cite official statistics with agency, indicator, period and base year

This is the last teaching lesson in Basic Statistics. The next page collects the references, all of them free.""",
    [{"question": "An index rises from 128 to 140. What is the percentage increase?",
      "choices": ["12%", "9.4%", "40%", "8.6%"], "correct": 1},
     {"question": "The unemployment rate can fall without anyone finding a job because:",
      "choices": ["The population grew", "Discouraged workers leave the labour force, shrinking the denominator",
                  "Inflation was rebased", "The CPI changed"], "correct": 1}],
)


# ===========================================================================
L(
    "Further Reading (Free & Open)",
    """## How to use this page

Everything here is free and legally available. The CHED references come from CMO 42 s. 2017 Annex B, which specifies the texts for Descriptive Statistics.

Work through **one** of the primary sources rather than sampling all of them. Depth beats breadth.

## The CHED-specified texts

- **Almeda, J.V., Capistrano, T.G., and Sarte, G. -- *Elementary Statistics*** (UP Press, Diliman). The reference CMO 42 names for Descriptive Statistics, written for Philippine classrooms with local examples. Available in most university libraries.
- **Freedman, D., Pisani, R., and Purves, R. -- *Statistics*** (W.W. Norton). Also named in CMO 42. Widely regarded as the best-written introductory statistics text in English; almost no formulas, relentless focus on reasoning.

## Free full courses

- **OpenIntro Statistics** -- openintro.org. A complete introductory textbook, free as a PDF, with video lectures, labs in R, and full solution sets. If you read only one thing after this course, read this.
- **Khan Academy -- Statistics and Probability**. Short videos with practice exercises that adapt to your level. Best for drilling a specific topic you found hard.
- **MIT OpenCourseWare 18.05, *Introduction to Probability and Statistics***. Full lecture notes and problem sets, openly licensed. A step up in rigour from this course.
- **Seeing Theory** -- seeing-theory.brown.edu. Interactive visual explanations of probability and inference. Genuinely excellent for building intuition about sampling distributions and confidence intervals.

## Free software worth installing

- **Jamovi** -- jamovi.org. Free, open source, and produces APA-formatted output. The friendliest route out of SPSS, and the one most Philippine graduate students can actually afford.
- **JASP** -- jasp-stats.org. Similar to Jamovi, with stronger Bayesian support.
- **R and RStudio** -- both free. Steeper to learn, but it is the language most statistical research is published in.
- **PSPP** -- free, and deliberately mimics the SPSS interface if that is what your adviser expects to see.

## Philippine data to practise on

- **PSA OpenSTAT** -- openstat.psa.gov.ph. Official statistics across every sector, downloadable.
- **PSA Data Archive** -- microdata from the Labour Force Survey, FIES and other national surveys, free for research use on request.
- **Bangko Sentral statistics** -- bsp.gov.ph, for financial and monetary series.
- **data.gov.ph** -- the national open data portal.

Practising on real Philippine data is far more useful than practising on clean textbook datasets. Real data has missing values, revisions, inconsistent categories and genuine outliers -- and handling those is the actual skill.

## How to keep the skills

Three habits that matter more than any further reading:

1. **Re-derive, do not re-read.** Close the page and reproduce the deviation table from memory. Recognition is not recall.
2. **Analyse something you care about.** Your barangay's data, your section's grades, your own expenses. Motivation carries you through the tedious parts.
3. **Explain it to someone.** If you cannot explain a confidence interval to a friend who has never studied statistics, you do not yet understand it well enough for a defence.

## Where to go next in this catalogue

| If you want to... | Take |
|---|---|
| Design a study that survives a panel | **Foundations of Research Methodology** |
| Choose the right test for your thesis | **Applied Statistics for Research** |
| Learn regression properly | **Intermediate Statistics: Building Real Models** |
| Understand the theory underneath all of this | **Probability & Mathematical Statistics** |
| Work with ordinal or non-normal data | **Nonparametric Statistics** |""",
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

        titles = {spec["title"] for spec in LESSONS}
        existing = {l.title: l for l in course.lessons}
        stale = [t for t in existing if t not in titles]

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
        print(f"[{course.title}]")
        print(f"  {added} lesson(s) added, {rewritten} rewritten, {len(LESSONS)} total")
        print(f"  {chars:,} characters of content ({chars // len(LESSONS):,} average per lesson)")
        if stale:
            print(f"  note: {len(stale)} lesson(s) left untouched and now sit after these: {', '.join(stale)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
