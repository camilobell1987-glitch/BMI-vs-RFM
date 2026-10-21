"""
Table 1. Baseline Characteristics by Sex
-----------------------------------------
Reproduces the descriptive statistics table (Both Genders / Male / Female,
each with Mean ± SD, Median, Range, plus a Male-vs-Female p-value) from the
raw RFM_paper_new.csv data.

Row groups:
  1. Continental Genetic Ancestry (European, South Asian, African, Other)
  2. Anthropometric Measures (height, weight, waist, hip, waist-to-hip, waist-to-height)
  3. Adiposity Indices (BMI, RFM, BMI-defined obesity, RFM-defined obesity)
  4. Imaging-Derived Fat Phenotypes (Liver PDFF, Pancreas PDFF, ASAT, VAT, IMAT, Total fat)

Continuous variables -> Mann-Whitney U test (male vs female)
Categorical/binary variables -> Chi-square test (male vs female)
"""

import pandas as pd
import numpy as np
from scipy import stats

# ─────────────────────────────────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────────────────────────────────
df = pd.read_csv("RFM_paper_new.csv")

# ─────────────────────────────────────────────────────────────────────────
# 2. DERIVE NEW VARIABLES
# ─────────────────────────────────────────────────────────────────────────

# 2a. BMI-defined obesity: WHO cutoff, BMI >= 30 kg/m^2
df["bmi_obese"] = (df["body_mass_index_2"] >= 30).astype(int)

# 2b. RFM-defined obesity: Woolcott & Bergman (2018) sex-specific cutoffs
#     Male: RFM >= 25%   Female: RFM >= 40%
df["rfm_obese"] = np.where(
    df["sex"] == "Male",
    (df["RFM"] >= 25).astype(int),
    (df["RFM"] >= 40).astype(int),
)

# 2c. Collapse continental genetic ancestry into 4 groups:
#     European, South Asian, African, Other (East Asian + Middle Eastern + Admixed American)
def ancestry_group(code):
    mapping = {"EUR": "European", "CSA": "South Asian", "AFR": "African"}
    return mapping.get(code, "Other")

df["ancestry_group"] = df["continental_genetic_ancestry"].apply(ancestry_group)

# Sex subsets used throughout
male_df = df[df["sex"] == "Male"]
female_df = df[df["sex"] == "Female"]

# ─────────────────────────────────────────────────────────────────────────
# 3. HELPER FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────

def cont_stats(series: pd.Series, decimals: int) -> dict:
    """Mean ± SD, median, and range (min-max) for a continuous variable."""
    s = series.dropna()
    return {
        "mean_sd": f"{s.mean():.{decimals}f} \u00B1 {s.std():.{decimals}f}",
        "median": f"{s.median():.{decimals}f}",
        "range": f"{s.min():.{decimals}f} \u2013 {s.max():.{decimals}f}",
        "n": int(s.shape[0]),
    }

def pct_n(series: pd.Series) -> str:
    """Format a binary 0/1 series as '% (n)' for the positive class."""
    s = series.dropna()
    n_pos = int(s.sum())
    pct = 100 * n_pos / len(s)
    return f"{pct:.1f}% (n={n_pos:,})"

def group_pct_n(full_series: pd.Series, group_label: str) -> str:
    """Format the proportion of `full_series` equal to `group_label` as '% (n)'."""
    n_grp = int((full_series == group_label).sum())
    pct = 100 * n_grp / len(full_series)
    return f"{pct:.1f}% (n={n_grp:,})"

def mwu_pvalue(col: str) -> float:
    """Mann-Whitney U test p-value, male vs female, for a continuous column."""
    u_stat, p = stats.mannwhitneyu(
        male_df[col].dropna(), female_df[col].dropna(), alternative="two-sided"
    )
    return p

def chisq_pvalue_ancestry(group_label: str) -> float:
    """Chi-square test p-value for an ancestry group's proportion, male vs female."""
    male_in = (male_df["ancestry_group"] == group_label).sum()
    female_in = (female_df["ancestry_group"] == group_label).sum()
    table = [
        [male_in, len(male_df) - male_in],
        [female_in, len(female_df) - female_in],
    ]
    chi2, p, dof, expected = stats.chi2_contingency(table)
    return p

def chisq_pvalue_binary(col: str) -> float:
    """Chi-square test p-value for a binary 0/1 column, male vs female."""
    table = pd.crosstab(df["sex"], df[col])
    chi2, p, dof, expected = stats.chi2_contingency(table)
    return p

def fmt_p(p: float) -> str:
    return "<0.001" if p < 0.001 else f"{p:.3f}"

# ─────────────────────────────────────────────────────────────────────────
# 4. BUILD EACH ROW GROUP
# ─────────────────────────────────────────────────────────────────────────
rows = []

# 4a. Continental Genetic Ancestry ------------------------------------------------
rows.append({"section": "Continental Genetic Ancestry, % (n)", "header": True})
for grp in ["European", "South Asian", "African", "Other"]:
    rows.append({
        "section": "Continental Genetic Ancestry, % (n)",
        "variable": grp,
        "categorical": True,
        "both": group_pct_n(df["ancestry_group"], grp),
        "male": group_pct_n(male_df["ancestry_group"], grp),
        "female": group_pct_n(female_df["ancestry_group"], grp),
        "p": chisq_pvalue_ancestry(grp),
    })

# 4b. Anthropometric Measures -------------------------------------------------
anthro_vars = [
    ("height_2", "Height (cm)", 1),
    ("weight_2", "Weight (kg)", 1),
    ("waist_circumference", "Waist circumference (cm)", 1),
    ("hip_circumference", "Hip circumference (cm)", 1),
    ("waist_to_hip", "Waist-to-hip ratio", 3),
    ("waist_to_height", "Waist-to-height ratio", 3),
]
rows.append({"section": "Anthropometric Measures", "header": True})
for col, label, dec in anthro_vars:
    rows.append({
        "section": "Anthropometric Measures",
        "variable": label,
        "categorical": False,
        "both": cont_stats(df[col], dec),
        "male": cont_stats(male_df[col], dec),
        "female": cont_stats(female_df[col], dec),
        "p": mwu_pvalue(col),
    })

# 4c. Adiposity Indices --------------------------------------------------------
adip_continuous = [
    ("body_mass_index_2", "BMI (kg/m\u00B2)", 1),
    ("RFM", "RFM (%)", 1),
]
adip_binary = [
    ("bmi_obese", "BMI-defined obesity, % (n)\u00B9"),
    ("rfm_obese", "RFM-defined obesity, % (n)\u00B2"),
]
rows.append({"section": "Adiposity Indices", "header": True})
for col, label, dec in adip_continuous:
    rows.append({
        "section": "Adiposity Indices",
        "variable": label,
        "categorical": False,
        "both": cont_stats(df[col], dec),
        "male": cont_stats(male_df[col], dec),
        "female": cont_stats(female_df[col], dec),
        "p": mwu_pvalue(col),
    })
for col, label in adip_binary:
    rows.append({
        "section": "Adiposity Indices",
        "variable": label,
        "categorical": True,
        "both": pct_n(df[col]),
        "male": pct_n(male_df[col]),
        "female": pct_n(female_df[col]),
        "p": chisq_pvalue_binary(col),
    })

# 4d. Imaging-Derived Fat Phenotypes -------------------------------------------
imaging_vars = [
    ("pdff_liver", "Liver PDFF (%)", 2),
    ("pdff_pancreas", "Pancreas PDFF (%)", 2),
    ("subcutaneous_fat", "ASAT (cm\u00B2)", 1),
    ("visceral_fat", "VAT (cm\u00B2)", 1),
    ("thigh_internal_fat", "IMAT (cm\u00B2)", 1),
    ("ml_volume.total_fat", "Total fat volume (mL)", 1),
]
rows.append({"section": "Imaging-Derived Fat Phenotypes", "header": True})
for col, label, dec in imaging_vars:
    rows.append({
        "section": "Imaging-Derived Fat Phenotypes",
        "variable": label,
        "categorical": False,
        "both": cont_stats(df[col], dec),
        "male": cont_stats(male_df[col], dec),
        "female": cont_stats(female_df[col], dec),
        "p": mwu_pvalue(col),
    })

# ─────────────────────────────────────────────────────────────────────────
# 5. FLATTEN INTO A DISPLAY-READY DATAFRAME
# ─────────────────────────────────────────────────────────────────────────
flat_rows = []
for r in rows:
    if r.get("header"):
        flat_rows.append({
            "Section": r["section"], "Variable": "", "Both_Mean_SD": "", "Both_Median": "",
            "Both_Range": "", "Male_Mean_SD": "", "Male_Median": "", "Male_Range": "",
            "Female_Mean_SD": "", "Female_Median": "", "Female_Range": "", "p_value": "",
        })
        continue

    if r["categorical"]:
        flat_rows.append({
            "Section": r["section"], "Variable": r["variable"],
            "Both_Mean_SD": r["both"], "Both_Median": "", "Both_Range": "",
            "Male_Mean_SD": r["male"], "Male_Median": "", "Male_Range": "",
            "Female_Mean_SD": r["female"], "Female_Median": "", "Female_Range": "",
            "p_value": fmt_p(r["p"]),
        })
    else:
        flat_rows.append({
            "Section": r["section"], "Variable": r["variable"],
            "Both_Mean_SD": r["both"]["mean_sd"], "Both_Median": r["both"]["median"], "Both_Range": r["both"]["range"],
            "Male_Mean_SD": r["male"]["mean_sd"], "Male_Median": r["male"]["median"], "Male_Range": r["male"]["range"],
            "Female_Mean_SD": r["female"]["mean_sd"], "Female_Median": r["female"]["median"], "Female_Range": r["female"]["range"],
            "p_value": fmt_p(r["p"]),
        })

table1 = pd.DataFrame(flat_rows)

# ─────────────────────────────────────────────────────────────────────────
# 6. OUTPUT
# ─────────────────────────────────────────────────────────────────────────
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)
print(table1.to_string(index=False))

table1.to_csv("table1_baseline_characteristics.csv", index=False)

# Footnotes (for reference when rendering the table elsewhere):
# 1. BMI-defined obesity: BMI >= 30 kg/m^2.
# 2. RFM-defined obesity (Woolcott & Bergman, 2018 cutoffs):
#    RFM >= 25% in males, RFM >= 40% in females.
# ASAT = abdominal subcutaneous adipose tissue
# VAT  = visceral adipose tissue
# IMAT = intermuscular/thigh internal adipose tissue
# "Other" ancestry = East Asian + Middle Eastern + Admixed American
