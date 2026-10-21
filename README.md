# BMI-vs-RFM
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

1) fisher_ci(r, n, z_crit=1.96)
This builds a 95% confidence interval for a correlation coefficient.

- r = correlation coefficient
- n = sample size
- z_crit = 1.96 for a 95% CI (roughly ±1.96 standard errors)

It uses Fisher’s z transform:
- z = arctanh(r)
- standard error ≈ 1 / sqrt(n - 3)

Then it computes:
- lower = tanh(z - 1.96 * SE)
- upper = tanh(z + 1.96 * SE)

Why do this?
Because raw correlations are bounded between -1 and 1, and the normal approximation is much better on the transformed z scale.

# Steiger Z test. A z-test is a way to check if a sample's average is genuinely different from a known population average, or if the difference is just due to random luck. It works best when your sample size is large (30 or more) and you already know the true standard deviation of the population.

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

Interpretation:
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

If you want, I can also explain the exact math behind the Steiger test in simpler terms, or walk through one sample calculation from the dataset.
