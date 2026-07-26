"""
Replaces every substantive lesson's content with a richly structured version:
Overview, Key Concepts, a Worked Example, and Common Mistakes & Pro Tips --
plus embedded original diagrams where a visual genuinely clarifies the concept.

This REPLACES existing lesson content (matched by course slug + lesson title),
so it's safe to re-run, and safe to run after the earlier seed scripts.

Usage:
    DATABASE_URL="postgresql://...your neon connection string..." python3 seed_rich_content.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal
from app import models

RICH_CONTENT = {}
RICH_CONTENT["research-methodology-foundations"] = {
"What Makes a Research Question Researchable": """## Overview

Not every question worth asking is a question you can study. A researchable question is specific, measurable, and answerable with data you can realistically collect -- and getting this right at the very start saves you from months of wasted work later.

## Key Concepts

- **Too broad vs. researchable**: "Does social media affect mental health?" is a topic, not a research question. "Does daily time spent on Instagram correlate with self-reported anxiety scores among college freshmen?" is researchable -- it names a population, a measurable variable, and a testable relationship.
- **The PICO/PICOT framework** (common in health research): Population, Intervention/Interest, Comparison, Outcome, and Time -- naming each of these forces specificity.
- **Feasibility matters as much as interest**: a fascinating question you can't get data for isn't a viable thesis topic.
- **Scope discipline**: narrow your question until you could realistically design a data collection instrument for it this month, not "eventually."

## Worked Example

A student wants to study "the impact of remote work." Too broad. Narrowed: "Does the number of days worked remotely per week correlate with self-reported job satisfaction among BPO employees in Metro Manila?" Now it names a population (BPO employees, Metro Manila), a measurable predictor (days remote per week), and a measurable outcome (job satisfaction score) -- a panel can evaluate whether this is answerable, and you can design an instrument for it immediately.

## Common Mistakes & Pro Tips

- Don't confuse a research **topic** (broad area of interest) with a research **question** (specific, testable statement) -- panels flag this constantly in proposal defenses.
- Write your question down and hand it to someone outside your field. If they can't tell you what data you'd need to collect, it's still too vague.
- Revisit your question after drafting your literature review -- it often needs one more round of narrowing once you see what's already been studied.""",

"Choosing a Research Design": """## Overview

Your research question dictates your design, not the other way around. Picking a design because it's familiar or fast, then forcing your question to fit it, is one of the most common structural mistakes in early-stage research.

## Key Concepts

- **Experimental / quasi-experimental design**: use when you're asking whether something *causes* a change, and you have (or can create) a comparison group.
- **Cross-sectional survey design**: use when you're describing what exists right now, at a single point in time.
- **Longitudinal design**: use when you're tracking change in the same subjects over time.
- **Qualitative design** (phenomenology, grounded theory, case study): use when you're exploring lived experience or meaning-making rather than testing a numeric hypothesis.
- **Mixed methods**: combines quantitative and qualitative components when neither alone fully answers your question.

## Worked Example

A researcher wants to know "why nurses leave hospital jobs within their first year." A purely quantitative cross-sectional survey could measure *how many* leave and correlate it with variables like shift length or pay -- but it won't capture *why* in the nurses' own words. A mixed-methods design (a survey for the "how many/how much," followed by interviews for the "why") answers the full question better than either approach alone.

</p>

![Diagram: Research design sequence from question to data collection](/static/diagrams/research-design-flow.svg)

## Common Mistakes & Pro Tips

- If your question includes the word "causes" or "affects," check whether your design can actually support a causal claim -- a cross-sectional survey usually can't.
- Design choice should be defensible in one sentence: "I chose X design because my question asks Y."
- Budget realistic time for whichever design you choose -- longitudinal designs in particular are often underestimated in thesis timelines.""",

"Sampling: Getting a Group That Actually Represents Your Population": """## Overview

Your results are only as trustworthy as your sample. A brilliant analysis run on a badly sampled dataset is still a badly supported conclusion -- sampling is where a study's credibility is won or lost before any statistics are even run.

## Key Concepts

- **Probability sampling** (simple random, stratified, systematic, cluster): every member of the population has a known chance of selection, which is what lets you generalize statistically to the wider population.
- **Non-probability sampling** (convenience, purposive, snowball): often necessary for hard-to-reach populations or qualitative work, but limits how far you can generalize your findings.
- **Stratified sampling** specifically: divide the population into subgroups (strata) first, then sample within each -- useful when you need guaranteed representation across key subgroups (e.g., by region or department).
- **Sample size and power**: too small a sample and you can't detect real effects even when they exist; too large relative to your resources wastes time and money on precision you didn't need.

## Worked Example

A researcher studying job satisfaction across a company with 40% management and 60% frontline staff uses simple random sampling and, by chance, draws a sample that's 70% frontline. Stratified sampling -- deliberately sampling proportionally within each group -- would have guaranteed the sample matched the real population structure, avoiding this distortion entirely.

## Common Mistakes & Pro Tips

- Use a formula like Cochran's to justify your sample size *before* data collection, not as an afterthought once a panel asks about it.
- "I surveyed whoever was willing" (convenience sampling) is sometimes the honest, necessary answer -- but say so explicitly and discuss the generalizability limits it creates.
- Document your sampling frame (the actual list or method you drew from) -- panels frequently ask exactly how participants were identified.""",

"Research Ethics and Informed Consent": """## Overview

Every study involving people carries an ethical obligation before it carries a statistical one. Skipping or rushing this step isn't just a procedural risk -- it can invalidate an otherwise well-designed study entirely.

## Key Concepts

- **Informed consent**: participants must understand the purpose of the study, what will be asked of them, any risks, and that they can withdraw at any point without penalty -- before they agree to participate.
- **Confidentiality vs. anonymity**: confidentiality means you know who participated but protect that identity; anonymity means there's no way to trace a response back to a person at all. These are not interchangeable terms.
- **Vulnerable populations**: minors, patients, prisoners, and employees reporting on their own employer require extra safeguards -- often additional consent layers or third-party oversight.
- **Ethics review board (IRB/ERB) approval**: most institutions require this *before* data collection begins, not as a formality after the fact.

## Worked Example

A researcher plans to survey hospital patients about their care experience. Because patients are a vulnerable population (in an unequal power relationship with the institution), the study needs explicit safeguards: consent forms in plain language, an assurance that care won't be affected by participation or refusal, and often a data collector who isn't the patient's own attending clinician, to avoid any perceived pressure to participate.

## Common Mistakes & Pro Tips

- Build ethics review approval into your project timeline from day one -- this is consistently one of the most underestimated delays in thesis timelines.
- Never conflate "participants agreed verbally" with informed consent -- most institutions require documented consent, and the documentation format itself is often reviewed.
- If your study involves any deception (common in some experimental designs), you need an explicit debriefing plan and stronger ethics justification.""",

"Writing a Literature Review That Actually Supports Your Study": """## Overview

A literature review isn't a book report -- it's an argument for why your study needs to exist. A well-built review makes your research question feel inevitable by the time a reader finishes it.

## Key Concepts

- **Organize thematically, not chronologically**: group sources by concept or variable rather than listing them paper-by-paper -- this shows how the field's understanding has developed, not just what's been published.
- **Every source should do one job**: establish what's already known, reveal a gap your study addresses, or provide theoretical grounding for your framework.
- **Synthesis over summary**: don't just describe each study in isolation -- explicitly connect sources to each other ("while Author A found X, Author B's later work complicated this by finding Y").
- **The gap statement**: end the review by explicitly naming the gap and positioning your study as the direct response to it.

## Worked Example

Three prior studies found conflicting results on whether remote work improves or harms productivity. Rather than listing each study separately, a strong literature review would group them under "productivity effects of remote work," note that the conflict may stem from differing definitions of "productivity" across studies, and use that identified inconsistency as the specific gap your study will address.

## Common Mistakes & Pro Tips

- A literature review that's just a list of summaries ("Smith (2020) found X. Jones (2021) found Y.") without synthesis is the single most common weakness panels flag.
- The final paragraph of your review is the one a panel reads most carefully -- make sure it explicitly states the gap and your study's contribution.
- Keep a running citation log from day one; reconstructing sources at the end is one of the most avoidable time sinks in thesis writing.""",

"Building Your Conceptual Framework": """## Overview

Your conceptual framework is the visual and logical map of how you believe your variables relate to each other -- grounded in theory and prior research, not intuition.

## Key Concepts

- **Independent, dependent, mediating, and moderating variables** should all be clearly identified before you draw a single arrow.
- **Every connection needs a source**: a strong framework draws each relationship from a specific theory or specific prior finding, cited directly beside the arrow it supports.
- **Directional arrows** show hypothesized relationships -- the direction itself is a claim that needs justification, not just an assumption.
- **Theoretical grounding**: your framework should be traceable to an established theory (e.g., Technology Acceptance Model, Social Exchange Theory) rather than assembled purely from convenience.

## Worked Example

A study on employee turnover proposes that "workload" affects "turnover intention," mediated by "burnout." The framework diagram shows workload -> burnout -> turnover intention, with each arrow labeled with the citation supporting that specific link -- not just a general reference to "prior research."

## Common Mistakes & Pro Tips

- A weak framework borrows variables from unrelated studies without justifying why they belong together in *your* model.
- If you can't cite a specific source for why two variables should be connected, that arrow probably shouldn't be in your framework yet.
- Revisit and simplify your framework after your literature review is complete -- frameworks built too early often include variables that turn out to be tangential.""",

"From Proposal to Final Defense: A Realistic Timeline": """## Overview

Most research timelines fail not because of bad planning but because of unbudgeted delays -- ethics review, data collection running long, and revision cycles with an adviser. Planning around this reality, rather than an idealized straight line, is what actually gets a thesis finished on time.

## Key Concepts

- **Buffer time at every stage**, not just at the end -- a delay in data collection cascades into every later stage, and a single end-of-project buffer can't absorb that.
- **Standard stage sequence**: proposal defense -> ethics approval -> instrument pilot testing -> full data collection -> analysis -> results write-up -> full draft to adviser -> revisions -> final defense.
- **Each stage needs its own deadline**, tracked independently, not just a single final defense date on the calendar.
- **Pilot testing is not optional** -- it catches instrument problems (confusing questions, technical issues) before they contaminate your full dataset.

## Worked Example

A student budgets two weeks for data collection and no time for ethics review delays. In practice, ethics approval takes five weeks, and once approved, only 40% of the target sample responds within the original two-week window, requiring a further three weeks of follow-up. Without buffers built in at each of these stages, the entire remaining timeline (analysis, writing, revisions) gets compressed into an unrealistic final sprint.

## Common Mistakes & Pro Tips

- Track stage-level deadlines in a shared document with your adviser -- this surfaces slippage early instead of at the final defense.
- Pilot test your instrument with 5-10 people who are *not* going to be part of your final sample.
- Build in at least one full revision cycle with your adviser before your final draft deadline -- treating the first full draft as the final one is a common and costly assumption.""",
}
RICH_CONTENT["applied-statistics-for-research"] = {
"From Research Question to Statistical Test": """## Overview

Every statistical test answers a specific kind of question, and picking the wrong one is the single most common error panels flag in a results chapter. The test should follow logically from the question -- not from whichever test you're most comfortable running.

## Key Concepts

- **How many groups/variables** are you comparing? Two independent groups on a continuous outcome points to a t-test; more than two points to ANOVA.
- **What type of data** do you have -- categorical, ordinal, or continuous? This alone rules out entire families of tests.
- **Independent or paired/related data?** Comparing the same subjects before and after an intervention needs a paired test, not an independent-samples test.
- **Relationship vs. comparison**: looking at how two continuous variables relate points to correlation or regression; comparing categorical variables points to chi-square.

## Worked Example

A researcher wants to know if a training program improved test scores for the *same* group of employees, measured before and after. Because it's the same people measured twice (paired data, continuous outcome), the correct test is a paired-samples t-test -- not an independent-samples t-test, which would incorrectly treat the before and after scores as coming from two separate groups.

![Diagram: The hypothesis testing process, from stating H0 to a decision](/static/diagrams/hypothesis-testing-flow.svg)

## Common Mistakes & Pro Tips

- Write your research question down first, then walk through these questions *before* opening any statistical software.
- Confusing paired and independent designs is one of the most common test-selection errors in applied research.
- If you're unsure between two tests, check whether your data meets each test's assumptions -- that alone often settles the choice.""",

"Choosing the Right Test: A Decision Framework": """## Overview

Build yourself a decision tree and use it every time, even once you're experienced -- consistency in test selection is what makes your analysis defensible under panel questioning.

## Key Concepts

- **Step 1**: Is the outcome variable continuous or categorical?
- **Step 2 (if continuous)**: Are you comparing groups (t-test/ANOVA) or examining relationships (correlation/regression)?
- **Step 3 (if categorical)**: Are you looking at frequencies (chi-square) or predicting group membership (logistic regression)?
- **Assumption check before committing**: normality, homogeneity of variance, and independence all need verification before you finalize a parametric test.
- **Non-parametric alternatives exist for nearly every parametric test**: Mann-Whitney U instead of an independent t-test, Kruskal-Wallis instead of one-way ANOVA, Spearman's rho instead of Pearson's r.

## Worked Example

A researcher wants to compare customer satisfaction scores (measured on a 1-10 scale, treated as continuous) across four store branches. The outcome is continuous, and there are more than two groups -- pointing to one-way ANOVA. Before running it, they check normality (Shapiro-Wilk) and homogeneity of variance (Levene's test) across the four branches; if either assumption fails badly, Kruskal-Wallis becomes the safer choice.

## Common Mistakes & Pro Tips

- Running a parametric test on clearly non-normal data *without at least acknowledging the violation* is one of the fastest ways to lose credibility with a panel.
- Keep your decision framework as a literal checklist you run through for every test in your analysis chapter -- don't rely on memory alone.
- When in doubt between a parametric and non-parametric test, running both and reporting whether conclusions agree is a defensible, transparent approach.""",

"Reading and Reporting Output the Way a Panel Expects": """## Overview

Statistical software gives you far more numbers than you need to report, and knowing which ones matter -- and how to present them -- is a distinct skill from running the analysis itself.

## Key Concepts

- **The core reporting set**: test statistic (t, F, chi-square value), degrees of freedom, p-value, and an effect size (Cohen's d, eta-squared, or similar).
- **A significant p-value alone is incomplete** -- it tells you an effect probably exists, not whether it's meaningful in practice. Effect size answers that second question.
- **APA format consistency**: report as "t(48) = 2.31, p = .025, d = 0.66" rather than pasting raw software output or screenshots.
- **Plain-language interpretation**: every statistical result needs an immediate follow-up sentence explaining what it means for your actual research question, in language a non-statistician could follow.

## Worked Example

Raw output shows: t = 2.314, df = 48, p = 0.0251, Cohen's d = 0.663. Reported properly: "There was a statistically significant difference in test scores between the two groups, t(48) = 2.31, p = .025, d = 0.66, indicating a medium-to-large practical effect." The number alone doesn't communicate the finding -- the sentence around it does.

## Common Mistakes & Pro Tips

- Never report a p-value without an accompanying effect size -- reviewers and panels increasingly expect both as standard.
- Round consistently (typically 2-3 decimal places) and follow your field's citation style exactly.
- Always translate the statistical result back into the language of your original research question in the same paragraph -- don't leave that connection for the reader to infer.""",

"Common Mistakes That Get Flagged in Defense": """## Overview

The same handful of errors show up again and again in thesis and dissertation defenses. Knowing them in advance means you can audit your own analysis chapter before anyone else sees it.

## Key Concepts

- **Multiple comparisons without correction**: running many tests without adjusting for the increased chance of false positives (no Bonferroni or similar correction) inflates your risk of reporting a spurious finding as real.
- **Significance vs. importance**: a p-value of .001 on a trivial effect size is not a strong finding -- panels increasingly ask "so what?" even for significant results.
- **Ordinal data treated as continuous** without justification -- Likert scale items are a frequent culprit.
- **Assumption checks skipped or unreported** -- silence on this point reads as either an oversight or an attempt to hide a violation, neither of which helps you.
- **Overstating causation** from correlational or cross-sectional data -- "X causes Y" language when your design can only support "X is associated with Y."

## Worked Example

A student runs 15 separate t-tests comparing subgroups without any correction, and reports three as "significant" at p < .05. Given the number of tests run, roughly one false positive would be expected by chance alone at this threshold -- a panel will ask directly whether a correction (like Bonferroni, dividing .05 by the number of tests) was applied, and "no" is a difficult answer to defend.

## Common Mistakes & Pro Tips

- Build a pre-defense checklist covering each of the errors above and run your full analysis chapter against it.
- If you must run many comparisons, decide on and report your correction method *before* seeing the results, not after.
- Read your causal language line by line -- "affects," "causes," "leads to" are strong claims your design may not support; "is associated with" is often the honest phrasing.""",

"Sample Size and Power Analysis for Your Specific Test": """## Overview

A study with too few participants can't detect a real effect even when one exists -- this is a power problem, and unlike most analysis issues, it's only fixable *before* data collection, not after.

## Key Concepts

- **Four inputs to a power analysis**: your significance level (typically .05), desired power (typically .80), expected effect size, and test type.
- **G*Power** is the standard free tool for running these calculations for most common test types.
- **Underpowered studies risk Type II errors** -- failing to detect a real effect, which can look identical to "there's no effect" in your results without a power analysis to contextualize it.
- **Reporting your power analysis** in the methodology chapter preempts one of the most common panel questions: "how did you arrive at this sample size?"

## Worked Example

A researcher expects a medium effect size (Cohen's d = 0.5) comparing two groups, wants standard power (.80) and significance (.05). G*Power indicates a minimum of roughly 64 participants per group (128 total) is needed to reliably detect that effect if it exists. Collecting only 40 total participants, as originally planned, would leave the study underpowered to detect even a real, moderate effect.

## Common Mistakes & Pro Tips

- Run your power analysis at the proposal stage, not after data collection -- it's meant to justify your sample size target, not explain a shortfall after the fact.
- If your expected effect size is uncertain, use a conservative (smaller) estimate -- this yields a larger, safer sample size target.
- A post-hoc power analysis (calculated after data collection to explain a non-significant result) is generally viewed skeptically by panels -- plan power in advance instead.""",

"Mediation and Moderation: What's Actually Different": """## Overview

These two terms get confused constantly, but they answer fundamentally different questions about how variables relate to each other.

## Key Concepts

- **Mediation** asks: does variable M explain *how* or *why* X affects Y? M sits on the causal pathway between X and Y.
- **Moderation** asks: does variable Z change the *strength or direction* of the X-to-Y relationship, without being on the causal path itself?
- **Testing mediation**: the classic approach checks whether the direct effect of X on Y shrinks once M is included (Baron & Kenny's steps); modern practice favors bootstrapping approaches for more robust significance testing of the indirect effect.
- **Testing moderation**: requires an interaction term (X multiplied by Z) included directly in a regression model.

## Worked Example

A study finds that "job training" (X) improves "job performance" (Y). If the effect works *through* increased "employee confidence" (M) -- training boosts confidence, which boosts performance -- that's mediation. If the training's effect on performance is *stronger for new employees than experienced ones* (Z = tenure), that's moderation -- tenure changes the strength of the relationship without being part of the causal chain itself.

## Common Mistakes & Pro Tips

- Don't test for both without a clear theoretical reason to expect each -- atheoretical "let's just test everything" mediation/moderation analyses are a common panel red flag.
- Bootstrapped confidence intervals (5,000 resamples is typical) are now the preferred method for testing indirect effects, over the older Sobel test.
- State explicitly in your hypotheses which variable you expect to mediate and which to moderate -- and why, grounded in theory.""",

"Preparing for Your Statistics Defense": """## Overview

Panels don't just check whether your numbers are right -- they check whether you understand what they mean. Preparing to explain your analysis without your slides is the real test.

## Key Concepts

- **Be ready to explain, unaided**: why you chose each test, what assumption checks you ran and what you found, and what your effect sizes actually indicate practically.
- **Prepare for the null result question**: what would it have meant for your study if your key hypothesis test had come back non-significant?
- **Know your weakest finding cold** -- that's almost always where the hardest defense questions land, not your strongest result.
- **Practice translating statistics into plain language** out loud, not just on paper -- the gap between writing and speaking under pressure is real.

## Worked Example

A student's regression model showed a non-significant relationship between one predictor and the outcome. Rather than treating this as a failure to hide, a well-prepared defense explains: "This suggests that, controlling for the other variables in the model, X does not have an independent effect on Y in this sample -- which is itself informative and consistent with [cite a specific theoretical reason]." Panels respond far better to this than to an evasive answer.

## Common Mistakes & Pro Tips

- Rehearse a plain-language, one-sentence summary for every single statistical result in your paper -- not just the significant ones.
- If a panel member challenges your test choice, the strongest response cites the specific assumption or data characteristic that led to your decision, not just "that's what my adviser suggested."
- Bring a printed copy of your full output tables to your defense, even if not required -- it signals preparation and lets you answer detail questions precisely.""",
}
RICH_CONTENT["basic-statistics"] = {
"Descriptive Statistics: Making Sense of Raw Numbers": """## Overview

Before any inference, you need to describe what your data actually looks like. This is the foundation every later statistical decision rests on.

## Key Concepts

- **Central tendency** -- mean, median, mode -- tells you where the center of your data sits, but each behaves differently with outliers: the mean is pulled toward extreme values, the median isn't.
- **Spread** -- range, variance, standard deviation -- tells you how tightly your data clusters around that center.
- **Center and spread must be read together**: a dataset with a mean of 50 and SD of 2 looks very different from one with the same mean and SD of 20, even though the "average" is identical.
- **Always visualize before testing**: a histogram or boxplot can reveal a shape (skew, bimodality, outliers) that changes which statistical test is even appropriate.

## Worked Example

Two classes both average 75% on an exam. Class A has a standard deviation of 3 (scores tightly clustered 70-80%); Class B has a standard deviation of 18 (scores ranging from 40-100%). Reporting only the mean would make these look identical, but they describe very different realities -- Class B likely has a mix of struggling and excelling students that Class A doesn't.

## Common Mistakes & Pro Tips

- Reporting only the mean without any measure of spread is one of the most common (and misleading) simplifications in early analysis writing.
- When your data is skewed, the median is often a more honest measure of "typical" than the mean.
- Always look at your histogram before choosing a statistical test -- numbers alone can hide a shape that matters.""",

"Probability Basics You Actually Need": """## Overview

You don't need a full probability theory course to do applied statistics well, but a handful of ideas underpin nearly everything that follows.

## Key Concepts

- **Probability** is a number between 0 and 1 describing how likely an event is.
- **Independent events** don't affect each other's probability -- a coin flip doesn't "remember" the last flip.
- **Conditional probability** -- the chance of one event given that another has occurred -- underlies concepts like sensitivity and specificity in diagnostic testing.
- **The sampling distribution concept**: if you took many samples from a population, the sample means would themselves form a predictable distribution. This is the conceptual bridge from basic probability to everything in hypothesis testing.

## Worked Example

A diagnostic test is 90% sensitive (correctly identifies 90% of people who truly have a condition). If a patient tests positive, that does *not* automatically mean a 90% chance they have the condition -- that number depends also on the test's specificity and how common the condition actually is in the population (Bayes' theorem territory). This distinction between "probability of a positive test given disease" and "probability of disease given a positive test" trips up even experienced practitioners.

## Common Mistakes & Pro Tips

- Don't confuse P(A given B) with P(B given A) -- they are frequently very different numbers, especially in diagnostic and screening contexts.
- "Independent" has a precise statistical meaning -- don't assume two variables are independent just because they seem unrelated intuitively; test it.
- The sampling distribution idea is worth sitting with until it's intuitive -- it's the concept that makes p-values and confidence intervals make sense later.""",

"The Normal Distribution and Why It Matters": """## Overview

The normal distribution -- the familiar bell curve -- matters because so much statistical theory assumes it, directly or indirectly, even when your raw data doesn't look like it at first glance.

## Key Concepts

- **Symmetric around the mean**, with a fixed percentage of data always falling within one, two, and three standard deviations (roughly 68%, 95%, and 99.7%).
- **The Central Limit Theorem**: even when raw data isn't normal, the distribution of *sample means* approaches normal as sample size grows -- this is why many parametric tests still work reasonably well on non-normal data, given a large enough sample.
- **Checking for normality**: visually with a histogram or Q-Q plot, or formally with the Shapiro-Wilk test, as a standard early step before choosing a test.
- **Standard deviations as a universal ruler**: expressing any value in terms of how many SDs it sits from the mean (a z-score) lets you compare across completely different scales.

![Diagram: The normal distribution with standard deviation bands](/static/diagrams/normal-distribution.svg)

## Worked Example

A student scores 85 on a test with a class mean of 70 and SD of 10. That's exactly 1.5 standard deviations above the mean -- placing them, under a normal distribution, in roughly the top 7% of the class, even without knowing every other student's exact score.

## Common Mistakes & Pro Tips

- Never assume normality -- always check it, even briefly, before running a parametric test.
- A histogram that looks "close enough" to bell-shaped is often fine for real-world work; perfect normality is rare and rarely required in practice.
- Remember the Central Limit Theorem's role: it's the reason large-sample parametric tests are more forgiving of non-normal raw data than small-sample ones.""",

"Your First Hypothesis Test": """## Overview

Every hypothesis test follows the same underlying logic, regardless of which specific test you eventually run. Understanding this shared structure makes every future test easier to learn.

## Key Concepts

- **Null hypothesis (H0)**: no effect or no difference exists.
- **Alternative hypothesis (H1)**: an effect or difference does exist.
- **The core logic**: collect data, calculate a test statistic, and ask -- how likely would this result be if the null hypothesis were true?
- **The p-value threshold**: if that likelihood is low enough (conventionally below .05), you reject the null in favor of the alternative.
- **What rejecting the null does NOT mean**: it doesn't prove the alternative is true -- it means the observed data would be unusual if the null were true.

![Diagram: The hypothesis testing process, step by step](/static/diagrams/hypothesis-testing-flow.svg)

## Worked Example

A one-sample t-test asks: "Is this sample's mean significantly different from a known population value?" A factory claims its light bulbs last 1,000 hours on average. A sample of 30 bulbs has a mean lifespan of 970 hours. The one-sample t-test asks how likely a sample mean this far from 1,000 would be if the true population mean really were 1,000 -- if that probability (p-value) is below .05, you'd reject the claim.

## Common Mistakes & Pro Tips

- "Failing to reject the null" is not the same as "proving the null is true" -- it just means your data didn't provide strong enough evidence against it.
- Decide your significance threshold (.05 is conventional, but not universal) *before* running the test, not after seeing the result.
- Practice this logic with a one-sample t-test before moving to more complex comparisons between groups -- the underlying reasoning is identical throughout.""",

"Understanding Confidence Intervals": """## Overview

A confidence interval gives you a range of plausible values for a population parameter, not just a single estimate -- and it's often more informative than a p-value alone.

## Key Concepts

- **What a 95% CI actually means**: if you repeated your sampling process many times, 95% of the intervals you'd calculate would contain the true population value -- it is not "a 95% chance the true value is in this specific interval."
- **Width signals precision**: a wide interval signals more uncertainty (often from a smaller sample); a narrow one signals a more precise estimate.
- **CIs and hypothesis tests are connected**: if a 95% CI for a difference between groups doesn't include zero, that difference is significant at p < .05.
- **Always report alongside point estimates**: a mean of 50 with a CI of 48-52 tells a very different story than a mean of 50 with a CI of 20-80.

## Worked Example

A survey estimates average customer satisfaction at 7.2 out of 10, with a 95% confidence interval of 6.9 to 7.5. This tells a manager not just the estimate, but the plausible range -- useful for deciding whether a target of "at least 7.0" has likely been met, versus a wider interval of 5.5 to 8.9, which would leave real doubt about whether the target was actually hit.

## Common Mistakes & Pro Tips

- Never say a specific interval has "a 95% chance of containing the true value" -- that misstates what confidence level means; the correct framing is about the long-run behavior of the method.
- Report confidence intervals for your key estimates by default, not just when asked -- it's increasingly expected in quantitative reporting.
- A very wide confidence interval is itself an important finding -- it signals your estimate is imprecise, likely due to a small sample.""",

"Correlation: What It Does and Doesn't Tell You": """## Overview

Correlation measures the strength and direction of a linear relationship between two continuous variables -- and understanding its limits is as important as understanding what it shows.

## Key Concepts

- **Range and interpretation**: correlation ranges from -1 to +1; values near 0 indicate little to no *linear* relationship, but don't rule out a strong non-linear one.
- **Always plot it**: a scatter plot can reveal a strong non-linear pattern that the correlation coefficient alone would miss entirely.
- **Correlation is not causation**: two variables can move together because one causes the other, because both are caused by a third variable, or by coincidence -- the statistic alone can't distinguish between these.
- **Strength conventions**: roughly, |r| around 0.1 is weak, 0.3 is moderate, 0.5+ is strong -- but these thresholds vary meaningfully by field.

## Worked Example

Ice cream sales and drowning incidents are positively correlated. Neither causes the other -- both are driven by a third variable, hot weather, which increases both ice cream purchases and swimming (and therefore drowning risk). Reporting this correlation as "ice cream sales cause drownings" would be a textbook example of mistaking correlation for causation.

## Common Mistakes & Pro Tips

- Always plot a scatter plot alongside any correlation you report -- the number alone can hide curved relationships.
- Watch for outliers -- a single extreme point can dramatically inflate or deflate a correlation coefficient in a small sample.
- When writing up correlational findings, use language like "is associated with," not "causes" or "leads to," unless your design specifically supports causal claims.""",

"Chi-Square Tests for Categorical Data": """## Overview

When both your variables are categorical rather than continuous, chi-square tests are your standard tool for examining relationships between them.

## Key Concepts

- **Chi-square test of independence**: asks whether two categorical variables are related (e.g., does smoking status relate to disease diagnosis?).
- **Chi-square goodness-of-fit test**: asks whether observed frequencies match an expected distribution.
- **The underlying comparison**: both versions compare observed counts to what you'd expect under the null hypothesis of no relationship or no difference from the expected distribution.
- **The small-cell-count caveat**: chi-square becomes unreliable when expected cell counts are too small (typically below 5) -- Fisher's exact test is the better alternative in that case.

## Worked Example

A researcher wants to know if product preference (A, B, or C) differs by age group (18-30, 31-50, 51+). A chi-square test of independence compares the actual counts in each age-group-by-preference combination against what would be expected if age and preference were unrelated. A significant result means preference genuinely varies by age group -- though it doesn't say which specific groups differ, which would need follow-up pairwise comparisons.

## Common Mistakes & Pro Tips

- Check your expected cell counts before trusting a chi-square result -- many small subgroups can silently invalidate the test.
- Chi-square tells you *whether* a relationship exists, not its strength -- report Cramer's V or a similar effect size alongside it.
- Don't use chi-square on continuous data that's been artificially chopped into categories -- this discards information and is rarely the best choice when a continuous-data test is available.""",
}
RICH_CONTENT["intermediate-statistics"] = {
"Simple and Multiple Linear Regression": """## Overview

Regression models the relationship between a continuous outcome and one or more predictors -- one of the most widely used tools in applied statistics, and the foundation for many more advanced methods.

## Key Concepts

- **Simple linear regression** uses one predictor; **multiple regression** uses several at once, letting you see each predictor's effect while holding the others constant.
- **The regression coefficient** tells you how much the outcome changes for a one-unit change in that predictor, controlling for other variables in the model.
- **R-squared** tells you what proportion of the variance in your outcome the model explains -- useful, but incomplete: a model can have high R-squared and still violate assumptions, or low R-squared and still be theoretically meaningful.
- **Always report both** coefficients and their statistical significance, and be explicit about which variables you controlled for and why.

![Diagram: Fitting a regression line through scattered data](/static/diagrams/regression-scatter.svg)

## Worked Example

A regression predicting salary from years of experience and education level finds a coefficient of 2,500 for years of experience. This means: for each additional year of experience, salary increases by an estimated 2,500 units, *holding education level constant*. Without the "holding constant" framing, the interpretation is incomplete -- the effect is specifically the experience effect isolated from education's influence.

## Common Mistakes & Pro Tips

- Never interpret a coefficient without mentioning what else is being held constant in a multiple regression.
- Check for multicollinearity (via variance inflation factor) when using several predictors -- highly correlated predictors can make individual coefficients unstable and hard to interpret.
- A high R-squared doesn't excuse skipping assumption checks -- always verify residual normality and homoscedasticity regardless of how well the model appears to fit.""",

"ANOVA: Comparing More Than Two Groups": """## Overview

Analysis of variance (ANOVA) extends t-test logic to three or more groups without inflating your false-positive rate the way running multiple separate t-tests would.

## Key Concepts

- **The omnibus test**: a significant ANOVA result tells you that *at least one* group differs from the others -- it does not tell you which ones.
- **Post-hoc tests** (Tukey's HSD, Bonferroni-corrected pairwise comparisons) are what identify which specific groups differ, and should be planned alongside your ANOVA, not treated as an afterthought.
- **Two-way ANOVA** examines two categorical predictors at once, including whether they *interact* -- whether the effect of one depends on the level of the other.
- **Assumptions**: normality within each group and homogeneity of variance across groups (checked via Levene's test) both need verification.

## Worked Example

A one-way ANOVA comparing customer satisfaction across four store branches returns a significant result (p < .05). This tells you satisfaction differs *somewhere* among the four branches -- but a follow-up Tukey's HSD test is needed to determine, for example, that Branch A differs significantly from Branch D, while Branches B and C don't differ significantly from anyone.

## Common Mistakes & Pro Tips

- Treating a significant ANOVA result as the final answer, without running post-hoc comparisons, is a common and easily avoidable gap in results chapters.
- With unequal group sizes, some post-hoc tests (like Tukey's) can behave differently -- check whether your chosen post-hoc method is appropriate for unbalanced designs.
- In two-way ANOVA, always check the interaction effect first -- a significant interaction changes how you interpret the main effects.""",

"Checking Your Assumptions": """## Overview

Every parametric test rests on assumptions, and skipping the check is one of the fastest ways to undermine an otherwise solid analysis -- panels and reviewers look for this explicitly.

## Key Concepts

- **Normality of residuals** (not your raw data -- the residuals) for regression and ANOVA.
- **Homogeneity of variance** across groups, checked via Levene's test.
- **Independence of observations** -- violated by repeated measures or clustered data without an appropriate model adjustment.
- **For regression specifically**: linearity and absence of severe multicollinearity (checked via variance inflation factor, VIF).
- **Three real options when assumptions are violated**: transform your data, use a robust or non-parametric alternative, or proceed with explicit acknowledgment and discussion of the violation.

## Worked Example

A regression's residual plot shows a clear funnel shape (residuals spreading wider as predicted values increase) -- a violation of homoscedasticity (constant variance). Rather than ignoring this, the researcher either applies a variance-stabilizing transformation to the outcome variable (like a log transform) or uses robust standard errors that adjust for the heteroscedasticity, and reports which approach was taken and why.

## Common Mistakes & Pro Tips

- Silence on assumption checks in a results chapter reads as either an oversight or an attempted omission -- always report what you checked, even briefly.
- Check residuals, not raw outcome data, when assessing normality for regression -- this is a common and consequential mix-up.
- Minor assumption violations in large samples are often tolerable given the Central Limit Theorem; severe violations in small samples are not.""",

"Introduction to Multivariate Thinking": """## Overview

Most real research questions involve more than one variable interacting at once -- multivariate methods exist specifically to handle this complexity rigorously rather than piecemeal.

## Key Concepts

- **MANOVA** examines several outcome variables simultaneously, rather than testing each one separately with repeated ANOVAs (which would inflate your false-positive risk).
- **Factor analysis** looks for underlying structure among many observed variables -- reducing a large item set to a smaller number of meaningful underlying factors.
- **The conceptual shift**: moving from "does X affect Y" toward "how do these variables relate to each other as a system."
- **This mindset is the on-ramp to SEM**: structural equation modeling, covered in the Advanced Statistics course, extends this systems-thinking approach even further.

## Worked Example

A researcher measures employee wellbeing using five separate outcome variables (job satisfaction, stress, engagement, burnout, and turnover intention). Running five separate ANOVAs to compare these across departments would inflate the false-positive risk considerably. A single MANOVA test examines all five outcomes together as a combined system, controlling that inflated risk while still allowing follow-up univariate tests if the overall result is significant.

## Common Mistakes & Pro Tips

- Don't run a series of separate univariate tests when your outcomes are conceptually related -- that's exactly the scenario multivariate methods exist to handle correctly.
- Before running factor analysis, check that your data is even suitable using the KMO measure and Bartlett's test of sphericity.
- Multivariate output is denser than univariate output -- budget real time to learn how to read and report it correctly, rather than treating it as a black box.""",

"Logistic Regression for Binary Outcomes": """## Overview

When your outcome variable has only two categories, linear regression is the wrong tool -- logistic regression is purpose-built for exactly this case.

## Key Concepts

- **What it predicts**: rather than the outcome directly, logistic regression predicts the log-odds of the outcome occurring, which is then converted to odds ratios for interpretation.
- **Odds ratio interpretation**: an odds ratio of 2.0 for a predictor means the odds of the outcome roughly double for each one-unit increase in that predictor.
- **Model fit assessment differs from linear regression**: look at the Hosmer-Lemeshow test, classification accuracy, and area under the ROC curve, rather than R-squared.
- **Multiple logistic regression** works the same way as multiple linear regression conceptually -- letting you control for several predictors while examining each one's independent effect.

## Worked Example

A logistic regression predicting loan default finds an odds ratio of 1.8 for "missed a previous payment." This means: applicants with a prior missed payment have roughly 1.8 times the odds of defaulting, holding other factors in the model constant -- a directly actionable finding for a lending risk model, expressed in a form that's more interpretable to a non-statistical audience than a raw log-odds coefficient.

## Common Mistakes & Pro Tips

- Report odds ratios, not raw log-odds coefficients, in your results write-up -- log-odds are not intuitively interpretable to most readers.
- Don't apply R-squared logic from linear regression to logistic models -- use the fit statistics designed for this model type instead.
- Check for separation (a predictor that perfectly predicts the outcome) -- it causes unstable estimates and is a signal to consider Firth's penalized regression, covered in the Advanced Statistics course.""",

"Factor Analysis: Finding Structure in Your Variables": """## Overview

Factor analysis helps you discover whether a large set of observed variables can be explained by a smaller number of underlying, unobserved factors -- commonly used to validate a survey instrument before using it in a main study.

## Key Concepts

- **Exploratory factor analysis (EFA)** lets the data suggest the factor structure, with no structure specified in advance.
- **Confirmatory factor analysis (CFA)** tests whether a theory-driven structure you've already specified actually fits your data.
- **Suitability checks before running EFA**: the KMO measure of sampling adequacy and Bartlett's test of sphericity both need to pass before factor analysis is even appropriate.
- **Factor loadings** indicate how strongly each observed item relates to an underlying factor -- loadings above roughly 0.4-0.5 are typically considered meaningful.

## Worked Example

A 20-item survey intended to measure "job satisfaction" is run through EFA, which reveals the items actually cluster into three distinct factors: satisfaction with pay, satisfaction with management, and satisfaction with work-life balance -- rather than one single "job satisfaction" factor as originally assumed. This finding reshapes how the researcher analyzes and reports the construct going forward.

## Common Mistakes & Pro Tips

- Skipping the KMO/Bartlett's suitability check is a common oversight that can produce uninterpretable or unreliable factor solutions.
- Don't confuse EFA and CFA -- using EFA when you already have a theory-specified structure (which calls for CFA) is a frequent methodological mismatch.
- Report factor loadings in a clear table, and name each factor based on the conceptual theme of its highest-loading items, not arbitrarily.""",

"Effect Sizes: Why p-Values Alone Aren't Enough": """## Overview

A statistically significant result tells you an effect probably isn't zero; it says nothing about whether that effect actually matters in practice. Effect sizes close this gap.

## Key Concepts

- **Cohen's d** for mean differences, **eta-squared** for ANOVA, **r-squared** or **f-squared** for regression -- each quantifies magnitude in standardized, comparable units.
- **Cohen's conventional benchmarks** (small ~0.2, medium ~0.5, large ~0.8 for d) are a starting point, not a rule -- a "small" effect can be highly meaningful in some fields (medicine) and trivial in others.
- **Sample size inflates significance, not effect size**: with a large enough sample, even a tiny, practically meaningless effect can become statistically significant -- effect size is what tells you whether it's worth caring about.
- **Reporting expectation**: effect size alongside significance is now standard in essentially every quantitative discipline's reporting guidelines.

## Worked Example

A study with 10,000 participants finds a statistically significant difference in test scores between two teaching methods (p < .001), but the effect size (Cohen's d = 0.05) is negligible -- the average score difference is less than half a point out of 100. The large sample made a practically trivial difference statistically detectable; the effect size is what reveals it isn't actually meaningful.

## Common Mistakes & Pro Tips

- Never present a p-value as the full story -- always pair it with an effect size and a plain-language statement of practical significance.
- Don't apply Cohen's benchmarks rigidly across every field -- check what's considered meaningful in your specific discipline's literature.
- When comparing your findings to prior studies, compare effect sizes, not just significance -- this is what allows genuine comparison across studies with different sample sizes.""",
}
RICH_CONTENT["advanced-statistics"] = {
"Structural Equation Modeling: The Big Picture": """## Overview

Structural equation modeling (SEM) lets you test an entire theoretical model at once -- relationships between multiple latent (unobserved) constructs, each measured by several observed indicators.

## Key Concepts

- **What SEM tests that regression can't**: a whole web of hypothesized relationships simultaneously, including mediation and moderation effects, rather than one outcome against predictors at a time.
- **CB-SEM (covariance-based)**: tests how well your theoretical model fits the observed covariance structure -- confirmatory, theory-testing in nature.
- **PLS-SEM (partial least squares)**: prediction-oriented and more forgiving of smaller samples and non-normal data, which is why it shows up so often in applied social science and business research.
- **Latent constructs**: unobserved concepts (like "job satisfaction" or "brand loyalty") measured indirectly through multiple observed indicator items.

![Diagram: SEM measurement model and structural paths](/static/diagrams/pls-sem-path.svg)

## Worked Example

A researcher wants to test a full theoretical model: "perceived usefulness" and "perceived ease of use" both affect "attitude toward technology," which in turn affects "intention to adopt." Regression could only test one piece of this chain at a time; SEM tests the entire structural model -- all the paths -- simultaneously, in a single coherent analysis that also accounts for measurement error in each latent construct.

## Common Mistakes & Pro Tips

- Choose CB-SEM vs. PLS-SEM based on your research goal (theory testing vs. prediction) and your data characteristics (sample size, normality) -- not by default or convenience.
- SEM requires strong theoretical grounding before you begin -- it's a confirmatory technique, not an exploratory one, for testing pre-specified relationships.
- Get comfortable with the measurement model / structural model distinction before diving into either type of SEM -- confusing the two is a foundational error that cascades through the whole analysis.""",

"PLS-SEM Step by Step": """## Overview

A PLS-SEM analysis follows a consistent, non-negotiable sequence -- and most student errors happen from skipping ahead to the structural model before the measurement model has actually passed its checks.

## Key Concepts

- **Step 1, Measurement Model**: indicator reliability, internal consistency (composite reliability, Cronbach's alpha), convergent validity (average variance extracted, AVE), and discriminant validity (HTMT ratio).
- **The most commonly flagged issue**: reverse-coded items that weren't handled correctly before analysis, which can silently break reliability and validity statistics.
- **Step 2, Structural Model** (only after Step 1 passes): path coefficients, R-squared for endogenous constructs, effect sizes (f-squared), and predictive relevance (Q-squared).
- **Bootstrapping** (typically 5,000 subsamples) generates significance tests for path coefficients, since PLS-SEM doesn't assume a known sampling distribution the way traditional regression does.

## Worked Example

A researcher includes a reverse-coded item ("I rarely feel satisfied with my job") within a scale otherwise worded positively, but forgets to reverse-score it before analysis. The item's correlation with the rest of the scale comes out strongly negative, tanking the construct's Cronbach's alpha and composite reliability -- a measurement model failure that looks like a data problem but is actually a coding oversight, and one of the single most common issues flagged in PLS-SEM defenses.

## Common Mistakes & Pro Tips

- Before running anything, create an explicit item-by-item checklist of which items are reverse-coded and confirm each was correctly re-scored in your dataset.
- Never proceed to the structural model until every measurement model criterion (reliability, convergent validity, discriminant validity) has passed -- a structural model built on a failing measurement model isn't salvageable by better structural results.
- Report HTMT ratios, not just the older Fornell-Larcker criterion, for discriminant validity -- HTMT is now the more widely accepted standard in current PLS-SEM literature.""",

"Survival Analysis Fundamentals": """## Overview

Survival analysis handles a data problem regular regression can't: time-to-event data with censoring, where some subjects haven't yet experienced the event of interest by the end of your study.

## Key Concepts

- **Censoring**: when a subject's event hasn't occurred by the study's end (or they drop out), their data is "censored" -- they're not excluded, but their incomplete follow-up must be handled correctly, not discarded.
- **Kaplan-Meier estimator**: a non-parametric picture of survival probability over time, usually the first descriptive step in any survival analysis.
- **Log-rank test**: compares survival curves between groups, answering "do these groups differ in their survival experience overall?"
- **Cox proportional hazards regression**: models the effect of multiple covariates on survival time while correctly handling censored data.
- **The proportional hazards assumption** needs explicit checking (commonly via Schoenfeld residuals), not just assuming it holds.

## Worked Example

A study tracks 100 post-surgical patients for complications over 12 months. By month 12, 30 patients experienced the complication, 60 completed the study without it, and 10 were lost to follow-up at various points. Simply excluding the 10 lost-to-follow-up patients would waste real information about how long they survived complication-free before dropping out -- survival analysis correctly incorporates their partial (censored) follow-up time instead of discarding it.

## Common Mistakes & Pro Tips

- Never simply delete censored observations -- that discards real information and can bias your results.
- Always check the proportional hazards assumption before trusting a Cox regression's coefficients -- a violation changes how (and whether) you can interpret them.
- Kaplan-Meier curves are a strong visual complement to your Cox regression results in a results chapter -- use both together, not one instead of the other.""",

"Firth Logistic Regression for Rare Events": """## Overview

Standard logistic regression struggles when you have rare outcomes or small samples -- coefficients can become unstable or fail to converge entirely, a problem known as separation. Firth's method exists specifically to correct this.

## Key Concepts

- **Separation**: occurs when a predictor (or combination of predictors) perfectly or near-perfectly predicts the outcome, causing standard logistic regression's estimates to become unstable or infinite.
- **Firth's penalized likelihood approach**: adds a small bias-reduction term to the estimation process, producing stable, interpretable estimates even under separation or with rare events.
- **When this comes up**: clinical and comparative studies with small samples -- surgical outcome studies comparing two techniques, for instance, where a complication occurs in only a handful of cases.
- **The real skill**: recognizing when standard logistic regression is quietly failing (unusually large standard errors, coefficients that seem implausibly extreme) rather than trusting an output that looks superficially fine.

## Worked Example

A study compares complication rates between two surgical techniques, with only 3 complications total across 80 patients. Standard logistic regression produces a wildly large coefficient and standard error for technique type -- a sign of near-separation given how rare the outcome is. Firth's penalized regression produces a much more stable, defensible estimate for the same comparison, which is why it's become the standard approach for exactly this kind of small-sample, rare-event clinical comparison.

## Common Mistakes & Pro Tips

- Watch for unusually large coefficients or standard errors in standard logistic regression -- this is often a sign of separation, not a genuinely huge effect.
- Firth's method is now available as a standard option in R (the `logistf` package) and most major statistical software -- there's rarely a reason not to use it when rare events are involved.
- Report that Firth's method was used and why (rare outcome, small sample) -- panels in clinical fields specifically look for this justification.""",

"Moderated Mediation and Complex PLS-SEM Models": """## Overview

Real theoretical models often combine mediation and moderation in the same structure. Moderated mediation tests whether an indirect effect itself depends on the level of a moderating variable -- genuinely advanced territory even for experienced researchers.

## Key Concepts

- **Conditional indirect effects**: rather than a single mediation estimate, you get several -- typically calculated at the moderator's mean, and one standard deviation above and below it.
- **In PLS-SEM**, this means adding interaction terms to *specific structural paths*, not the whole model uniformly.
- **Index of moderated mediation**: a formal test of whether the indirect effect genuinely differs across levels of the moderator, rather than just eyeballing the conditional estimates.
- **Sequencing matters**: get your basic measurement model rock-solid (reliability, validity) before attempting this level of structural complexity -- complex models built on shaky foundations rarely hold up.

## Worked Example

A study proposes that "training" improves "performance" through increased "confidence" (mediation), but that this indirect effect is stronger for employees with low prior experience than high prior experience (moderation of the mediation pathway by experience level). The analysis reports three conditional indirect effects -- for low, average, and high experience -- rather than a single overall mediation estimate, revealing that the training-to-confidence-to-performance pathway is meaningfully weaker among highly experienced employees.

## Common Mistakes & Pro Tips

- Don't attempt moderated mediation without a specific theoretical reason to expect the indirect effect to vary by the moderator -- this is not a technique to apply exploratively.
- Always report the index of moderated mediation itself, not just the conditional indirect effects at each level -- the index is the formal test of whether moderation is actually occurring.
- This level of model complexity demands larger sample sizes than simple mediation or simple moderation alone -- budget for this in your sampling plan.""",

"Handling Missing Data the Right Way": """## Overview

How you handle missing data can change your results as much as your choice of statistical test, yet it's often treated as an afterthought rather than a deliberate methodological decision.

## Key Concepts

- **Missingness mechanisms**: missing completely at random (MCAR), missing at random (MAR), or missing not at random (MNAR) -- this classification determines which handling methods are even statistically valid.
- **Listwise deletion**: simple, but can badly bias results under MAR or MNAR conditions -- it's only safe under MCAR, and even then it wastes information.
- **Multiple imputation**: the current gold standard for MAR data, generating several plausible completed datasets and pooling results across them rather than guessing a single replacement value.
- **MNAR is the hardest case**: it requires modeling the missingness mechanism itself, which is complex and often requires sensitivity analyses rather than a single definitive fix.

## Worked Example

In a salary survey, higher earners are less likely to disclose their income (missingness related to the very value that's missing -- MNAR). Simply deleting those non-responses (listwise deletion) would systematically underestimate the true average salary, because the missing values are disproportionately from the high end of the distribution. Multiple imputation using other available variables (job title, tenure, department) as predictors would produce a far less biased estimate than deletion.

## Common Mistakes & Pro Tips

- Diagnose your missingness mechanism explicitly before choosing a handling method -- don't default to listwise deletion out of convenience.
- Report your missing data rate and handling method in your methodology chapter -- this is increasingly expected, not optional, in quantitative reporting.
- Multiple imputation software (like R's `mice` package) makes this far more accessible than it once was -- there's rarely a strong justification for simple deletion when MAR is plausible.""",

"Publishing and Peer Review for Quantitative Studies": """## Overview

Getting a quantitative study published involves a distinct set of expectations beyond a thesis defense -- knowing them in advance smooths what can otherwise be a frustrating review process.

## Key Concepts

- **Pre-registration**: increasingly expected for confirmatory (hypothesis-testing) studies -- registering your hypotheses and analysis plan before data collection, to distinguish planned analyses from exploratory ones.
- **Complete reporting**: all measures and conditions used in the study, not just the significant findings -- selective reporting is a well-documented threat to the credibility of published research.
- **Data and code availability statements**: an increasingly standard requirement, reflecting the field's broader push toward reproducibility.
- **Reporting guidelines by study type**: STROBE for observational studies, CONSORT for randomized trials -- citing the specific guideline you followed in your methods section materially improves your odds of a smooth review.

## Worked Example

A manuscript reporting a randomized controlled trial explicitly follows the CONSORT checklist, includes a flow diagram showing participant recruitment and attrition at each stage, and reports all pre-specified outcomes (not just the significant ones). Reviewers familiar with CONSORT can quickly verify completeness against the checklist, which meaningfully speeds up and smooths the review process compared to a manuscript that doesn't reference any reporting standard.

## Common Mistakes & Pro Tips

- Identify the correct reporting guideline for your study design early, and structure your methods and results sections around it from the start, not retrofitted before submission.
- Report all measured outcomes, including non-significant ones -- selective reporting is one of the most scrutinized issues in current peer review.
- If pre-registration wasn't done, clearly label any exploratory analyses as exploratory rather than presenting them as confirmatory hypothesis tests.""",
}
RICH_CONTENT["ai-ml-for-practitioners"] = {
"What Machine Learning Actually Is (and Isn't)": """## Overview

Machine learning is, at its core, a set of methods for finding patterns in data and using them to make predictions on new data -- it is not magic, and not automatically better than a well-specified statistical model.

## Key Concepts

- **Supervised learning**: training a model on labeled data, where you already know the outcome for each example, so the model learns the mapping from inputs to outputs.
- **Unsupervised learning**: finds structure in data with no labels at all -- clustering similar customers together, for instance, with no predefined "correct" grouping.
- **ML vs. traditional statistics**: less a difference in the underlying math (much of it overlaps heavily) and more a difference in goal -- statistics traditionally prioritizes interpretability and inference, ML traditionally prioritizes predictive accuracy, sometimes at the cost of interpretability.
- **Reinforcement learning** (a third major category, less common in typical business applications): learning through trial-and-error interaction with an environment, guided by rewards and penalties.

## Worked Example

A hospital wants to predict which patients are at risk of readmission. A supervised learning approach uses historical data where the outcome (readmitted or not) is already known, training a model to recognize the patterns associated with readmission. An unsupervised approach, by contrast, might instead group patients into clusters based on similarity across many variables, without knowing in advance which cluster relates to readmission risk -- a fundamentally different task, useful for exploration rather than prediction.

## Common Mistakes & Pro Tips

- Don't reach for machine learning by default -- a well-specified logistic regression is often more interpretable and just as accurate for many structured, tabular business problems.
- Match your method to your actual goal: prediction accuracy vs. understanding *why* a relationship exists are different objectives that call for different tools.
- "Machine learning" and "artificial intelligence" are often used interchangeably in casual conversation but mean different things technically -- know the distinction when communicating with technical stakeholders.""",

"Classification vs Regression Problems": """## Overview

The first decision in any supervised learning project is what kind of outcome you're predicting -- this single decision determines which entire family of algorithms and evaluation metrics is even appropriate.

## Key Concepts

- **Classification problems** predict a category: will this customer churn or not, is this transaction fraudulent or not, which of five categories does this image belong to.
- **Regression problems** (in the ML sense, same underlying idea as statistical regression) predict a continuous number: next month's revenue, a patient's expected recovery time.
- **Algorithm variants**: logistic regression, decision trees, and random forests all have both classification and regression versions -- but you must select the correct variant for your problem type.
- **Evaluation metrics differ completely**: accuracy, precision, recall, and F1-score for classification; RMSE (root mean squared error) and R-squared for regression.

![Diagram: A decision tree splitting data into purer groups](/static/diagrams/decision-tree.svg)

## Worked Example

A retailer wants to predict "will this customer make a purchase in the next 30 days" (classification -- yes/no) versus "how much will this customer spend in the next 30 days" (regression -- a dollar amount). These require entirely different model setups, different evaluation approaches, and answer genuinely different business questions, even though they might draw on the exact same underlying customer data.

## Common Mistakes & Pro Tips

- Misidentifying your problem type early cascades into every later step -- confirm classification vs. regression before choosing an algorithm or evaluation metric.
- For classification with imbalanced classes (e.g., 95% non-fraud, 5% fraud), accuracy alone is misleading -- precision, recall, and F1-score matter far more in that scenario.
- Some problems can be framed either way -- predicting "will revenue exceed $10,000" (classification) versus "predict exact revenue" (regression) -- choose based on what decision the prediction will actually inform.""",

"Training, Validation, and Test Sets": """## Overview

A model that performs beautifully on the data it was trained on and poorly on new data is worthless in practice -- this is why you never evaluate a model on the same data it learned from.

## Key Concepts

- **Training set**: the data the model actually learns patterns from.
- **Validation set**: used to tune hyperparameters and make development decisions -- a second, separate check that isn't used for learning itself.
- **Test set**: touched exactly once, at the very end, to get an honest, unbiased estimate of real-world performance.
- **Cross-validation** (commonly k-fold): rotates which portion of your data serves as validation across several rounds, giving a more stable performance estimate when your dataset is limited in size.

![Diagram: Splitting a dataset into training, validation, and test sets](/static/diagrams/train-val-test-split.svg)

## Worked Example

A model achieves 98% accuracy on its training data but only 71% on a held-out test set -- a massive gap that reveals the model memorized quirks of the training data rather than learning generalizable patterns. Without the discipline of a separate test set, the 98% figure alone would have created dangerously false confidence about the model's real-world performance.

## Common Mistakes & Pro Tips

- Never use your test set more than once, and never use it to make any development decisions -- doing so effectively turns it into a second validation set and inflates your final performance estimate.
- With small datasets, k-fold cross-validation (commonly k=5 or k=10) gives a more reliable estimate than a single train/validation split.
- Always report both training and test performance -- a large gap between them is itself an important diagnostic, not just a footnote.""",

"Overfitting and How to Avoid It": """## Overview

Overfitting happens when a model learns the noise in your training data rather than the underlying signal -- it memorizes rather than generalizes, performing far worse on new data than its training performance would suggest.

## Key Concepts

- **Signs of overfitting**: a large gap between training accuracy and validation accuracy, and models that get more complex without actually improving on held-out data.
- **Regularization** (L1/L2): penalizes overly complex models directly within the training process, discouraging the model from relying too heavily on any single feature.
- **Simplifying the model**: fewer parameters or a shallower tree structure often generalizes better than a maximally complex one, especially with limited data.
- **More training data**: often the single most effective countermeasure, when it's actually available.
- **Cross-validation discipline**: using it religiously, rather than trusting a single train/test split, catches overfitting that a lucky single split might hide.

## Worked Example

A decision tree grown to full depth achieves 100% accuracy on training data by essentially memorizing every individual training example -- including noise and outliers specific to that particular dataset. Pruning the tree (limiting its maximum depth) reduces training accuracy to 92%, but *improves* test accuracy from 68% to 85% -- a textbook illustration of how reducing model complexity can improve real-world performance even as it reduces training performance.

## Common Mistakes & Pro Tips

- A model with perfect or near-perfect training accuracy should raise immediate suspicion of overfitting, not celebration.
- Regularization strength (how heavily you penalize complexity) is itself a hyperparameter -- tune it using your validation set, not your test set.
- The disciplined anti-overfitting practices used in serious production ML pipelines -- extensive cross-validation, held-out test sets, regularization, monitoring for training/validation gaps -- exist precisely because this failure mode is easy to fall into and costly once deployed.""",

"Feature Engineering: Where Most of the Real Work Happens": """## Overview

The features (input variables) you feed a model usually matter more than the algorithm you choose -- a well-engineered feature set with a simple model regularly beats a sophisticated model on raw, unprocessed data.

## Key Concepts

- **Interaction terms**: creating new features that capture how two variables combine (e.g., "price per square meter" from "price" and "area").
- **Categorical encoding**: one-hot encoding, ordinal encoding, and target encoding each fit different situations -- picking the wrong one can genuinely hurt model performance.
- **Feature scaling**: standardizing numeric features so no single feature dominates purely because of its raw magnitude (e.g., "income in dollars" vs. "age in years" on very different scales).
- **Extracting structure from complex data**: pulling meaningful components from dates (day of week, is-holiday flags) or text, rather than feeding raw, unprocessed values into a model.

## Worked Example

A model predicting retail sales performs modestly using raw "date" as a feature. Engineering that single field into "day of week," "is weekend," "is holiday," and "days until next holiday" dramatically improves performance -- the raw date itself carried little direct predictive signal, but the derived features captured the actual patterns driving sales fluctuations.

## Common Mistakes & Pro Tips

- Budget real project time for feature engineering -- it's frequently where the majority of a practitioner's actual working time goes, not model tuning.
- Be careful with target encoding (encoding a category by its average outcome value) -- done carelessly, it can leak information from your target variable into your features, producing misleadingly optimistic results.
- Always scale features before using distance-based algorithms (like k-nearest neighbors) or regularized models -- unscaled features can silently distort these methods' results.""",

"Tree-Based Models: Decision Trees, Random Forests, and Gradient Boosting": """## Overview

Tree-based methods are a workhorse of applied machine learning because they handle mixed data types well and require relatively little preprocessing compared to many other algorithm families.

## Key Concepts

- **Decision trees**: split data repeatedly on feature thresholds to separate classes or predict values, but tend to overfit heavily on their own without pruning or depth limits.
- **Random forests**: average many trees trained on random subsets of data and features, trading some interpretability for much better generalization than a single tree.
- **Gradient boosting** (XGBoost, LightGBM): builds trees sequentially, each one correcting the errors of the ones before it, and frequently wins on structured, tabular data -- the kind most business and research applications actually involve.
- **Feature importance**: tree-based models naturally produce interpretable rankings of which features mattered most to the model's predictions, useful for both interpretation and communication.

![Diagram: How a decision tree splits data](/static/diagrams/decision-tree.svg)

## Worked Example

A single decision tree predicting customer churn achieves 74% test accuracy and is prone to overfitting on any particular training sample. A random forest of 200 such trees, each trained on a different random subset of data and features, achieves 85% test accuracy with much more stable performance across different data samples -- the averaging effect across many imperfect, differently-overfit trees produces a far more robust combined prediction.

## Common Mistakes & Pro Tips

- A single decision tree is rarely your best production model -- it's most useful as an interpretable baseline or a building block within an ensemble like a random forest.
- Gradient boosting models are more sensitive to hyperparameter tuning than random forests -- budget real time for this step if you choose XGBoost or LightGBM.
- Use feature importance rankings as a starting point for interpretation, not a final causal explanation -- they show what mattered to the *model's predictions*, not necessarily true real-world causal drivers.""",

"Deploying a Model Responsibly": """## Overview

A model that performs well in a notebook isn't automatically ready for production -- deployment introduces a distinct set of risks that development-stage evaluation can miss entirely.

## Key Concepts

- **Data leakage**: information from outside the training set that inflated your performance estimates during development -- a frequent, subtle cause of models that look great in testing but fail in production.
- **Genuinely held-out testing**: test on data collected *after* model development, not just a random split of existing historical data, whenever feasible.
- **Concept drift**: real-world data patterns shift over time in ways your original training data never captured, gradually degrading a deployed model's performance if left unmonitored.
- **Documentation of limitations**: the population a model was actually trained and validated on should be documented explicitly -- deploying outside that population is one of the most common and consequential production failures.

## Worked Example

A credit risk model trained and validated entirely on pre-pandemic economic data is deployed without retraining during a period of unusual economic disruption. Its predictions, calibrated to a very different economic environment, become systematically unreliable -- a textbook case of concept drift that ongoing performance monitoring (comparing live prediction accuracy against actual outcomes) would have caught early, before it caused real financial harm.

## Common Mistakes & Pro Tips

- Build a data leakage checklist specific to your project -- check whether any feature could only be known *after* the outcome occurs (a common, easy-to-miss leakage source).
- Set up ongoing performance monitoring before deployment, not as an afterthought -- comparing live predictions against eventual real outcomes is how concept drift gets caught early.
- Document your model's training population and known limitations in plain language, accessible to non-technical stakeholders who will rely on its outputs.""",
}
RICH_CONTENT["data-management-essentials"] = {
"What Good Data Structure Looks Like": """## Overview

Well-structured data follows a simple rule: one row per observation, one column per variable, and consistent data types within each column. Almost every downstream analysis problem traces back to a violation of this "tidy data" principle.

## Key Concepts

- **One row, one observation**: each row should represent exactly one instance of whatever you're measuring -- mixing observation levels in one table (some rows per customer, others per transaction) breaks downstream analysis.
- **One column, one variable**: embedding multiple variables in a single column (a "name" field containing both first and last name) forces error-prone parsing later.
- **Consistent units within a column**: mixing kilograms and pounds in the same "weight" column silently corrupts any calculation on that field.
- **Avoid merged cells and multiple header rows**: common in hand-built spreadsheets, and one of the most reliable ways to break automated analysis tools.

## Worked Example

A spreadsheet tracks sales with a column labeled "Amount" that mixes values in both USD and PHP without indicating which currency applies to which row. Any total or average computed on this column is meaningless until the currencies are separated -- a problem that's completely avoidable by using two separate columns ("amount" and "currency") from the start.

## Common Mistakes & Pro Tips

- Design your data entry template *before* collecting a single real row -- retrofitting structure onto already-collected messy data costs far more time than getting it right initially.
- If you find yourself needing to "split" a column during analysis, that's a strong signal it should have been multiple columns from the start.
- Test your template with a handful of realistic dummy records before full deployment -- structural problems are far cheaper to catch early.""",

"Data Cleaning Fundamentals": """## Overview

Real data is never clean on arrival. Data cleaning is not a one-time chore before "real" analysis begins -- it's a deliberate, documentable process with its own set of best practices.

## Key Concepts

- **Missing values**: need a deliberate strategy -- deletion, imputation, or flagging -- chosen based on *why* the data is missing, not filled in reflexively.
- **Duplicate records**: especially common after merging datasets from multiple sources, and need explicit detection rules rather than a visual scan.
- **Inconsistent categorical values**: "Male," "M," "male" all meaning the same thing need standardizing before any grouping or analysis.
- **Outliers need investigation, not automatic deletion**: some are genuine data entry errors; others are the most interesting finding in your dataset.

![Diagram: The data cleaning pipeline from raw to documented data](/static/diagrams/data-cleaning-pipeline.svg)

## Worked Example

A dataset merged from three regional offices has "Manila," "manila," and "MNL" all representing the same city in different rows. Grouping by city without first standardizing these values would incorrectly split what should be one group into three separate, artificially small groups -- silently distorting any analysis that aggregates by location.

## Common Mistakes & Pro Tips

- Document every cleaning decision you make -- a cleaning process nobody (including future you) can reconstruct later is itself a data quality risk.
- Investigate outliers before removing them -- an unusually high sales figure might be a data entry error, or it might be your single most important record.
- Build a standardized value-mapping table for recurring categorical inconsistencies (like city names or department labels) so cleaning is reproducible across future data batches.""",

"Data Validation Rules": """## Overview

Validation catches errors at the point of entry, which is far cheaper than catching them during analysis -- prevention beats cleanup in nearly every case.

## Key Concepts

- **Range checks**: an age field shouldn't accept 250; a percentage field shouldn't accept 150.
- **Format checks**: a date field should reject non-date text before it ever enters the dataset.
- **Consistency checks**: an end date shouldn't precede a start date -- a logical relationship between two fields, not just a single-field rule.
- **Referential checks**: a foreign key (like a customer ID in a sales record) should match an existing record in the customer table.

## Worked Example

A form allows free-text entry for "Date of Birth" without format validation, resulting in entries like "1990," "January 1990," and "01/1990" all representing roughly the same information in incompatible formats. A simple date-picker or format-validated field at entry time would have prevented every one of these downstream cleaning headaches from ever occurring.

## Common Mistakes & Pro Tips

- Build validation into your data entry forms or spreadsheet templates directly (data validation rules in Excel/Google Sheets, or form-level constraints) -- relying on manual review after the fact catches far less.
- Range and format checks are cheap to build and catch the majority of common entry errors -- prioritize these first if you're validation-constrained on time.
- Referential checks matter most when combining data from multiple sources or systems -- this is where "orphaned" records (referencing something that doesn't exist) most often creep in.""",

"Documentation and Metadata": """## Overview

A dataset without documentation is a liability, even to the person who created it, six months later. Documentation is what makes a dataset genuinely reusable rather than a one-time-use artifact.

## Key Concepts

- **A proper data dictionary** records, for every variable: its name, its meaning in plain language, its data type, its valid range or categories, and how it was derived if not collected directly.
- **Dataset-level metadata**: collection dates, sampling method, known limitations, and version history all belong alongside the data itself.
- **This isn't bureaucratic overhead**: it's what lets someone else -- or you, much later -- actually reuse the data correctly instead of guessing at what a column labeled "score_2" was supposed to mean.
- **Version history matters**: as a dataset is cleaned, corrected, or updated over time, tracking what changed and when prevents confusion about which version is authoritative.

## Worked Example

A researcher returns to a dataset six months after initial collection to run a follow-up analysis, but finds a column labeled "score_2" with no documentation of what it measures or how it was calculated. Without a data dictionary, reconstructing this meaning requires guesswork or, in the worst case, re-contacting original data sources -- entirely avoidable time loss that proper documentation at collection time would have prevented.

## Common Mistakes & Pro Tips

- Write your data dictionary *while* building your dataset, not after -- reconstructing variable definitions from memory later is unreliable and time-consuming.
- Include units of measurement explicitly in your data dictionary, not just the variable name -- "weight" alone doesn't tell you kilograms or pounds.
- Store your data dictionary alongside the dataset itself, not in a separate, easily-disconnected location.""",

"Master Data vs Transactional Data": """## Overview

Understanding this distinction prevents a lot of downstream confusion about how different types of data should actually be managed and governed.

## Key Concepts

- **Master data**: describes the core entities your organization deals with repeatedly -- customers, products, employees, locations -- and changes relatively rarely.
- **Transactional data**: records events involving those entities -- a specific sale, a specific claim, a specific login -- and grows continuously over time.
- **Master data needs**: strict deduplication and a single, authoritative source of truth for each entity.
- **Transactional data needs**: efficient handling of high volume more than exhaustive validation on every single field.

## Worked Example

A company has three different systems each storing a slightly different version of "Customer #4471's" address, due to updates made independently in each system over time. This is a master data governance failure -- without a single authoritative source of truth, reports pulling customer address data from different systems will silently produce inconsistent results, undermining trust in any report that depends on that field.

## Common Mistakes & Pro Tips

- Treating fast-growing transactional data with master-data-level manual review creates unsustainable bottlenecks -- match your governance intensity to the data type.
- Establish a single "system of record" for each master data entity (customers, products, etc.) and treat all other copies as derived, not authoritative.
- Master data quality problems compound over time -- an unresolved duplicate customer record from years ago still distorts every report that touches it today.""",

"Data Governance Basics": """## Overview

Data governance is the set of policies and responsibilities that determine who can access, modify, and be accountable for data across an organization -- not a bureaucratic afterthought reserved for large enterprises.

## Key Concepts

- **Data ownership**: who is accountable for a given dataset's accuracy and upkeep -- every important dataset should have a named owner, not an implied "everyone's responsibility" default.
- **Access control**: who can view or edit what -- especially important as datasets contain more sensitive personal or financial information.
- **Change logs**: for anything mission-critical, tracking what changed, when, and by whom.
- **Retention and deletion policy**: a clear policy for how long data is kept and when it's archived or deleted, both for storage efficiency and regulatory compliance.

## Worked Example

A small team shares a single spreadsheet with no defined owner and no access log. When a critical formula breaks, nobody can determine who changed it or when -- a problem a basic governance structure (a named data owner, a change log, and restricted edit access) would have prevented entirely, even without any large enterprise-grade tooling.

## Common Mistakes & Pro Tips

- Even a solo practitioner or small team benefits from writing these ownership and access decisions down explicitly, rather than relying on informal memory.
- Start with your most business-critical datasets when building out governance practices -- you don't need to govern everything with equal rigor on day one.
- Review your retention policy against any applicable data privacy regulations relevant to your industry and location -- this is increasingly a compliance requirement, not just good practice.""",

"Choosing Between Spreadsheets, Databases, and Data Warehouses": """## Overview

Not every project needs a database, and not every database needs to be a full warehouse -- picking the right tool for your actual scale saves significant time and avoids both under- and over-engineering.

## Key Concepts

- **Spreadsheets**: work well for small, mostly manual datasets a single person or small team manages directly, with low concurrency needs.
- **Relational databases**: become worthwhile once you have related tables, multiple concurrent users, or a need for real query performance beyond what a spreadsheet can handle.
- **Data warehouses**: become worthwhile once you're regularly combining data from multiple source systems specifically for reporting and analysis (covered in depth in the Data Warehousing Fundamentals course).
- **The scaling signal**: if you're regularly fighting spreadsheet performance limits, manually reconciling multiple files, or hitting version-control chaos with shared spreadsheets, it's a sign to move up a tier.

## Worked Example

A small team manages inventory in a shared spreadsheet, but as the team grows to 15 concurrent users regularly editing the same file, version conflicts and slow load times become a daily problem. Moving to a proper relational database with defined access controls and real concurrency support solves problems that no amount of spreadsheet workaround (locked cells, manual merge processes) can fully address at that scale.

## Common Mistakes & Pro Tips

- Don't over-engineer early -- building a full data warehouse for a five-person team's simple reporting needs is often unnecessary complexity and maintenance burden.
- Watch for the specific pain signals (concurrency conflicts, performance limits, multi-source reporting needs) rather than migrating tools based on trend or assumption alone.
- A relational database is often the right middle step between spreadsheets and a full warehouse -- don't feel pressured to skip straight to warehouse-scale tooling.""",
}
RICH_CONTENT["data-warehousing-fundamentals"] = {
"What a Data Warehouse Is (and Why Spreadsheets Aren't Enough)": """## Overview

A data warehouse is a centralized repository designed specifically for analysis and reporting, pulling together data from multiple operational systems into one consistent structure.

## Key Concepts

- **Why operational systems and warehouses are kept separate**: operational systems are optimized for fast individual transactions (recording one sale), not for aggregating millions of them for a report.
- **A warehouse's specific job**: periodically pull, clean, and restructure data specifically for querying and reporting, without slowing down the systems people rely on to actually run the business.
- **The scale problem spreadsheets hit**: manually combining exports from multiple systems becomes unsustainable well before an organization reaches genuine "big data" scale.
- **Consistency as the core value**: a warehouse gives every report and dashboard a single, consistent source of truth, rather than each report pulling and interpreting source data slightly differently.

## Worked Example

A retail company's point-of-sale system handles thousands of individual transactions per minute efficiently, but running a single query aggregating a full year of sales data directly against that same live system would slow down the checkout process for every customer currently shopping. A data warehouse solves this by periodically copying and restructuring that transaction data into a separate system built specifically for heavy analytical queries, leaving the operational system free to do its actual job.

## Common Mistakes & Pro Tips

- Don't run heavy analytical queries directly against operational (transactional) systems if you can avoid it -- this is exactly the problem warehouses exist to solve.
- A warehouse doesn't need to be enormous to be worthwhile -- the value comes from consistent structure and separation of concerns, not sheer data volume.
- Start warehouse design with your actual reporting questions in mind ("what do people need to ask of this data regularly?"), not with the source systems' existing structure.""",

"Dimensional Modeling: Facts and Dimensions": """## Overview

Dimensional modeling is the standard approach to structuring a data warehouse for reporting -- built around a clear distinction between measurable events and the descriptive context around them.

## Key Concepts

- **Fact tables**: hold the measurable events you care about -- a sale, a claim, a lab result -- along with numeric measures (amount, quantity, duration).
- **Dimension tables**: hold the descriptive context around those facts -- customer details, product details, time periods, locations -- that let you slice and filter the facts meaningfully.
- **The payoff**: a sales fact table paired with customer, product, and date dimension tables lets you answer "total sales by region, by month, by product category" without redesigning anything, because the dimensions already contain that descriptive structure.
- **Grain**: the level of detail a single row in your fact table represents (e.g., one row per individual transaction line item) -- getting this decision right early is one of the most consequential choices in dimensional modeling.

![Diagram: Star schema with a central fact table and surrounding dimensions](/static/diagrams/star-schema.svg)

## Worked Example

A sales fact table has one row per transaction, with columns for amount and quantity, plus foreign keys linking to Customer, Product, Date, and Location dimension tables. Answering "what were total sales in Cebu for electronics products in March" requires no new table design -- it's a straightforward query joining the fact table to the relevant dimensions and filtering on their attributes, because the dimensional structure was built to support exactly this kind of question from the start.

## Common Mistakes & Pro Tips

- Decide your fact table's grain explicitly and early -- changing it after significant data has been loaded is expensive and disruptive.
- Don't mix multiple grains in a single fact table (e.g., some rows per transaction, others per daily summary) -- this silently corrupts aggregations.
- Dimension tables should be designed around how people actually ask questions ("by region," "by month," "by category"), not around how the source system happens to be structured.""",

"ETL Basics: Extract, Transform, Load": """## Overview

ETL describes the standard process of moving data into your warehouse -- three distinct concerns that, regardless of which order you handle them in, all need deliberate attention.

## Key Concepts

- **Extract**: pulls raw data from source systems -- databases, APIs, exported files -- as the first step.
- **Transform**: cleans, standardizes, and restructures that data into your warehouse's dimensional model -- this is where data cleaning and validation rules actually get applied at scale.
- **Load**: writes the transformed data into warehouse tables, either replacing existing data or appending new records depending on your update strategy.
- **ELT as a modern variant**: load first, transform after, inside the warehouse itself -- increasingly common with modern cloud warehouses that have ample compute power for in-warehouse transformation.

![Diagram: The Extract, Transform, Load pipeline](/static/diagrams/etl-pipeline.svg)

## Worked Example

A company pulls daily sales data from its point-of-sale system (Extract), standardizes product names and currency formats and joins in customer demographic data (Transform), then writes the cleaned, structured result into the warehouse's fact and dimension tables (Load). If this pipeline runs nightly, every morning's reports reflect a consistent, fully-processed version of the previous day's activity.

## Common Mistakes & Pro Tips

- Build monitoring and alerting into your ETL pipeline from the start -- a silently failing nightly job can leave reports quietly stale for days before anyone notices.
- Decide your load strategy (full replace vs. incremental append) deliberately based on data volume and how far back historical accuracy needs to be guaranteed.
- ELT vs. ETL is a legitimate architectural choice, not a right-or-wrong debate -- the right choice depends on your specific platform's compute capabilities and data volume.""",

"Star Schema vs Snowflake Schema": """## Overview

These are the two standard approaches to structuring dimension tables in a warehouse, and choosing between them is a real design decision with practical tradeoffs.

## Key Concepts

- **Star schema**: keeps dimension tables denormalized -- flat, with some redundancy -- which makes queries simpler and faster because reporting tools need fewer joins to answer a question.
- **Snowflake schema**: normalizes dimension tables further, splitting them into related sub-tables, which reduces storage redundancy but adds query complexity.
- **The practical default**: for most reporting and BI use cases, star schema is the practical choice -- storage is cheap, and query simplicity matters more than eliminating redundancy.
- **When snowflake makes sense**: reach for it only when a dimension is genuinely large and complex enough that the normalization meaningfully pays off, rather than as a default modeling choice.

## Worked Example

A "Product" dimension in star schema format includes category and subcategory names directly as columns within the product table, even though this repeats the same category name across many product rows. In snowflake schema, category and subcategory would instead be split into separate linked tables. For most reporting tools, the star schema version answers "sales by category" with a single simple join, while the snowflake version requires an additional join -- a small but real difference in both query simplicity and performance.

## Common Mistakes & Pro Tips

- Default to star schema unless you have a specific, demonstrated reason to normalize further -- it's the better fit for the vast majority of reporting and BI workloads.
- Don't let a desire for "clean," normalized design override practical query performance and simplicity for your actual reporting tools and users.
- If you do use snowflake schema for a genuinely large dimension, document why -- this decision should be traceable to a specific scale or complexity justification.""",

"Slowly Changing Dimensions": """## Overview

Dimension data isn't actually static -- a customer's address changes, a product's category gets reclassified -- and how you handle these changes materially affects your historical reporting accuracy.

## Key Concepts

- **Type 1 (overwrite)**: simply replaces the old value with the new one, losing history but keeping the structure simple.
- **Type 2 (add new row)**: preserves history by creating a new row for each change, with effective-date columns marking which version was active when.
- **Type 3 (add new column)**: keeps limited history in additional columns (current value plus one previous value) -- a middle ground between Type 1 and Type 2.
- **The deciding question**: does your reporting need to reflect "as it was then" (favoring Type 2) or only "as it is now" (favoring Type 1)?

## Worked Example

A customer moves from Cebu to Manila partway through the year. With Type 1 handling, all historical sales to that customer now appear attributed to Manila, even the ones that occurred while they lived in Cebu -- distorting any "sales by region over time" report. With Type 2 handling, the customer dimension retains both address records with effective dates, so historical sales correctly stay attributed to Cebu for the period when that was actually their address.

## Common Mistakes & Pro Tips

- Decide your slowly-changing-dimension strategy per dimension attribute, not just once for the whole warehouse -- some fields (like a customer's name) may reasonably use Type 1 while others (like address, for regional reporting) need Type 2.
- Type 2 significantly increases table size over time -- factor this into your storage and performance planning for genuinely high-change-frequency dimensions.
- Always document which strategy applies to which dimension attribute -- this is easy to forget and hard to reverse-engineer later.""",

"Data Warehouse Performance and Indexing": """## Overview

A dimensional model that's theoretically correct can still perform poorly without deliberate attention to how it's actually queried in practice.

## Key Concepts

- **Indexing fact table foreign keys**: dramatically speeds up the join-and-aggregate queries reporting tools generate constantly against fact and dimension tables.
- **Partitioning large fact tables** (commonly by date): lets queries skip irrelevant partitions entirely, rather than scanning the whole table for every request.
- **Materialized views / pre-aggregated summary tables**: trade some storage and refresh complexity for much faster response times on your most common, heaviest reporting queries.
- **Query pattern awareness**: performance tuning should be driven by how the warehouse is actually queried in practice, not by generic best practices applied blindly.

## Worked Example

A dashboard querying five years of unindexed, unpartitioned transaction data takes 45 seconds to load, frustrating daily users. Partitioning the fact table by month (so queries for "this year" only scan relevant partitions) combined with proper indexing on the foreign keys used in the dashboard's joins brings load time down to under 2 seconds -- the same underlying data, restructured for how it's actually being queried.

## Common Mistakes & Pro Tips

- Identify your most frequently-run, heaviest queries first, and optimize specifically for those rather than trying to optimize everything uniformly.
- Partitioning by date is the most common and often most effective strategy for large fact tables, since most reporting naturally filters by a time range.
- Materialized views need a refresh strategy of their own -- decide how stale a pre-aggregated summary is allowed to be before it needs updating.""",

"Modern Cloud Data Warehouses": """## Overview

Cloud data warehouses (Snowflake, BigQuery, Redshift) have largely replaced traditional on-premises warehouses for new projects, fundamentally changing the underlying infrastructure while leaving the core modeling principles intact.

## Key Concepts

- **Separated storage and compute**: you pay for and scale each independently, rather than provisioning a single fixed-capacity system for both.
- **Elastic scaling**: run a heavy analytical query without provisioning permanent infrastructure for peak load -- compute scales up temporarily, then back down.
- **Cheap long-term storage**: store years of historical data economically, since storage and compute no longer scale together as a single bundled cost.
- **What didn't change**: the dimensional modeling principles from earlier lessons still apply directly -- the cloud platforms changed the infrastructure underneath, not the fundamental logic of organizing facts and dimensions for reporting.

## Worked Example

A company running a traditional on-premises warehouse had to provision hardware sized for their busiest reporting period (month-end close), leaving that capacity mostly idle the rest of the month. Moving to a cloud warehouse with separated storage and compute lets them scale compute up automatically during month-end close and back down afterward, paying only for the capacity actually used -- while the underlying star schema design they'd already built required no fundamental redesign to make the move.

## Common Mistakes & Pro Tips

- Migrating to a cloud warehouse is primarily an infrastructure decision, not a reason to abandon good dimensional modeling practices -- the same star schema principles still apply.
- Understand your chosen platform's specific pricing model (storage vs. compute, query-based vs. capacity-based) before committing -- cost structures vary meaningfully between providers.
- Cloud warehouses generally make it easier to experiment and scale, but query and schema design discipline still matters just as much for controlling both cost and performance.""",
}
RICH_CONTENT["business-intelligence-dashboards"] = {
"BI Tool Landscape: Choosing What Fits": """## Overview

Business intelligence tools generally fall into a few tiers, and the right choice depends far more on your actual constraints than on which tool is "best" in the abstract.

## Key Concepts

- **Spreadsheet-based tools**: still legitimate for small-scale, low-frequency reporting, especially for single-person or small-team use.
- **Dedicated BI platforms** (Power BI, Tableau, Looker): built specifically for interactive dashboards connected to live data sources, at the cost of more setup and licensing overhead.
- **Embedded / custom solutions**: built for a specific product's own reporting needs, offering maximum flexibility at the cost of build and maintenance effort.
- **The real deciding factors**: who needs to view the dashboard, how often the underlying data changes, your budget, and what your data sources already are.

## Worked Example

A five-person team needs a weekly sales summary and already keeps all its data in a single spreadsheet. A full dedicated BI platform would add licensing cost and setup complexity disproportionate to the actual need -- a well-organized spreadsheet with a simple chart may genuinely be the right tool here, at least until the team or data complexity grows meaningfully.

## Common Mistakes & Pro Tips

- Choosing a tool because it's popular or was mentioned in an article, rather than because it fits your actual data infrastructure and audience, is a common and costly mistake.
- Reassess your tool choice as your team and data needs grow -- the right tool at 5 users may not be the right tool at 50.
- Factor in who will actually maintain the dashboards long-term, not just who builds the first version -- tool complexity has an ongoing maintenance cost, not just a setup cost.""",

"Dashboard Design Principles That Actually Get Used": """## Overview

The most common dashboard failure isn't technical -- it's that nobody actually looks at it after the first week. Good design is what determines whether a dashboard becomes part of someone's routine or gets quietly abandoned.

## Key Concepts

- **Answer a specific, recurring question**: for a specific audience, rather than displaying every available metric "just in case."
- **Visual hierarchy**: put the most important number where the eye lands first (top-left in most reading patterns).
- **Grouping**: related metrics should be grouped together visually, not scattered based on arbitrary layout convenience.
- **Consistent color coding**: across the whole dashboard -- not different meanings for the same color in different sections, which quietly confuses viewers over time.
- **Avoid decorative chart junk**: 3D effects, unnecessary gridlines, and excessive color add visual noise without adding information.

![Diagram: A simple, well-organized executive dashboard](/static/diagrams/dashboard-mockup.svg)

## Worked Example

An early dashboard draft crams 25 metrics onto one screen with inconsistent colors (red meaning "bad" in one chart and "this quarter" in another). After redesign -- three key metrics prominently at the top, consistent color meaning throughout, and secondary detail moved to a drill-down view -- daily active usage of the dashboard by the sales team increases substantially, simply because it now answers their actual recurring questions clearly rather than overwhelming them with everything at once.

## Common Mistakes & Pro Tips

- If a viewer needs a legend to understand what a color means instead of the color making it obvious, reconsider the palette.
- Resist the temptation to add "just one more metric" to an already-focused dashboard -- every addition dilutes attention from what matters most.
- Test your dashboard with an actual intended viewer before finalizing it -- what seems obvious to the builder is often not obvious to the audience.""",

"Choosing the Right Chart for the Right Question": """## Overview

Different questions call for genuinely different chart types, and the wrong choice actively misleads a viewer even when the underlying data is completely correct.

## Key Concepts

- **Comparing categories**: bar chart.
- **Showing change over time**: line chart.
- **Showing part-to-whole relationships**: stacked bar, or sparingly, a pie chart (only with very few categories).
- **Showing relationship between two continuous variables**: scatter plot.
- **Showing distribution**: histogram or box plot.
- **The pie chart trap**: humans genuinely struggle to compare angles accurately, especially with many categories or similar-sized slices -- a simple bar chart communicates the same data far more clearly in almost every case.

## Worked Example

A report uses a pie chart with nine similarly-sized slices to show market share across nine competitors -- viewers genuinely cannot rank the competitors accurately just from the angles. Converting the same data to a simple sorted horizontal bar chart makes the ranking immediately, unambiguously clear at a glance, using the exact same underlying numbers.

## Common Mistakes & Pro Tips

- Default to a bar chart when in doubt between bar and pie -- it's rarely the wrong choice and almost always at least as clear.
- Never use a 3D chart variant -- the added visual depth distorts perceived proportions and adds no informational value.
- Match your chart type to the specific question the chart needs to answer, not to whichever chart type looks most visually interesting in the tool's gallery.""",

"Automating Recurring Reports": """## Overview

If you're manually rebuilding the same report every week, that time is almost always automatable -- and automation delivers consistency benefits beyond just saved time.

## Key Concepts

- **Scheduled refresh**: most BI tools support pulling live data on a set interval so the dashboard is always current without manual intervention.
- **Scheduled exports / API-triggered automation**: for reports that need to be pushed out (emailed, posted to a channel) rather than pulled by viewers.
- **The consistency win**: an automated report runs the same way every time, eliminating the small manual errors (a missed filter, a stale copy-paste) that creep into hand-built reports over weeks and months.
- **Monitoring automated pipelines**: an automated report that silently fails is worse than a manual one that's late but noticed -- build in failure alerts.

## Worked Example

A weekly sales report was manually rebuilt every Monday by copying data into a template, taking roughly two hours and occasionally including a stale filter left over from the previous week. Automating the pipeline to pull live data and refresh the report every Monday morning eliminates both the two hours of manual work and the recurring stale-filter error, since the automated process applies the exact same logic every single time.

## Common Mistakes & Pro Tips

- Set up failure alerts for any automated report pipeline -- a silent failure that goes unnoticed for weeks is a common and damaging automation pitfall.
- Start automation with your most time-consuming, most error-prone recurring report first, for the clearest immediate payoff.
- Document what the automated pipeline does and how to troubleshoot it -- automation that only one person understands creates a new kind of fragility.""",

"KPIs: Choosing Metrics That Actually Drive Decisions": """## Overview

A dashboard full of metrics nobody acts on is decoration, not business intelligence. A genuine key performance indicator earns its place by being tied directly to a real decision.

## Key Concepts

- **The decision test**: a real KPI should be directly tied to a decision someone will actually make differently depending on its value.
- **Ownership**: every KPI should be owned by a specific person or team accountable for moving it -- a metric with no owner tends to be ignored regardless of how important it seems.
- **Consistent measurement**: a KPI needs to be measured consistently over time for trends to be meaningful -- changing its definition midstream breaks historical comparison.
- **The vanity metric trap**: numbers that go up and to the right but don't connect to any decision are the most common trap in dashboard design.

## Worked Example

A dashboard prominently features "total page views" (a vanity metric that looks impressive but rarely drives specific action) alongside "conversion rate by traffic source" (a genuine KPI, since a low-performing traffic source directly informs a decision to reduce or improve that channel's spend). Removing the vanity metric and elevating the actionable one meaningfully sharpens what the dashboard's viewers actually do with the information.

## Common Mistakes & Pro Tips

- For every metric on a dashboard, ask: if this number changed dramatically tomorrow, would anyone do anything differently? If not, question whether it belongs there.
- Assign explicit ownership to your top-tier KPIs -- an unowned metric tends to drift out of anyone's actual attention over time.
- Revisit your KPI list periodically -- what was actionable at one stage of a business or project can become a vanity metric later as priorities shift.""",

"Connecting Live Data Sources": """## Overview

A dashboard is only as useful as the freshness of its underlying data -- and matching your data connection strategy to actual usage patterns is a real design decision, not a technical afterthought.

## Key Concepts

- **Direct live connections**: give the most current data but can slow down source systems under heavy query load.
- **Scheduled refreshes** (hourly, daily): reduce that load at the cost of data being slightly stale.
- **Matching freshness to usage**: an operations dashboard checked hourly needs different freshness than an executive summary reviewed once a week -- there's no single universally correct refresh strategy.
- **API-based connections**: increasingly common for pulling data from external tools and platforms into a unified dashboard.

## Worked Example

An operations team needs to react to inventory stockouts within the hour, so their dashboard uses a near-live connection refreshing every 15 minutes. A monthly executive summary reviewing quarterly trends doesn't need anything close to that freshness -- a nightly scheduled refresh is entirely sufficient and puts far less load on source systems. Applying the operations team's refresh frequency to the executive dashboard (or vice versa) would either waste system resources or fail to serve the actual need.

## Common Mistakes & Pro Tips

- Match refresh frequency to actual decision cadence, not to "as fresh as technically possible" by default -- unnecessary high-frequency refreshes waste system resources.
- Direct live connections to heavily-used operational systems can create real performance problems -- consider a replicated reporting copy instead for heavy dashboard query loads.
- Clearly display the "last updated" timestamp on every dashboard, regardless of refresh strategy, so viewers know exactly how current the data is.""",

"Making Dashboards People Actually Trust": """## Overview

Adoption fails just as often from trust problems as from design problems -- and trust, once lost, is hard to rebuild even after the underlying issue is fixed.

## Key Concepts

- **The consistency requirement**: if a number on a dashboard ever visibly contradicts a number from another report, viewers quietly stop trusting the whole dashboard, even if the discrepancy was explainable.
- **Explicit metric definitions**: document exactly what each metric means (does "active user" mean logged in this week or this month?) and keep that definition consistent everywhere it appears.
- **Data freshness transparency**: version and date-stamp your dashboards so viewers know exactly when the underlying data was last refreshed.
- **Ambiguity is the enemy**: unclear definitions or unclear freshness are among the fastest ways to erode confidence in an otherwise well-built report.

## Worked Example

Two dashboards report different "total customers" figures because one counts all-time signups and the other counts only currently active accounts -- neither is wrong, but the undocumented difference makes both look unreliable to anyone comparing them. Adding a clear, consistent definition ("Active Customers: logged in within the last 30 days") to both dashboards, and using it consistently, resolves what otherwise looks like an unexplained discrepancy.

## Common Mistakes & Pro Tips

- Maintain a single shared metric-definitions document across all your dashboards, so the same term always means the same thing everywhere it appears.
- Investigate and resolve any discrepancy between two reports immediately, even a minor one -- small unexplained inconsistencies are disproportionately damaging to overall trust.
- Prominently display data freshness on every dashboard -- ambiguity about how current the numbers are is one of the most common, avoidable trust failures.""",
}


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    total_updated, courses_touched = 0, 0
    try:
        for slug, lessons in RICH_CONTENT.items():
            course = db.query(models.Course).filter(models.Course.slug == slug).first()
            if not course:
                print(f"[missing] '{slug}' -- run earlier seed scripts first.")
                continue

            updated_here = 0
            for lesson in course.lessons:
                if lesson.title in lessons:
                    lesson.content = lessons[lesson.title]
                    updated_here += 1
                    total_updated += 1

            if updated_here:
                courses_touched += 1
                print(f"[{course.title}] rewrote {updated_here} lesson(s)")
            else:
                print(f"[{course.title}] no matching lessons found -- check titles")

        db.commit()
    finally:
        db.close()

    print(f"\nDone. {total_updated} lesson(s) rewritten with rich content across {courses_touched} course(s).")


if __name__ == "__main__":
    run()
