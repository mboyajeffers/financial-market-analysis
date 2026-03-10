# Financial Market Analysis

![Reports](https://img.shields.io/badge/reports-89_PDFs-blue)
![Data Points](https://img.shields.io/badge/data_points-4.3M%2B-green)
![Industries](https://img.shields.io/badge/industries-8_verticals-orange)
![Cadences](https://img.shields.io/badge/cadences-weekly_|_monthly_|_quarterly-purple)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Automated intelligence reports built from **4.3M+ data points** across finance, crypto, energy, and sports — delivered at weekly, monthly, and quarterly cadences. Every metric traces back to a verifiable public data source.

---

## Report Catalog

### Recurring Intelligence (23 reports)

| Cadence | Count | Verticals |
|---------|-------|-----------|
| **Weekly** | 9 | Finance, Brokerage, Crypto, Gaming, Sports, Weather, Solar, Compliance, Executive |
| **Monthly** | 9 | Same verticals — month-over-month trend analysis |
| **Quarterly** | 5 | Financial Markets, Digital Economy, Energy & Climate, Sports & Compliance, Executive Review |

### Industry Analysis & Deep-Dives (39 reports)

Industry-specific analysis reports across 7 verticals:

| Vertical | Count | Examples |
|----------|-------|---------|
| **Media** | 8 | Content trends, platform KPIs, audience analytics |
| **Crypto** | 7 | Market analysis, portfolio risk, DeFi metrics |
| **Betting** | 6 | Odds modeling, spread accuracy, league analysis |
| **Finance** | 5 | Macro indicators, equity performance, sector rotation |
| **Solar** | 5 | Resource screening, generation estimates, ROI |
| **Compliance** | 4 | Regulatory filing patterns, XBRL analysis |
| **Gaming** | 2 | Player engagement, pricing, retention |
| **Sports** | 1 | Premier League snapshot |
| **Weather** | 1 | 5-year multi-city analysis |

Browse: [`reports/industry/`](reports/industry/) · [`samples/`](samples/)

### Methodology & Summaries (12 reports)

| Type | Count | Contents |
|------|-------|---------|
| **Executive Summaries** | 6 | Federal Awards, SEC XBRL, Aviation, Healthcare, Cybersecurity, Energy Grid |
| **Methodology** | 6 | Data validation approaches, KPI derivation, pipeline architecture |

Browse: [`reports/summaries/`](reports/summaries/) · [`reports/methodology/`](reports/methodology/)

### Enterprise Showcase (11 reports)

Branded reports generated for fictional enterprise clients — demonstrating production report quality:

| Client | Vertical | Reports |
|--------|----------|---------|
| **Apex Capital Advisors** | Finance | [Quarterly](showcase/finance/Apex_Capital_Q3_2025_Comprehensive_Analysis.pdf) · [Monthly](showcase/finance/Apex_Capital_Monthly_Portfolio_Review_2025-11.pdf) · [Weekly](showcase/finance/Apex_Capital_Weekly_Market_Pulse_2025-11-21.pdf) |
| **Meridian Digital Assets** | Crypto | [Quarterly](showcase/crypto/Meridian_Crypto_Q3_2025_Portfolio_Analysis.pdf) · [Monthly](showcase/crypto/Meridian_Crypto_Monthly_Review_2025-11.pdf) · [Weekly](showcase/crypto/Meridian_Crypto_Weekly_Snapshot_2025-11-21.pdf) |
| **Sentinel Energy Partners** | Energy | [Monthly](showcase/energy/Sentinel_Energy_Monthly_Production_2025-11.pdf) |
| **Baseline Sports Analytics** | Sports | [Weekly](showcase/sports/Baseline_Sports_Weekly_Intelligence_2025-11-21.pdf) |
| **Platform Overview** | All | [Showcase Index](showcase/Enterprise_Showcase_Index.pdf) · [Platform Capabilities](showcase/Data_Platform_Capabilities.pdf) |

---

## Sample Report Pages

<table>
<tr>
<td align="center"><strong>Finance</strong></td>
<td align="center"><strong>Crypto</strong></td>
<td align="center"><strong>Energy</strong></td>
<td align="center"><strong>Sports</strong></td>
</tr>
<tr>
<td><img src="images/finance-1.png" width="200"/></td>
<td><img src="images/crypto-1.png" width="200"/></td>
<td><img src="images/energy-1.png" width="200"/></td>
<td><img src="images/sports-1.png" width="200"/></td>
</tr>
<tr>
<td><img src="images/finance-2.png" width="200"/></td>
<td><img src="images/crypto-2.png" width="200"/></td>
<td><img src="images/energy-2.png" width="200"/></td>
<td><img src="images/sports-2.png" width="200"/></td>
</tr>
<tr>
<td><img src="images/finance-3.png" width="200"/></td>
<td><img src="images/crypto-3.png" width="200"/></td>
<td><img src="images/energy-3.png" width="200"/></td>
<td><img src="images/sports-3.png" width="200"/></td>
</tr>
</table>

---

## Report Generators

Each vertical has a standalone Python generator that pulls live data from public APIs and produces a branded PDF:

| Generator | Data Source | What It Produces |
|-----------|------------|-----------------|
| [`generate_finance_report.py`](generators/generate_finance_report.py) | FRED + Yahoo Finance | Macro analysis, portfolio performance, risk metrics (Sharpe, beta, alpha, max drawdown) |
| [`generate_crypto_report.py`](generators/generate_crypto_report.py) | CoinGecko | Portfolio KPIs (VaR, Sortino, HHI concentration), top-20 market data |
| [`generate_energy_report.py`](generators/generate_energy_report.py) | EIA API + Yahoo Finance | Crude/gas production trends, WTI pricing, revenue estimates |
| [`generate_sports_report.py`](generators/generate_sports_report.py) | ESPN | NFL standings, Pythagorean win analysis, conference breakdowns |

### Running a Generator

```bash
pip install weasyprint
python generators/generate_finance_report.py
```

Each generator fetches live data, computes KPIs, and outputs a branded PDF to `output/`. No API keys required (all public endpoints).

The shared [`report_template.py`](generators/report_template.py) provides consistent styling — KPI grids, risk badges, methodology sections, and industry-specific color schemes.

---

## Services

Automated analytics reports available across four verticals:

### Crypto Portfolio Analytics
Portfolio performance, risk metrics (VaR, Sharpe, Sortino), allocation analysis, volume anomaly detection.

| Cadence | Starter | Pro | Enterprise |
|---------|---------|-----|------------|
| Weekly | $250 | $500 | $1,200 |
| Monthly | $500 | $1,500 | $3,500 |
| Quarterly | $1,200 | $3,500 | $8,000 |

### Financial Analytics
Macro indicators (FRED), equity performance (Yahoo Finance), risk decomposition, sector analysis.

| Cadence | Starter | Pro | Enterprise |
|---------|---------|-----|------------|
| Weekly | $200 | $400 | $1,000 |
| Monthly | $400 | $1,200 | $3,000 |
| Quarterly | $1,000 | $3,000 | $7,000 |

### Energy Market Intelligence
Production trends (EIA), commodity pricing, revenue estimates, compliance monitoring.

| Cadence | Starter | Pro | Enterprise |
|---------|---------|-----|------------|
| Weekly | $200 | $400 | $1,000 |
| Monthly | $400 | $1,200 | $3,000 |
| Quarterly | $1,000 | $3,000 | $7,000 |

### Sports Analytics
League standings, Pythagorean projections, conference analysis, performance trends.

| Cadence | Starter | Pro | Enterprise |
|---------|---------|-----|------------|
| Weekly | $150 | $300 | $800 |
| Monthly | $300 | $900 | $2,500 |
| Quarterly | $800 | $2,500 | $6,000 |

**Tier differences:** Starter = core KPIs, single-portfolio. Pro = full KPI suite, benchmark comparisons, data exports. Enterprise = multi-portfolio, compliance formatting, sign-off workflows, audit trails.

[View full service details](showcase/Service_Offerings_2026.pdf)

### How to Order

Email **MboyaJeffers9@gmail.com** with:
1. Vertical (crypto, finance, energy, or sports)
2. Cadence (weekly, monthly, or quarterly)
3. Tier (starter, pro, or enterprise)

---

## Data Sources

Every report is backed by real data from public APIs:

| Source | API | What It Provides | Scale |
|--------|-----|-----------------|-------|
| FRED | St. Louis Fed | 50 macroeconomic series (GDP, rates, labor, prices) | 368K observations |
| Yahoo Finance | Market Data | OHLCV for 200 equities, 5-year history | 529K price records |
| Open-Meteo | ERA5 Archive | Hourly weather for 30 US cities, 10-year history | 2.6M hourly readings |
| SEC EDGAR | XBRL API | Corporate filings and financial facts | 570K filing records |
| CoinGecko | Crypto API | Market data for top cryptocurrencies | 21K market records |
| ESPN | Sports API | Standings and results across 4 major leagues | 21K standings records |
| EIA | Energy API | US crude/gas production, pricing | Production time series |
| Steam / SteamSpy | Gaming APIs | Player counts, ownership data | 37K game records |

**Total: 4.3M+ data points across 30+ star schema tables.**

## Data Quality

Every pipeline output passes validation before report generation:

- **Completeness** — null rates below 5% on all measure columns
- **Uniqueness** — no duplicate natural keys in dimension tables
- **Range** — values within expected bounds
- **Consistency** — same metric produces the same value across all reports
- **Attribution** — every number traceable to a specific API endpoint and date

## Methodology

Raw API data is transformed into Kimball star schemas — dimension tables for descriptive attributes, fact tables for numeric measures. Industry-specific KPIs are computed from the fact tables. Reports are generated as branded PDFs using WeasyPrint with industry-specific color schemes.

Full methodology: [KPI definitions](methodology/kpi-definitions.md) · [API reference](data-sources/api-reference.md)

## Folder Structure

```
financial-market-analysis/
├── generators/                  # Python report generators
│   ├── generate_crypto_report.py
│   ├── generate_finance_report.py
│   ├── generate_energy_report.py
│   ├── generate_sports_report.py
│   └── report_template.py       # Shared styling/components
├── reports/
│   ├── weekly/                  # 9 weekly intelligence PDFs
│   ├── monthly/                 # 9 monthly review PDFs
│   ├── quarterly/               # 5 quarterly strategic PDFs
│   ├── industry/                # 39 industry analysis reports (7 verticals)
│   ├── summaries/               # 6 executive summaries
│   └── methodology/             # 6 methodology deep-dives
├── samples/                     # Sample reports (finance, crypto, energy, sports, weather)
├── showcase/                    # Enterprise showcase reports
│   ├── finance/                 # Apex Capital reports
│   ├── crypto/                  # Meridian reports
│   ├── energy/                  # Sentinel Energy reports
│   ├── sports/                  # Baseline Sports reports
│   └── Service_Offerings_2026.pdf
├── images/                      # Report page samples
├── methodology/                 # KPI definitions
├── data-sources/                # API reference
└── LICENSE
```

## Tech Stack

| Layer | Tools |
|-------|-------|
| Data Sources | 8 public APIs (no paid subscriptions) |
| Processing | Python, pandas |
| Storage | Parquet (columnar, compressed) |
| Modeling | Kimball star schema (dimensions + facts) |
| Reports | WeasyPrint PDF generation |
| ML | scikit-learn, statsmodels (GARCH, momentum classification) |
| Infrastructure | GCP Compute Engine, PostgreSQL |

## Author

**Mboya Jeffers** — Data & ML Engineer

- [GitHub](https://github.com/mboyajeffers)
- [LinkedIn](https://linkedin.com/in/mboya-jeffers-6377ba325)
- **MboyaJeffers9@gmail.com** · Open to remote data engineering roles and analytics consulting
