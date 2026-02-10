# KPI Definitions

Standard KPI definitions used across all industry intelligence reports.

## Finance

| KPI | Formula | Source |
|-----|---------|--------|
| GDP Growth Rate | (GDP_t - GDP_t-1) / GDP_t-1 * 100 | FRED: GDP |
| Unemployment Delta | UNRATE_t - UNRATE_t-1 | FRED: UNRATE |
| CPI Inflation Rate | (CPI_t - CPI_t-12) / CPI_t-12 * 100 | FRED: CPIAUCSL |
| Real Interest Rate | FEDFUNDS - CPI_inflation | FRED: FEDFUNDS, CPIAUCSL |
| Yield Curve Spread | DGS10 - DGS2 | FRED: DGS10, DGS2 |
| 10Y-3M Spread | DGS10 - DGS3MO | FRED: DGS10, DGS3MO |

## Brokerage

| KPI | Formula | Source |
|-----|---------|--------|
| Daily Return | (close_t - close_t-1) / close_t-1 * 100 | Yahoo: historical |
| Sharpe Ratio | mean(returns) / std(returns) * sqrt(252) | Computed |
| RSI (14-day) | 100 - (100 / (1 + avg_gain/avg_loss)) | Yahoo: historical |
| Volume Trend | volume_t / SMA(volume, 20) | Yahoo: historical |
| Sector Alpha | sector_return - SPY_return | Yahoo: historical |

## Crypto

| KPI | Formula | Source |
|-----|---------|--------|
| Market Cap Change % | (mcap_t - mcap_t-1) / mcap_t-1 * 100 | CoinGecko: markets |
| BTC Dominance | btc_mcap / total_mcap * 100 | CoinGecko: markets |
| 24h Volume Ratio | volume_24h / market_cap | CoinGecko: markets |
| Price Volatility | std(returns, 30d) * sqrt(365) | Computed |

## Gaming

| KPI | Formula | Source |
|-----|---------|--------|
| Current Players | Live count | Steam API |
| Ownership Estimate | SteamSpy median | SteamSpy API |
| Revenue Estimate | owners * price * conversion_rate | Computed |
| Player Retention | current_players / peak_players | Steam API |

## Weather

| KPI | Formula | Source |
|-----|---------|--------|
| Temp Anomaly | temp_t - mean(temp, 10yr) | Open-Meteo: ERA5 |
| Precip Deviation | precip_t - mean(precip, 10yr) | Open-Meteo: ERA5 |
| Heating Degree Days | max(0, 18 - avg_temp) | Computed |
| Cooling Degree Days | max(0, avg_temp - 18) | Computed |

## Solar

| KPI | Formula | Source |
|-----|---------|--------|
| Capacity Factor | actual_gen / max_gen * 100 | NREL: PVWatts |
| LCOE | total_cost / lifetime_gen | Computed |
| Payback Period | install_cost / annual_savings | Computed |
| Generation Efficiency | actual_kwh / irradiance_kwh * 100 | NREL: PVWatts |

## Compliance

| KPI | Formula | Source |
|-----|---------|--------|
| Filing Frequency | filings_count / period_days | SEC EDGAR |
| Fact Density | facts_count / filing_count | SEC EDGAR: XBRL |
| Sector Concentration | sector_filings / total_filings * 100 | SEC EDGAR |

## Betting

| KPI | Formula | Source |
|-----|---------|--------|
| Win Percentage | wins / (wins + losses) * 100 | ESPN |
| Conference Rank | Ordinal position in conference | ESPN |
| Streak Length | Consecutive W or L count | ESPN |
