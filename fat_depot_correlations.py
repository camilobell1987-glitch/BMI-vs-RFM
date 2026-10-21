"""
Spearman correlations of RFM and BMI with each fat depot, by sex,
with 95% CIs (Fisher z) and Steiger (1980) z-tests comparing the two
dependent correlations.   Run:  python fat_depot_correlations.py
"""
import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv("RFM_paper_new.csv")

DEPOTS = {
    "pdff_liver":          "Liver Fat (PDFF, %)",
    "pdff_pancreas":       "Pancreas Fat (PDFF, %)",
    "subcutaneous_fat":    "Subcutaneous Fat (cm2)",
    "visceral_fat":        "Visceral Fat (cm2)",
    "thigh_internal_fat":  "Thigh Internal Fat (cm2)",
    "ml_volume.total_fat": "Total Fat Volume (mL)",
}

def fisher_ci(r, n, z_crit=1.96):
    """95% CI for a correlation via Fisher z-transformation."""
    se = 1.0 / np.sqrt(n - 3)
    z = np.arctanh(r)
    return np.tanh(z - z_crit * se), np.tanh(z + z_crit * se)

def steiger_1980(r_jk, r_jh, r_kh, n):
    """
    Steiger (1980) test for two DEPENDENT, OVERLAPPING correlations.
      j  = fat depot (shared outcome)
      k  = RFM,  h = BMI
      r_jk = corr(depot, RFM); r_jh = corr(depot, BMI); r_kh = corr(RFM, BMI)
    Returns (z, two-sided p). Negative z => BMI correlates more strongly.
    """
    z_jk, z_jh = np.arctanh(r_jk), np.arctanh(r_jh)
    # asymptotic covariance of the two correlations
    c = r_kh * (1 - r_jk**2 - r_jh**2) \
        - 0.5 * r_jk * r_jh * (1 - r_jk**2 - r_jh**2 - r_kh**2)
    # covariance of the two Fisher z values
    cov_z = c / ((1 - r_jk**2) * (1 - r_jh**2))
    z = (z_jk - z_jh) * np.sqrt(n - 3) / np.sqrt(2 - 2 * cov_z)
    return z, 2 * stats.norm.sf(abs(z))

def analyse(sex):
    out = []
    sub_sex = df[df["sex"] == sex]
    for col, label in DEPOTS.items():
        d = sub_sex[["RFM", "body_mass_index_2", col]].dropna()   # complete cases per depot
        n = len(d)
        r_rfm, p_rfm = stats.spearmanr(d["RFM"], d[col])
        r_bmi, p_bmi = stats.spearmanr(d["body_mass_index_2"], d[col])
        r_rb, _      = stats.spearmanr(d["RFM"], d["body_mass_index_2"])
        z, p_st      = steiger_1980(r_rfm, r_bmi, r_rb, n)
        lo_r, hi_r   = fisher_ci(r_rfm, n)
        lo_b, hi_b   = fisher_ci(r_bmi, n)
        out.append({
            "Sex": sex, "Fat depot": label, "N": n,
            "rho_RFM": r_rfm, "RFM_CI_low": lo_r, "RFM_CI_high": hi_r, "p_RFM": p_rfm,
            "rho_BMI": r_bmi, "BMI_CI_low": lo_b, "BMI_CI_high": hi_b, "p_BMI": p_bmi,
            "rho_RFM_BMI": r_rb, "Steiger_z": z, "p_Steiger": p_st,
            "Stronger predictor": "RFM" if abs(r_rfm) > abs(r_bmi) else "BMI",
        })
    return out

results = pd.DataFrame(analyse("Male") + analyse("Female"))
results.to_csv("correlation_results_corrected.csv", index=False)
pd.set_option("display.width", 220); pd.set_option("display.max_columns", None)
print(results.round(4).to_string(index=False))
