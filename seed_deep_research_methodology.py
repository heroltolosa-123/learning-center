"""
Rewrites Foundations of Research Methodology at teaching depth.

The course a thesis candidate takes first. Ten lessons covering everything
between "I have a topic" and "I have analysable data."

Verified arithmetic used throughout (population N = 2,400 SHS students):

  Slovin  n = N/(1 + Ne^2)
    e=.10 -> 96      e=.05 -> 343      e=.03 -> 760
  Cochran (p=.5, z=1.96)
    e=.05 -> n0 = 384.16 -> 385;  with finite population correction -> 332
    e=.03 -> n0 = 1067.11 -> 1068;  with FPC -> 739
  Proportional stratified allocation of n=331 across 900/700/500/300
    -> 124 / 97 / 69 / 41, summing to 331
  Design effect  DEFF = 1 + (m-1)*ICC, cluster size 20
    ICC .02 -> 1.38 (600 behaves like 435)
    ICC .05 -> 1.95 (600 behaves like 308)
    ICC .10 -> 2.90 (600 behaves like 207)
  Cronbach's alpha worked by hand, 5 items x 10 respondents
    sum of item variances 4.8667, total score variance 19.7333
    alpha = (5/4)(1 - 4.8667/19.7333) = .9417

Safe to re-run. Lessons matched by title and replaced in place.

Usage:
    python3 seed_deep_research_methodology.py
"""
import json
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal, sync_columns
from app import models

COURSE_SLUG = "research-methodology-foundations"
LESSONS = []


def L(title, content, quiz=None, preview=False):
    LESSONS.append({"title": title, "content": content, "quiz": quiz, "preview": preview})


# ===========================================================================
L(
    "What Makes a Research Question Researchable",
    """## What you will be able to do

Take a vague topic and sharpen it into a question that can actually be answered with data you can realistically collect -- and recognise the four kinds of question that cannot be answered by research at all.

## The situation

<div class="callout callout-case" markdown="1">
<span class="callout-label">Scenario</span>
A candidate submits: *"The Effect of Social Media on Students."*

Every panel member will ask the same things. **Which** social media? **Which** effect? **Which** students? Measured **how**? Over **what** period?

None of those are hostile questions. They are the questions the title left unanswered, and until it answers them no study exists.
</div>

## The four tests

<div class="callout callout-key" markdown="1">
<span class="callout-label">A researchable question is FINE</span>

- **F**easible -- you can get the data, in the time and with the resources you have
- **I**nteresting -- to someone other than you
- **N**ovel -- it adds something, even a small something
- **E**thical -- it can be done without harming anyone

Add a fifth from the medical literature: **Relevant** -- the answer would change something.
</div>

### Test 1: Feasible

Ask concretely:

- **Who** will give me data, and will they agree?
- **How many** can I realistically reach?
- **How long** will collection take?
- **What will it cost**, in fares, printing, software, incentives?
- **Do I have permission**, from the school, the agency, the ethics board?

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The most common feasibility failure</span>
Proposing a study that needs 400 respondents across five municipalities, with one semester and no budget.

A smaller, well-executed study beats an ambitious one that collapses in the field. Scope to what you can finish.
</div>

### Test 2: Interesting and Test 3: Novel

Novel does **not** mean nobody has studied it. A genuine contribution can be:

| Type | Example |
|---|---|
| New population | A well-studied intervention, tested in a Philippine public school |
| New context | An urban finding, retested in a rural setting |
| New method | An established question, measured better |
| New variable | An added moderator nobody has examined |
| Replication | Checking whether a finding holds at all |

Replication is undervalued and entirely legitimate. Say so explicitly and justify why it matters here.

### Test 4: Ethical

Covered fully in lesson 4. The screening question now: **could this harm anyone, and do I have a way to prevent it?**

## Questions research cannot answer

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Four kinds to rule out immediately</span>

1. **Value questions.** *"Should K-12 be abolished?"* Research can tell you the effects; whether they are worth it is a value judgement.
2. **Questions with no measurable outcome.** *"Is education important?"*
3. **Questions answerable by looking it up.** *"What is the enrolment rate in Region IV-A?"* That is a fact, not a finding.
4. **Questions too broad to answer.** *"What causes poverty?"*
</div>

## The sharpening procedure

Work down from topic to question in five steps.

<div class="callout callout-case" markdown="1">
<span class="callout-label">Worked example</span>

**Step 1 -- Topic.** Social media and students.

**Step 2 -- Narrow the population.** Grade 11 students in one public senior high school in Batangas City.

**Step 3 -- Narrow the variables.** Not "social media" but **daily hours on social media for non-academic purposes**. Not "effect" but **academic achievement, measured by first-semester general weighted average**.

**Step 4 -- Name the relationship.** A relationship, not a cause -- we cannot randomly assign social media use.

**Step 5 -- Write the question.**

> *"Is there a significant relationship between daily non-academic social media use and first-semester general weighted average among Grade 11 students at [school], School Year 2026-2027?"*
</div>

Notice what the final version contains: a named population, a time frame, two operationalised variables, and a relationship claim the design can support.

## Specific, Measurable, Answerable

Test every question against three questions of your own:

| Test | Failing version | Passing version |
|---|---|---|
| **Specific** | "students" | "Grade 11 STEM students at X" |
| **Measurable** | "social media addiction" | "score on the Bergen Social Media Addiction Scale" |
| **Answerable** | "why do students fail?" | "which of these five factors predicts failure?" |

## From question to Statement of the Problem

Philippine thesis formats require a numbered Statement of the Problem. Build it as a ladder: descriptive questions first, then relational.

```
1. What is the profile of the respondents in terms of
   1.1 sex;
   1.2 strand; and
   1.3 daily hours of non-academic social media use?
      -> frequencies, percentages, mean, SD

2. What is the level of academic achievement of the respondents?
      -> mean, SD

3. Is there a significant relationship between daily non-academic
   social media use and academic achievement?
      -> Pearson r (or Spearman)

4. Is there a significant difference in academic achievement
   when respondents are grouped by sex?
      -> independent-samples t-test
```

<div class="callout callout-key" markdown="1">
<span class="callout-label">The one-to-one rule</span>
**Every numbered problem gets exactly one analysis. Every analysis answers exactly one numbered problem.**

Write the mapping table in Chapter 3 before you collect anything. It is the single most effective defence preparation available, and it catches unanswerable questions while they are still cheap to fix.
</div>

## Scope and delimitation

Two different things, and panels notice when they are confused.

| | Meaning | Example |
|---|---|---|
| **Scope** | What the study **covers** | Grade 11 students at one school, SY 2026-2027 |
| **Delimitation** | What you **deliberately excluded**, and why | Grade 12 excluded because they were on immersion |
| **Limitation** | Weaknesses you could **not** control | Self-reported usage may be inaccurate |

Delimitations are choices. Limitations are constraints. Putting a choice in the limitations section reads as an excuse.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- research question</span>
This study sought to determine whether a significant relationship exists between *daily non-academic social media use* and *academic achievement* among *Grade 11 students at [school]* during *School Year 2026-2027*.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- scope and delimitation</span>
This study was limited to *Grade 11* students enrolled at *[school]* during *School Year 2026-2027*. *Grade 12* students were excluded because they were on work immersion during the data collection period. Social media use was delimited to *non-academic* use, self-reported in hours per day. Academic achievement was delimited to the *first-semester general weighted average*.
</div>

## Common mistakes

- **A title that is a topic, not a question.**
- **No named population or time frame.**
- **Variables that cannot be measured** as written.
- **A question the design cannot answer.** Asking about *effect* from a correlational design.
- **Too many questions.** Four to six well-chosen ones beat twelve.
- **A question already answered by a statistic you could look up.**
- **Confusing delimitation with limitation.**

## Practice

**1.** Sharpen this: "A Study on the Teaching Strategies of Teachers."

<details markdown="1">
<summary>Show the worked answer</summary>

**What is missing:** which teachers, which strategies, which outcome, where, when, and what relationship is claimed.

**Step 1 -- narrow the population.** Public elementary Mathematics teachers in one district.

**Step 2 -- narrow the independent variable.** Not "teaching strategies" but a specific, nameable one: **use of manipulatives in teaching fractions**.

**Step 3 -- name an outcome.** **Pupils' achievement on a 30-item fractions test.**

**Step 4 -- decide the relationship the design can support.** If you can assign classes to methods, this is quasi-experimental and you may compare. If you can only observe, it is correlational.

**Sharpened version:**

> *"Is there a significant difference in fractions achievement between Grade 4 pupils taught using manipulatives and those taught using the conventional method in [district], School Year 2026-2027?"*

**Statement of the Problem:**
```
1. What is the pretest achievement of both groups?
2. What is the posttest achievement of both groups?
3. Is there a significant difference in posttest achievement
   between the two groups, controlling for pretest?  -> ANCOVA
```

**What improved:** a named population, one specific strategy, a measured outcome, a time frame, and a design that can support the comparison.
</details>

**2.** Why can research not answer "Should the school implement a no-homework policy?"

<details markdown="1">
<summary>Show the answer</summary>

**It is a value question, not an empirical one.** "Should" asks what is *right*, which depends on what the school values -- and no amount of data settles a disagreement about values.

**What research CAN answer:**

- What is the relationship between homework hours and achievement at this grade level?
- Do students in no-homework classes differ in achievement, stress, or sleep?
- What do teachers, parents and students report about homework's effects?

**Why the distinction matters:** you could find that homework raises achievement by *d* = 0.15 while measurably increasing reported stress and reducing sleep. The evidence is now complete, and people will **still** disagree about whether to keep it — because they weigh achievement and wellbeing differently.

**How to write the researchable version:**

> *"Is there a significant relationship between weekly homework hours and (a) academic achievement and (b) self-reported stress among Grade 9 students at [school]?"*

Then your Recommendations may say: *"Given that homework showed a small association with achievement but a moderate association with reported stress, the school may wish to review its homework policy."* That is evidence informing a decision, which is the proper role. It is not the research making the decision.
</details>

**3.** Your adviser says your question is "not novel" because three studies have examined it. Is that fatal?

<details markdown="1">
<summary>Show the answer</summary>

**No — but you must state your contribution explicitly rather than assume it is obvious.**

Find your angle among these:

1. **Population.** Were the three studies on Filipino students? Public schools? This age group? A well-supported finding from a US university sample is genuinely untested in a Philippine public senior high school.

2. **Context.** Were they conducted before a policy change, before the pandemic, before a curriculum revision? Context shifts, and findings expire.

3. **Method.** Did they use self-report where you can use records? A cross-sectional design where you can do longitudinal? A small convenience sample where you can sample properly?

4. **Extension.** Can you add a moderator or mediator none of them examined?

5. **Conflicting findings.** If the three studies **disagree**, resolving that disagreement is a strong contribution on its own.

6. **Replication.** If they agree but none has been replicated locally, say so. The replication crisis has made direct replication respectable, and many journals now welcome it.

**How to write it into Chapter 1:**

> While Santos (2022), Reyes (2023) and Cruz (2024) examined this relationship, all three used private-school samples in Metro Manila. No study has examined it in a public senior high school in a rural setting, where access to devices and study conditions differ substantially. This study addresses that gap.

**One sentence naming the gap** converts "not novel" into a justified contribution.
</details>

## Before you move on

- [ ] My question names a specific population and time frame
- [ ] Every variable in it can actually be measured
- [ ] It passes all four FINE tests
- [ ] It is not a value question, a lookup, or too broad
- [ ] My Statement of the Problem maps one-to-one onto analyses
- [ ] I can state my contribution in one sentence

Next: choosing the design that can actually answer it.""",
    [{"question": "\"Should the school ban mobile phones?\" cannot be answered by research because it is:",
      "choices": ["Too narrow", "A value question rather than an empirical one",
                  "Already answered", "Unethical"], "correct": 1},
     {"question": "Excluding Grade 12 students because they were on immersion belongs in:",
      "choices": ["Limitations", "Delimitations", "Recommendations", "Assumptions"], "correct": 1}],
    preview=True,
)


# ===========================================================================
L(
    "Choosing a Research Design",
    """## What you will be able to do

Pick the design that can actually answer your question, name it correctly, and state honestly what conclusions it does and does not license.

## The design decides your verbs

<div class="callout callout-key" markdown="1">
<span class="callout-label">The rule that governs Chapter 5</span>
**Only random assignment licenses causal language.**

| Design | Permitted verbs |
|---|---|
| True experiment | causes, affects, improves, reduces |
| Quasi-experiment | is associated with; *may* contribute to |
| Correlational | is associated with, is related to, predicts |
| Descriptive | describes, reports, characterises |

Writing "the module improved achievement" from intact sections is the most common overclaim in thesis work, and panels are trained to catch it.
</div>

## The design map

### Quantitative designs

| Design | Random assignment? | Manipulation? | Answers |
|---|---|---|---|
| **True experimental** | Yes | Yes | Does X cause Y? |
| **Quasi-experimental** | No | Yes | Do groups differ after X? |
| **Pre-experimental** | No | Yes, but no control | (Very weak) |
| **Correlational** | No | No | Are X and Y related? |
| **Descriptive** | No | No | What is the level of X? |
| **Comparative (causal-comparative / ex post facto)** | No | No, groups already differ | Do existing groups differ on Y? |

### Common notation

Campbell and Stanley's shorthand appears in most Philippine thesis manuals:

```
R  = random assignment      O = observation/measurement      X = treatment

One-group pretest-posttest (PRE-EXPERIMENTAL, weak):
        O1   X   O2

Non-equivalent control group (QUASI-EXPERIMENTAL):
        O1   X   O2
        O1       O2

Randomised pretest-posttest control group (TRUE EXPERIMENT):
   R    O1   X   O2
   R    O1       O2

Posttest-only control group (TRUE EXPERIMENT):
   R         X   O
   R             O
```

## Why the one-group design is weak

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Five rival explanations it cannot rule out</span>
A single group measured before and after cannot distinguish your treatment from:

1. **Maturation** -- participants changed anyway over the period
2. **History** -- something else happened at the same time
3. **Testing** -- taking the pretest itself improved posttest performance
4. **Instrumentation** -- the measure or the scorer changed
5. **Regression to the mean** -- extreme pretest scorers drift toward average regardless

**A control group rules out all five at once**, because it experiences everything except the treatment. That single addition is the biggest improvement available to most thesis designs.
</div>

## Validity: the four kinds

| Type | Asks | Threatened by |
|---|---|---|
| **Internal** | Did X really cause the change? | The five threats above, plus selection and attrition |
| **External** | Does it generalise? | Non-representative sampling, artificial settings |
| **Construct** | Am I measuring what I claim? | Poor instruments, single measures |
| **Statistical conclusion** | Is the statistical inference sound? | Low power, violated assumptions, multiple testing |

<div class="callout callout-key" markdown="1">
<span class="callout-label">The trade-off</span>
Internal and external validity usually pull against each other. A tightly controlled laboratory study has strong internal validity and weak external validity; a naturalistic classroom study has the reverse.

**You cannot maximise both.** Choose deliberately, and defend the choice in Chapter 3.
</div>

## Cross-sectional or longitudinal

| | Cross-sectional | Longitudinal |
|---|---|---|
| Measurement | One point in time | Repeated over time |
| Cost | Low | High |
| Attrition | None | A serious problem |
| Establishes temporal order | **No** | **Yes** |
| Typical thesis feasibility | High | Low |

Temporal order matters for any mediation or causal claim. If X and Y are measured at the same moment, you cannot show X came first -- which is why cross-sectional mediation claims are routinely challenged.

## Mixed methods

| Design | Sequence | Purpose |
|---|---|---|
| **Explanatory sequential** | QUANT &rarr; qual | Numbers first; interviews explain *why* |
| **Exploratory sequential** | QUAL &rarr; quant | Interviews first; build an instrument from them |
| **Convergent parallel** | QUANT + QUAL together | Compare for convergence |
| **Embedded** | One inside the other | A small qual component supports a larger quant study |

Capitalisation signals priority: QUANT &rarr; qual means the quantitative strand dominates.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Mixed methods is not "I did a survey with open-ended items"</span>
Genuine mixed methods requires a stated **design**, a stated **sequence**, a stated **priority**, and an explicit **point of integration** -- where and how the two strands are brought together.

Without those, you have a quantitative study with some comments in it.
</div>

## Choosing: the decision sequence

<div class="callout callout-key" markdown="1">
<span class="callout-label">Four questions, in order</span>

1. **Can I randomly assign participants to conditions?**
   Yes &rarr; true experiment. No &rarr; continue.
2. **Can I manipulate the independent variable at all, even with intact groups?**
   Yes &rarr; quasi-experimental. No &rarr; continue.
3. **Am I comparing groups that already differ, or relating two continuous variables?**
   Groups &rarr; comparative. Variables &rarr; correlational.
4. **Am I only describing, with no comparison or relationship?**
   &rarr; descriptive.
</div>

<div class="callout callout-case" markdown="1">
<span class="callout-label">Worked example</span>
**Question.** Does a self-paced module improve Grade 11 statistics achievement?

1. *Can I randomly assign?* No -- the school will not break up intact sections. Continue.
2. *Can I manipulate?* Yes -- I can give one section the module and the other the usual lecture.

&rarr; **Quasi-experimental, non-equivalent control group design.**

**What this licenses:** "students taught with the module scored significantly higher."
**What it does not:** "the module caused higher scores."

**How to strengthen it within the constraint:**
- Collect a **pretest** and analyse with ANCOVA
- Check the sections were comparable at baseline on prior grades and demographics
- Report any teacher differences as a confound you could not remove
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- Chapter 3, research design</span>
This study employed a *quasi-experimental, non-equivalent control group* design. Random assignment of individual students was not feasible because the school operates intact sections; two comparable sections were therefore assigned to the *treatment* and *control* conditions. A pretest was administered to establish baseline comparability and was used as a covariate in the analysis. The design is represented as:

```
O1   X   O2       (treatment)
O1       O2       (control)
```

where O denotes measurement and X the intervention.
</div>

## Common mistakes

- **Calling a quasi-experiment an experiment.**
- **A one-group pretest-posttest design** with no acknowledgement of its threats.
- **Causal verbs from a correlational design.**
- **No design named at all** in Chapter 3.
- **Claiming mixed methods** without a named design, sequence and integration point.
- **Cross-sectional data supporting a mediation claim** without acknowledging the temporal-order problem.

## Practice

**1.** You compare Board exam passing rates between graduates of two universities. What design is this, and what can you conclude?

<details markdown="1">
<summary>Show the worked answer</summary>

**Causal-comparative (ex post facto).** The groups already existed; you neither assigned students to universities nor manipulated anything. You are comparing pre-existing groups on an outcome that has already occurred.

**What you may conclude:** graduates of University A passed at a significantly higher rate than graduates of University B.

**What you may not conclude:** that University A provides better education. The confounds are severe:

- **Selection.** University A may admit stronger students to begin with. Its higher pass rate may reflect admission standards, not teaching.
- **Self-selection.** Students choose universities for reasons correlated with ability and resources.
- **Attrition.** If A dismisses weak students before graduation and B does not, A's graduating cohort is pre-filtered.
- **Socio-economic factors.** Review-centre access, ability to study full-time, family support.

**How to strengthen it:** control for admission test scores or entering GPA, if you can obtain them. That turns a raw comparison into an adjusted one — still not causal, but far more informative.

**How to write the conclusion:**

> Graduates of University A passed at a significantly higher rate (78.2%) than those of University B (61.4%), *&chi;²*(1) = 14.2, *p* < .001, *&phi;* = .18. Because students were not randomly assigned to institutions, this difference cannot be attributed to instructional quality; differences in admission selectivity and student background are plausible alternative explanations.
</details>

**2.** A study measures burnout and job satisfaction in 200 nurses at one time point and concludes "burnout reduces job satisfaction." What is wrong?

<details markdown="1">
<summary>Show the answer</summary>

**Two problems: an unsupported causal claim, and no evidence of temporal order.**

**Problem 1 — the verb.** This is cross-sectional correlational data. Nothing was manipulated and nobody was assigned. The defensible verb is *"is negatively associated with."*

**Problem 2 — direction is undetermined.** Three explanations fit the same correlation equally well:

- Burnout reduces job satisfaction
- **Low job satisfaction causes burnout** — the reverse
- Both are caused by something else: understaffing, poor management, excessive overtime

Because both were measured at the same moment, the data contains no information about which came first.

**What would establish direction:**

- **Longitudinal design.** Measure burnout at Time 1 and satisfaction at Time 2, controlling for satisfaction at Time 1. This is the standard route.
- **Experimental manipulation.** Usually unethical here — you cannot randomly assign nurses to a burnout condition.
- **Instrumental variables**, if a plausible instrument exists.

**The corrected sentence:**

> Burnout was significantly negatively associated with job satisfaction, *r*(198) = &minus;.54, *p* < .001. Because the design was cross-sectional, the direction of this relationship cannot be determined.

**A related trap:** the same study running a mediation analysis with all three variables measured at once. Mediation assumes M occurs after X and before Y. Cross-sectional data cannot support that ordering, and reviewers increasingly reject such claims outright.
</details>

**3.** Why does adding a control group fix so many problems at once?

<details markdown="1">
<summary>Show the answer</summary>

**Because the control group experiences everything your treatment group experiences except the treatment itself.**

Take the five threats to a one-group design:

| Threat | How a control group handles it |
|---|---|
| **Maturation** | Both groups mature over the same period. Any difference beyond that is not maturation. |
| **History** | Both groups live through the same events. |
| **Testing** | Both take the same pretest, so practice effects apply to both. |
| **Instrumentation** | Both are measured with the same instrument by the same procedure. |
| **Regression to the mean** | Both groups regress equally if selected the same way. |

**What remains after adding a control group:**

- **Selection.** If the groups differed to begin with, that difference is still confounded with treatment. This is why the design is *quasi*-experimental and why a pretest plus ANCOVA matters.
- **Differential attrition.** If dropout differs between groups, the comparison is compromised. Report attrition per group.
- **Compensatory rivalry or demoralisation.** The control group may work harder because they know they are the control, or give up. Minimise by not advertising who is which.

**The practical implication:** if you can add a control group, do. It is usually the single largest improvement available, and it costs only the effort of measuring one more intact section.
</details>

## Before you move on

- [ ] I can name my design using standard terminology
- [ ] I can draw it in Campbell and Stanley notation
- [ ] My verbs in Chapter 5 match what the design licenses
- [ ] I know which of the five threats my design does and does not control
- [ ] I have stated the internal/external validity trade-off I chose
- [ ] If I claim mixed methods, I have named the design, sequence and integration point

Next: choosing who is actually in the study.""",
    [{"question": "Which design licenses the verb \"causes\"?",
      "choices": ["Correlational", "Quasi-experimental", "True experimental with random assignment", "Descriptive"], "correct": 2},
     {"question": "A one-group pretest-posttest design cannot rule out:",
      "choices": ["Sampling error", "Maturation, history, testing and regression to the mean",
                  "Measurement error", "Multicollinearity"], "correct": 1}],
)


# ===========================================================================
L(
    "Sampling: Getting a Group That Actually Represents Your Population",
    """## What you will be able to do

Compute a sample size three different ways, allocate it across strata, and explain to a panel why your number is defensible -- or why it is a limitation you have stated honestly.

## The vocabulary panels use

| Term | Meaning |
|---|---|
| **Population** | Everyone you want to conclude about |
| **Target population** | The population as you define it, with inclusion criteria |
| **Sampling frame** | The actual list you draw from |
| **Sample** | Those you collect data from |
| **Sampling unit** | What gets selected -- a student, a class, a barangay |
| **Element** | What gets measured |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Frame error</span>
Your conclusions apply to the **sampling frame**, not to the population you wish you had.

If your frame is the enrolment list and 12% of enrolled students have stopped attending, your findings describe enrolled students, not attending ones. State the frame explicitly and name any gap between it and the target population.
</div>

## Probability versus non-probability

<div class="callout callout-key" markdown="1">
<span class="callout-label">The dividing line</span>
**Probability sampling** gives every element a **known, non-zero** chance of selection. Only probability designs support statistical inference to a population.

**Non-probability sampling** does not. Convenience, purposive, quota and snowball samples can be appropriate -- for exploratory work, hard-to-reach populations and qualitative research -- but no sample-size formula makes them generalisable.
</div>

| Probability | Non-probability |
|---|---|
| Simple random | Convenience |
| Systematic | Purposive |
| Stratified | Quota |
| Cluster | Snowball |
| Multistage | Total enumeration* |

\\* Total enumeration (studying everyone) is not sampling at all -- and it is often the right answer for a small population. If your population is 60 teachers, study all 60 and skip this lesson's arithmetic.

## Computing sample size

<div class="callout callout-case" markdown="1">
<span class="callout-label">Our population</span>
**N = 2,400** senior high school students in one division.
</div>

### Method 1 -- Slovin's formula

The formula most Philippine thesis manuals teach.

<div class="formula" markdown="1">
**n = N / (1 + Ne&sup2;)**
<span class="formula-note">e = margin of error, as a decimal</span>
</div>

**At e = 0.05:**
```
n = 2400 / (1 + 2400 x 0.05^2)
  = 2400 / (1 + 2400 x 0.0025)
  = 2400 / (1 + 6.00)
  = 2400 / 7.00
  = 342.86  ->  343
```

At other margins:

| Margin of error | n |
|---|---:|
| 10% | 96 |
| 5% | 343 |
| 3% | 760 |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">What Slovin does not do</span>
Slovin's formula assumes a **95% confidence level** and **maximum variability (p = .5)**, and neither appears in the formula. It also says nothing about **statistical power**.

Panels increasingly ask for a power analysis instead, because Slovin cannot tell you whether you can detect the effect you are looking for. If your study tests hypotheses, compute both: Slovin for precision, G*Power for power, and take the larger.
</div>

### Method 2 -- Cochran's formula

Used when estimating a proportion, and the basis for most survey sample sizes.

<div class="formula" markdown="1">
**n&#8320; = z&sup2;pq / e&sup2;**
<span class="formula-note">z = 1.96 for 95%; p = expected proportion; q = 1 &minus; p</span>
</div>

**At p = .5 (maximum variability) and e = .05:**
```
n0 = (1.96)^2 x 0.5 x 0.5 / (0.05)^2
   = 3.8416 x 0.25 / 0.0025
   = 0.9604 / 0.0025
   = 384.16  ->  385
```

**Then apply the finite population correction**, because 385 is a large share of 2,400:

<div class="formula" markdown="1">
**n = n&#8320; / (1 + (n&#8320; &minus; 1)/N)**
</div>

```
n = 384.16 / (1 + (384.16 - 1)/2400)
  = 384.16 / (1 + 383.16/2400)
  = 384.16 / 1.1597
  = 331.27  ->  332
```

Note Cochran with the correction (332) lands close to Slovin (343). That agreement is reassuring and worth mentioning in a defence.

### Method 3 -- Power analysis

Covered in Applied Statistics. For a medium effect (*d* = 0.50) at 80% power, an independent t-test needs **64 per group**. If your design compares two groups, that is the binding number regardless of what Slovin says.

<div class="callout callout-key" markdown="1">
<span class="callout-label">Which to use</span>
- **Descriptive survey estimating proportions** &rarr; Slovin or Cochran
- **Hypothesis-testing study** &rarr; power analysis
- **Both** &rarr; compute both and take the **larger**

Then **add for attrition**: 10-20% above the computed minimum.
</div>

## Proportional stratified allocation

Once you have n, distribute it so each subgroup is represented in proportion to its share of the population.

<div class="formula" markdown="1">
**n<sub>h</sub> = n &times; (N<sub>h</sub> / N)**
</div>

With n = 331 across four strands:

| Strand | N<sub>h</sub> | N<sub>h</sub>/N | &times; 331 | Allocated |
|---|---:|---:|---:|---:|
| STEM | 900 | .3750 | 124.12 | **124** |
| ABM | 700 | .2917 | 96.54 | **97** |
| HUMSS | 500 | .2083 | 68.96 | **69** |
| GAS | 300 | .1250 | 41.38 | **41** |
| **Total** | **2,400** | **1.0000** | | **331** |

Always show this table in Chapter 3. It is concrete evidence the sample was designed rather than gathered.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">When proportional allocation fails you</span>
If a stratum is small -- say 40 students in a fifth strand -- proportional allocation gives you 6, too few to analyse separately.

Use **disproportional allocation**: oversample the small stratum to an analysable size, then **weight** the results back when computing overall estimates. Say clearly that you did this.
</div>

## Drawing the sample

### Simple random

1. Number the frame 1 to N
2. Generate n random numbers without replacement
3. Select those elements

```
Excel:  =RANDBETWEEN(1, 2400)     then remove duplicates
R:      sample(1:2400, 331)
```

### Systematic

1. Compute the interval **k = N/n** = 2400/331 &asymp; 7
2. Pick a random start between 1 and 7
3. Take every 7th element

Easy in the field. **Dangerous if the list has a periodic pattern** matching k -- for instance, if every 7th name is a class president.

### Cluster

Select whole groups, then measure everyone in the selected groups. Cheaper, but less precise per person -- see the design effect below.

## The design effect

<div class="callout callout-key" markdown="1">
<span class="callout-label">Why clustered samples need more people</span>
People within a cluster resemble each other, so each additional person from the same cluster adds less new information.

<div class="formula" markdown="1">
**DEFF = 1 + (m &minus; 1) &times; ICC**
<span class="formula-note">m = cluster size, ICC = intracluster correlation</span>
</div>
</div>

With 30 sections of 20 students each (600 total):

| ICC | DEFF | Effective sample size |
|---:|---:|---:|
| .02 | 1.38 | 435 |
| .05 | 1.95 | 308 |
| .10 | 2.90 | 207 |

```
ICC = .05:  DEFF = 1 + (20 - 1) x 0.05 = 1 + 0.95 = 1.95
            effective n = 600 / 1.95 = 308
```

**600 students sampled in clusters carry roughly the information of 308 sampled individually.** Analysing them as 600 independent cases makes every confidence interval about 40% too narrow.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- Chapter 3, sampling</span>
The population consisted of *2,400* Grade 11 students enrolled in *[division]* during *SY 2026-2027*. Using Slovin's formula at a *5%* margin of error, a minimum sample of *343* was required; Cochran's formula with a finite population correction yielded *332*. A sample of *343* was therefore targeted and increased to *380* to allow for non-response. Proportional stratified random sampling was used, with allocation based on strand enrolment.
</div>

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- a non-probability sample, stated honestly</span>
Purposive sampling was used to select *45* teachers who met the inclusion criteria of *at least three years' experience teaching Grade 11 Mathematics*. Because the sample was not randomly selected, findings describe this group and are not statistically generalisable to the wider population of teachers.
</div>

That second template is what most thesis-scale studies actually need, and panels accept it when it is stated plainly.

## Common mistakes

- **Using Slovin and calling it a power analysis.** Different questions.
- **Applying a sample-size formula to a convenience sample.** The formula assumes random selection.
- **Not stating the sampling frame.**
- **Ignoring the design effect** in a clustered sample.
- **No attrition allowance.**
- **Proportional allocation that leaves a stratum too small to analyse.**
- **Claiming generalisability from a purposive sample.**

## Practice

**1.** N = 850 teachers, e = 5%. Compute n using Slovin, then allocate proportionally across 400 elementary, 300 junior high and 150 senior high.

<details markdown="1">
<summary>Show the worked answer</summary>

**Slovin:**
```
n = 850 / (1 + 850 x 0.05^2)
  = 850 / (1 + 850 x 0.0025)
  = 850 / (1 + 2.125)
  = 850 / 3.125
  = 272.0  ->  272
```

**Proportional allocation:**

| Level | N&#8341; | N&#8341;/N | &times; 272 | Allocated |
|---|---:|---:|---:|---:|
| Elementary | 400 | .4706 | 128.00 | **128** |
| Junior high | 300 | .3529 | 96.00 | **96** |
| Senior high | 150 | .1765 | 48.00 | **48** |
| **Total** | **850** | **1.0000** | | **272** |

The allocations come out as whole numbers here, which is unusual and convenient. When they do not, round and adjust the largest stratum so the total matches exactly.

**Add for attrition:** at 15% non-response, target 272 &times; 1.15 &asymp; **313**, allocated in the same proportions.

**One check worth making:** is 48 senior high teachers enough to analyse that group separately? If your Statement of the Problem compares levels, yes. If you wanted to compare within senior high by subject area, 48 split four ways is 12 each — too few. That would argue for disproportional allocation.
</details>

**2.** Your adviser says "just get 100 respondents, that's enough." How do you respond?

<details markdown="1">
<summary>Show the answer</summary>

**Ask what 100 buys, and compute it. Then decide with evidence rather than a rule of thumb.**

**If the study is descriptive**, invert Slovin to find the margin of error 100 delivers:
```
n = N/(1 + Ne^2)  ->  e = sqrt((N - n)/(n x N))

With N = 2400 and n = 100:
e = sqrt((2400 - 100)/(100 x 2400))
  = sqrt(2300/240000)
  = sqrt(0.009583)
  = 0.0979  ->  about a 9.8% margin of error
```
So a reported 50% becomes "between 40% and 60%." Whether that is acceptable depends on the decision the number informs.

**If the study tests hypotheses**, run a power analysis. For an independent t-test with 50 per group, you can detect *d* &ge; 0.57 at 80% power. Anything smaller will likely be missed.

**How to raise it:**

> *"With 100 the margin of error is about 10%, and for the group comparison we would only detect large effects. Slovin at 5% gives 343. Could we aim for 343, or should we accept the wider margin and state it as a limitation?"*

**Why this works:** you are not refusing; you are quantifying the trade-off and letting the adviser choose with full information. If 100 is genuinely all that is feasible, you now have the sentence for your limitations section already written.
</details>

**3.** You sample 25 sections of 24 students each and analyse all 600 as independent cases. What is wrong, and how bad is it?

<details markdown="1">
<summary>Show the worked answer</summary>

**The observations are clustered, not independent. Students in the same section share a teacher, a schedule and a peer group, so they resemble one another.**

**How bad depends on the ICC.** With cluster size m = 24:

```
ICC = .02:  DEFF = 1 + 23 x 0.02 = 1.46   effective n = 600/1.46 = 411
ICC = .05:  DEFF = 1 + 23 x 0.05 = 2.15   effective n = 600/2.15 = 279
ICC = .10:  DEFF = 1 + 23 x 0.10 = 3.30   effective n = 600/3.30 = 182
```

Educational data typically shows ICC between .05 and .20 for achievement within classrooms, so **your 600 probably carry the information of fewer than 280 independent students**.

**The consequence:** standard errors computed as if n = 600 are too small by a factor of &radic;2.15 = 1.47. Confidence intervals are about 32% too narrow and p-values are too small. You will over-declare significance.

**What to do, in order of preference:**

1. **Multilevel (mixed) model** with section as a random effect. The correct analysis, and it estimates the ICC for you as a by-product.
2. **Cluster-robust standard errors**, clustering on section. Simpler, keeps your existing model.
3. **Analyse at the cluster level** — use the 25 section means as your units. Correct but wasteful, and n = 25.
4. **At minimum**, report the ICC and design effect and acknowledge the limitation.

**How to report it:**

> Because students were sampled in intact sections, a multilevel model with section as a random intercept was used. The intraclass correlation was .08, indicating a design effect of 2.84; ignoring clustering would have understated standard errors substantially.
</details>

## Before you move on

- [ ] I can compute n with Slovin and with Cochran plus the finite population correction
- [ ] I know when to use a power analysis instead, and to take the larger number
- [ ] I can allocate a sample proportionally and show the table
- [ ] I state my sampling frame and any gap from the target population
- [ ] I know the design effect formula and when clustering applies
- [ ] I do not claim generalisability from a non-probability sample

Next: the approvals and protections that must be in place before any of this happens.""",
    [{"question": "Slovin's formula with N = 2400 and e = 5% gives a sample size of:",
      "choices": ["96", "343", "760", "385"], "correct": 1},
     {"question": "Sampling 30 clusters of 20 students with ICC = .05 gives a design effect of 1.95. This means 600 students carry the information of about:",
      "choices": ["600 independent cases", "308 independent cases", "1,170 independent cases", "30 independent cases"], "correct": 1}],
)


# ===========================================================================
L(
    "Research Ethics and Informed Consent",
    """## What you will be able to do

Prepare a complete ethics submission, write a consent form that actually informs, handle minors correctly, and comply with the Philippine Data Privacy Act -- which is a separate requirement from ethics clearance.

## Why this comes before data collection

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The rule that catches students out</span>
**Ethics approval must be obtained BEFORE any data is collected.** It cannot be granted retroactively.

Data collected without approval usually cannot be used, cannot be published, and in many institutions cannot be defended. The study restarts.
</div>

## The four principles

| Principle | Means | In practice |
|---|---|---|
| **Respect for persons** | People decide for themselves | Informed consent; extra protection for those who cannot consent |
| **Beneficence** | Maximise benefit, minimise harm | Risk-benefit assessment; safe procedures |
| **Justice** | Fair distribution of burdens and benefits | Do not study only the convenient or the vulnerable |
| **Respect for communities** | Local values and structures matter | Community consent where culturally required |

That fourth principle appears in Philippine guidance specifically, and matters for research in indigenous communities -- where **Free and Prior Informed Consent** under the IPRA law is a legal requirement, not a courtesy.

## Informed consent: the eight elements

<div class="callout callout-key" markdown="1">
<span class="callout-label">A consent form must contain all eight</span>

1. **Purpose** of the study, in plain language
2. **Procedures** -- what exactly the participant will do, and for how long
3. **Risks and discomforts**, honestly stated
4. **Benefits**, without overstating them
5. **Confidentiality** -- how data will be stored, who sees it, how long it is kept
6. **Voluntary participation** -- and the right to withdraw at any time without penalty
7. **Contact information** for the researcher and the ethics committee
8. **A signature block**, with a copy for the participant
</div>

### Plain language is a requirement

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Consent that nobody understands is not consent</span>
Write at roughly a **Grade 6 reading level**. Provide a **Filipino** or local-language version if participants are more comfortable in it -- and have the translation checked, not machine-produced.

**Not this:** *"This study employs a quasi-experimental design to ascertain the efficacy of a pedagogical intervention on cognitive achievement outcomes."*

**This:** *"We want to find out whether a new way of teaching statistics helps students learn better. You will use a learning module for eight weeks and take two short tests."*
</div>

## Minors, and the Philippine rules

Most senior high school research involves respondents under 18.

<div class="callout callout-key" markdown="1">
<span class="callout-label">You need both</span>

- **Parental or guardian CONSENT** -- written, from the parent or legal guardian
- **Child ASSENT** -- the minor's own agreement, in language they understand

A minor who assents but whose parent refuses **does not participate**. A minor who refuses **does not participate**, even if the parent consented. Either refusal is final.
</div>

For school-based research you will typically also need:

1. **Division office** permission (DepEd Regional or Schools Division Office)
2. **School head** permission
3. **Ethics committee** approval from your institution
4. **Parental consent** and **child assent**
5. For some studies, the **teacher's** consent as well

Each takes time. Build it into your timeline -- these approvals routinely take four to eight weeks.

## Data privacy: RA 10173

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Ethics clearance does not cover data privacy</span>
The **Data Privacy Act of 2012** is a separate legal requirement. Approval from a research ethics board does not exempt you from it.
</div>

| Category | Examples | Requirement |
|---|---|---|
| **Personal information** | Name, address, email, student number | Lawful basis, usually consent |
| **Sensitive personal information** | Health, education records, religion, ethnicity, government IDs, offences | Stricter conditions; consent must be explicit |

### The five practical obligations

1. **Data minimisation.** Collect only what the research question needs. Every unnecessary identifier is a liability with no analytical return.
2. **Purpose limitation.** Use the data only for the stated purpose. A consent for "this study" does not cover reuse in a later one.
3. **Separate the identifiers.** Generate a random respondent ID at encoding. Keep the linking file encrypted, separately, with restricted access.
4. **Security.** Organisational (policies), physical (locked storage) and technical (encryption, access control) -- the law names all three.
5. **Retention and disposal.** State how long you will keep the data and how you will destroy it.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Removing names is not anonymisation</span>
Barangay plus age plus sex plus occupation frequently identifies exactly one person in a small community.

True anonymisation means the data cannot be linked back **by anyone, including you**. If you keep a key, the data is **pseudonymised**, not anonymous, and remains covered by the Act.
</div>

## Special situations

| Situation | Requirement |
|---|---|
| **Vulnerable groups** (children, prisoners, patients, employees of the researcher) | Extra safeguards; justify why this group |
| **Indigenous peoples** | Free and Prior Informed Consent under IPRA; NCIP clearance |
| **Deception** | Only if unavoidable; requires full debriefing and strong justification |
| **Withholding a beneficial treatment** from the control group | Offer it after the study ends |
| **Online surveys** | Consent via a required checkbox before the first question |
| **Secondary data** | Check the original consent covered reuse |

<div class="callout callout-key" markdown="1">
<span class="callout-label">The power-relationship problem</span>
A teacher recruiting their **own students** creates coercion risk -- students may fear that refusing affects their grade.

Standard safeguards: have someone else recruit; make participation invisible to the grader; collect consent before grades are assigned; state explicitly and repeatedly that refusal has no academic consequence.
</div>

## The ethics submission

Most Philippine institutional review boards ask for:

- [ ] Completed application form
- [ ] Research proposal (Chapters 1-3)
- [ ] Data collection instruments, in every language used
- [ ] Informed consent form, in every language used
- [ ] Assent form, if minors are involved
- [ ] Permission letters (division office, school head, agency)
- [ ] Researcher's CV
- [ ] Certificate of ethics training, where required
- [ ] Data management plan

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- Chapter 3, ethical considerations</span>
Ethical clearance was obtained from the *[institution]* Research Ethics Committee (Protocol No. *____*, approved *date*) prior to data collection. Permission was secured from the *Schools Division Office* and the *school head*. Written parental consent and child assent were obtained from all participants. Participation was voluntary, and respondents were informed they could withdraw at any time without penalty. No identifying information was collected on the questionnaires; responses were assigned random codes, and the linking file was stored separately in an encrypted, password-protected file accessible only to the researcher. Data will be retained for *three* years following publication and then securely deleted, in accordance with RA 10173.
</div>

## Common mistakes

- **Collecting data before approval.** Usually unrecoverable.
- **Consent forms written in academic language.**
- **Assent from minors but no parental consent**, or the reverse.
- **Treating ethics clearance as covering data privacy.**
- **Overstating benefits** to encourage participation.
- **Storing identifiers in the same file as the analysis data.**
- **No retention or disposal plan.**
- **Recruiting your own students** without addressing coercion.

## Practice

**1.** You want to survey Grade 10 students about family income and study habits. List every approval needed.

<details markdown="1">
<summary>Show the answer</summary>

**Approvals, in the order you should seek them:**

1. **Institutional Research Ethics Committee.** Apply first — the others often ask whether you have it.
2. **DepEd Schools Division Office.** Written permission to conduct research in public schools in that division.
3. **School head.** Endorsement and scheduling.
4. **Parental or guardian consent.** Written, because Grade 10 students are minors.
5. **Child assent.** Separate, in age-appropriate language.
6. **Class adviser**, as a practical courtesy and usually required for classroom access.

**Additional obligations specific to this topic:**

- **Family income is sensitive.** Collect it in bands rather than exact figures if bands answer your question, and explain in the consent form why you need it at all.
- **Minimise.** Do you need income, or would a proxy such as 4Ps beneficiary status suffice? Fewer identifiers, less risk.
- **No names on the questionnaire.** Use a code, with the linking file stored separately and encrypted.
- **Consider distress.** Questions about family finances can embarrass a student in a classroom setting. Administer privately, and allow item-level non-response.

**Timeline reality:** ethics review commonly takes three to six weeks, and division office approval another two to four. **Allow eight to ten weeks before your first questionnaire.** Students who plan for two weeks lose a semester.
</details>

**2.** Your consent form says: "Participation will improve your academic performance." What is wrong?

<details markdown="1">
<summary>Show the answer</summary>

**It overstates the benefit, and in doing so it undermines the validity of consent.**

**Three specific problems:**

1. **It is not true.** If the intervention's effect were known, you would not be studying it. The whole point is that the outcome is uncertain.

2. **It is coercive.** A student who believes participation will raise their grades is not making a free choice — they are responding to a promised benefit that may not exist. Consent obtained this way is not informed consent.

3. **It may be an inducement.** Ethics committees scrutinise anything that might unduly influence a decision to participate, particularly with minors and other vulnerable groups.

**The honest version:**

> *"You may or may not benefit directly from taking part. The results may help teachers understand how students learn statistics, which could benefit future students."*

**The general rule:** state benefits **truthfully and modestly**, and distinguish clearly between:

- **Direct benefits** to the participant — often none in educational research, and it is fine to say so
- **Indirect benefits** to the wider community or field

**Also check the reverse error:** understating risks. If your questionnaire asks about anxiety, bullying or family conflict, say that some questions may be uncomfortable and that participants may skip any item.
</details>

**3.** You finish your thesis. What do you do with the data file containing names and student numbers?

<details markdown="1">
<summary>Show the answer</summary>

**Follow the retention and disposal plan you committed to in your ethics application — and if you did not write one, that is itself a compliance gap.**

**The standard sequence:**

1. **Check what you promised.** Your consent form and ethics application stated a retention period. That is binding.

2. **Separate what must be kept from what must go.** Typically:
   - The **de-identified analysis dataset** may be retained for verification, replication, or later publication
   - The **linking file** (codes to names) should be destroyed as soon as it is no longer needed — usually once data cleaning is complete and before analysis begins

3. **Destroy securely.** Deleting a file does not erase it. Use secure deletion for digital files and shredding for paper. Emptying the recycle bin is not disposal.

4. **Document the disposal.** Note the date and method. Some committees require a completion report confirming it.

**Typical retention periods** in Philippine institutions run three to five years after completion or publication, to allow verification of findings. Check yours.

**What not to do:**

- Keep identifiable data indefinitely "in case it is useful." This is precisely what the Data Privacy Act exists to prevent.
- Leave the file in a shared drive, a personal laptop, or an unencrypted cloud folder.
- Pass the dataset to a junior researcher for a new study. The original consent covered **your** stated purpose, not theirs.

**The design lesson, for next time:** if you had generated random IDs at the point of data entry and never entered names into the analysis file at all, this problem would not exist. Build that into the procedure rather than solving it afterwards.
</details>

## Before you move on

- [ ] I know approval must precede data collection
- [ ] My consent form has all eight elements and is written in plain language
- [ ] I have both parental consent and child assent where minors are involved
- [ ] I know data privacy is a separate requirement from ethics clearance
- [ ] My identifiers are stored separately from the analysis data
- [ ] I have a written retention and disposal plan
- [ ] I have addressed any power relationship with my participants

Next: building the literature review that justifies all of it.""",
    [{"question": "For research with Grade 10 students, what is required?",
      "choices": ["Parental consent only", "Child assent only",
                  "Both parental consent and child assent", "Neither, if the school approves"], "correct": 2},
     {"question": "Ethics committee approval means you have also satisfied the Data Privacy Act.",
      "choices": ["True", "False -- they are separate requirements",
                  "True, if the study is educational", "Only for minors"], "correct": 1}],
)


# ===========================================================================
L(
    "Writing a Literature Review That Actually Supports Your Study",
    """## What you will be able to do

Search systematically, organise sources thematically rather than one-by-one, synthesise rather than summarise, and end the chapter with a gap statement that makes your study inevitable.

## What a literature review is for

<div class="callout callout-key" markdown="1">
<span class="callout-label">Three jobs, in order</span>

1. **Establish what is known**, so your reader understands the field
2. **Identify the gap** -- what is not yet known, or is contested
3. **Justify your study** as the thing that addresses it

A review that does 1 and stops is an annotated bibliography, not a review.
</div>

## The failure mode

<div class="callout callout-warn" markdown="1">
<span class="callout-label">What "study-by-study" looks like</span>
> *Santos (2021) studied social media and achievement among 200 students and found a negative relationship. Reyes (2022) studied social media and achievement among 150 students and found a negative relationship. Cruz (2023) studied social media and achievement and found no relationship.*

Each paragraph is one study. Nothing connects them, nothing is compared, and the disagreement between Cruz and the others is never addressed -- even though **that disagreement is the most interesting thing on the page.**
</div>

**The synthesised version:**

> *Most studies report a negative association between social media use and achievement (Santos, 2021; Reyes, 2022), though effect sizes are modest and findings are not unanimous. Cruz (2023) found no relationship, a discrepancy that may reflect measurement: Santos and Reyes measured total screen time, while Cruz distinguished academic from non-academic use. This suggests the relationship may depend on the type of use rather than the amount -- a distinction the present study adopts.*

Same three sources. Now they are in conversation, the disagreement is explained, and the explanation becomes your study's rationale.

## Searching systematically

### Where to search

| Source | Access | Note |
|---|---|---|
| **Google Scholar** | Free | Broadest; use "Cited by" to trace forward |
| **ERIC** | Free | Education research |
| **PubMed** | Free | Health and medicine |
| **DOAJ** | Free | Directory of Open Access Journals |
| **Semantic Scholar** | Free | Good AI-assisted related-paper suggestions |
| **HERDIN** | Free | Philippine health research |
| **Philippine E-Journals** | Institutional | Local studies, essential for a local gap claim |
| **Your university library** | Institutional | JSTOR, EBSCO, ProQuest |

### Building the search string

```
("social media" OR "social networking")
AND ("academic performance" OR "academic achievement" OR "GPA")
AND (student* OR adolescent*)
AND (Philippines OR Filipino)
```

- **Quotation marks** keep phrases together
- **OR** captures synonyms -- essential, because authors name things differently
- **AND** narrows
- **Asterisk** truncates: `student*` catches student, students, students'

### Recording the search

Keep a table. Panels ask, and systematic reviews require it.

| Database | Search string | Date | Hits | Screened | Included |
|---|---|---|---:|---:|---:|
| Google Scholar | as above | 2026-08-14 | 412 | 38 | 12 |
| ERIC | as above | 2026-08-14 | 87 | 15 | 6 |

### Inclusion and exclusion criteria

State them before screening:

- **Years.** Usually the last 5-10, unless a classic is foundational
- **Language.** English and Filipino
- **Type.** Peer-reviewed articles, theses, official reports
- **Population.** Age range, education level
- **Excluded.** Opinion pieces, blogs, predatory journals

## Organising thematically

<div class="callout callout-key" markdown="1">
<span class="callout-label">Organise by IDEA, never by author</span>
Each section is a **theme**. Within a theme, sources are compared.

```
2.1 Social media use among adolescents
    2.1.1 Prevalence and patterns
    2.1.2 Measurement approaches and their problems

2.2 Social media and academic outcomes
    2.2.1 Studies reporting negative associations
    2.2.2 Studies reporting null or mixed findings
    2.2.3 Why they disagree: measurement and context

2.3 Mechanisms proposed
    2.3.1 Displacement of study time
    2.3.2 Sleep disruption
    2.3.3 Attention fragmentation

2.4 The Philippine context
    2.4.1 Local studies
    2.4.2 What has not been examined

2.5 Synthesis and research gap
```

The structure itself argues. By 2.5 the gap should feel obvious.
</div>

## The synthesis matrix

The tool that makes synthesis possible. Build it as you read.

| Study | Sample | Design | IV measure | Outcome | Finding | Limitation |
|---|---|---|---|---|---|---|
| Santos (2021) | 200 college, Manila | Cross-sectional | Total hours, self-report | GPA | *r* = &minus;.32 | Self-report; private school |
| Reyes (2022) | 150 SHS, Cebu | Cross-sectional | Total hours, self-report | GWA | *r* = &minus;.28 | Single school |
| Cruz (2023) | 320 SHS, Davao | Cross-sectional | **Academic vs non-academic** | GWA | ns overall; &minus;.24 for non-academic | Cross-sectional |

<div class="callout callout-key" markdown="1">
<span class="callout-label">The matrix does the work</span>
Read down the **IV measure** column and Cruz's difference jumps out. Read down **Limitation** and "cross-sectional" repeats -- there is a methodological gap.

**Patterns appear in columns, not in paragraphs.** This is why the matrix comes before the writing.
</div>

## Writing the gap statement

Three sentences, at the end of the chapter.

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template</span>
**Sentence 1 -- what is established.**
> Research consistently reports a modest negative association between non-academic social media use and academic achievement among adolescents.

**Sentence 2 -- what is missing.**
> However, most studies have measured total screen time rather than distinguishing academic from non-academic use, and all have been conducted in urban private-school settings.

**Sentence 3 -- what this study does.**
> The present study addresses both gaps by distinguishing type of use and by sampling from a rural public senior high school.
</div>

## Citing sources

Philippine institutions normally use APA 7th.

```
In-text, one author         (Santos, 2021)
Two authors                 (Santos & Reyes, 2022)
Three or more               (Cruz et al., 2023)
Narrative                   Santos (2021) found that...
Direct quotation            (Santos, 2021, p. 45)
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Plagiarism, including the accidental kind</span>
- **Paraphrasing too closely.** Changing a few words is still plagiarism. Close the source, write from your notes, then check.
- **Citing a source you did not read.** If you found Santos cited in Reyes, either read Santos or write "(Santos, 2021, as cited in Reyes, 2022)."
- **Self-plagiarism.** Reusing your own earlier text without citing it.
- **Over-quoting.** A review should be overwhelmingly your own synthesis.
</div>

Use a reference manager -- **Zotero** and **Mendeley** are both free -- from the first paper. Retyping references is where errors and omissions come from.

## Doing it in practice

**Zotero** (zotero.org), free and open source:
1. Install the desktop app and the browser connector
2. Click the connector icon on any article page to save it with its metadata and PDF
3. Organise by theme in collections
4. In Word or LibreOffice, use the Zotero tab to insert citations
5. Generate the reference list in one click, in APA 7th

Fixing citation style later takes seconds instead of a weekend.

## Common mistakes

- **Study-by-study summaries** with no synthesis.
- **No gap statement.**
- **Sources that do not connect to your variables.**
- **Only old sources**, or only very recent ones with no foundational work.
- **No local literature**, which weakens any claim to a Philippine gap.
- **Ignoring studies that contradict you.** Address them -- they are your most interesting material.
- **Citing from abstracts** without reading the paper.

## Practice

**1.** Turn these into a synthesised paragraph: Study A (n=200) found a negative relationship; Study B (n=150) found a negative relationship; Study C (n=320) found no relationship but measured the IV differently.

<details markdown="1">
<summary>Show the worked answer</summary>

> Two studies report a negative association between social media use and academic achievement among adolescents (Study A, *n* = 200; Study B, *n* = 150). Study C (*n* = 320), however, found no overall relationship. The discrepancy appears to be methodological rather than substantive: A and B measured **total** daily screen time, while C distinguished **academic** from **non-academic** use and found a negative association only for the latter. This pattern suggests that the type of use, rather than the total amount, drives the relationship — a distinction the present study adopts.

**What makes this synthesis rather than summary:**

1. **Grouped by finding**, not listed by author
2. **The disagreement is named** and then **explained** rather than ignored
3. **The explanation is specific** — a measurement difference, not vague "methodological variation"
4. **It ends by connecting to the present study**

**What was deliberately left out:** each study's full methods, exact statistics, and authors' conclusions. A review is not a set of abstracts. Detail belongs in the synthesis matrix, and only what advances the argument goes in the prose.

**The give-away of good synthesis:** you could not restore the original three paragraphs from this one. The sources have been genuinely combined.
</details>

**2.** Your search returns 800 results. How do you get to a manageable set?

<details markdown="1">
<summary>Show the answer</summary>

**Screen in three passes, narrowing each time. Record the count at each stage.**

**Pass 1 — titles only (800 &rarr; ~100).** Fast. Exclude anything obviously off-topic. Takes an hour or two.

**Pass 2 — abstracts (100 &rarr; ~30).** Apply your stated inclusion criteria:
- Right population?
- Right variables?
- Empirical, not opinion?
- Within your year range?
- Peer-reviewed or a credible report?

**Pass 3 — full text (30 &rarr; ~15-20).** Read properly. Exclude those whose methods turn out not to fit. Build the synthesis matrix as you go.

**Then chase references in both directions:**
- **Backward:** check the reference lists of your best sources for papers you missed
- **Forward:** use Google Scholar's "Cited by" to find newer work that built on them

This nearly always surfaces key sources no keyword search found.

**Record it as a flow:**
```
Identified through database searching     800
Removed after title screening            -700
Screened by abstract                      100
Excluded by abstract                      -70
Full-text assessed                         30
Excluded after full text                  -12
Included in review                         18
```

That flow diagram is standard in systematic reviews and impressive in a thesis — it demonstrates the search was systematic rather than opportunistic.

**If 800 still feels unmanageable, your search is too broad.** Add a population term, a geographic term, or a narrower date range.
</details>

**3.** You find only two Philippine studies on your topic. Is that a problem?

<details markdown="1">
<summary>Show the answer</summary>

**No — it is very likely your gap, and it should be stated as one.**

**First, make sure the scarcity is real.** Check the sources that do not appear in Google Scholar:

- **Philippine E-Journals** (ejournals.ph)
- **HERDIN** for health topics
- **University repositories** — many Philippine theses are not indexed anywhere else
- **CHED and DepEd research portals**
- **Conference proceedings** of Philippine professional associations
- Search in **Filipino** as well as English

Local work is systematically under-indexed, and a second search often doubles what you find.

**If it really is only two:**

1. **Say so explicitly.** *"Only two studies have examined this relationship in the Philippine context (Santos, 2021; Cruz, 2023), both conducted in urban private schools."*

2. **Use international literature for the theoretical base** and local literature for the contextual argument. That division is normal and expected.

3. **Argue why context matters.** Device access, household study conditions, class sizes and curriculum differ from the settings where most research was done. If context plausibly changes the finding, testing it locally is a genuine contribution.

4. **Do not manufacture depth.** Padding with loosely related sources is visible and weakens the chapter.

**How to write it:**

> While the relationship has been examined extensively in Western contexts, only two Philippine studies were located, both in urban private schools. Given documented differences in device access and household study conditions between urban private and rural public settings, the generalisability of existing findings to the present population is unestablished. This study addresses that gap.

**Scarcity of local literature is the argument, not an obstacle to it.**
</details>

## Before you move on

- [ ] My review is organised by theme, not by author
- [ ] I have a synthesis matrix covering every included source
- [ ] I address studies that disagree with each other
- [ ] I have a three-sentence gap statement
- [ ] I have searched Philippine sources specifically
- [ ] I am using a reference manager
- [ ] Every citation in the text appears in the reference list, and vice versa

Next: turning the literature into a diagram of your own study.""",
    [{"question": "A literature review organised study-by-study rather than thematically is really:",
      "choices": ["A synthesis", "An annotated bibliography", "A meta-analysis", "A conceptual framework"], "correct": 1},
     {"question": "You find a study that contradicts your expected finding. You should:",
      "choices": ["Omit it", "Include and address it, explaining the discrepancy",
                  "Cite it without comment", "Only cite it if it is recent"], "correct": 1}],
)


# ===========================================================================
L(
    "Building Your Conceptual Framework",
    """## What you will be able to do

Distinguish a theoretical framework from a conceptual one, draw a framework that matches your actual analysis, and defend every arrow in it.

## The two frameworks

<div class="callout callout-key" markdown="1">
<span class="callout-label">They are not the same thing</span>

| | **Theoretical** framework | **Conceptual** framework |
|---|---|---|
| Comes from | Existing, named theory | Your synthesis of the literature |
| Scope | General, applies broadly | Specific to **your** study |
| Contains | Constructs from the theory | **Your** variables |
| Example | Self-Determination Theory | Your diagram: motivation &rarr; engagement &rarr; achievement |

Many Philippine thesis formats require **both**. The theoretical framework names the lens; the conceptual framework shows your study through it.
</div>

## Why panels focus on it

The framework is a **picture of your Chapter 4**. Every box should be a measured variable; every arrow should be a test you will run.

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The question that exposes a decorative framework</span>
*"Which analysis tests this arrow?"*

If you cannot name one, the arrow does not belong. A framework containing boxes you never measured, or arrows you never test, tells a panel the diagram was drawn to satisfy a template.
</div>

## The common Philippine formats

### IPO -- Input, Process, Output

```
   INPUT                 PROCESS                OUTPUT
+-------------+      +--------------+      +--------------+
| Profile:    |      | Administer   |      | Level of     |
|  - sex      | ---> | questionnaire| ---> | achievement  |
|  - strand   |      | Analyse data |      |              |
| Social media|      |              |      | Relationship |
|  usage      |      |              |      | between      |
+-------------+      +--------------+      | variables    |
                                           +--------------+
```

Widely used and widely criticised. Its weakness: **Process** is usually just "what I did," which is method, not concept. If your manual requires IPO, use it -- but make sure Input and Output are genuine variables.

### IV-DV diagram -- usually clearer

```
    INDEPENDENT                          DEPENDENT

  +------------------+                +---------------+
  | Non-academic     |  ------------> |  Academic     |
  | social media use |                |  achievement  |
  +------------------+                +---------------+
           |                                  ^
           |          +-------------+         |
           +--------> | Sleep hours | --------+
                      +-------------+
                        (mediator)

  Moderator:  Sex  ---------+
                            |
                            v
                      (on the IV -> DV path)
```

Each element has a name that matches a statistical role:

| Role | Meaning | Tested by |
|---|---|---|
| **Independent** | Predictor | Regression coefficient |
| **Dependent** | Outcome | -- |
| **Mediator** | Explains *how* | Indirect effect (a&times;b) |
| **Moderator** | Changes *when/for whom* | Interaction term |
| **Covariate** | Controlled for | Included in the model |

## Building it in five steps

<div class="callout callout-case" markdown="1">
<span class="callout-label">Worked example</span>

**Step 1 -- list every variable you will measure.**
```
sex, strand, age                     (demographics)
non-academic social media hours      (IV)
sleep hours                          (possible mediator)
general weighted average             (DV)
```

**Step 2 -- assign each a role.** Demographics are covariates unless a hypothesis names them. Here, sex is hypothesised as a moderator, so it gets an arrow.

**Step 3 -- draw only arrows you can test.**
```
social media  ->  GWA           tested by regression
social media  ->  sleep  -> GWA tested by mediation
sex x social media -> GWA       tested by interaction
```

**Step 4 -- check each arrow against your Statement of the Problem.** Every arrow must correspond to a numbered problem, and every numbered relational problem must appear as an arrow.

**Step 5 -- justify each arrow from the literature.** One sentence and one citation per arrow, in the text beneath the diagram.
</div>

## Defending the diagram

Prepare an answer for each:

| Question | Your answer names |
|---|---|
| Why is this variable independent? | The theory and the temporal order |
| What theory supports this arrow? | The named theory and a citation |
| Which analysis tests this arrow? | The specific test |
| Why is this a mediator and not a moderator? | Mediation = mechanism; moderation = condition |
| Why is this variable a covariate? | It affects the DV and you must control it |
| Can you claim these arrows are causal? | **Only with random assignment** |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Arrows are not causal claims by default</span>
In a cross-sectional design, an arrow means *"is hypothesised to predict"* -- not *"causes."*

Say so explicitly under the diagram: *"Arrows indicate hypothesised predictive relationships; the cross-sectional design does not permit causal inference."* That one sentence pre-empts the most common framework question.
</div>

## Mediator or moderator?

The distinction panels probe most.

<div class="callout callout-key" markdown="1">
<span class="callout-label">One sentence each</span>

- **Mediator** -- answers **how**. X affects M, which affects Y. *"Social media reduces sleep, and less sleep lowers achievement."* The mediator must occur **after** X.
- **Moderator** -- answers **when** or **for whom**. The X-Y relationship differs by level of W. *"Social media affects achievement more for boys than for girls."* The moderator usually **pre-exists**.

Mediation is a chain. Moderation is a switch.
</div>

## The theoretical framework

Name a real theory and use it consistently.

| Theory | Useful for |
|---|---|
| **Self-Determination Theory** (Deci & Ryan) | Motivation, autonomy |
| **Social Cognitive Theory** (Bandura) | Self-efficacy, modelling |
| **Technology Acceptance Model** (Davis) | Technology adoption |
| **Theory of Planned Behaviour** (Ajzen) | Intention and behaviour |
| **Constructivism** (Piaget, Vygotsky) | Learning and instruction |
| **Uses and Gratifications** | Media use motives |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Do not name a theory you never use again</span>
If Chapter 2 names Self-Determination Theory and the word "autonomy" never appears again, the panel will notice. A theory should shape your variables, your instrument and your discussion -- or it should not be there.
</div>

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- conceptual framework text</span>
Figure *1* presents the conceptual framework of the study. Drawing on *Uses and Gratifications Theory*, the framework posits that *non-academic social media use* is negatively associated with *academic achievement* (Santos, 2021; Reyes, 2022). This relationship is hypothesised to operate partly through *sleep duration*, as displaced sleep has been linked to reduced academic performance (Cruz, 2023). *Sex* is included as a moderator, following evidence that usage patterns differ between male and female adolescents (Dela Cruz, 2022). *Strand* and *age* are treated as covariates. Arrows indicate hypothesised predictive relationships; the cross-sectional design does not permit causal inference.
</div>

Every arrow has a citation. Every citation is doing work.

## Common mistakes

- **A framework that does not match the analysis.** Boxes never measured; arrows never tested.
- **A theoretical framework named once and abandoned.**
- **Confusing mediator and moderator.**
- **Arrows presented as causal** in a correlational design.
- **Using IPO where Process is just "I gave a questionnaire."**
- **Demographics drawn as if hypothesised** when they are only controls.
- **No figure number, no caption**, not referenced in the text.

## Practice

**1.** Your framework has an arrow from "Teacher Competence" to "Student Achievement," but you never measured teacher competence. What do you do?

<details markdown="1">
<summary>Show the answer</summary>

**Remove the arrow and the box. You cannot test what you did not measure.**

A framework is a picture of your analysis. An unmeasured box is a claim your study cannot support, and the first panel question — *"which analysis tests this arrow?"* — has no answer.

**Three legitimate alternatives:**

1. **Measure it.** If teacher competence is genuinely central, add an instrument. This changes your scope and timeline, so decide early.

2. **Move it to the discussion.** Remove it from the framework, then in Chapter 5 note that teacher competence is a plausible unmeasured influence and recommend it for future study. This is honest and often the right answer.

3. **Reframe it as a constant, not a variable.** If all respondents had the same teacher, competence does not vary and cannot explain differences between students. Say so in your delimitations — it is actually a design strength, since it removes a confound.

**What not to do:** leave it in because it "makes the framework look more complete." Frameworks are not decorated; they are specifications.

**A useful test before finalising any framework:** write the analysis beside each arrow. If any arrow has a blank, it comes out.
</details>

**2.** A panel asks: "Is sleep a mediator or a moderator in your framework?" How do you decide?

<details markdown="1">
<summary>Show the answer</summary>

**Ask which question sleep answers: *how* or *for whom*.**

**Mediator** if your claim is:
> *Social media use reduces sleep, and reduced sleep lowers achievement.*

Sleep is the **mechanism** — the path through which the effect travels. Sleep must occur **after** social media use in time, and it must be affected by it.

```
social media  ->  sleep  ->  achievement
```
Tested by: an indirect effect (a&times;b), with a bootstrapped confidence interval.

**Moderator** if your claim is:
> *Social media use harms achievement more for students who sleep less.*

Sleep is a **condition** that changes the strength of the relationship. It pre-exists and is not itself caused by social media use.

```
social media  ->  achievement
        (sleep changes the strength of this path)
```
Tested by: an interaction term, followed by simple slopes.

**Which is right here?** Mediation is more defensible theoretically, because social media use plausibly *causes* less sleep. Moderation would require arguing that sleep is a stable pre-existing characteristic, which is harder.

**The honest caveat to add:** *"Because all three variables were measured at the same time point, the temporal ordering required for mediation cannot be established from these data. The mediation model is therefore tested as a statistical model, not as evidence of a causal mechanism."*

Saying that before the panel does is the strongest possible answer.
</details>

**3.** Why do panels ask "which analysis tests this arrow?"

<details markdown="1">
<summary>Show the answer</summary>

**Because it is the fastest way to find out whether the framework describes your study or decorates it.**

The question checks four things at once:

1. **Did you measure everything in the diagram?** An unmeasured box has no analysis.
2. **Do you understand the statistical roles?** If you drew a mediator but plan a simple correlation, you do not yet know what mediation requires.
3. **Does the framework match the Statement of the Problem?** Both should describe the same set of relationships.
4. **Did you build the study, or fill in a template?** Frameworks copied from another thesis usually contain arrows the student cannot account for.

**How to be ready:** build a table and keep it in your appendix.

| Arrow | Hypothesis | Analysis | Where reported |
|---|---|---|---|
| Social media &rarr; GWA | H1 | Pearson *r*, then regression | Table 5 |
| Social media &rarr; sleep &rarr; GWA | H2 | Mediation, bootstrapped CI | Table 7 |
| Sex &times; social media &rarr; GWA | H3 | Moderated regression, simple slopes | Table 8 |
| Strand, age | -- | Covariates in the regression | Table 6 |

Hand that table over when asked, and the question is answered completely in one move.

**The deeper point:** if you can build this table, your framework, your Statement of the Problem and your Chapter 4 are all consistent — which is most of what a methods defence is checking.
</details>

## Before you move on

- [ ] I can distinguish theoretical from conceptual framework
- [ ] Every box in my diagram is a variable I will measure
- [ ] Every arrow corresponds to an analysis I will run
- [ ] I can name the theory behind each arrow, with a citation
- [ ] I know which variables are mediators, moderators and covariates, and why
- [ ] I have stated that arrows are predictive, not causal, if my design is correlational
- [ ] My framework matches my Statement of the Problem exactly

Next: how long all of this actually takes.""",
    [{"question": "A variable that explains HOW X affects Y is a:",
      "choices": ["Moderator", "Mediator", "Covariate", "Confounder"], "correct": 1},
     {"question": "Your framework contains a box for a variable you did not measure. You should:",
      "choices": ["Leave it for completeness", "Remove it, or measure it",
                  "Mark it with a dashed line", "Mention it only in the abstract"], "correct": 1}],
)


# ===========================================================================
L(
    "From Proposal to Final Defense: A Realistic Timeline",
    """## What you will be able to do

Build a timeline that survives contact with reality, identify the three steps that actually cause delays, and know what each defence is testing.

## The timeline students plan versus the one that happens

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Where the time actually goes</span>
Students budget generously for writing and almost nothing for **waiting**. The three biggest delays are all approvals:

- **Ethics review**: 3-6 weeks, longer if revisions are required
- **Division office / agency permission**: 2-4 weeks
- **Adviser feedback**: 1-2 weeks **per submission**, and there will be several

That is potentially **two to three months of waiting** before a single questionnaire is distributed.
</div>

## A realistic two-semester schedule

| Phase | Weeks | Output |
|---|---:|---|
| Topic selection and reading | 1-3 | Topic approved by adviser |
| Literature search and synthesis matrix | 3-7 | Chapter 2 draft |
| Chapters 1-3 drafting | 6-10 | Full proposal draft |
| Adviser revisions | 10-12 | Proposal ready |
| **Proposal defence** | 13 | Approval with revisions |
| Revisions from panel | 14-15 | Revised proposal |
| **Ethics submission** | 15 | Submitted |
| *Waiting for ethics* | 15-20 | -- |
| Agency / division permission | 18-21 | Permission letters |
| Instrument pilot and revision | 20-22 | Final instrument |
| **Data collection** | 22-28 | Raw data |
| Encoding and cleaning | 28-30 | Clean dataset |
| Analysis | 30-32 | Results |
| Chapters 4-5 drafting | 32-36 | Full draft |
| Adviser revisions | 36-38 | Ready |
| **Final defence** | 39 | Approval with revisions |
| Revisions and binding | 40-42 | Submitted |

<div class="callout callout-key" markdown="1">
<span class="callout-label">Work the approvals in parallel</span>
Ethics review and division permission can often run **at the same time**, and both can be prepared while you await proposal revisions.

The single largest timeline saving available to most students is preparing the ethics application **before** the proposal defence, so it is ready to submit the day revisions are approved.
</div>

## Instrument development

If you build your own instrument rather than adopting a validated one, budget for this properly.

| Step | What it involves |
|---|---|
| 1. Draft items from the literature and framework | Each item maps to a variable |
| 2. **Content validation** | 3-5 experts rate each item for relevance |
| 3. Revise | Based on expert comments |
| 4. **Pilot test** | 20-30 respondents *similar to but not in* your sample |
| 5. **Reliability analysis** | Cronbach's alpha per subscale |
| 6. Revise or drop weak items | Then finalise |

### Content validity index

Experts rate each item 1-4 for relevance. The item-level CVI is the proportion rating it 3 or 4.

```
5 experts, 4 rate item as relevant:  I-CVI = 4/5 = 0.80
```

**I-CVI &ge; 0.78** with 3-5 experts is the usual acceptance threshold. Scale-level CVI (the average) should be **&ge; 0.90**.

### Reliability, computed by hand

<div class="formula" markdown="1">
**&alpha; = [k/(k&minus;1)] &times; [1 &minus; (&Sigma;s&sup2;<sub>item</sub> / s&sup2;<sub>total</sub>)]**
</div>

<div class="callout callout-case" markdown="1">
<span class="callout-label">Worked example -- 5 items, 10 pilot respondents</span>

```
Item variances:  0.9889, 1.1556, 1.1667, 0.6222, 0.9333
Sum of item variances    =  4.8667
Variance of total scores = 19.7333

alpha = (5/4) x (1 - 4.8667/19.7333)
      = 1.25 x (1 - 0.2466)
      = 1.25 x 0.7534
      = 0.9417
```

**&alpha; = .94** -- excellent internal consistency.

Note the caution from Intermediate Statistics: check the **mean inter-item correlation** too. Very high alpha on a short scale can indicate redundant items.
</div>

| Alpha | Verdict |
|---|---|
| &ge; .90 | Excellent |
| .80-.89 | Good |
| .70-.79 | Acceptable |
| .60-.69 | Questionable |
| &lt; .60 | Poor -- revise |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Pilot respondents are not study respondents</span>
Pilot participants must be **similar to** your sample but **not in** it. Using them twice contaminates your data -- they have seen the instrument, and practice effects are real.

Draw the pilot from a parallel section, a neighbouring school, or the year above.
</div>

## The two defences

### Proposal defence -- "should this study be done?"

Tests: the problem, the literature, the design, the instrument, the sampling, the ethics plan.

Typical questions:
- What is your research gap?
- Why this design?
- How did you arrive at your sample size?
- What are your variables and how are they measured?
- Is your instrument valid and reliable?
- What are your ethical considerations?

### Final defence -- "was it done well, and what does it mean?"

Tests: execution, analysis, interpretation, limitations.

Typical questions:
- Why this statistical test?
- Did you check assumptions?
- What does this p-value mean?
- Is the effect practically important?
- Can you claim causation?
- What are your limitations?
- What are the implications?

<div class="callout callout-key" markdown="1">
<span class="callout-label">What a panel is really assessing</span>
Not whether you are a statistician. Whether **you understand your own study** -- every choice, and why you made it.

The answer that always fails is *"that is what my adviser said"* or *"that is what the software gave."*
</div>

## Managing revisions

- **Write down every comment** during the defence, or have someone do it. You will not remember them.
- **Build a revision matrix**: comment, panel member, action taken, page number. Most institutions require one.
- **Address every comment**, even to explain why you disagree -- with a reason.
- **Ask for clarification during the defence**, not afterwards.

| Comment | Panel member | Action taken | Page |
|---|---|---|---|
| Sample size justification unclear | Dr. Reyes | Added G*Power output and Slovin computation | 42 |
| Causal language in conclusion | Dr. Santos | Changed "improved" to "was associated with" throughout Ch. 5 | 88-91 |

## Common mistakes

- **No time budgeted for approvals.** The single most common cause of a missed deadline.
- **Starting data collection before ethics approval.** Usually unrecoverable.
- **Skipping the pilot test.** You discover the instrument's problems in your real data.
- **Piloting on your actual sample.**
- **Submitting to the adviser and assuming a fast turnaround.**
- **No revision matrix**, then forgetting half the comments.

## Practice

**1.** You have 16 weeks until your final defence and have not started data collection. Is it feasible?

<details markdown="1">
<summary>Show the worked answer</summary>

**It depends entirely on one question: do you already have ethics approval?**

**If you have approval and permissions in hand:**
```
Weeks 1-2    Finalise and pilot the instrument
Weeks 3-8    Data collection (6 weeks)
Weeks 9-10   Encoding and cleaning
Weeks 11-12  Analysis
Weeks 13-15  Write Chapters 4-5, adviser revisions
Week 16      Defence
```
**Tight but feasible**, with no slack for problems. Any delay in collection consumes the writing time.

**If you do NOT have approval:**
```
Weeks 1-5    Ethics review (optimistic)
Weeks 4-7    Division permission (parallel)
Weeks 8-12   Data collection (compressed)
Weeks 13-14  Encoding, cleaning, analysis
Weeks 15-16  Write two chapters and defend
```
**Not realistically feasible.** Any ethics revision request ends it.

**What to do instead of hoping:**

1. **Talk to your adviser now.** Deferring one term is far better than defending an unfinished study.
2. **Reduce scope.** Fewer respondents, one school instead of three, one outcome instead of four. A smaller completed study beats a larger abandoned one.
3. **Submit the ethics application this week**, whatever state the proposal is in — it is the longest pole.
4. **Consider secondary data.** If suitable data already exists (PSA microdata, school records with permission), you skip collection entirely.

**The honest calculation:** the binding constraint is almost never your writing speed. It is the approvals queue, which you do not control.
</details>

**2.** Your pilot gives Cronbach's alpha of .58 for one subscale. What do you do?

<details markdown="1">
<summary>Show the worked answer</summary>

**.58 is below the .60 threshold — the subscale is not yet reliable and must be revised before the main study.**

**Step 1 — look at "alpha if item deleted."** Every package reports this. If removing one item raises alpha substantially — say from .58 to .74 — that item is not measuring the same construct.

**Step 2 — examine the offending items.** Common causes:
- **Reverse-scored items not recoded.** The single most frequent cause, and it is a five-second fix. Check this first.
- **Double-barrelled items** asking two things at once
- **Ambiguous wording** that different respondents read differently
- **An item that belongs to a different construct**

**Step 3 — check the item-total correlations.** Anything below .30 is a candidate for removal.

**Step 4 — act:**

| Finding | Action |
|---|---|
| Reverse items not recoded | Recode, recompute — often fixes it entirely |
| One bad item | Remove it, recompute |
| Several weak items | Rewrite them and pilot again |
| Subscale has only 3 items | Add items — alpha rises with length |
| Items measure different things | The subscale is not unidimensional; reconsider the construct |

**Step 5 — re-pilot if you made substantive changes.** A revised instrument needs fresh evidence.

**What not to do:** proceed with .58 and report it. A panel will ask, and unreliable measurement attenuates every correlation you compute — you will under-detect real relationships in your main study.

**If you genuinely cannot fix it:** consider dropping that subscale from the study and saying so in your delimitations. A study with three reliable subscales is stronger than one with four where one is unreliable.
</details>

**3.** A panel member makes a comment you think is wrong. What do you do?

<details markdown="1">
<summary>Show the answer</summary>

**Engage with it respectfully, during the defence, and document your response in the revision matrix either way.**

**During the defence:**

1. **Clarify first.** *"May I make sure I understand — are you suggesting that...?"* A surprising number of disagreements turn out to be misunderstandings.

2. **Acknowledge the concern before responding.** *"That is a fair point about the sampling."*

3. **Respond with evidence, not assertion.** *"I used Slovin's formula at a 5% margin of error, which gave 343, and I collected 380. May I show the computation?"*

4. **Concede where they are right.** Defending an indefensible point is how a defence goes badly. *"You are right, I cannot rule that out."*

5. **If you still disagree**, say so once, with your reason, and then accept their direction. *"My understanding is that oblique rotation is recommended when factors correlate, but I will review the source you mentioned and adjust if needed."*

**After the defence, in the revision matrix:**

| Comment | Action taken | Page |
|---|---|---|
| Use Varimax rather than Oblimin | Reviewed Costello & Osborne (2005); retained Oblimin as factors correlated at *r* = .42, and added justification | 51 |

**Documenting a disagreement with a reason is acceptable.** Silently ignoring a comment is not — and it is exactly what gets caught at the next submission.

**The judgement call:** distinguish comments that are **matters of standard** (where the panel member may simply be working from older guidance) from those that are **matters of authority** (formatting, institutional requirements). On the second kind, comply without argument. On the first, cite your source and let the evidence carry it.
</details>

## Before you move on

- [ ] My timeline includes realistic waiting time for ethics and permissions
- [ ] I am preparing the ethics application before the proposal defence
- [ ] I have budgeted for content validation and a pilot test
- [ ] My pilot respondents are not in my study sample
- [ ] I know what each defence is testing
- [ ] I have a revision matrix template ready

Next: the sampling designs the national curriculum treats as a full course.""",
    [{"question": "Pilot test respondents should be:",
      "choices": ["Drawn from your actual sample", "Similar to but not included in your sample",
                  "Experts in the field", "As few as possible"], "correct": 1},
     {"question": "Cronbach's alpha of .58 for a subscale means you should:",
      "choices": ["Proceed and note it as a limitation", "Revise the subscale before the main study",
                  "Add more respondents", "Use a different statistical test"], "correct": 1}],
)


# ===========================================================================
L(
    "Sampling Designs: From Simple Random to Multistage",
    """## What you will be able to do

Construct, implement and evaluate each of the probability sampling designs CMO 42 treats as a full three-unit course, and compute the estimators that go with them.

## The designs, and what each costs you

| Design | Precision | Field cost | Needs a full frame? |
|---|---|---|---|
| Simple random | Baseline | High | **Yes** |
| Systematic | &asymp; SRS | Low | Yes, ordered |
| Stratified | **Better** than SRS | Medium | Yes, plus stratum membership |
| Cluster | **Worse** than SRS | **Low** | Only of clusters |
| Multistage | Worse than SRS | Lowest | Only stage by stage |
| PPS | Good | Medium | Cluster sizes needed |

<div class="callout callout-key" markdown="1">
<span class="callout-label">The central trade-off</span>
**Stratification improves precision. Clustering reduces cost but damages precision.**

Stratifying makes each group internally homogeneous and you sample within every one -- so you never miss a group. Clustering makes you sample only some groups, and members of a cluster resemble one another, so each adds less information.

Most real national surveys use **both**: stratify by region, then cluster within.
</div>

## Simple random sampling

Every possible sample of size n has an equal chance of selection.

**Estimator of the mean:**
<div class="formula" markdown="1">
**x&#772; = &Sigma;x<sub>i</sub> / n** &nbsp;&nbsp;&nbsp; **SE(x&#772;) = &radic;[ (1 &minus; n/N) &times; s&sup2;/n ]**
<span class="formula-note">the (1 &minus; n/N) term is the finite population correction</span>
</div>

```
N = 2400, n = 343, s = 8.2

SE = sqrt( (1 - 343/2400) x 8.2^2 / 343 )
   = sqrt( (1 - 0.1429) x 67.24 / 343 )
   = sqrt( 0.8571 x 0.19604 )
   = sqrt( 0.16803 )
   = 0.410
```

The correction matters here: without it, SE would be 0.443 -- 8% larger. **Apply it whenever n/N exceeds about 5%.**

## Systematic sampling

**Procedure:**
1. Compute the interval **k = N/n**
2. Draw a random start **r** between 1 and k
3. Select elements r, r+k, r+2k, ...

```
N = 2400, n = 343  ->  k = 2400/343 = 6.997  ->  use k = 7
random start = 4
selected: 4, 11, 18, 25, 32, ...
```

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Periodicity is the danger</span>
If the list has a cycle matching k, the sample is biased. A class list ordered by rank where every 7th student is a section leader; a daily sales record where k = 7 always lands on Monday.

**Check the ordering before choosing k.** If the list is ordered by something related to your outcome -- say, by grade -- systematic sampling actually becomes an *implicit stratification* and can be **more** precise than SRS. Ordering matters in both directions.
</div>

## Stratified sampling

Divide the population into **homogeneous** strata, then sample within each.

### Allocation methods

| Method | Formula | Use when |
|---|---|---|
| **Proportional** | n&#8341; = n &times; N&#8341;/N | Default; strata have similar variability |
| **Equal** | n&#8341; = n/L | You need to compare strata directly |
| **Neyman (optimal)** | n&#8341; = n &times; (N&#8341;s&#8341;) / &Sigma;(N&#8341;s&#8341;) | Strata differ in variability, and you know s&#8341; |

**Neyman allocation** puts more sample where there is more variation -- which is where the extra precision is available.

### The stratified mean

<div class="formula" markdown="1">
**x&#772;<sub>st</sub> = &Sigma; W<sub>h</sub> x&#772;<sub>h</sub>** &nbsp;&nbsp; where W<sub>h</sub> = N<sub>h</sub>/N
</div>

<div class="callout callout-case" markdown="1">
<span class="callout-label">Worked example</span>

| Strand | N&#8341; | W&#8341; | x&#772;&#8341; | W&#8341;x&#772;&#8341; |
|---|---:|---:|---:|---:|
| STEM | 900 | .3750 | 84.0 | 31.500 |
| ABM | 700 | .2917 | 75.8 | 22.108 |
| HUMSS | 500 | .2083 | 73.5 | 15.312 |
| GAS | 300 | .1250 | 71.2 | 8.900 |
| **Total** | **2,400** | **1.0000** | | **77.820** |

**Stratified mean = 77.82**

Note this is **not** the simple average of the four means (76.13). Weighting by stratum size is what makes the estimate unbiased.
</div>

## Cluster sampling

Select whole groups; measure everyone within the selected groups.

**When to use it:** when no list of individuals exists but a list of clusters does. You can list all sections in a division far more easily than all students.

**The cost:** the design effect from lesson 3.

```
DEFF = 1 + (m - 1) x ICC
```

**Always report the design effect and use software that accounts for clustering.**

## Probability proportional to size (PPS)

Larger clusters get a proportionally larger chance of selection.

**Why it matters:** if you select clusters with equal probability and then take everyone, students in small sections are over-represented. PPS fixes this.

<div class="callout callout-case" markdown="1">
<span class="callout-label">PPS worked with cumulative totals</span>

| Section | Size | Cumulative | Range |
|---|---:|---:|---|
| A | 45 | 45 | 1-45 |
| B | 30 | 75 | 46-75 |
| C | 52 | 127 | 76-127 |
| D | 38 | 165 | 128-165 |
| E | 41 | 206 | 166-206 |

To select 2 sections from a total of 206 students:
```
k = 206/2 = 103
random start between 1 and 103, say 37

selections: 37   -> falls in 1-45    -> Section A
           140   -> falls in 128-165 -> Section D
```

Section C, the largest, has the greatest chance of selection because it occupies the widest range.
</div>

**Combined with taking a fixed number per selected cluster, PPS makes the design self-weighting** -- every student has the same overall probability of selection, so no weights are needed in analysis. That is why national surveys use it.

## Ratio and regression estimators

When you know an auxiliary variable for the whole population, you can use it to sharpen your estimate.

<div class="formula" markdown="1">
**Ratio estimator: &Ŷ;<sub>R</sub> = (y&#772;/x&#772;) &times; X**
<span class="formula-note">X = the known population total of the auxiliary variable</span>
</div>

<div class="callout callout-case" markdown="1">
<span class="callout-label">Worked example</span>
You want total expenditure. You know total household **income** for the population (from a census) and measured both in your sample.

```
sample mean expenditure  y-bar = 12,400
sample mean income       x-bar = 18,500
known population income  X     = 44,400,000

ratio estimate of total expenditure
  = (12,400 / 18,500) x 44,400,000
  = 0.6703 x 44,400,000
  = 29,760,000
```

This is more precise than simply scaling the sample mean, **provided expenditure and income are strongly correlated** -- which they are.
</div>

**Use a ratio estimator when** the relationship passes through the origin. **Use a regression estimator when** it does not.

## Multistage sampling

Sample in stages, narrowing each time.

```
Stage 1: select 5 divisions from 15          (PPS by enrolment)
Stage 2: select 4 schools per division       (PPS by enrolment)
Stage 3: select 2 sections per school        (simple random)
Stage 4: select 10 students per section      (simple random)

Total: 5 x 4 x 2 x 10 = 400 students
```

The design effect compounds across stages. A four-stage design can easily produce DEFF above 3, meaning 400 students carry the information of fewer than 140.

## Doing it in software

### R
```r
# simple random
sample(1:2400, 343)

# systematic
k <- floor(2400/343); start <- sample(1:k, 1)
seq(start, 2400, by = k)

# stratified, proportional
library(dplyr)
frame %>% group_by(strand) %>%
  slice_sample(prop = 343/2400)

# complex survey analysis, accounting for the design
library(survey)
des <- svydesign(id = ~section, strata = ~strand,
                 weights = ~wt, fpc = ~N_h, data = dat)
svymean(~score, des)         # correct SEs
svyby(~score, ~strand, des, svymean)
```

The `survey` package is the tool for any design more complex than SRS. Ordinary `mean()` and `t.test()` give the wrong standard errors for clustered or weighted data.

### SPSS
The **Complex Samples** add-on module handles stratification, clustering and weights. Without it, SPSS's standard procedures assume simple random sampling.

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template</span>
A *stratified random sampling* design was employed, with *strand* as the stratification variable. Proportional allocation was used, yielding *124*, *97*, *69* and *41* respondents from the *STEM*, *ABM*, *HUMSS* and *GAS* strands respectively. Within each stratum, respondents were selected by simple random sampling using a random number generator applied to the enrolment list. The finite population correction was applied in computing standard errors, as the sampling fraction exceeded *5%*.
</div>

## Common mistakes

- **Calling a convenience sample "random."**
- **Ignoring clustering** in the analysis.
- **Omitting the finite population correction** when n/N is large.
- **Systematic sampling on a periodically ordered list.**
- **Simple-averaging stratum means** instead of weighting by stratum size.
- **No weights** where selection probabilities differ.

## Practice

**1.** N = 5,000, n = 400, s = 12. Compute SE of the mean with and without the finite population correction.

<details markdown="1">
<summary>Show the worked answer</summary>

**Without the correction:**
```
SE = s / sqrt(n) = 12 / sqrt(400) = 12 / 20 = 0.600
```

**With the correction:**
```
sampling fraction = n/N = 400/5000 = 0.08

SE = sqrt( (1 - 0.08) x 12^2 / 400 )
   = sqrt( 0.92 x 144 / 400 )
   = sqrt( 0.92 x 0.36 )
   = sqrt( 0.3312 )
   = 0.575
```

**The correction reduces SE from 0.600 to 0.575 — about 4% narrower.**

**Why it exists:** if you sampled the *entire* population, there would be no sampling error at all. The correction (1 &minus; n/N) shrinks the standard error as your sample approaches the population. At n = N it becomes zero.

**When to apply it:** the usual rule is when the sampling fraction **exceeds 5%**. Here 8% clears that, so it should be applied.

**Practical effect on a confidence interval:**
```
without: 95% CI = x-bar +/- 1.96 x 0.600 = +/- 1.176
with   : 95% CI = x-bar +/- 1.96 x 0.575 = +/- 1.127
```
Modest here, but with a 40% sampling fraction the correction would cut SE by more than 20% — and omitting it would overstate your uncertainty substantially.
</details>

**2.** Why is the stratified mean 77.82 rather than the simple average of 76.13?

<details markdown="1">
<summary>Show the worked answer</summary>

**Because the four strata are different sizes, and the simple average treats them as equal.**

```
Simple average of the four means:
  (84.0 + 75.8 + 73.5 + 71.2) / 4 = 304.5 / 4 = 76.13

Weighted by stratum size:
  .3750(84.0) + .2917(75.8) + .2083(73.5) + .1250(71.2)
  = 31.500 + 22.108 + 15.312 + 8.900
  = 77.820
```

**Why the weighted version is higher:** STEM has both the highest mean (84.0) and the largest share of the population (37.5%). The simple average gives it the same weight as GAS, which has the lowest mean and only 12.5% of students.

**Which is correct:** the **weighted** one, 77.82. It estimates the mean of the *population*, where STEM students genuinely are more numerous. The unweighted average estimates the mean of the four stratum means, which is a different and usually uninteresting quantity.

**The general principle:** whenever selection probabilities differ across groups — by design or by differential response — estimates must be **weighted back** to the population structure. This is the same reason national surveys publish weighted results.

**Where students go wrong:** taking the sample mean of all respondents pooled together. That is correct **only** under proportional allocation with equal response rates. With disproportional allocation — which you would use if you oversampled a small stratum — the pooled mean is biased and weighting is mandatory.
</details>

**3.** Your sampling frame is the enrolment list, but 12% of enrolled students have stopped attending. What is the implication?

<details markdown="1">
<summary>Show the answer</summary>

**You have frame error: the sampling frame does not match the target population, and your conclusions apply to the frame, not to the population you intended.**

**What actually happens in the field:** you draw 343 names from the enrolment list. Roughly 41 of them (12%) cannot be found. You end up with about 302 respondents, and your realised sample is **all attending students** — a different population from "all enrolled students."

**Why this matters substantively:** the 12% who stopped attending are almost certainly not a random subset. They are more likely to be struggling academically, facing financial difficulty, or working. If your outcome is achievement, you have systematically excluded the low end of the distribution — and your estimated mean will be biased upward.

**What to do:**

1. **Define the target population to match reality.** If you can only reach attending students, say your population is *actively enrolled, attending* students. Then the frame is correct and there is no error.

2. **Document the discrepancy.** Report how many selected students could not be located and why.

3. **Compare what you can.** If the school has demographic data on non-attenders, test whether they differ from your respondents on sex, strand or prior grades. If they do not differ on observables, that is partial reassurance.

4. **State it as a limitation** if you cannot resolve it: *"Findings describe actively attending students; the 12% of enrolled students no longer attending were not reachable and may differ systematically on the outcome."*

**The design lesson:** check the frame's currency **before** drawing the sample. An enrolment list from June is a poor frame in March. Ask the registrar for a current attendance-verified list if one exists.
</details>

## Before you move on

- [ ] I can compute SE with the finite population correction
- [ ] I know when stratification helps and when clustering hurts
- [ ] I can allocate proportionally and compute a weighted stratified mean
- [ ] I understand why PPS makes a design self-weighting
- [ ] I know the design effect compounds across stages
- [ ] I check my sampling frame against my target population

Next: everything between having a design and having clean data.""",
    [{"question": "Compared with simple random sampling of the same size, cluster sampling is:",
      "choices": ["More precise and cheaper", "Less precise but cheaper",
                  "More precise but more expensive", "Identical in precision"], "correct": 1},
     {"question": "The stratified mean weights each stratum mean by:",
      "choices": ["Its sample size", "Its share of the population (N_h/N)",
                  "Its variance", "Equally"], "correct": 1}],
)


# ===========================================================================
L(
    "Survey Operations: From Questionnaire to Clean Data",
    """## What you will be able to do

Write questionnaire items that do not break, run a field operation that produces the sample you designed, and turn raw responses into an analysable dataset with a documented audit trail.

## Where studies actually fail

<div class="callout callout-key" markdown="1">
<span class="callout-label">Non-sampling error usually exceeds sampling error</span>
Sampling error shrinks predictably with sample size. **Non-sampling error does not shrink at all.**

- A badly worded item produces wrong data from 400 respondents just as reliably as from 40
- A 40% response rate with unknown non-respondents cannot be fixed by collecting more from the same group
- An encoding error propagates into every table

Most thesis data quality is lost here, not in the sampling.
</div>

## Writing items that work

### The seven item faults

| Fault | Broken | Fixed |
|---|---|---|
| **Double-barrelled** | "Are you satisfied with the speed and quality of service?" | Split into two items |
| **Leading** | "Don't you agree that the new policy is helpful?" | "How helpful is the new policy?" |
| **Ambiguous** | "Do you use social media often?" | "How many hours per day do you use social media?" |
| **Double negative** | "Do you disagree that students should not be required to...?" | Rewrite positively |
| **Assumes** | "How satisfied are you with your adviser?" | Add a filter: "Do you have an adviser?" |
| **Jargon** | "Rate your metacognitive regulation." | "How often do you check whether you understood what you read?" |
| **Non-exhaustive options** | Civil status: Single / Married | Add Widowed, Separated, Prefer not to say |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">The double-barrelled item, in detail</span>
*"Are you satisfied with the speed and quality of service?"*

A respondent who found service **fast but poor** cannot answer honestly. Whatever they choose, the data is wrong -- and **no analysis can repair it**, because the two constructs were never recorded separately.

Splitting costs one line in the instrument. Discovering it in your data costs the study.
</div>

### Response scales

| Scale | Points | Note |
|---|---|---|
| Agreement | 5 or 7 | Odd number allows a neutral midpoint |
| Frequency | 5 | Use concrete anchors: "Never / Rarely / Sometimes / Often / Always" |
| Forced choice | 4 or 6 | No midpoint; forces a direction |

**Label every point**, not just the ends. "1 = Strongly disagree ... 5 = Strongly agree" with 2, 3 and 4 unlabelled invites inconsistent interpretation.

**Balance reverse-scored items** through the instrument to detect careless responding -- and remember to recode them before computing any total.

## Pre-testing

<div class="callout callout-key" markdown="1">
<span class="callout-label">Two different activities</span>

**Cognitive pre-test (5-10 people).** Sit with respondents and ask them to think aloud as they answer. You are checking whether they understand each item the way you intended. This catches ambiguity that no statistic will.

**Pilot test (20-30 people).** Administer the full instrument under realistic conditions. You are checking timing, flow, completion rate and reliability.
</div>

Record from the pilot: how long it took, which items were skipped most, which produced no variance, and Cronbach's alpha per subscale.

## Field operations

### Before

- [ ] All permissions in hand
- [ ] Enumerators trained, with a written protocol
- [ ] Consent and assent forms printed in every language used
- [ ] Questionnaires numbered sequentially
- [ ] A tracking sheet listing every selected respondent
- [ ] A call-back rule agreed: how many attempts before a non-contact is recorded

### During

- **Standardise administration.** Same instructions, same conditions. If one section takes it during a free period and another during a class they resent missing, that difference is in your data.
- **Supervise.** Spot-check completed forms daily, not at the end.
- **Track non-response by reason**: refused, absent, could not be located, incomplete. The reasons matter more than the count.
- **Never substitute freely.** Replacing an absent selected student with whoever is available destroys the probability design. If you must substitute, use a pre-specified rule and document it.

### Non-response

| Type | Meaning | Handling |
|---|---|---|
| **Unit non-response** | Whole questionnaire not obtained | Report the rate; compare respondents with non-respondents on anything you know |
| **Item non-response** | Specific questions skipped | Report per-item missingness; consider imputation |

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Response rate is not the whole story</span>
A 40% response rate is not fatal **if you can characterise who is missing**. It is fatal if you cannot.

Compare respondents and non-respondents on whatever the frame gives you -- sex, strand, section, prior grades. If they do not differ on observables, that is partial reassurance. If they do, say so and interpret accordingly.
</div>

## Coding and encoding

### The codebook

Build it **before** encoding, not after.

| Variable | Label | Type | Values | Missing |
|---|---|---|---|---|
| `id` | Respondent ID | Nominal | 001-380 | -- |
| `sex` | Sex | Nominal | 1 = Male, 2 = Female | 9 |
| `strand` | Strand | Nominal | 1 = STEM, 2 = ABM, 3 = HUMSS, 4 = GAS | 9 |
| `sm_hours` | Non-academic social media, hrs/day | Ratio | 0-24 | 99 |
| `sat1` | Satisfaction item 1 | Ordinal | 1-5 | 9 |
| `sat1r` | Item 1, **reverse-scored** | Ordinal | 1-5 | 9 |
| `gwa` | General weighted average | Ratio | 60-100 | 999 |

<div class="callout callout-key" markdown="1">
<span class="callout-label">Missing-value codes must be impossible values</span>
Coding missing as **0** for an item scored 1-5 is fine. Coding missing as **0** for *number of absences* is a disaster -- zero absences is a real value, and the software cannot tell them apart.

Use 9, 99 or 999 depending on the variable's range, and **declare them as missing in the software** so they are excluded from calculations.
</div>

### Quality control at entry

1. **Double entry** for critical variables -- two people encode independently and the files are compared. The gold standard.
2. **Range checks.** An age of 150 or a GWA of 12 is caught at entry, not at analysis.
3. **Consistency checks.** A respondent who answered "no adviser" should have no adviser-satisfaction rating.
4. **Spot-check 10%** of encoded records against the paper forms.

### Cleaning

<div class="callout callout-warn" markdown="1">
<span class="callout-label">Never edit the raw file</span>
Keep `data_raw.csv` untouched. Do every correction in a **script** or a documented sequence, producing `data_clean.csv`.

Two reasons: you can always go back, and you can show exactly what was changed. "The data were cleaned" is not a method.
</div>

**Document every step:**

```
1. Recoded reverse items sat3, sat7, sat12  (6 - x)
2. Declared 9, 99, 999 as missing
3. Corrected 2 transcription errors verified against paper forms
   (ID 041 gwa 8.7 -> 87; ID 156 sm_hours 42 -> 4.2)
4. Excluded 5 cases with >20% item non-response on the primary scale
5. Final analysable n = 302
```

## Presenting findings back

CMO 42 lists presentation of research findings as a course outcome for a reason: a survey that never reports back to its respondents is poor practice.

- Offer a summary to the school or agency that hosted you
- Strip all identifiers
- Report at the level you sampled -- school-level findings, not individual results
- If you promised a report in the consent form, deliver it

## Writing it up

<div class="callout callout-write" markdown="1">
<span class="callout-label">Template -- data collection and processing</span>
Data were collected between *October 3* and *October 28, 2026*. Of *380* questionnaires distributed, *321* were returned, yielding a response rate of *84.5%*. Non-response comprised *34* absences, *18* refusals and *7* incomplete returns. Respondents and non-respondents did not differ significantly by sex, *&chi;&sup2;*(*1*) = *0.42*, *p* = *.52*, or strand, *&chi;&sup2;*(*3*) = *2.11*, *p* = *.55*. Following the exclusion criteria specified in the research plan, *19* cases were removed for exceeding *20%* item non-response, leaving *302* cases for analysis. Reverse-scored items were recoded prior to scale computation. Data were double-entered and reconciled; the raw data file was retained unmodified.
</div>

## Common mistakes

- **Double-barrelled items.** Unrepairable after collection.
- **No pre-test**, so problems surface in the real data.
- **Free substitution** of absent respondents.
- **Missing coded as 0** on a variable where zero is meaningful.
- **Forgetting to recode reverse items** before computing totals.
- **Editing the raw file.**
- **Reporting a response rate with no breakdown by reason.**
- **No comparison of respondents with non-respondents.**

## Practice

**1.** Fix this item: "Do you agree that the new curriculum is effective and should be continued?"

<details markdown="1">
<summary>Show the worked answer</summary>

**Two faults: double-barrelled, and leading.**

**Fault 1 — double-barrelled.** It asks two separate things:
- Is the curriculum effective?
- Should it be continued?

A respondent could think it is effective but too expensive to continue, or ineffective but worth persisting with. Neither can answer honestly.

**Fault 2 — leading.** "Do you agree that..." invites agreement. It presupposes the positive position and makes disagreement the effortful choice.

**The fix — two neutral items:**

```
1. How effective do you find the new curriculum?
   Very ineffective / Ineffective / Neutral / Effective / Very effective

2. Should the new curriculum be continued?
   Definitely not / Probably not / Unsure / Probably yes / Definitely yes
```

**What improved:**
- Each item asks one thing
- Neither presupposes an answer
- Scales are balanced, with equal numbers of positive and negative options
- Every point is labelled

**A bonus you gain:** you can now examine the *relationship* between the two — respondents who find it effective but do not want it continued are an interesting group, and the original item would have hidden them completely.
</details>

**2.** Your response rate is 62%. Is the study usable?

<details markdown="1">
<summary>Show the answer</summary>

**Very likely yes — but only if you can say something about who is missing.**

**62% is respectable** for survey research. Published education surveys often report 50-70%. The rate alone is not the problem.

**What determines usability:**

1. **Is non-response related to your outcome?** If students with low grades were more likely to be absent on collection day, your achievement mean is biased upward. If absence was unrelated to the outcome, the loss costs precision but not validity.

2. **Can you compare respondents with non-respondents?** Use whatever the sampling frame gives you — sex, strand, section, prior grades. Run a chi-square or t-test.
```
Respondents vs non-respondents by sex:    chi2(1) = 0.42, p = .52
Respondents vs non-respondents by strand: chi2(3) = 2.11, p = .55
```
No significant differences on observables is meaningful partial reassurance.

3. **What were the reasons?** Report the breakdown. Refusals are more worrying than absences, because refusal may correlate with attitude toward the topic.

**How to report it:**

> A response rate of 62.4% was obtained. Non-respondents did not differ significantly from respondents by sex or strand. However, because no data were available on the academic performance of non-respondents, the possibility of non-response bias on the primary outcome cannot be excluded, and this is acknowledged as a limitation.

**What would make it unusable:** a 62% rate where the 38% are systematically different in a way that bears on the outcome, and you have no way to check. Then the honest conclusion is that the sample does not represent the frame.
</details>

**3.** You find two impossible values: GWA of 8.7 and social media use of 42 hours per day. What do you do?

<details markdown="1">
<summary>Show the worked answer</summary>

**Both are almost certainly transcription errors with obvious corrections — but you must verify against the source, not guess.**

**Step 1 — go back to the paper form.** This is not optional. The correction must be evidence-based.

**Step 2 — the likely diagnosis:**

| Value | Probable original | Reasoning |
|---|---|---|
| GWA 8.7 | **87** | A decimal point keyed in error. GWA scales run 60-100. |
| 42 hours/day | **4.2** | A misplaced decimal. There are 24 hours in a day. |

Both are consistent with a single keystroke error, which is the most common encoding fault.

**Step 3 — act on what you find:**

- **Form confirms 87 and 4.2** &rarr; correct both, document the change.
- **Form itself shows 8.7** &rarr; the respondent wrote it. Treat as missing, because a GWA of 8.7 is not interpretable.
- **Form is illegible** &rarr; code as missing. Do not guess.

**Step 4 — document it:**
```
Corrected 2 transcription errors verified against paper forms:
  ID 041  gwa       8.7  -> 87
  ID 156  sm_hours   42  -> 4.2
```

**Step 5 — build the check that prevents recurrence.** Range validation at entry would have caught both instantly:
```
gwa       must be 60-100
sm_hours  must be 0-24
```

**The wider lesson:** these two were caught because they are *impossible*. An error that produces a *plausible* value — 78 keyed as 87 — is invisible to range checks and is exactly why **double entry** and **10% spot-checking** exist. Impossible values are the tip; plausible errors are the risk.
</details>

## Before you move on

- [ ] Every item asks exactly one thing and does not lead
- [ ] I have pre-tested cognitively and piloted
- [ ] My codebook exists before encoding starts
- [ ] Missing-value codes are impossible values, declared as missing
- [ ] Reverse items are recoded before any total is computed
- [ ] My raw file is untouched and my cleaning is scripted
- [ ] I report response rate by reason and compare respondents with non-respondents

Next: the references, all free.""",
    [{"question": "\"Are you satisfied with the speed and quality of service?\" is flawed because it is:",
      "choices": ["Leading", "Double-barrelled", "Ambiguous", "Too long"], "correct": 1},
     {"question": "For a variable counting absences, coding missing values as 0 is:",
      "choices": ["Standard practice", "A serious error, since 0 absences is a real value",
                  "Fine if documented", "Required by SPSS"], "correct": 1}],
)


# ===========================================================================
L(
    "Further Reading (Free & Open)",
    """## How to use this page

The CHED references come from CMO 42 s. 2017, which specifies texts for Survey Sampling and Survey Operations. Everything else is free.

## The CHED-specified references

- **Lohr, S.L. -- *Sampling: Design and Analysis***. Named in CMO 42 Annex B for Survey Sampling. The standard text, and unusually readable for the subject.
- **UN Statistics Division (2005). *An Analysis of Operating Characteristics of Surveys in Developing and Transition Countries: Survey Costs, Design Effects and Non-sampling Errors***. Named for Survey Operations. **Free from the UN**, and the best source on design effects and non-sampling error in contexts like ours.

## Research methods, free and complete

- **Creswell, J.W. -- *Research Design***. Not free, but in every university library and the standard reference for design selection and mixed methods.
- **Trochim, W. -- Research Methods Knowledge Base** (conjointly.com/kb). **Completely free online.** The clearest treatment of validity, design notation and measurement available at any price.
- **SAGE Research Methods** -- many institutions subscribe; check your library.
- **Open University, *Succeeding in Postgraduate Study*** -- free on OpenLearn.

## Sampling

- **Cochran, W.G. -- *Sampling Techniques***. The classic. Where Cochran's formula comes from.
- **Raosoft sample size calculator** -- free, quick, and shows its assumptions.
- **G*Power** -- free, for power-based sample size. Screenshot the output for your appendix.

## Instrument development and validity

- **Polit, D.F. and Beck, C.T. (2006). The content validity index.** *Research in Nursing and Health, 29*, 489-497. The source of the I-CVI thresholds used in this course.
- **DeVellis, R.F. -- *Scale Development: Theory and Applications***. The standard on building an instrument properly.
- **Tavakol, M. and Dennick, R. (2011). Making sense of Cronbach's alpha.** *International Journal of Medical Education, 2*, 53-55. **Free**, two pages, and corrects most of the common misuses.

## Ethics and data privacy

- **Philippine Health Research Ethics Board (PHREB)** -- ethics.healthresearch.ph. The **National Ethical Guidelines for Health and Health-Related Research**, free, and the reference most Philippine ethics committees work from.
- **National Privacy Commission** -- privacy.gov.ph. RA 10173, its implementing rules, advisories and template consent language.
- **NCIP** -- for research involving indigenous peoples; the FPIC guidelines are mandatory, not advisory.

## Writing and citation

- **APA Style** -- apastyle.apa.org. Free guidance on 7th edition formatting.
- **Purdue OWL** -- owl.purdue.edu. Free, comprehensive, and the fastest answer to any citation question.
- **Zotero** -- zotero.org. Free reference manager. Install it before you read your first paper.

## Philippine data and literature

- **Philippine E-Journals** -- ejournals.ph. Local studies, essential for a local gap claim.
- **HERDIN** -- herdin.ph. Philippine health research index.
- **PSA Data Archive** -- microdata from the LFS, FIES and other national surveys, free for research use on request.
- **PSA OpenSTAT** -- openstat.psa.gov.ph.
- **CHED and DepEd research portals**, plus your own university repository. Much Philippine research is indexed nowhere else.

## The habits that matter most

1. **Write the Statement of the Problem to analysis mapping table before you collect anything.** It catches unanswerable questions while they are still cheap to fix.
2. **Submit the ethics application early.** It is the longest pole in the timeline and you do not control it.
3. **Keep the raw data untouched.** Everything else can be rebuilt from it.
4. **Explain your design to someone outside your field.** If they cannot follow it, neither will your panel.

## Where to go next in this catalogue

| If you want to... | Take |
|---|---|
| Choose and run the right test | **Applied Statistics for Research** |
| Learn the descriptive tools properly | **Basic Statistics: A Practical Start** |
| Build and diagnose regression models | **Intermediate Statistics** |
| Run a genuine randomised experiment | **Design & Analysis of Experiments** |
| Handle ordinal or non-normal data | **Nonparametric Statistics** |
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
