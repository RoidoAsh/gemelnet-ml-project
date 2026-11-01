# Gemel-Net ML Project

Data Mining course project (2026): classification and clustering of Israeli provident and study funds.

**Dataset:** [Gemel-Net (גמל-נט)](https://data.gov.il/he/datasets/cma/gemelnet), published by the Capital Market, Insurance and Savings Authority on data.gov.il. Monthly reports per fund track: assets, fees, deposits and withdrawals, returns (monthly, YTD, 3Y, 5Y), standard deviation, Alpha, Sharpe ratio and market exposures.

## Goals

1. **Classification:** end-to-end pipeline (preprocessing, feature engineering, hyperparameter optimization, evaluation) comparing at least 5 models.
2. **Clustering:** discover risk-return profiles of funds, comparing at least 3 models.

## Structure

```
data/raw/        original CSVs from data.gov.il
data/processed/  cleaned datasets
notebooks/       exploration and modeling notebooks
src/             reusable code
reports/         proposal, figures and final report
```
