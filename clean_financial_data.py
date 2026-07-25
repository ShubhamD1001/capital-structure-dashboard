"""
clean_financial_data.py
-----------------------
Cleans the raw financial dataset before it is loaded into Power BI for the
Capital Structure and Financial Performance dashboard.

Input : financialdata.xlsx          (226 companies, 40 fields)
Output: financialdata_cleaned.xlsx   the cleaned dataset
        data_cleaning_log.csv        a record of every cleaning decision

Guiding principle: never invent a number. Every missing value is either left
blank and flagged, or only filled using a rule that was checked against the
rest of the data first.
"""

import pandas as pd

# ---------------------------------------------------------------------------
# 0. Load
# ---------------------------------------------------------------------------
SRC = "financialdata.xlsx"
df = pd.read_excel(SRC)

log = []
def note(msg):
    print(msg)
    log.append(msg)

note(f"Loaded {len(df)} rows and {len(df.columns)} columns from {SRC}")

# ---------------------------------------------------------------------------
# 1. Text fields
# ---------------------------------------------------------------------------
text_cols = ["shortName", "industry", "symbol", "quoteType", "financialCurrency"]
for col in text_cols:
    before = df[col].copy()
    df[col] = df[col].astype(str).str.strip()
    changed = (before.astype(str) != df[col]).sum()
    if changed:
        note(f"Trimmed whitespace in '{col}': {changed} value(s) affected")

# ---------------------------------------------------------------------------
# 2. Currency and units
# ---------------------------------------------------------------------------
# Confirm a single currency before doing any totals across companies.
currencies = df["financialCurrency"].unique()
if len(currencies) == 1 and currencies[0] == "USD":
    note("Currency check passed: all records report in USD, no conversion needed.")
else:
    note(f"Warning: mixed currencies detected {currencies}, manual conversion required.")

# Absolute-dollar columns arrive in raw dollars (e.g. 128217997312), which is
# hard to read in charts and easy to mis-scale. Convert to millions and make
# the unit explicit in the column name.
dollar_cols = [
    "operatingCashflow", "ebitda", "grossProfits", "freeCashflow",
    "totalCash", "totalDebt", "totalRevenue", "enterpriseValue", "marketCap",
]
for col in dollar_cols:
    df[col + "_USDmm"] = (df[col] / 1_000_000).round(2)
df.drop(columns=dollar_cols, inplace=True)
note(f"Converted {len(dollar_cols)} dollar columns to millions with a '_USDmm' suffix.")

# Per-share figures stay in dollars, rounded to two decimals.
per_share_cols = ["currentPrice", "bookValue", "forwardEps",
                  "trailingEps", "revenuePerShare", "totalCashPerShare"]
for col in per_share_cols:
    if col in df.columns:
        df[col] = df[col].round(2)
note("Rounded per-share dollar fields to two decimals.")

# ---------------------------------------------------------------------------
# 3. Duplicate check
# ---------------------------------------------------------------------------
# Alphabet appears twice (GOOG / GOOGL). These are two share classes of the
# same company with distinct market caps, not duplicate records. Flag them.
df["dualShareClassFlag"] = df["shortName"].duplicated(keep=False)
note("Flagged dual-share-class companies (e.g. Alphabet GOOG/GOOGL) rather than dropping them.")

# ---------------------------------------------------------------------------
# 4. Missing values
# ---------------------------------------------------------------------------
# 4a. debtToEquity: undefined when book equity is negative, which is why the
#     source returned a blank. This is a real signal, so flag rather than fill.
df["negativeEquityFlag"] = df["bookValue"] < 0
neg_and_missing = df[df["negativeEquityFlag"] & df["debtToEquity"].isna()].shape[0]
note(f"debtToEquity is blank for {df['debtToEquity'].isna().sum()} rows; "
     f"{neg_and_missing} of those have negative equity (flagged in 'negativeEquityFlag'). "
     f"Left blank; exclude from debt-to-equity comparisons or treat as a separate cohort.")

# 4b. marketCap / shares / bookValue / EPS / priceToBook all missing together
#     for 2 companies (Visa, Starbucks), consistent with a failed data pull.
#     Rebuilding marketCap from enterprise value was too unreliable (errors up
#     to ~195% on outliers), so leave blank and flag.
bundle = ["marketCap_USDmm", "sharesOutstanding", "bookValue",
          "forwardEps", "trailingEps", "priceToBook", "forwardPE"]
df["incompleteMarketDataFlag"] = df[bundle].isna().all(axis=1)
note(f"{df['incompleteMarketDataFlag'].sum()} row(s) missing the entire market-data bundle, "
     f"left blank and flagged in 'incompleteMarketDataFlag'.")

# 4c. Growth metrics are undefined off a negative or zero base. Accurate blanks.
for col in ["earningsGrowth", "earningsQuarterlyGrowth", "pegRatio"]:
    note(f"'{col}': {df[col].isna().sum()} blanks left as-is (undefined off a negative base).")

# 4d. Small scattered gaps in liquidity and cash-flow fields. Too few rows to
#     justify median imputation on a small dataset, so leave blank.
for col in ["currentRatio", "quickRatio", "returnOnAssets",
            "operatingCashflow_USDmm", "freeCashflow_USDmm"]:
    if col in df.columns and df[col].isna().sum():
        note(f"'{col}': {df[col].isna().sum()} blanks left as-is (too few to impute).")

# ---------------------------------------------------------------------------
# 5. Market-value leverage fields
# ---------------------------------------------------------------------------
# The source only has a book-value debtToEquity. A capital-structure view needs
# market-value weights, so add these two ratios using market cap as equity value.
df["marketDebtToEquity"] = (df["totalDebt_USDmm"] / df["marketCap_USDmm"]).round(4)
df["debtToCapital_market"] = (
    df["totalDebt_USDmm"] / (df["totalDebt_USDmm"] + df["marketCap_USDmm"])
).round(4)
note("Added 'marketDebtToEquity' and 'debtToCapital_market' using market cap as equity value.")

# ---------------------------------------------------------------------------
# 6. Order and index
# ---------------------------------------------------------------------------
df = df.sort_values("marketCap_USDmm", ascending=False).reset_index(drop=True)
df["Sr_No"] = range(1, len(df) + 1)
first_cols = ["Sr_No", "shortName", "symbol", "industry", "quoteType", "financialCurrency"]
df = df[first_cols + [c for c in df.columns if c not in first_cols]]
note(f"Sorted by market cap and numbered rows 1 to {len(df)}.")

# ---------------------------------------------------------------------------
# 7. Export
# ---------------------------------------------------------------------------
OUT_XLSX = "financialdata_cleaned.xlsx"
OUT_LOG = "data_cleaning_log.csv"

df.to_excel(OUT_XLSX, index=False, sheet_name="Cleaned Data")
pd.DataFrame({"cleaning_step": log}).to_csv(OUT_LOG, index=False)

note(f"Saved cleaned dataset to {OUT_XLSX}")
note(f"Saved cleaning log to {OUT_LOG}")
note(f"Final shape: {df.shape[0]} rows by {df.shape[1]} columns")
