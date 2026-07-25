# Data Cleaning Log

Documentation of every cleaning decision applied to the raw financial dataset before it was loaded into Power BI. The raw file held 226 companies across 40 fields. The guiding principle throughout was to leave a value blank and flag it rather than invent a number, so that no imputed figure could distort the analysis.

## Source Data

- 226 companies, 40 columns
- All values reported in USD, so no currency conversion was needed
- FY2022 financial snapshot

## Text Fields

Trimmed leading and trailing whitespace from company names, tickers, industry labels, and currency codes so that values would group correctly and joins would not fail on invisible spaces.

## Currency and Units

The absolute-dollar columns (debt, revenue, market cap, cash, EBITDA, and similar) arrived in raw dollars, for example 5,243,136,620,160. At that scale the numbers are unreadable in charts and easy to mis-scale in calculations, so each was converted to millions and renamed with a `_USDmm` suffix. Per-share figures such as price and earnings per share were rounded to two decimal places, the standard convention for those values.

## Missing Values

### Debt-to-equity (17 missing)

Sixteen of the seventeen companies with no debt-to-equity value had negative book equity. The ratio is mathematically undefined when equity is negative, which is why the source returned a blank rather than a number. This is a genuine signal about the company, not a gap to be filled, so these rows were left blank and marked with a `negativeEquityFlag`. They should be excluded from any debt-to-equity comparison or grouped separately as an equity-deficit cohort.

### Market data bundle (2 companies)

Visa and Starbucks were each missing their entire block of market-related fields: market cap, shares outstanding, book value, earnings per share, and price-to-book. This pattern points to a failed data pull for those two tickers rather than random gaps. Reconstructing market cap from the enterprise-value identity was tested against the 224 complete rows and produced errors as large as 195 percent on outliers, so the fields were left blank and flagged with `incompleteMarketDataFlag`. These rows should be excluded from any market-cap-weighted calculation.

### Growth metrics

Earnings growth (33 missing), quarterly earnings growth (32), and PEG ratio (5) are undefined whenever the prior-period figure they compare against is negative or zero. These blanks are accurate and were left in place.

### Liquidity and cash-flow fields

Current ratio, quick ratio, and return on assets (3 missing each), along with operating cash flow (6) and free cash flow (7), had small scattered gaps. With so few affected rows, filling them with an industry median risked skewing a small dataset more than the blanks themselves, so they were left as-is.

## Duplicate Companies

Alphabet appears twice under two ticker symbols (GOOG and GOOGL). These are two distinct share classes of the same company with different market values, not duplicate records, so both were kept and marked with a `dualShareClassFlag`.

## Added Fields

Two market-value leverage measures were added for the capital-structure analysis: `marketDebtToEquity` (debt divided by market cap) and `debtToCapital_market` (debt over debt plus market cap). The source only provided a book-value debt-to-equity figure, but a proper capital-structure view needs market-value weights.

## Result

The cleaned dataset carries 226 rows with standardised units, documented blanks, and three flag columns that let the analysis include or exclude problematic rows on demand rather than being polluted by silently filled values.
