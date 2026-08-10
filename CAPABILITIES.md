# Platform Capabilities

Vertical-by-vertical breakdown of data sources, KPIs, and report outputs.

---

## Crypto

**Data pulled:**
- CoinGecko: top 20 assets by market cap — price, 24h volume, market cap, 7-day change, circulating supply
- On-chain volume and dominance metrics

**KPIs computed:**
- Realized volatility (7-day, 30-day rolling)
- Volume-weighted average price (VWAP)
- Market cap concentration (top 5 vs. rest)
- Relative strength index (RSI)
- Bitcoin dominance trend
- Drawdown from ATH

**Report contents:**
- Portfolio performance summary
- Asset-level KPI table with trend arrows
- Market structure analysis (bull/bear/sideways)
- Risk-adjusted return vs. BTC benchmark
- Weekly snapshot + monthly deep-dive + quarterly comprehensive review

**Sample reports:**
- [Q3 2025 Portfolio Analysis](reports/crypto/Meridian_Crypto_Q3_2025_Portfolio_Analysis.pdf)
- [Weekly Snapshot 2025-11-21](reports/crypto/Meridian_Crypto_Weekly_Snapshot_2025-11-21.pdf)
- [Monthly Review 2025-11](reports/crypto/Meridian_Crypto_Monthly_Review_2025-11.pdf)

---

## Finance

**Data pulled:**
- Yahoo Finance: equity prices, ETF NAV, commodity futures, index levels
- FRED: federal funds rate, CPI, unemployment, yield curve (2Y/10Y spread), M2 money supply

**KPIs computed:**
- Portfolio return vs. SPY benchmark
- Sharpe ratio, Sortino ratio
- Beta, correlation matrix
- Sector allocation drift
- Macro regime indicators (yield curve inversion, CPI trend)
- Earnings momentum proxies

**Report contents:**
- Weekly market pulse (top movers, macro snapshot)
- Monthly portfolio review (attribution, risk, outlook)
- Quarterly comprehensive (full factor analysis, drawdown periods, rebalancing recommendations)

**Sample reports:**
- [Weekly Market Pulse 2025-11-21](reports/finance/Apex_Capital_Weekly_Market_Pulse_2025-11-21.pdf)
- [Monthly Portfolio Review 2025-11](reports/finance/Apex_Capital_Monthly_Portfolio_Review_2025-11.pdf)
- [Q3 2025 Comprehensive Analysis](reports/finance/Apex_Capital_Q3_2025_Comprehensive_Analysis.pdf)

---

## Oil & Gas / Energy

**Data pulled:**
- EIA API v2: crude oil production (MBBL/D), natural gas production (MMCF), rig count, refinery utilization
- Yahoo Finance: WTI futures (CL=F), natural gas futures (NG=F)
- Open-Meteo: temperature forecasts (heating/cooling demand proxy)

**KPIs computed:**
- Production vs. prior month delta
- Price realization vs. benchmark
- Rig count trend (leading indicator)
- Days of supply
- Weather-adjusted demand forecast

**Report contents:**
- Monthly production summary
- Commodity price performance
- Operational efficiency metrics
- Forward-looking demand indicators

**Sample report:**
- [Monthly Production Report 2025-11](reports/energy/Sentinel_Energy_Monthly_Production_2025-11.pdf)

---

## Solar / Renewables

**Data pulled:**
- NREL: solar irradiance, capacity factors, generation estimates by region
- Open-Meteo: cloud cover, temperature, wind speed

**KPIs computed:**
- Capacity factor vs. seasonal average
- Generation forecast (7-day, 30-day)
- Weather-adjusted performance ratio
- Grid export efficiency

**Report contents:**
- Monthly generation report
- Weather impact analysis
- Regional performance benchmarking

---

## Sports

**Data pulled:**
- ESPN API (public): NFL, NBA, MLB, NHL — scores, standings, player stats, team performance
- Historical game-by-game data for trend analysis

**KPIs computed:**
- Win probability models (ELO-based)
- Player performance z-scores vs. positional average
- Team offensive/defensive efficiency ratings
- Schedule strength adjustment
- Injury impact flags

**Report contents:**
- Weekly intelligence briefing (league leaders, trending performers)
- Team performance dashboard
- Betting market context (line movements vs. model)

---

## Compliance / SEC Filings

**Data pulled:**
- SEC EDGAR: 10-K, 10-Q, 8-K filings — structured financial data via EDGAR JSON API

**KPIs computed:**
- Revenue growth YoY / QoQ
- Gross margin, operating margin, net margin trends
- R&D / revenue ratio
- Debt-to-equity, interest coverage
- Cash runway
- 8-K material event flags

**Report contents:**
- Filing summary with key financial highlights
- Multi-period trend analysis
- Peer comparison (same SIC code)
- Red flag detection (restatements, going concern language)

---

## Gaming / Media

**Data pulled:**
- Yahoo Finance: publicly traded gaming and media equities
- FRED: consumer spending on recreation
- Supplementary: app store rank data (web scrape where available)

**KPIs computed:**
- Revenue per user proxies
- Subscriber growth trends
- Content spend vs. revenue ratio
- Competitive positioning vs. sector ETFs

**Report contents:**
- Sector performance snapshot
- Company-level KPI dashboard
- Valuation multiples vs. historical range

---

## Weather

**Data pulled:**
- Open-Meteo: temperature, precipitation, wind, solar radiation — global coverage, 7-day forecast + 90-day historical

**KPIs computed:**
- Heating Degree Days (HDD) / Cooling Degree Days (CDD)
- Precipitation anomaly vs. 30-year average
- Extreme weather event flags
- Agricultural stress index (drought / frost risk)

**Report contents:**
- Regional weather intelligence
- Energy demand impact analysis
- Agricultural / commodity price risk assessment

---

## Platform Overview

For the full platform capabilities summary, see:
- [Data Platform Capabilities PDF](reports/platform/Data_Platform_Capabilities.pdf)

Back to [README](README.md)
