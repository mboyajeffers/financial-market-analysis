#!/usr/bin/env python3
"""
Generate Sample Financial Analytics Report
Apex Capital Advisors — Quarterly Market Intelligence
Uses Yahoo Finance + FRED CSV (direct download) — REAL DATA ONLY (no fallback)
"""

import json
import math
import os
import time
import urllib.request
import urllib.error
import csv
import io
from datetime import datetime, timedelta
from weasyprint import HTML

# --- FRED Data Pull (CSV direct — no API key needed) ---
def fetch_fred_csv(series_id, max_retries=3):
    """Pull latest values from FRED via direct CSV download (no API key needed)."""
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}&cosd=2024-01-01"
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                text = resp.read().decode()
                reader = csv.reader(io.StringIO(text))
                header = next(reader)
                rows = list(reader)
                # Get latest non-empty value
                for row in reversed(rows):
                    if len(row) >= 2 and row[1] and row[1] != ".":
                        return {"date": row[0], "value": float(row[1])}
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            raise RuntimeError(f"FRED CSV {series_id} failed after {max_retries} attempts: {e}")
    raise RuntimeError(f"FRED CSV {series_id}: no data returned")

# --- Yahoo Finance Data Pull ---
def fetch_yahoo_chart(ticker, max_retries=3):
    """Pull 3-month daily OHLCV from Yahoo Finance. Returns closes list."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=3mo&interval=1d"
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                result = data["chart"]["result"][0]
                meta = result["meta"]
                closes = result["indicators"]["quote"][0]["close"]
                closes = [c for c in closes if c is not None]
                if not closes:
                    raise RuntimeError(f"Yahoo {ticker}: empty closes")

                current = closes[-1]
                prev = closes[0] if len(closes) > 1 else current
                pct_change = ((current - prev) / prev * 100) if prev else 0

                # Daily returns for risk metrics
                returns = []
                for i in range(1, len(closes)):
                    if closes[i-1] and closes[i-1] > 0:
                        returns.append((closes[i] - closes[i-1]) / closes[i-1])

                vol = math.sqrt(sum(r**2 for r in returns) / len(returns)) * math.sqrt(252) * 100 if returns else 0
                avg_return = sum(returns) / len(returns) if returns else 0
                ann_return = avg_return * 252 * 100

                # Max drawdown
                peak = closes[0]
                max_dd = 0
                for c in closes:
                    if c > peak:
                        peak = c
                    dd = (c - peak) / peak * 100 if peak else 0
                    if dd < max_dd:
                        max_dd = dd

                return {
                    "ticker": ticker,
                    "name": meta.get("shortName", meta.get("symbol", ticker)),
                    "price": current,
                    "change_3mo": pct_change,
                    "high_3mo": max(closes),
                    "low_3mo": min(closes),
                    "volatility": vol,
                    "ann_return": ann_return,
                    "max_drawdown": max_dd,
                    "currency": meta.get("currency", "USD"),
                    "exchange": meta.get("exchangeName", ""),
                    "daily_returns": returns,
                }
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            raise RuntimeError(f"Yahoo Finance {ticker} failed after {max_retries} attempts: {e}")


def compute_r_squared(stock_returns, benchmark_returns):
    """Compute R-squared between stock and benchmark returns."""
    n = min(len(stock_returns), len(benchmark_returns))
    if n < 5:
        return 0.0
    sr = stock_returns[-n:]
    br = benchmark_returns[-n:]
    mean_s = sum(sr) / n
    mean_b = sum(br) / n
    ss_res = sum((s - mean_s - (b - mean_b))**2 for s, b in zip(sr, br))
    ss_tot = sum((s - mean_s)**2 for s in sr)
    if ss_tot == 0:
        return 0.0
    return max(0, 1 - ss_res / ss_tot)


def compute_beta(stock_returns, benchmark_returns):
    """Compute beta of stock vs benchmark."""
    n = min(len(stock_returns), len(benchmark_returns))
    if n < 5:
        return 1.0
    sr = stock_returns[-n:]
    br = benchmark_returns[-n:]
    mean_s = sum(sr) / n
    mean_b = sum(br) / n
    cov = sum((s - mean_s) * (b - mean_b) for s, b in zip(sr, br)) / n
    var_b = sum((b - mean_b)**2 for b in br) / n
    if var_b == 0:
        return 1.0
    return cov / var_b


def compute_portfolio_kpis(stocks, benchmark):
    """Compute portfolio-level KPIs using real benchmark data."""
    n = len(stocks)
    if n == 0:
        return {}

    # Equal-weight portfolio
    avg_return = sum(s["ann_return"] for s in stocks) / n
    avg_vol = sum(s["volatility"] for s in stocks) / n
    avg_dd = sum(s["max_drawdown"] for s in stocks) / n
    rf = 4.33  # Will be overridden by real FRED data

    sharpe = (avg_return - rf) / avg_vol if avg_vol > 0 else 0

    # Compute real beta and R-squared vs SPY benchmark
    betas = []
    r_squareds = []
    bench_returns = benchmark.get("daily_returns", [])
    for s in stocks:
        sr = s.get("daily_returns", [])
        b = compute_beta(sr, bench_returns)
        r2 = compute_r_squared(sr, bench_returns)
        betas.append(b)
        r_squareds.append(r2)

    avg_beta = sum(betas) / len(betas) if betas else 1.0
    avg_r_squared = sum(r_squareds) / len(r_squareds) if r_squareds else 0.0

    # Jensen's alpha = actual return - (rf + beta * (market_return - rf))
    market_return = benchmark.get("ann_return", avg_return)
    alpha = avg_return - (rf + avg_beta * (market_return - rf))

    return {
        "avg_ann_return": avg_return,
        "avg_volatility": avg_vol,
        "avg_max_drawdown": avg_dd,
        "sharpe_ratio": sharpe,
        "portfolio_beta": avg_beta,
        "jensens_alpha": alpha,
        "r_squared": avg_r_squared,
        "risk_free_rate": rf,
        "num_holdings": n,
        "benchmark_return": market_return,
    }


def fmt_pct(val):
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.2f}%"

def pct_color(val):
    if val > 0: return "#16a34a"
    if val < 0: return "#dc2626"
    return "#6b7280"


def generate_html(stocks, macro, kpis, benchmark):
    today = datetime.now().strftime("%B %d, %Y")

    stock_rows = ""
    for s in stocks:
        stock_rows += f"""
        <tr>
            <td style="font-weight:600;">{s['ticker']}</td>
            <td>{s['name']}</td>
            <td style="text-align:right;">${s['price']:,.2f}</td>
            <td style="text-align:right;color:{pct_color(s['change_3mo'])}">{fmt_pct(s['change_3mo'])}</td>
            <td style="text-align:right;">${s['high_3mo']:,.2f}</td>
            <td style="text-align:right;">${s['low_3mo']:,.2f}</td>
            <td style="text-align:right;">{s['volatility']:.1f}%</td>
            <td style="text-align:right;color:{pct_color(s['max_drawdown'])}">{fmt_pct(s['max_drawdown'])}</td>
        </tr>"""

    macro_rows = ""
    for key, m in macro.items():
        val = m["value"]
        if key in ("UNRATE", "FEDFUNDS", "DGS10"):
            val_str = f"{val:.2f}%"
        elif key == "GDP":
            val_str = f"${val:,.0f}B"
        else:
            val_str = f"{val:.1f}"
        macro_rows += f"""
        <tr>
            <td style="font-weight:600;">{m['label']}</td>
            <td>{m['series']}</td>
            <td style="text-align:right;">{val_str}</td>
            <td>{m['date']}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{
    size: letter;
    margin: 0.6in 0.75in;
    @bottom-center {{
        content: "Sample Report — Analyst: Mboya Jeffers | Live market data from Yahoo Finance + FRED";
        font-size: 7pt;
        color: #9ca3af;
    }}
    @bottom-right {{
        content: "Page " counter(page) " of " counter(pages);
        font-size: 7pt;
        color: #9ca3af;
    }}
}}
body {{
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-size: 9.5pt;
    line-height: 1.5;
    color: #1f2937;
}}
.cover {{
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 8.5in;
    text-align: center;
}}
.cover-title {{
    font-size: 28pt;
    font-weight: 700;
    color: #1e3a5f;
    margin-bottom: 8px;
}}
.cover-subtitle {{
    font-size: 16pt;
    color: #6b7280;
    margin-bottom: 40px;
}}
.cover-line {{
    width: 80px;
    height: 3px;
    background: #1e3a5f;
    margin: 24px auto;
}}
.cover-detail {{
    font-size: 13pt;
    color: #4b5563;
    margin-bottom: 6px;
}}
.cover-date {{
    font-size: 11pt;
    color: #9ca3af;
}}
h1 {{
    font-size: 16pt;
    color: #1e3a5f;
    border-bottom: 2px solid #1e3a5f;
    padding-bottom: 4px;
    margin-top: 20px;
}}
h2 {{
    font-size: 12pt;
    color: #2563eb;
    margin-top: 16px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 8.5pt;
}}
th {{
    background: #1e3a5f;
    color: white;
    padding: 6px 8px;
    text-align: left;
    font-weight: 600;
    font-size: 8pt;
}}
td {{
    padding: 5px 8px;
    border-bottom: 1px solid #e5e7eb;
}}
tr:nth-child(even) {{
    background: #e8f0f7;
}}
.kpi-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    margin: 12px 0;
}}
.kpi-card {{
    background: #e8f0f7;
    border: 1px solid #bfdbfe;
    border-radius: 6px;
    padding: 10px 12px;
    text-align: center;
}}
.kpi-value {{
    font-size: 16pt;
    font-weight: 700;
    color: #1e3a5f;
}}
.kpi-label {{
    font-size: 7.5pt;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.exec-box {{
    background: #e8f0f7;
    border-left: 4px solid #1e3a5f;
    padding: 12px 16px;
    margin: 12px 0;
    border-radius: 0 6px 6px 0;
}}
.risk-high {{ color: #dc2626; font-weight: 600; }}
.risk-med {{ color: #d97706; font-weight: 600; }}
.risk-low {{ color: #16a34a; font-weight: 600; }}
.disclaimer {{
    margin-top: 24px;
    padding: 12px;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    font-size: 7.5pt;
    color: #6b7280;
}}
.section-break {{
    page-break-before: always;
}}
.footer-attribution {{
    text-align: center;
    font-size: 8pt;
    color: #9ca3af;
    margin-top: 30px;
    border-top: 1px solid #e5e7eb;
    padding-top: 8px;
}}
ul, ol {{ padding-left: 18px; }}
li {{ margin-bottom: 4px; }}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
    <div class="cover-title">Apex Capital Advisors</div>
    <div class="cover-line"></div>
    <div class="cover-subtitle">Quarterly Market Intelligence Report</div>
    <div class="cover-detail">Equity Portfolio & Macroeconomic Analysis</div>
    <div class="cover-detail">{kpis['num_holdings']} Equity Holdings | SPY Benchmark | 5 FRED Macro Indicators</div>
    <div class="cover-date">Report Date: {today}</div>
    <div class="cover-date" style="margin-top:30px;font-size:9pt;color:#6b7280;">
        SAMPLE REPORT — Live market data from Yahoo Finance + Federal Reserve (FRED)
    </div>
</div>

<!-- EXECUTIVE SUMMARY -->
<h1>1. Executive Summary</h1>
<div class="exec-box">
    <ul>
        <li><strong>Portfolio Return (Annualized):</strong> <span style="color:{pct_color(kpis['avg_ann_return'])}">{fmt_pct(kpis['avg_ann_return'])}</span> vs. SPY benchmark <span style="color:{pct_color(kpis['benchmark_return'])}">{fmt_pct(kpis['benchmark_return'])}</span></li>
        <li><strong>Risk Profile:</strong> Sharpe ratio of {kpis['sharpe_ratio']:.2f} | Beta {kpis['portfolio_beta']:.2f} | R-squared {kpis['r_squared']:.2f} vs. SPY</li>
        <li><strong>Macro Environment:</strong> Fed Funds at {macro['FEDFUNDS']['value']:.2f}%, unemployment at {macro['UNRATE']['value']:.1f}%, 10Y yield at {macro['DGS10']['value']:.2f}%</li>
        <li><strong>Drawdown Risk:</strong> Average max drawdown of {fmt_pct(kpis['avg_max_drawdown'])} — {"within normal range" if kpis['avg_max_drawdown'] > -15 else "elevated drawdown risk warrants monitoring"}</li>
        <li><strong>Sector Mix:</strong> Diversified across Technology, Financials, Healthcare, and Energy</li>
    </ul>
</div>

<!-- MACRO OVERVIEW -->
<h1>2. Macroeconomic Environment</h1>
<p>Key economic indicators sourced directly from the Federal Reserve Economic Data (FRED) system via CSV download. All values are the latest available observations.</p>
<table>
    <thead>
        <tr><th>Indicator</th><th>FRED Series</th><th style="text-align:right;">Latest Value</th><th>As Of</th></tr>
    </thead>
    <tbody>
        {macro_rows}
    </tbody>
</table>

<h2>Economic Outlook</h2>
<p>The macroeconomic backdrop reflects {"a moderating growth environment" if macro['FEDFUNDS']['value'] > 4 else "an accommodative monetary environment"}. With the Federal Funds rate at {macro['FEDFUNDS']['value']:.2f}% and the 10-Year Treasury yielding {macro['DGS10']['value']:.2f}%, the yield curve {"remains inverted, historically signaling caution" if macro['DGS10']['value'] < macro['FEDFUNDS']['value'] else "reflects expectations for sustained growth"}. Unemployment at {macro['UNRATE']['value']:.1f}% indicates a {"tight labor market" if macro['UNRATE']['value'] < 4.5 else "softening labor market"} with implications for consumer spending and corporate earnings.</p>

<!-- EQUITY PORTFOLIO -->
<div class="section-break"></div>
<h1>3. Equity Portfolio Overview</h1>
<table>
    <thead>
        <tr>
            <th>Ticker</th>
            <th>Company</th>
            <th style="text-align:right;">Price</th>
            <th style="text-align:right;">3mo Change</th>
            <th style="text-align:right;">3mo High</th>
            <th style="text-align:right;">3mo Low</th>
            <th style="text-align:right;">Ann. Vol</th>
            <th style="text-align:right;">Max DD</th>
        </tr>
    </thead>
    <tbody>
        {stock_rows}
    </tbody>
</table>
<p style="font-size:7.5pt;color:#9ca3af;">Data sourced from Yahoo Finance API. Equal-weight portfolio. Benchmark: SPY (S&P 500 ETF). Prices as of {today}. All data independently verifiable.</p>

<!-- KPI DASHBOARD -->
<h1>4. KPI Dashboard</h1>
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-value">{kpis['sharpe_ratio']:.2f}</div>
        <div class="kpi-label">Sharpe Ratio</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['portfolio_beta']:.2f}</div>
        <div class="kpi-label">Portfolio Beta (vs SPY)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{fmt_pct(kpis['jensens_alpha'])}</div>
        <div class="kpi-label">Jensen's Alpha</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{fmt_pct(kpis['avg_ann_return'])}</div>
        <div class="kpi-label">Annualized Return</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['avg_volatility']:.1f}%</div>
        <div class="kpi-label">Portfolio Volatility</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['r_squared']:.2f}</div>
        <div class="kpi-label">R-Squared (vs SPY)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{fmt_pct(kpis['avg_max_drawdown'])}</div>
        <div class="kpi-label">Avg Max Drawdown</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['risk_free_rate']:.2f}%</div>
        <div class="kpi-label">Risk-Free Rate (FRED)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['num_holdings']}</div>
        <div class="kpi-label">Holdings Count</div>
    </div>
</div>

<h2>Full KPI Table</h2>
<table>
    <thead>
        <tr><th>KPI</th><th style="text-align:right;">Value</th><th>Interpretation</th></tr>
    </thead>
    <tbody>
        <tr><td>Sharpe Ratio (Annualized)</td><td style="text-align:right;">{kpis['sharpe_ratio']:.2f}</td><td>{"Strong risk-adjusted returns" if kpis['sharpe_ratio'] > 0.5 else "Below-average risk-adjusted returns"}</td></tr>
        <tr><td>Portfolio Beta (vs SPY)</td><td style="text-align:right;">{kpis['portfolio_beta']:.2f}</td><td>{"Market-neutral exposure" if abs(kpis['portfolio_beta'] - 1) < 0.15 else "Deviation from market beta"} — computed from daily returns regression</td></tr>
        <tr><td>Jensen's Alpha</td><td style="text-align:right;">{fmt_pct(kpis['jensens_alpha'])}</td><td>{"Positive alpha generation" if kpis['jensens_alpha'] > 0 else "Negative alpha — underperforming CAPM expectations"}</td></tr>
        <tr><td>R-Squared (vs SPY)</td><td style="text-align:right;">{kpis['r_squared']:.2f}</td><td>{"High correlation to S&P 500" if kpis['r_squared'] > 0.7 else "Moderate market correlation"} — computed from daily returns</td></tr>
        <tr><td>Annualized Return</td><td style="text-align:right;color:{pct_color(kpis['avg_ann_return'])}">{fmt_pct(kpis['avg_ann_return'])}</td><td>{"Exceeds risk-free rate" if kpis['avg_ann_return'] > kpis['risk_free_rate'] else "Below risk-free rate"}</td></tr>
        <tr><td>SPY Benchmark Return</td><td style="text-align:right;color:{pct_color(kpis['benchmark_return'])}">{fmt_pct(kpis['benchmark_return'])}</td><td>S&P 500 ETF annualized return (same period)</td></tr>
        <tr><td>Portfolio Volatility</td><td style="text-align:right;">{kpis['avg_volatility']:.1f}%</td><td>{"Within typical equity range (15-25%)" if 15 < kpis['avg_volatility'] < 25 else "Outside typical equity range"}</td></tr>
        <tr><td>Average Max Drawdown</td><td style="text-align:right;color:{pct_color(kpis['avg_max_drawdown'])}">{fmt_pct(kpis['avg_max_drawdown'])}</td><td>{"Normal drawdown range" if kpis['avg_max_drawdown'] > -15 else "Elevated drawdown risk"}</td></tr>
        <tr><td>Risk-Free Rate (FRED FEDFUNDS)</td><td style="text-align:right;">{kpis['risk_free_rate']:.2f}%</td><td>Live Fed Funds rate from FRED (as of {macro['FEDFUNDS']['date']})</td></tr>
        <tr><td>Equity Risk Premium</td><td style="text-align:right;">{fmt_pct(kpis['avg_ann_return'] - kpis['risk_free_rate'])}</td><td>{"Positive premium for equity risk" if kpis['avg_ann_return'] > kpis['risk_free_rate'] else "Negative premium — bonds may be preferable"}</td></tr>
    </tbody>
</table>

<!-- RISK ASSESSMENT -->
<div class="section-break"></div>
<h1>5. Risk Assessment</h1>
<table>
    <thead>
        <tr><th>Risk Factor</th><th>Level</th><th>Commentary</th></tr>
    </thead>
    <tbody>
        <tr><td>Interest Rate Risk</td><td class="{'risk-high' if macro['FEDFUNDS']['value'] > 5 else 'risk-med' if macro['FEDFUNDS']['value'] > 4 else 'risk-low'}">{"HIGH" if macro['FEDFUNDS']['value'] > 5 else "MEDIUM" if macro['FEDFUNDS']['value'] > 4 else "LOW"}</td><td>Fed Funds at {macro['FEDFUNDS']['value']:.2f}% — {"restrictive territory pressuring valuations" if macro['FEDFUNDS']['value'] > 5 else "elevated but potentially near cycle peak"}</td></tr>
        <tr><td>Volatility Risk</td><td class="{'risk-high' if kpis['avg_volatility'] > 25 else 'risk-med' if kpis['avg_volatility'] > 20 else 'risk-low'}">{"HIGH" if kpis['avg_volatility'] > 25 else "MEDIUM" if kpis['avg_volatility'] > 20 else "LOW"}</td><td>Annualized volatility of {kpis['avg_volatility']:.1f}% is {"above" if kpis['avg_volatility'] > 20 else "within"} historical norms</td></tr>
        <tr><td>Drawdown Risk</td><td class="{'risk-high' if kpis['avg_max_drawdown'] < -15 else 'risk-med' if kpis['avg_max_drawdown'] < -8 else 'risk-low'}">{"HIGH" if kpis['avg_max_drawdown'] < -15 else "MEDIUM" if kpis['avg_max_drawdown'] < -8 else "LOW"}</td><td>Average peak-to-trough of {fmt_pct(kpis['avg_max_drawdown'])} over trailing 3 months</td></tr>
        <tr><td>Concentration Risk</td><td class="risk-low">LOW</td><td>Equal-weight across {kpis['num_holdings']} sectors reduces single-stock impact</td></tr>
        <tr><td>Inflation Risk</td><td class="risk-med">MEDIUM</td><td>CPI at {macro['CPI']['value']:.1f} — monitor for persistence above target</td></tr>
    </tbody>
</table>

<!-- RECOMMENDATIONS -->
<h1>6. Recommendations & Watch Items</h1>
<div class="exec-box">
    <ol>
        <li><strong>Yield curve positioning:</strong> {"The inverted yield curve suggests defensive positioning — consider overweighting dividend payers and reducing duration exposure" if macro['DGS10']['value'] < macro['FEDFUNDS']['value'] else "The steepening yield curve favors cyclical exposure and longer-duration assets"}</li>
        <li><strong>Sector rotation:</strong> With the macro environment {"restrictive" if macro['FEDFUNDS']['value'] > 4.5 else "accommodative"}, maintain diversification across Technology, Financials, Healthcare, and Energy</li>
        <li><strong>Risk management:</strong> Implement stop-loss triggers at -12% per position and -8% at the portfolio level</li>
        <li><strong>Next review:</strong> Rebalance at end of quarter or upon FOMC rate decision materially diverging from expectations</li>
    </ol>
</div>

<!-- METHODOLOGY -->
<h1>7. Methodology & Data Sources</h1>
<table>
    <thead>
        <tr><th>Component</th><th>Detail</th></tr>
    </thead>
    <tbody>
        <tr><td>Equity Data</td><td>Yahoo Finance Chart API (3-month daily OHLCV) — live pull at report generation</td></tr>
        <tr><td>Benchmark</td><td>SPY (SPDR S&P 500 ETF) — real daily returns for beta and R-squared computation</td></tr>
        <tr><td>Macro Data</td><td>Federal Reserve Economic Data (FRED) via CSV download — GDPC1, CPIAUCSL, UNRATE, FEDFUNDS, DGS10</td></tr>
        <tr><td>Portfolio Weighting</td><td>Equal-weight across all holdings</td></tr>
        <tr><td>Risk-Free Rate</td><td>Federal Funds Effective Rate (latest FRED observation: {macro['FEDFUNDS']['date']})</td></tr>
        <tr><td>Beta</td><td>Covariance of stock returns with SPY returns / variance of SPY returns</td></tr>
        <tr><td>R-Squared</td><td>1 - (SS_residual / SS_total) from daily returns regression vs SPY</td></tr>
        <tr><td>Volatility</td><td>Annualized from daily returns (sqrt(252) scaling)</td></tr>
        <tr><td>Sharpe Ratio</td><td>(Annualized Return - Risk-Free Rate) / Annualized Volatility</td></tr>
        <tr><td>Jensen's Alpha</td><td>Portfolio Return - [Rf + Beta * (Market Return - Rf)]</td></tr>
        <tr><td>Report Period</td><td>Q1 2026 (trailing 3-month snapshot as of {today})</td></tr>
    </tbody>
</table>
<p style="font-size:7.5pt;color:#9ca3af;">All data sources are public and independently verifiable. Yahoo Finance: finance.yahoo.com | FRED: fred.stlouisfed.org</p>

<div class="disclaimer">
    <strong>Disclaimer & Disclosure:</strong> This report uses <strong>live market data sourced from Yahoo Finance and the Federal Reserve (FRED)</strong> at the time of generation. "Apex Capital Advisors" is a fictional firm name used for demonstration — all underlying market data is real and independently verifiable. This report does not constitute financial advice, investment recommendation, or solicitation. Past performance does not guarantee future results.
</div>

<div class="footer-attribution">
    Report prepared by Mboya Jeffers | MboyaJeffers9@gmail.com
</div>

</body>
</html>"""
    return html


if __name__ == "__main__":
    print("Fetching FRED macro data (CSV direct download — no API key)...")
    fred_series = {
        "GDP": ("GDPC1", "Real GDP (Billions $)"),
        "CPI": ("CPIAUCSL", "Consumer Price Index"),
        "UNRATE": ("UNRATE", "Unemployment Rate (%)"),
        "FEDFUNDS": ("FEDFUNDS", "Federal Funds Rate (%)"),
        "DGS10": ("DGS10", "10-Year Treasury Yield (%)"),
    }
    macro = {}
    for key, (series_id, label) in fred_series.items():
        print(f"  Pulling {series_id}...")
        result = fetch_fred_csv(series_id)
        macro[key] = {"date": result["date"], "value": result["value"], "label": label, "series": series_id}
        print(f"    {label}: {result['value']} ({result['date']})")

    print("\nFetching Yahoo Finance stock data (real data only)...")
    tickers = ["AAPL", "MSFT", "JPM", "JNJ", "XOM"]
    stocks = []
    for t in tickers:
        print(f"  Pulling {t}...")
        result = fetch_yahoo_chart(t)
        stocks.append(result)
        print(f"    {result['name']}: ${result['price']:,.2f} ({fmt_pct(result['change_3mo'])} 3mo)")

    print("\nFetching SPY benchmark (for real beta/R-squared)...")
    benchmark = fetch_yahoo_chart("SPY")
    print(f"  SPY: ${benchmark['price']:,.2f} ({fmt_pct(benchmark['change_3mo'])} 3mo)")

    # Use real FRED Fed Funds rate as risk-free rate
    print("\nComputing portfolio KPIs (real R-squared and beta vs SPY)...")
    kpis = compute_portfolio_kpis(stocks, benchmark)
    kpis["risk_free_rate"] = macro["FEDFUNDS"]["value"]
    # Recompute Sharpe with real risk-free rate
    kpis["sharpe_ratio"] = (kpis["avg_ann_return"] - kpis["risk_free_rate"]) / kpis["avg_volatility"] if kpis["avg_volatility"] > 0 else 0

    print("Generating HTML...")
    html = generate_html(stocks, macro, kpis, benchmark)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    html_path = os.path.join(output_dir, "Sample_Financial_Analytics_Report.html")
    pdf_path = os.path.join(output_dir, "Sample_Financial_Analytics_Report.pdf")

    with open(html_path, "w") as f:
        f.write(html)
    print(f"HTML saved: {html_path}")

    print("Generating PDF...")
    HTML(string=html).write_pdf(pdf_path)
    print(f"PDF saved: {pdf_path}")
    print("Done — all data is REAL (Yahoo Finance + FRED CSV).")
