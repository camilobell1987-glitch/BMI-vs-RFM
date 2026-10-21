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
