# BMI-vs-RFM fat depo correlations explanation
RFM vs BMI paper statistics and code
This script is doing a statistical comparison of how strongly two predictors — RFM and BMI — correlate with several fat depots, separately for men and women.
# Fat depo correlations
The key idea:
- For each fat depot (liver fat, visceral fat, etc.), it computes:
  - Spearman correlation between RFM and that depot
  - Spearman correlation between BMI and that depot
  - The correlation between RFM and BMI themselves
- Then it checks whether the two correlations are significantly different using a Steiger test.
- It also computes confidence intervals for each correlation.

What the functions do

# Fisher 95% confidence correlation coefficient. The Fisher z-test (or Fisher z-transformation) converts a Pearson sample correlation coefficient (r) into a normally distributed value (z) so you can test hypotheses or build confidence intervals. Because sample correlations are skewed—especially near 1 or -1—this transformation stabilizes the variance.
###

1) fisher_ci(r, n, z_crit=1.96)
This builds a 95% confidence interval for a correlation coefficient.

- r = correlation coefficient
- n = sample size
- z_crit = 1.96 for a 95% CI (roughly ±1.96 standard errors)


It uses Fisher’s z transform:
- z = arctanh(r)
- standard error ≈ 1 / sqrt(n - 3)
  
# arctanh is the inverse of tanh.

In plain terms:

tanh(x) squashes numbers into the range (-1, 1)
arctanh(y) takes a value y in (-1, 1) and returns the x such that tanh(x) = y
The formula is:

arctanh(y) = 0.5 * ln((1 + y) / (1 - y))

For example:

arctanh(0.5) ≈ 0.5493
because tanh(0.5493) ≈ 0.5
Why it is used here:

A correlation r is always between -1 and 1
But the sampling distribution of r is not symmetric and is bounded
Fisher’s z transform uses arctanh(r) to make the correlation behave much more like a normal variable.
z = np.arctanh(r)

means:

take the correlation coefficient r
transform it into Fisher’s z scale
Then later:

return np.tanh(z - z_crit * se), np.tanh(z + z_crit * se)

This converts the z-scale CI back into the original correlation scale, because tanh and arctanh are inverse operations.

So the flow is:

correlation r
transform with arctanh to z
do statistics in z space
transform back with tanh
This is standard in correlation inference because it makes the confidence interval and significance testing much more stable.

One important detail:

arctanh is only defined for values strictly between -1 and 1
if r is exactly ±1, then arctanh is infinite, which is why correlations very close to ±1 can be numerically tricky.
###

# tanh is the hyperbolic tangent function.

It looks like this:

tanh(x) = (e^x - e^-x) / (e^x + e^-x)

It has a few very useful properties:

it always returns a value between -1 and 1
it is odd:
tanh(-x) = -tanh(x)
it is smooth and monotonic increasing
it behaves like:
near 0: tanh(x) ≈ x
for large positive x: tanh(x) → 1
for large negative x: tanh(x) → -1

z = arctanh(r)
tanh(z) = r
This is why the function does:

np.tanh(z - z_crit * se), np.tanh(z + z_crit * se)

It transforms the confidence limits from the Fisher z scale back into the original correlation scale.

Example:

if z = 0.5
tanh(0.5) ≈ 0.4621
So:

arctanh(0.4621) ≈ 0.5
tanh(arctanh(0.4621)) = 0.4621
This pair of functions is mathematically inverse to each other, just like:

exp and log
sin and arcsin
Why this matters in statistics:

correlations must stay in (-1, 1)
Fisher z is a transformed scale where calculations are easier
after calculating the interval in z-space, tanh maps it back into a valid correlation range
So in plain English:

arctanh converts a correlation into a “more normal” scale
tanh converts it back

# Steiger Z test. A z-test is a way to check if a sample's average is genuinely different from a known population average, or if the difference is just due to random luck. It works best when your sample size is large (30 or more) and you already know the true standard deviation of the population.
###

2) steiger_1980(r_jk, r_jh, r_kh, n)
This is a significance test for whether two dependent correlations are different.

In this script:
- j = fat depot
- k = RFM
- h = BMI

So:
- r_jk = correlation(depot, RFM)
- r_jh = correlation(depot, BMI)
- r_kh = correlation(RFM, BMI)

The function transforms these into Fisher z values, computes a z-statistic that accounts for the fact that the two correlations share the same depot and are therefore dependent, and returns:
- z statistic
- two-sided p-value

# Interpretation:

- If the z is negative, it means the BMI correlation is stronger (in the negative/positive direction depending on sign)
- The code comments say: “Negative z => BMI correlates more strongly.”

3) analyse(sex)
This is the main worker.

For each sex:
- Filter the dataset to that sex
- Loop through each depot defined in DEPOTS
- Use complete cases only:
  - d = sub_sex[["RFM", "body_mass_index_2", col]].dropna()
- Compute:
  - r_rfm, p_rfm = spearmanr(RFM, depot)
  - r_bmi, p_bmi = spearmanr(BMI, depot)
  - r_rb = spearmanr(RFM, BMI)
- Run Steiger test:
  - steiger_1980(r_rfm, r_bmi, r_rb, n)
- Compute confidence intervals:
  - fisher_ci(r_rfm, n)
  - fisher_ci(r_bmi, n)
- Store results in a dictionary with fields like:
  - Sex
  - Fat depot
  - N
  - rho_RFM
  - RFM_CI_low / RFM_CI_high
  - p_RFM
  - rho_BMI
  - BMI_CI_low / BMI_CI_high
  - p_BMI
  - rho_RFM_BMI
  - Steiger_z
  - p_Steiger
  - Stronger predictor

Finally:
- results = pd.DataFrame(analyse("Male") + analyse("Female"))
- Save as CSV
- Print a nicely formatted table

“For each fat depot, is RFM more strongly associated than BMI, and is that difference statistically significant, separately for male and female participants?”

# Fisher confidence interval
Function: def fisher_ci(r, n, z_crit=1.96): se = 1.0 / np.sqrt(n - 3) z = np.arctanh(r) return np.tanh(z - z_crit * se), np.tanh(z + z_crit * se)

# What it is doing:

r is a Pearson/Spearman correlation coefficient
n is the sample size
The code transforms the correlation into Fisher’s z: z = atanh(r) = 0.5 * ln((1 + r) / (1 - r))
This is important because:

correlations are bounded between -1 and 1
their sampling distribution is skewed near the ends
Fisher’s z makes the distribution closer to normal
Then:

standard error of z is approximately: SE = 1 / sqrt(n - 3)
So a 95% CI for the transformed correlation is:

z ± 1.96 * SE
That means:

lower_z = z - 1.96 / sqrt(n - 3)
upper_z = z + 1.96 / sqrt(n - 3)
Finally, convert back to correlation scale using:

rho = tanh(z)
So the final confidence interval is:

tanh(z - 1.96/√(n-3))
tanh(z + 1.96/√(n-3))
This is exactly what the function returns.

Steiger (1980) test for dependent correlations
Function: def steiger_1980(r_jk, r_jh, r_kh, n): z_jk, z_jh = np.arctanh(r_jk), np.arctanh(r_jh) c = r_kh * (1 - r_jk2 - r_jh2)
- 0.5 * r_jk * r_jh * (1 - r_jk2 - r_jh2 - r_kh2) cov_z = c / ((1 - r_jk2) * (1 - r_jh**2)) z = (z_jk - z_jh) * np.sqrt(n - 3) / np.sqrt(2 - 2 * cov_z) return z, 2 * stats.norm.sf(abs(z))

# This is testing whether two correlations are significantly different when they share a common variable.

In your script:

j = the fat depot
k = RFM
h = BMI
So:

r_jk = correlation(fat depot, RFM)
r_jh = correlation(fat depot, BMI)
r_kh = correlation(RFM, BMI)
This is not a simple comparison of independent correlations, because both correlations involve the same fat depot variable. They are dependent and overlapping.

# Step by step:

a) Fisher transform each correlation

z_jk = atanh(r_jk)
z_jh = atanh(r_jh)
This turns the correlations into approximately normal variables.

b) Compute covariance of the two Fisher z-values The code computes:

c = r_kh * (1 - r_jk^2 - r_jh^2) - 0.5 * r_jk * r_jh * (1 - r_jk^2 - r_jh^2 - r_kh^2)
Then:

cov_z = c / ((1 - r_jk^2) * (1 - r_jh^2))
This is the asymptotic covariance between z_jk and z_jh, derived from the Steiger 1980 formula.

c) Standardize the difference The test statistic is:

z = (z_jk - z_jh) * sqrt(n - 3) / sqrt(2 - 2 * cov_z)
Equivalent idea:

difference in Fisher z-values = z_jk - z_jh
divide by its standard error
use n-3 because the large-sample approximation for Fisher z
So:

if z is large in magnitude, the two correlations differ significantly
d) Convert to p-value

p = 2 * P(|Z| > |z|) = 2 * sf(abs(z))
In SciPy:

stats.norm.sf(abs(z)) = 1 - Φ(|z|)
so 2 * sf(abs(z)) is the two-sided p-value
Interpretation:

If z < 0, then z_jk - z_jh < 0, meaning r_jk < r_jh
since k = RFM and h = BMI, that means BMI is more strongly associated with the depot than RFM
the comment in your code says: “Negative z => BMI correlates more strongly.”
That matches the logic.

Why this matters in your script
In analyse(sex), for each depot:

r_rfm = spearmanr(RFM, depot)
r_bmi = spearmanr(BMI, depot)
r_rb = spearmanr(RFM, BMI)
z, p = steiger_1980(r_rfm, r_bmi, r_rb, n)
So it is testing:

H0: correlation(depot, RFM) = correlation(depot, BMI)

against: H1: they are not equal

This is exactly the right test when the two correlations share the same depot variable, since they are not independent.

# Summary in one sentence
The script:

transforms each correlation with Fisher z,
computes the covariance between the two transformed correlations because they share the same depot,
standardizes their difference,
and tests whether the difference is significant.

# walkthrough of the script:

j = fat depot
k = RFM
h = BMI
So the script compares:

r_jk = correlation(depot, RFM)
r_jh = correlation(depot, BMI)
r_kh = correlation(RFM, BMI)
and tests whether r_jk and r_jh are significantly different.

Step 1: Convert each correlation to Fisher z
The script does:

z_jk = atanh(r_jk)
z_jh = atanh(r_jh)
where:

atanh(x) = 0.5 * ln((1 + x) / (1 - x))
This is Fisher’s z transformation. It is used because correlations are bounded between -1 and 1, and the transformed values are closer to a normal distribution.

Example: Suppose:

r_jk = 0.45
r_jh = 0.60
Then:

z_jk = atanh(0.45) ≈ 0.485
z_jh = atanh(0.60) ≈ 0.693
So the raw difference is:

z_jk - z_jh = -0.208
If that value is negative, it means the BMI correlation is larger than the RFM correlation, because the function is effectively comparing:

z_jk vs z_jh
Step 2: Account for the fact that the correlations are dependent
The key complication is that both correlations involve the same depot variable, so they are not independent.

The script computes:

c = r_kh * (1 - r_jk^2 - r_jh^2) - 0.5 * r_jk * r_jh * (1 - r_jk^2 - r_jh^2 - r_kh^2)

Then: cov_z = c / ((1 - r_jk^2) * (1 - r_jh^2))

This is the covariance between the two Fisher-transformed correlations.

Example: Let:

r_jk = 0.45
r_jh = 0.60
r_kh = 0.70
First calculate the pieces:

r_jk^2 = 0.2025
r_jh^2 = 0.3600
r_kh^2 = 0.4900
Now:

1 - r_jk^2 - r_jh^2 = 1 - 0.2025 - 0.3600 = 0.4375
So:

c = 0.70 * 0.4375 - 0.5 * 0.45 * 0.60 * (1 - 0.2025 - 0.3600 - 0.4900)
c = 0.30625 - 0.135 * (-0.0525)
c = 0.30625 + 0.00709
c ≈ 0.31334
Now denominator:

(1 - r_jk^2) * (1 - r_jh^2) = (1 - 0.2025) * (1 - 0.3600)
= 0.7975 * 0.6400
= 0.5104
So:

cov_z = 0.31334 / 0.5104
cov_z ≈ 0.614
This tells us that the Fisher z values are positively correlated because the two correlations share the same depot outcome.

Step 3: Form the test statistic
The function computes:

z = (z_jk - z_jh) * sqrt(n - 3) / sqrt(2 - 2 * cov_z)

This is the Steiger z statistic.

Why this formula?

z_jk - z_jh is the difference in the transformed correlations
sqrt(n - 3) is the scaling for sample size
sqrt(2 - 2 * cov_z) is the standard error term that adjusts for the dependency between the two correlations
Example with n = 100:

z_jk - z_jh = -0.208
sqrt(n - 3) = sqrt(97) ≈ 9.849
2 - 2 * cov_z = 2 - 2*0.614 = 0.772
sqrt(0.772) ≈ 0.879
Then:

z = (-0.208) * 9.849 / 0.879
z ≈ -2.33
This is the test statistic.

Step 4: Convert to p-value
The script then does:

p = 2 * stats.norm.sf(abs(z))

This is the two-sided p-value for a standard normal distribution.

For z = -2.33:

abs(z) = 2.33
P(|Z| > 2.33) ≈ 0.02
So:

p ≈ 0.02
Interpretation:

The difference between the RFM and BMI correlations is statistically significant at about the 5% level.
Since z is negative, the BMI correlation is larger.
This matches the comment in the code:

“Negative z => BMI correlates more strongly.”
Why the sign matters
The function is comparing:

z_jk - z_jh
So:

If z_jk > z_jh, then z is positive
RFM correlation is stronger
If z_jk < z_jh, then z is negative
BMI correlation is stronger
In other words, the sign tells you which predictor is more strongly associated with the depot.

What the whole function does in one sentence
The function tests:

Is the difference between correlation(depot, RFM) and correlation(depot, BMI) large enough to be unlikely under the null hypothesis of equal correlations, given that both correlations share the same depot variable?


