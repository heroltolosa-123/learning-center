"""
Elementary-level rewrite of the Basic Statistics course: plainer language,
two worked examples per lesson, and a real diagram in every single lesson.
This REPLACES the existing content for these 7 lessons (matched by title).

Usage:
    DATABASE_URL="postgresql://...your neon connection string..." python3 seed_basic_stats_elementary.py
"""
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import Base, engine, SessionLocal
from app import models

LESSONS = {
"Descriptive Statistics: Making Sense of Raw Numbers": """## Overview

Before you can say anything smart about a pile of numbers, you first need to describe what that pile actually looks like. That's all "descriptive statistics" means -- describing your data in simple, honest terms before you try to draw any conclusions from it.

## Let's Break It Down

Imagine you're a teacher and you have the exam scores of 30 students. Just staring at 30 numbers doesn't tell you much. Descriptive statistics gives you two questions to ask about any pile of numbers:

- **Where is the center?** This is "central tendency." The **mean** is the everyday average -- add everything up, divide by how many there are. The **median** is the middle value when you line everyone up from lowest to highest. The **mode** is whichever value shows up most often.
- **How spread out are the numbers?** This is "variability." The **range** is just the highest score minus the lowest. The **standard deviation** is a more precise way of asking: on average, how far does each score sit from the mean?

Here's the part people miss: two groups can have the *exact same average* and still be completely different in real life, depending on how spread out the scores are.

![Diagram: Same average, very different spread](/static/diagrams/spread-comparison.svg)

## Worked Example 1

Two sections of a class both average 75 on an exam. Section A's scores are all bunched between 70 and 80 -- every student is doing about the same. Section B's scores range from 40 to 100 -- some students are excelling, others are failing badly. If you only reported "both sections averaged 75," you'd completely hide the fact that Section B needs urgent, targeted help while Section A just needs a small overall push. The average alone lied to you by omission.

## Worked Example 2

A sari-sari store owner tracks daily sales for a month: mostly around ₱2,000-₱2,500 a day, except three days during a fiesta where sales spiked to ₱8,000. The mean daily sales might come out to ₱2,800 -- but that number is being pulled upward by just those three unusual days. The median (the middle value when you sort all 30 days) would be closer to ₱2,200, which better reflects a "typical" day. This is exactly why the mean can mislead you when a few extreme values are present -- the median is often the more honest number in that situation.

## Common Mistakes & Pro Tips

- Never report a mean without also reporting a measure of spread (range or standard deviation) -- the mean alone hides how consistent or scattered the data really is.
- When a few extreme values exist (like the fiesta sales spike), the median is usually a more honest "typical" number than the mean.
- Always sketch a quick histogram or boxplot before doing anything else with a new dataset -- your eyes will catch patterns a table of numbers won't.""",

"Probability Basics You Actually Need": """## Overview

Probability sounds intimidating, but you already use it every day without realizing it -- "there's a good chance it'll rain later" is a probability statement. For applied statistics, you only need a small, practical slice of full probability theory.

## Let's Break It Down

Probability is just a number between 0 and 1 (or 0% to 100%) that tells you how likely something is. A probability of 0 means "impossible." A probability of 1 means "certain." Everything else is somewhere in between.

A few ideas you'll actually use:

- **Independent events** don't affect each other. Flipping a coin and getting heads doesn't make the next flip more or less likely to be heads too -- the coin has no memory.
- **All possible outcomes** of an event can be listed out and counted. If you flip a coin twice, there are exactly 4 equally likely outcomes: heads-heads, heads-tails, tails-heads, tails-tails.
- **Conditional probability** is the chance of something happening *given that* something else already happened. This shows up constantly in medical testing: "given that this test came back positive, what's the actual chance the patient has the disease?" -- which, surprisingly, is often lower than people assume.

![Diagram: All 4 outcomes of flipping a coin twice](/static/diagrams/probability-basics.svg)

## Worked Example 1

Flip a fair coin twice. What's the probability of getting heads both times? Looking at the diagram above, there are 4 equally likely outcomes, and only 1 of them (heads-heads) is what we want. So the probability is 1 out of 4, or 25%. This is the core logic behind almost every probability calculation: count all the equally likely outcomes, then count how many of them match what you're looking for.

## Worked Example 2

A jeepney driver notices that about 1 out of every 5 passengers pays with a ₱500 bill needing change. If the next 3 passengers board one after another, does the driver "expect" one of them to pay with ₱500 just because the average is 1 in 5? No -- each passenger's payment is independent of the others, just like coin flips. The driver could easily get 3 passengers in a row with exact change, or 3 in a row all needing change from a ₱500 bill. The 1-in-5 figure describes the long-run pattern across hundreds of passengers, not a guarantee about any specific handful of them.

## Common Mistakes & Pro Tips

- Don't assume something is "due" to happen just because it hasn't happened in a while (this is called the gambler's fallacy) -- independent events truly have no memory.
- Conditional probability answers a different question than plain probability -- always be precise about what you're conditioning on.
- When in doubt, list out every possible outcome and count carefully. Most probability mistakes come from miscounting, not from bad logic.""",

"The Normal Distribution and Why It Matters": """## Overview

The normal distribution is the classic "bell curve" shape you've probably seen before -- and it matters because a huge amount of statistical theory quietly assumes your data looks something like it, even when you don't realize it.

## Let's Break It Down

Picture a histogram of adult heights in a big population. Most people cluster around the average height, with fewer and fewer people as you move toward "very short" or "very tall." That symmetric, hump-shaped pattern is the normal distribution.

Three facts make it so useful:

- It's perfectly symmetric around the mean -- the left half is a mirror image of the right half.
- A fixed percentage of data always falls within a certain distance of the mean, measured in "standard deviations": about 68% falls within 1 standard deviation, about 95% within 2, and about 99.7% within 3.
- Even when your raw data *isn't* shaped like a bell curve, the averages of many samples taken from that data tend to form a bell curve anyway, as your sample size grows. This is called the Central Limit Theorem, and it's the quiet reason so many statistical tests still work reasonably well even on messy, non-normal data.

![Diagram: The normal distribution with standard deviation bands](/static/diagrams/normal-distribution.svg)

## Worked Example 1

A class's exam scores have a mean of 70 and a standard deviation of 10. A student scores 85. How unusual is that? 85 is 15 points above the mean, which is 1.5 standard deviations above it. Since roughly 95% of scores fall within 2 standard deviations of the mean, and 68% within 1, a score 1.5 standard deviations up puts this student solidly in the top 10% or so of the class -- without needing to see anyone else's individual score.

## Worked Example 2

A barangay health worker measures the blood pressure of 200 residents. Most readings cluster around a normal range, with progressively fewer people as readings get unusually high or low in either direction -- a textbook bell-curve shape. Because the data follows this pattern, the health worker can use standard reference ranges (which assume a normal distribution) to flag which individual readings are unusual enough to warrant a follow-up visit, without having to manually compare each person to all 199 others.

## Common Mistakes & Pro Tips

- Not all data is normally distributed -- income, for example, is typically skewed with a long tail of very high earners. Always check before assuming.
- A histogram or Q-Q plot is a fast, visual way to check whether your data looks roughly normal.
- Remember the Central Limit Theorem's practical payoff: with a large enough sample, the *average* often behaves normally even when individual data points don't.""",

"Your First Hypothesis Test": """## Overview

A hypothesis test is really just a formal, disciplined way of asking: "is what I'm seeing in my data a real pattern, or could it just be random noise?"

## Let's Break It Down

Every hypothesis test, no matter how complicated it eventually gets, follows the exact same logical skeleton:

1. Start with a **null hypothesis** -- a boring, "nothing special is happening" claim (for example, "this coin is fair").
2. State an **alternative hypothesis** -- the more interesting claim you actually suspect (for example, "this coin is biased").
3. Collect data and calculate a **test statistic** -- a single number summarizing how far your data is from what the null hypothesis would predict.
4. Ask: **how likely would this result be, if the null hypothesis were actually true?** That likelihood is your p-value.
5. If that likelihood is low enough (conventionally below 5%, written as p < .05), you reject the null hypothesis in favor of the alternative.

The key thing to understand: you are never *proving* the alternative hypothesis is true. You're only saying the data would be surprising if the boring, "nothing's happening" explanation were correct.

![Diagram: The hypothesis testing process, step by step](/static/diagrams/hypothesis-testing-flow.svg)

## Worked Example 1

A factory claims its light bulbs last 1,000 hours on average. You test a sample of 30 bulbs and find they lasted an average of 970 hours. Is that meaningfully different from 1,000, or just normal variation? A one-sample hypothesis test asks exactly this: given normal manufacturing variation, how likely is it that a random sample of 30 bulbs would average as low as 970 hours if the true average really were 1,000? If that probability turns out to be very low, you'd reject the factory's claim.

## Worked Example 2

A tricycle terminal operator suspects that fares tend to be higher on rainy days. On 20 dry days, the average fare was ₱35. On 20 rainy days, the average fare was ₱42. Before concluding "rain really does raise fares," a hypothesis test checks whether a ₱7 difference this large would be unusual to see by pure chance alone, even if rain had no real effect. If the test shows this difference would be very unlikely under "no real effect," that supports the operator's suspicion; if a difference this size happens often by chance, the evidence isn't strong enough to draw that conclusion yet.

## Common Mistakes & Pro Tips

- "Failing to reject the null" is not the same as "proving the null is true" -- it just means your data didn't give strong enough evidence against it.
- Decide your significance threshold (commonly .05) before you look at your results, not after -- picking it afterward to fit what you want to conclude undermines the whole test.
- Practice this five-step logic on a simple one-sample test before moving on to comparisons between multiple groups -- the underlying reasoning never changes, only the formula.""",

"Understanding Confidence Intervals": """## Overview

A confidence interval gives you a realistic *range* for your answer instead of pretending you know the exact number -- and honestly, that range is often more useful than the single number by itself.

## Let's Break It Down

Say you survey 200 customers and find their average satisfaction score is 7.2 out of 10. Is the *true* average satisfaction across all your customers exactly 7.2? Almost certainly not -- you only surveyed a sample, not everyone. A confidence interval acknowledges this honestly by giving you a plausible range instead: "we're 95% confident the true average is somewhere between 6.9 and 7.5."

Here's the careful, correct way to think about that 95%: if you repeated this entire survey process many, many times, about 95% of the intervals you'd calculate would contain the true average. It is *not* saying "there's a 95% chance the true value is in this one specific interval" -- that's a common but subtly incorrect shortcut.

What really matters practically: a **narrow** interval means your estimate is precise (often from a bigger sample). A **wide** interval means there's a lot of uncertainty (often from a smaller sample or more variable data).

![Diagram: A point estimate with its confidence interval](/static/diagrams/confidence-interval.svg)

## Worked Example 1

Two market researchers both estimate average monthly spending at a mall to be ₱5,000. Researcher A's confidence interval is ₱4,800 to ₱5,200 (narrow, precise). Researcher B's is ₱2,000 to ₱8,000 (wide, imprecise). Even though both reported the same central estimate, Researcher A's finding is far more useful for planning purposes -- Researcher B's wide interval is really admitting "we're not very sure," even if that wasn't said explicitly.

## Worked Example 2

A small barangay clinic estimates that 30% of visiting patients have high blood pressure, based on just 25 patients, giving a wide confidence interval of roughly 14% to 50%. A larger city hospital estimates the same 30% figure from 2,000 patients, giving a tight interval of about 28% to 32%. Both report "30%" as their headline number, but the hospital's estimate is dramatically more trustworthy simply because of its much larger sample size -- the confidence interval is what reveals that difference, which the headline number alone would hide.

## Common Mistakes & Pro Tips

- Never say a specific interval has "a 95% chance of containing the true value" -- describe it as the *method's* long-run reliability instead.
- Always report a confidence interval alongside any key estimate, not just the single number -- it's expected practice in serious research and business reporting alike.
- A surprisingly wide interval is itself useful information: it's telling you the estimate needs a bigger sample before anyone should act on it confidently.""",

"Correlation: What It Does and Doesn't Tell You": """## Overview

Correlation tells you whether two things tend to move together -- but it cannot tell you *why*, and mixing those two questions up is one of the most common statistical mistakes people make, in both schoolwork and real life.

## Let's Break It Down

Correlation is measured with a number between -1 and +1, usually called "r":

- **Close to +1** means as one variable goes up, the other tends to go up too (a positive relationship).
- **Close to -1** means as one variable goes up, the other tends to go down (a negative relationship).
- **Close to 0** means there's little to no straight-line relationship between them.

Here is the single most important sentence in this entire lesson: **correlation is not causation.** Just because two things move together does not mean one causes the other. Sometimes a hidden third factor is driving both of them at once.

## Worked Example 1

Ice cream sales and drowning incidents are positively correlated -- in months when ice cream sales go up, drowning incidents also go up. Does eating ice cream cause drowning? Of course not. Both are driven by a third factor: hot weather. Hot weather causes more ice cream buying *and* more swimming (which increases drowning risk). The correlation between ice cream and drowning is real, but the causal story behind it involves a variable neither one directly controls.

![Diagram: A scatter plot showing two variables moving together](/static/diagrams/regression-scatter.svg)

## Worked Example 2

A tutoring center notices that students who attend more review sessions tend to score higher on exams -- a clear positive correlation. Does attending sessions *cause* the higher scores? Probably, at least partly -- but a skeptical analyst would also ask: are more motivated, harder-working students both more likely to attend extra sessions *and* more likely to study harder on their own, regardless of the sessions? If so, some of that correlation might reflect student motivation rather than the sessions themselves. This doesn't mean the sessions don't help -- it means correlation alone can't cleanly separate "the sessions helped" from "the kind of student who attends sessions would have scored higher anyway."

## Common Mistakes & Pro Tips

- Always ask "could a third variable explain both of these?" before assuming a causal relationship from a correlation.
- A correlation near 0 rules out a straight-line relationship, but not necessarily a more complex, curved one -- always look at a scatter plot, not just the r value.
- In your own writing, use careful language: "is associated with" is honest; "causes" or "leads to" is a much stronger claim that needs a much stronger design (like a controlled experiment) to back it up.""",

"Chi-Square Tests for Categorical Data": """## Overview

When your data is made of categories rather than numbers -- yes/no, smoker/non-smoker, brand A/B/C -- the chi-square test is your standard tool for asking whether two categories are actually related.

## Let's Break It Down

Imagine you organize your data into a grid, with one category across the top and another down the side, and you count how many cases fall into each combination. This grid is called a contingency table.

The chi-square test compares what you *actually observed* in that table against what you'd *expect to see* if the two categories had absolutely nothing to do with each other. If the real counts are very different from that "no relationship" expectation, that's evidence the two categories genuinely are connected.

![Diagram: A contingency table comparing two categories](/static/diagrams/contingency-table.svg)

## Worked Example 1

A researcher wants to know if smoking status is related to a particular diagnosis. Looking at the contingency table above: 48 smokers were diagnosed, 32 smokers were not; 20 non-smokers were diagnosed, 100 non-smokers were not. If smoking truly had nothing to do with the diagnosis, you'd expect roughly the same *proportion* of diagnoses in both groups. Instead, a much higher share of smokers were diagnosed compared to non-smokers. The chi-square test formally checks whether this size of difference is too large to reasonably be explained by chance alone.

## Worked Example 2

A store owner wants to know whether customers' preferred payment method (cash, GCash, or card) differs by age group (young adult, middle-aged, senior). She builds a contingency table counting how many customers of each age group used each payment method. A chi-square test tells her whether payment preference and age group are genuinely related, or whether the differences she's noticing informally are small enough to just be normal day-to-day variation. If the test comes back significant, she has real evidence to justify offering different payment promotions to different age groups.

## Common Mistakes & Pro Tips

- Chi-square becomes unreliable when expected counts in any cell of the table are too small (typically below 5) -- in that case, Fisher's exact test is the safer choice.
- A significant chi-square result tells you *that* a relationship exists, not how strong it is -- report an effect size like Cramer's V alongside it for the full picture.
- Don't force continuous data (like exact age in years) into artificial categories just to run a chi-square test -- if a test built for continuous data is available and appropriate, it usually preserves more information.""",
}


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    course = db.query(models.Course).filter(models.Course.slug == "basic-statistics").first()
    if not course:
        print("[missing] basic-statistics course not found -- run seed_courses.py first.")
        return

    updated = 0
    for lesson in course.lessons:
        if lesson.title in LESSONS:
            lesson.content = LESSONS[lesson.title]
            updated += 1
            print(f"[updated] {lesson.title}")

    db.commit()
    db.close()
    print(f"\nDone. {updated}/{len(LESSONS)} lessons rewritten for Basic Statistics.")


if __name__ == "__main__":
    run()
