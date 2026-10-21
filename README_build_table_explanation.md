# This file is a Python script that builds a publication-style “Table 1: Baseline Characteristics by Sex” from a dataset called RFM_paper_new.csv.

# What it does:

Loads the raw CSV data.
Creates new derived variables:
BMI-defined obesity
RFM-defined obesity
ancestry group categories (European, South Asian, African, Other)
Splits the dataset into male and female subsets for sex comparisons.
Defines summary helpers to compute:
Mean ± SD, median, and range for continuous variables
Percentages and counts for categorical/binary variables
p-values comparing males vs females:
Mann-Whitney U test for continuous variables
Chi-square test for categorical/binary variables
Organizes results into row groups:
Continental genetic ancestry
Anthropometric measures
Adiposity indices
Imaging-derived fat phenotypes
Flattens the results into a pandas DataFrame and prints it.
Saves the final table as a CSV file: table1_baseline_characteristics.csv
The script is designed to produce a table with columns for:

Both sexes
Male
Female
p-value for male vs female
Main variables included:

Height, weight, waist, hip, waist-to-hip, waist-to-height
BMI, RFM
BMI-defined obesity, RFM-defined obesity
Liver PDFF, pancreas PDFF, ASAT, VAT, IMAT, total fat
Ancestry proportions

# So in short: this is a data-reporting pipeline for generating a baseline demographics and clinical characteristics table for a research paper.

# Below is a complete inventory of the functions and main variables in the file build_table1 (2).py.

# Imported modules
pd
pandas, used for DataFrame and Series operations.
np
NumPy, used for array-based operations and np.where.
stats
from scipy import stats, used for statistical tests:
stats.mannwhitneyu
stats.chi2_contingency
Functions defined in the file
ancestry_group(code)

Purpose: Maps a genetic ancestry code to a broad group label.
Input: code (a string like "EUR", "CSA", "AFR", etc.)
Output:
"European" for "EUR"
"South Asian" for "CSA"
"African" for "AFR"
"Other" for anything else
Example: ancestry_group("EUR") returns "European"
cont_stats(series: pd.Series, decimals: int) -> dict

Purpose: Computes summary statistics for a continuous variable.
Input:
series: a pandas Series
decimals: number of decimal places to round to
Output: dictionary with:
"mean_sd": mean ± SD
"median": median
"range": min – max
"n": number of non-missing values
Example output structure:
{"mean_sd": "32.10 ± 8.40", "median": "31.50", "range": "15.00 – 61.00", "n": 250}
pct_n(series: pd.Series) -> str

Purpose: Formats a binary 0/1 variable as a percentage and count of the positive class.
Input: series of binary values
Output like:
"32.5% (n=42)"
It counts the total number of 1 values and expresses as a percent of the non-missing values.
group_pct_n(full_series: pd.Series, group_label: str) -> str

Purpose: Formats a categorical group proportion as percentage and count.
Input:
full_series: a Series with categories
group_label: category to evaluate
Output like:
"60.0% (n=120)"
It calculates the fraction of observations equal to group_label.
mwu_pvalue(col: str) -> float

Purpose: Computes the p-value for a male-vs-female comparison on a continuous variable.
Input: column name in the dataframe
Method:
Uses Mann-Whitney U test via stats.mannwhitneyu
Compares male_df[col].dropna() vs female_df[col].dropna()
alternative="two-sided"
Output: p-value as a float
chisq_pvalue_ancestry(group_label: str) -> float

Purpose: Computes a chi-square test p-value for a specific ancestry category by sex.
Input: ancestry category label, e.g. "European"
Method:
Builds a 2x2 contingency table:
rows: male/female
columns: in group / not in group
Uses stats.chi2_contingency(table)
Output: p-value
chisq_pvalue_binary(col: str) -> float

Purpose: Computes a chi-square p-value for a binary 0/1 variable by sex.
Input: binary column name
Method:
Uses pd.crosstab(df["sex"], df[col])
Runs chi-square contingency test
Output: p-value
fmt_p(p: float) -> str

Purpose: Formats p-values for display in the final table.
Output:
"<0.001" if p < 0.001
otherwise a 3-decimal value like "0.034"
Main variables and data structures
df

Type: pandas DataFrame
Created by:
df = pd.read_csv("RFM_paper_new.csv")
Purpose: holds the raw dataset read from the CSV file.
male_df

Type: pandas DataFrame
Created by:
male_df = df[df["sex"] == "Male"]
Purpose: subset of rows where sex == Male
female_df

Type: pandas DataFrame
Created by:
female_df = df[df["sex"] == "Female"]
Purpose: subset of rows where sex == Female
Derived new columns on df

df["bmi_obese"]
Type: int series
Definition:
(df["body_mass_index_2"] >= 30).astype(int)
Meaning: 1 if BMI >= 30, else 0
df["rfm_obese"]
Type: int series
Definition:
np.where(df["sex"] == "Male", (df["RFM"] >= 25).astype(int), (df["RFM"] >= 40).astype(int))
Meaning:
Male: 1 if RFM >= 25%
Female: 1 if RFM >= 40%
df["ancestry_group"]
Type: string/object series
Definition:
df["continental_genetic_ancestry"].apply(ancestry_group)
Meaning: collapses ancestry codes into:
European
South Asian
African
Other
Lists used to define rows in the table
anthro_vars

Type: list of tuples
Columns:
("height_2", "Height (cm)", 1)
("weight_2", "Weight (kg)", 1)
("waist_circumference", "Waist circumference (cm)", 1)
("hip_circumference", "Hip circumference (cm)", 1)
("waist_to_hip", "Waist-to-hip ratio", 3)
("waist_to_height", "Waist-to-height ratio", 3)
Purpose: defines anthropometric variables, labels, and decimal places
adip_continuous

Type: list of tuples
Columns:
("body_mass_index_2", "BMI (kg/m²)", 1)
("RFM", "RFM (%)", 1)
Purpose: continuous adiposity variables
adip_binary

Type: list of tuples
Columns:
("bmi_obese", "BMI-defined obesity, % (n)¹")
("rfm_obese", "RFM-defined obesity, % (n)²")
Purpose: obesity indicators encoded as binary yes/no
imaging_vars

Type: list of tuples
Columns:
("pdff_liver", "Liver PDFF (%)", 2)
("pdff_pancreas", "Pancreas PDFF (%)", 2)
("subcutaneous_fat", "ASAT (cm²)", 1)
("visceral_fat", "VAT (cm²)", 1)
("thigh_internal_fat", "IMAT (cm²)", 1)
("ml_volume.total_fat", "Total fat volume (mL)", 1)
Purpose: imaging-derived fat phenotypes
Table-building variables
rows

Type: list of dictionaries
Purpose: stores each row definition before flattening into a display-ready DataFrame
Contains:
section
variable
categorical
both / male / female
p
Example row entry:
{"section": "Anthropometric Measures", "variable": "Height (cm)", ...}
flat_rows

Type: list of dictionaries
Purpose: converts row entries into a flattened format suitable for a DataFrame
It includes:
Section
Variable
Both_Mean_SD
Both_Median
Both_Range
Male_Mean_SD
Male_Median
Male_Range
Female_Mean_SD
Female_Median
Female_Range
p_value
table1

Type: pandas DataFrame
Created by:
table1 = pd.DataFrame(flat_rows)
Purpose: final table summarizing baseline characteristics by sex
Loop variables (temporary/local) These are not “main” variables, but they are used in the script:
grp
loop variable over ancestry groups: ["European", "South Asian", "African", "Other"]
col
column name in loops for variable definition
label
display label for each variable
dec
decimal precision for summary statistics
r
row object while iterating over rows
Notable output/display settings
pd.set_option("display.max_columns", None)
shows all columns in DataFrame display
pd.set_option("display.width", 200)
widens output so table prints cleanly
Final output file
"table1_baseline_characteristics.csv"
Written via:
table1.to_csv("table1_baseline_characteristics.csv", index=False)
Purpose: saves the final table as CSV

