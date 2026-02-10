# Financial Market Analysis

![Reports](https://img.shields.io/badge/reports-23_PDFs-blue)
![Data Points](https://img.shields.io/badge/data_points-4.3M%2B-green)
![Industries](https://img.shields.io/badge/industries-8-orange)
![Cadences](https://img.shields.io/badge/cadences-weekly_|_monthly_|_quarterly-purple)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Multi-industry intelligence reports built from **4.3M+ data points** across 8 verticals — delivered at weekly, monthly, and quarterly cadences.

## What This Is

23 automated intelligence reports covering finance, brokerage, crypto, gaming, sports betting, weather, solar energy, and regulatory compliance. Every metric in every report traces back to a verifiable public data source. No synthetic data. No simulated results.

## Report Catalog

### Weekly Intelligence (9 reports)

| # | Report | Data Source | Key Metrics |
|---|--------|-------------|-------------|
| 01 | Finance Weekly Intelligence | FRED (St. Louis Fed) | GDP growth, unemployment, CPI, Fed funds rate, yield curve |
| 02 | Brokerage Trading Performance | Yahoo Finance | Portfolio returns, sector rotation, volume trends, RSI signals |
| 03 | Crypto Market Intelligence | CoinGecko | Market cap changes, dominance shifts, volume spikes, volatility |
| 04 | Gaming Industry Metrics | Steam + SteamSpy | Player counts, ownership trends, revenue estimates, genre analysis |
| 05 | Sports Weekend Recap | ESPN | League standings, win streaks, conference rankings across NFL/NBA/MLB/NHL |
| 06 | Weather Climate Summary | Open-Meteo | Temperature anomalies, precipitation patterns, wind trends across 30 US cities |
| 07 | Solar Generation Report | NREL | Generation capacity, efficiency metrics, economic viability by region |
| 08 | Compliance Filing Monitor | SEC EDGAR | Filing volumes, XBRL fact counts, sector filing patterns |
| 10 | Executive Summary | All sources | Cross-vertical KPI rollup, trend highlights, risk flags |

### Monthly Reviews (9 reports)

Month-over-month trend analysis with deeper statistical context:

| # | Report | Focus |
|---|--------|-------|
| 01 | Finance Monthly Review | MoM macro shifts, FRED series trend analysis |
| 02 | Brokerage Monthly Review | 30-day performance attribution, sector rebalancing signals |
| 03 | Crypto Monthly Review | Monthly market cap changes, correlation with macro indicators |
| 04 | Gaming Monthly Review | Player retention trends, new release impact analysis |
| 05 | Sports Monthly Review | Season progression, playoff probability shifts |
| 06 | Weather Monthly Review | Monthly climate patterns vs 10-year normals |
| 07 | Solar Monthly Review | Seasonal generation variance, capacity utilization |
| 08 | Compliance Monthly Review | Filing cadence analysis, material filing alerts |
| 09 | Executive Monthly Summary | Cross-vertical monthly rollup with MoM deltas |

### Quarterly Reviews (5 reports)

Strategic analysis combining related verticals:

| # | Report | Coverage |
|---|--------|----------|
| 01 | Financial Markets Q4 2025 | Finance + Brokerage: macro backdrop, equity performance, yield dynamics |
| 02 | Digital Economy Q4 2025 | Crypto + Gaming + Ecommerce: digital asset trends, platform economics |
| 03 | Energy & Climate Q4 2025 | Weather + Solar + Oil & Gas: seasonal patterns, generation economics |
| 04 | Sports & Compliance Q4 2025 | Betting + Compliance: season results, regulatory filing trends |
| 05 | Executive Review Q4 2025 | All verticals: QoQ trends, YoY comparisons, strategic outlook |

## Data Foundation

Every report is backed by real data from public APIs:

| Source | API | What It Provides | Scale |
|--------|-----|-----------------|-------|
| FRED | St. Louis Fed | 50 macroeconomic series (GDP, rates, labor, prices, money supply) | 368K observations |
| Yahoo Finance | Market Data | OHLCV for 200 equities across 10 sectors, 5-year history | 529K price records |
| Open-Meteo | ERA5 Archive | Hourly weather for 30 US cities, 10-year history | 2.6M hourly readings |
| Open-Meteo | Forecast API | Daily weather, 30 cities | 109K daily readings |
| SEC EDGAR | XBRL API | Corporate filings and financial facts | 570K filing records |
| Steam / SteamSpy | Gaming APIs | Player counts, ownership data, revenue estimates | 37K game records |
| ESPN | Sports API | Standings and results across 4 major leagues | 21K standings records |
| CoinGecko | Crypto API | Market data for top cryptocurrencies | 21K market records |

**Total: 4,307,796 data points across 30+ star schema tables.**

## Methodology

### Dimensional Modeling

Raw API data is transformed into Kimball star schemas — dimension tables for descriptive attributes, fact tables for numeric measures. This enables consistent KPI computation across verticals.

### KPI Computation

Each vertical has industry-specific KPIs computed from the fact tables:

**Finance:** GDP growth rate, unemployment delta, CPI inflation rate, yield curve spread, real interest rate
**Brokerage:** Daily returns, Sharpe ratio, sector alpha, volume-weighted average price, RSI
**Crypto:** Market cap change %, BTC dominance, 24h volume ratio, volatility index
**Gaming:** Monthly active users, average playtime, revenue per user, ownership growth rate
**Weather:** Temperature anomaly vs 10-year mean, precipitation deviation, wind speed percentile
**Solar:** Capacity factor, levelized cost of energy, generation efficiency, economic payback period
**Compliance:** Filing frequency, fact density per filing, sector filing concentration
**Betting:** Win percentage, conference standing, streak analysis, strength of schedule

### Report Generation

Reports are generated as branded PDFs using WeasyPrint, with industry-specific color schemes and consistent formatting across all cadences.

## Industry Color Schemes

| Industry | Accent Color | Rationale |
|----------|-------------|-----------|
| Finance | Navy (#1e3a5f) | Trust, stability |
| Brokerage | Navy (#1e3a5f) | Consistent with finance |
| Media | Blue (#2563eb) | Technology, streaming |
| Ecommerce | Amber (#d97706) | Commerce, energy |
| Gaming | Pink (#db2777) | Entertainment, engagement |
| Crypto | Purple (#9333ea) | Innovation, digital |
| Solar | Gold (#ca8a04) | Energy, sunlight |
| Oil & Gas | Burnt Orange (#c2410c) | Industry, petroleum |
| Betting | Green (#16a34a) | Sports, money |
| Compliance | Indigo (#4f46e5) | Regulation, authority |

## Data Quality

Every pipeline output passes validation before report generation:

- **Completeness** — null rates below 5% on all measure columns
- **Uniqueness** — no duplicate natural keys in dimension tables
- **Range** — values within expected bounds (no negative volumes, temperatures in physical range)
- **Consistency** — same metric produces the same value across all reports
- **Attribution** — every number traceable to a specific API endpoint and date

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data Sources | 8 public APIs (no paid subscriptions) |
| Processing | Python, pandas |
| Storage | Parquet (columnar, compressed) |
| Modeling | Kimball star schema (dimensions + facts) |
| Reports | WeasyPrint PDF generation |
| Infrastructure | GCP Compute Engine, PostgreSQL |

## Folder Structure

```
reports/
├── weekly/       # 9 weekly intelligence PDFs
├── monthly/      # 9 monthly review PDFs
└── quarterly/    # 5 quarterly strategic PDFs
methodology/      # KPI definitions, data source documentation
data-sources/     # API reference and data dictionary
```

## Author

**Mboya Jeffers** — Data Analyst & Engineer

- [GitHub](https://github.com/mboyajeffers)
- [LinkedIn](https://linkedin.com/in/mboyajeffers)
