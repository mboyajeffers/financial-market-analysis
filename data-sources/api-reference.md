# Data Source Reference

Documentation for all 8 public APIs used in report generation.

## FRED (Federal Reserve Economic Data)

- **Provider:** Federal Reserve Bank of St. Louis
- **URL:** https://fred.stlouisfed.org
- **Auth:** Free API key (register at fred.stlouisfed.org)
- **Rate Limit:** 120 requests/minute
- **Coverage:** 800,000+ economic time series
- **Used Series:** 50 (GDP, unemployment, CPI, Fed funds, yield curve, labor, housing, money supply, exchange rates, industrial production)
- **Update Frequency:** Varies (daily to quarterly depending on series)

## Yahoo Finance

- **Provider:** Yahoo Inc.
- **Access:** Public API (no key required)
- **Rate Limit:** ~200 requests/minute
- **Coverage:** Global equities, ETFs, indices
- **Used Tickers:** 200 (S&P 500 top holdings across 10 sectors)
- **Data Types:** OHLCV bars, company profiles, financial statements
- **History:** Up to 10 years daily

## Open-Meteo

- **Provider:** Open-Meteo.com
- **URL:** https://open-meteo.com
- **Auth:** None required (free tier)
- **Rate Limit:** 10,000 requests/day
- **APIs Used:**
  - **Forecast API** — 16-day forecast + recent history
  - **ERA5 Archive API** — Historical hourly data back to 1940
- **Coverage:** Global (0.25 degree resolution)
- **Used Locations:** 30 major US cities
- **Variables:** Temperature, humidity, precipitation, wind speed, surface pressure

## SEC EDGAR

- **Provider:** U.S. Securities and Exchange Commission
- **URL:** https://efts.sec.gov/LATEST/
- **Auth:** User-Agent header with contact email
- **Rate Limit:** 10 requests/second
- **Coverage:** All SEC-registered companies
- **Data Types:** XBRL filings, financial facts, company metadata
- **Used Tickers:** 5-10 major companies per extraction

## CoinGecko

- **Provider:** CoinGecko
- **URL:** https://api.coingecko.com/api/v3
- **Auth:** None required (free tier)
- **Rate Limit:** 10-30 requests/minute (free tier)
- **Coverage:** 10,000+ cryptocurrencies
- **Data Types:** Market data, coin details, historical prices, exchanges
- **Used Coins:** Top 100-250 by market cap

## Steam Web API + SteamSpy

- **Provider:** Valve Corporation / SteamSpy
- **URLs:**
  - https://api.steampowered.com
  - https://steamspy.com/api.php
- **Auth:** Steam API key (free) / SteamSpy (no key)
- **Rate Limit:** Steam ~200 req/5min, SteamSpy 1 req/1.5sec
- **Coverage:** 50,000+ games on Steam
- **Data Types:** App details, player counts, ownership estimates, reviews

## ESPN

- **Provider:** ESPN / Disney
- **Access:** Public API endpoints
- **Auth:** None required
- **Coverage:** NFL, NBA, MLB, NHL
- **Data Types:** League standings, team records, conference rankings
- **Update Frequency:** Real-time during seasons

## NREL (National Renewable Energy Laboratory)

- **Provider:** U.S. Department of Energy
- **URL:** https://developer.nrel.gov
- **Auth:** Free API key
- **Coverage:** Solar resource data for any US location
- **Data Types:** PVWatts solar generation estimates, irradiance data
- **Models:** PVWatts v8 (system performance), TMY (typical meteorological year)
