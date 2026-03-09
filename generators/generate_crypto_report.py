#!/usr/bin/env python3
"""
Generate Sample Crypto Portfolio Report
Meridian Digital Assets Fund — Q1 2026 Portfolio Analysis
Uses CoinGecko public API — REAL DATA ONLY (no fallback)
"""

import json
import math
import os
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from weasyprint import HTML

# --- Data Pull: CoinGecko (real data, retry on rate limit) ---
def fetch_crypto_data(max_retries=3):
    """Pull top 20 coins from CoinGecko public API. Retries on rate limit."""
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=20&page=1&sparkline=false&price_change_percentage=7d,30d"
    for attempt in range(max_retries):
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode())
                if data and len(data) > 0:
                    return data
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait = (attempt + 1) * 15
                print(f"Rate limited (429). Retrying in {wait}s... (attempt {attempt+1}/{max_retries})")
                time.sleep(wait)
                continue
            raise RuntimeError(f"CoinGecko API failed after {max_retries} attempts: {e}")
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise RuntimeError(f"CoinGecko API failed after {max_retries} attempts: {e}")
    raise RuntimeError("CoinGecko API: no data returned after all retries")

def compute_kpis(coins):
    """Compute portfolio-level KPIs from coin data."""
    total_mcap = sum(c.get("market_cap", 0) or 0 for c in coins)
    total_vol = sum(c.get("total_volume", 0) or 0 for c in coins)

    # Portfolio weights by market cap
    weights = [(c.get("market_cap", 0) or 0) / total_mcap if total_mcap > 0 else 0 for c in coins]

    # Weighted avg 24h return
    returns_24h = [c.get("price_change_percentage_24h", 0) or 0 for c in coins]
    weighted_return = sum(w * r for w, r in zip(weights, returns_24h))

    # Portfolio volatility (using 30d changes as proxy)
    returns_30d = [c.get("price_change_percentage_30d_in_currency", 0) or 0 for c in coins]
    mean_30d = sum(r for r in returns_30d) / len(returns_30d) if returns_30d else 0
    variance = sum((r - mean_30d) ** 2 for r in returns_30d) / len(returns_30d) if returns_30d else 0
    volatility = math.sqrt(variance)

    # Sharpe Ratio (annualized, risk-free = 4.5%)
    annualized_return = weighted_return * 365
    sharpe = (annualized_return - 4.5) / (volatility * math.sqrt(12)) if volatility > 0 else 0

    # Sortino (only downside vol)
    downside_returns = [r for r in returns_30d if r < 0]
    downside_var = sum(r ** 2 for r in downside_returns) / len(downside_returns) if downside_returns else 0
    downside_vol = math.sqrt(downside_var)
    sortino = (annualized_return - 4.5) / (downside_vol * math.sqrt(12)) if downside_vol > 0 else 0

    # VaR (95% parametric)
    var_95 = mean_30d - 1.645 * volatility

    # Max drawdown from ATH
    drawdowns = [c.get("ath_change_percentage", 0) or 0 for c in coins]
    max_drawdown = min(drawdowns) if drawdowns else 0
    avg_drawdown = sum(drawdowns) / len(drawdowns) if drawdowns else 0

    # Stablecoin ratio
    stablecoins = [c for c in coins if c.get("symbol", "").lower() in ("usdt", "usdc", "dai", "busd", "tusd")]
    stable_mcap = sum(c.get("market_cap", 0) or 0 for c in stablecoins)
    stablecoin_ratio = (stable_mcap / total_mcap * 100) if total_mcap > 0 else 0

    # Concentration (HHI)
    hhi = sum(w ** 2 for w in weights) * 10000

    # Top 3 concentration
    sorted_weights = sorted(weights, reverse=True)
    top3_concentration = sum(sorted_weights[:3]) * 100 if len(sorted_weights) >= 3 else 0

    return {
        "total_market_cap": total_mcap,
        "total_24h_volume": total_vol,
        "weighted_24h_return": weighted_return,
        "annualized_return": annualized_return,
        "portfolio_volatility": volatility,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "var_95": var_95,
        "max_drawdown": max_drawdown,
        "avg_drawdown": avg_drawdown,
        "stablecoin_ratio": stablecoin_ratio,
        "hhi": hhi,
        "top3_concentration": top3_concentration,
        "num_assets": len(coins),
        "volume_mcap_ratio": (total_vol / total_mcap * 100) if total_mcap > 0 else 0,
    }

def fmt_usd(val):
    if abs(val) >= 1e12: return f"${val/1e12:.2f}T"
    if abs(val) >= 1e9: return f"${val/1e9:.2f}B"
    if abs(val) >= 1e6: return f"${val/1e6:.2f}M"
    if abs(val) >= 1e3: return f"${val/1e3:.1f}K"
    return f"${val:,.2f}"

def fmt_pct(val):
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.2f}%"

def pct_color(val):
    if val > 0: return "#16a34a"
    if val < 0: return "#dc2626"
    return "#6b7280"

def generate_html(coins, kpis):
    today = datetime.now().strftime("%B %d, %Y")
    q_label = f"Q1 2026"

    # Build holdings table rows
    holdings_rows = ""
    total_mcap = kpis["total_market_cap"]
    for c in coins:
        mcap = c.get("market_cap", 0) or 0
        weight = (mcap / total_mcap * 100) if total_mcap > 0 else 0
        chg24 = c.get("price_change_percentage_24h", 0) or 0
        chg7d = c.get("price_change_percentage_7d_in_currency", 0) or 0
        chg30d = c.get("price_change_percentage_30d_in_currency", 0) or 0
        holdings_rows += f"""
        <tr>
            <td style="font-weight:600;">{c['name']}</td>
            <td>{c['symbol'].upper()}</td>
            <td style="text-align:right;">${c.get('current_price', 0):,.2f}</td>
            <td style="text-align:right;">{fmt_usd(mcap)}</td>
            <td style="text-align:right;">{weight:.1f}%</td>
            <td style="text-align:right;color:{pct_color(chg24)}">{fmt_pct(chg24)}</td>
            <td style="text-align:right;color:{pct_color(chg7d)}">{fmt_pct(chg7d)}</td>
            <td style="text-align:right;color:{pct_color(chg30d)}">{fmt_pct(chg30d)}</td>
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
        content: "Sample Report — Analyst: Mboya Jeffers | Live CoinGecko data";
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
    color: #9333ea;
    margin-bottom: 8px;
}}
.cover-subtitle {{
    font-size: 16pt;
    color: #6b7280;
    margin-bottom: 40px;
}}
.cover-fund {{
    font-size: 13pt;
    color: #4b5563;
    margin-bottom: 6px;
}}
.cover-date {{
    font-size: 11pt;
    color: #9ca3af;
}}
.cover-line {{
    width: 80px;
    height: 3px;
    background: #9333ea;
    margin: 24px auto;
}}
h1 {{
    font-size: 16pt;
    color: #9333ea;
    border-bottom: 2px solid #9333ea;
    padding-bottom: 4px;
    margin-top: 20px;
}}
h2 {{
    font-size: 12pt;
    color: #7c3aed;
    margin-top: 16px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 8.5pt;
}}
th {{
    background: #9333ea;
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
    background: #faf5ff;
}}
.kpi-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    margin: 12px 0;
}}
.kpi-card {{
    background: #faf5ff;
    border: 1px solid #e9d5ff;
    border-radius: 6px;
    padding: 10px 12px;
    text-align: center;
}}
.kpi-value {{
    font-size: 16pt;
    font-weight: 700;
    color: #9333ea;
}}
.kpi-label {{
    font-size: 7.5pt;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.exec-box {{
    background: #faf5ff;
    border-left: 4px solid #9333ea;
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
ul {{ padding-left: 18px; }}
li {{ margin-bottom: 4px; }}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
    <div class="cover-title">Meridian Digital Assets Fund</div>
    <div class="cover-line"></div>
    <div class="cover-subtitle">{q_label} Portfolio Analysis</div>
    <div class="cover-fund">Comprehensive Crypto Portfolio Performance Review</div>
    <div class="cover-fund">{kpis['num_assets']} Assets Tracked | {fmt_usd(kpis['total_market_cap'])} Total Market Cap</div>
    <div class="cover-date">Report Date: {today}</div>
    <div class="cover-date" style="margin-top:30px;font-size:9pt;color:#6b7280;">
        SAMPLE REPORT — Live market data from CoinGecko public API
    </div>
</div>

<!-- EXECUTIVE SUMMARY -->
<h1>1. Executive Summary</h1>
<div class="exec-box">
    <ul>
        <li><strong>Portfolio Size:</strong> {kpis['num_assets']} digital assets with combined market capitalization of {fmt_usd(kpis['total_market_cap'])}</li>
        <li><strong>24h Weighted Return:</strong> <span style="color:{pct_color(kpis['weighted_24h_return'])}">{fmt_pct(kpis['weighted_24h_return'])}</span> — {"positive momentum across major holdings" if kpis['weighted_24h_return'] > 0 else "slight pullback across major holdings"}</li>
        <li><strong>Risk Profile:</strong> Portfolio Sharpe ratio of {kpis['sharpe_ratio']:.2f} with 95% monthly VaR of {fmt_pct(kpis['var_95'])}</li>
        <li><strong>Concentration Risk:</strong> Top 3 assets represent {kpis['top3_concentration']:.1f}% of total portfolio — {"high concentration warrants monitoring" if kpis['top3_concentration'] > 70 else "moderate diversification"}</li>
        <li><strong>Stablecoin Allocation:</strong> {kpis['stablecoin_ratio']:.1f}% in stablecoins — {"adequate liquidity buffer" if kpis['stablecoin_ratio'] > 5 else "consider increasing defensive allocation"}</li>
    </ul>
</div>

<!-- PORTFOLIO OVERVIEW -->
<h1>2. Portfolio Composition</h1>
<table>
    <thead>
        <tr>
            <th>Asset</th>
            <th>Ticker</th>
            <th style="text-align:right;">Price (USD)</th>
            <th style="text-align:right;">Market Cap</th>
            <th style="text-align:right;">Weight</th>
            <th style="text-align:right;">24h</th>
            <th style="text-align:right;">7d</th>
            <th style="text-align:right;">30d</th>
        </tr>
    </thead>
    <tbody>
        {holdings_rows}
    </tbody>
</table>
<p style="font-size:7.5pt;color:#9ca3af;">Data sourced from CoinGecko API. Market cap weighted. Prices as of {today}.</p>

<!-- KPI DASHBOARD -->
<div class="section-break"></div>
<h1>3. KPI Dashboard</h1>

<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-value">{kpis['sharpe_ratio']:.2f}</div>
        <div class="kpi-label">Sharpe Ratio</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['sortino_ratio']:.2f}</div>
        <div class="kpi-label">Sortino Ratio</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{fmt_pct(kpis['var_95'])}</div>
        <div class="kpi-label">VaR (95%, Monthly)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['portfolio_volatility']:.1f}%</div>
        <div class="kpi-label">30d Volatility</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{fmt_pct(kpis['max_drawdown'])}</div>
        <div class="kpi-label">Max Drawdown (from ATH)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['stablecoin_ratio']:.1f}%</div>
        <div class="kpi-label">Stablecoin Ratio</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['hhi']:.0f}</div>
        <div class="kpi-label">HHI (Concentration)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['top3_concentration']:.1f}%</div>
        <div class="kpi-label">Top 3 Concentration</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['volume_mcap_ratio']:.1f}%</div>
        <div class="kpi-label">Volume/MCap Ratio</div>
    </div>
</div>

<h2>Full KPI Table</h2>
<table>
    <thead>
        <tr><th>KPI</th><th style="text-align:right;">Value</th><th>Interpretation</th></tr>
    </thead>
    <tbody>
        <tr><td>Sharpe Ratio (Annualized)</td><td style="text-align:right;">{kpis['sharpe_ratio']:.2f}</td><td>{"Above 1.0 — strong risk-adjusted returns" if kpis['sharpe_ratio'] > 1 else "Positive but below 1.0 — moderate risk-adjusted returns" if kpis['sharpe_ratio'] > 0 else "Negative — returns below risk-free rate on annualized basis"}</td></tr>
        <tr><td>Sortino Ratio</td><td style="text-align:right;">{kpis['sortino_ratio']:.2f}</td><td>{"Above 1.0 — favorable downside risk profile" if kpis['sortino_ratio'] > 1 else "Positive but below 1.0 — moderate downside risk" if kpis['sortino_ratio'] > 0 else "Negative — elevated downside risk relative to risk-free rate"}</td></tr>
        <tr><td>Value at Risk (95%, 30d)</td><td style="text-align:right;">{fmt_pct(kpis['var_95'])}</td><td>Maximum expected monthly loss at 95% confidence</td></tr>
        <tr><td>Portfolio Volatility (30d)</td><td style="text-align:right;">{kpis['portfolio_volatility']:.2f}%</td><td>{"High volatility — typical for crypto" if kpis['portfolio_volatility'] > 10 else "Moderate volatility range"}</td></tr>
        <tr><td>Max Drawdown (from ATH)</td><td style="text-align:right;">{fmt_pct(kpis['max_drawdown'])}</td><td>Worst single-asset drawdown from all-time high</td></tr>
        <tr><td>Avg Drawdown (from ATH)</td><td style="text-align:right;">{fmt_pct(kpis['avg_drawdown'])}</td><td>Average distance from ATH across holdings</td></tr>
        <tr><td>Stablecoin Allocation</td><td style="text-align:right;">{kpis['stablecoin_ratio']:.1f}%</td><td>{"Adequate defensive buffer" if kpis['stablecoin_ratio'] > 5 else "Low liquidity buffer"}</td></tr>
        <tr><td>HHI (Concentration Index)</td><td style="text-align:right;">{kpis['hhi']:.0f}</td><td>{"Concentrated (>2500)" if kpis['hhi'] > 2500 else "Moderately concentrated (1500-2500)" if kpis['hhi'] > 1500 else "Diversified (<1500)"}</td></tr>
        <tr><td>Top 3 Concentration</td><td style="text-align:right;">{kpis['top3_concentration']:.1f}%</td><td>Share of portfolio in top 3 assets</td></tr>
        <tr><td>24h Volume/MCap Ratio</td><td style="text-align:right;">{kpis['volume_mcap_ratio']:.2f}%</td><td>{"Strong liquidity" if kpis['volume_mcap_ratio'] > 5 else "Adequate liquidity"}</td></tr>
        <tr><td>Weighted 24h Return</td><td style="text-align:right;color:{pct_color(kpis['weighted_24h_return'])}">{fmt_pct(kpis['weighted_24h_return'])}</td><td>Market-cap weighted portfolio return</td></tr>
        <tr><td>Number of Assets</td><td style="text-align:right;">{kpis['num_assets']}</td><td>Total tracked positions</td></tr>
    </tbody>
</table>

<!-- ANALYSIS & COMMENTARY -->
<h1>4. Analysis & Commentary</h1>

<h2>Market Context</h2>
<p>The digital asset market continues to evolve as institutional adoption increases alongside regulatory clarity in major jurisdictions. Bitcoin dominance remains elevated at approximately {(coins[0].get('market_cap',0) or 0) / kpis['total_market_cap'] * 100:.1f}% of tracked portfolio market capitalization, reflecting a flight-to-quality bias among institutional allocators.</p>

<h2>Risk Assessment</h2>
<table>
    <thead>
        <tr><th>Risk Factor</th><th>Level</th><th>Commentary</th></tr>
    </thead>
    <tbody>
        <tr><td>Concentration Risk</td><td class="{'risk-high' if kpis['top3_concentration'] > 70 else 'risk-med' if kpis['top3_concentration'] > 50 else 'risk-low'}">{"HIGH" if kpis['top3_concentration'] > 70 else "MEDIUM" if kpis['top3_concentration'] > 50 else "LOW"}</td><td>Top 3 assets represent {kpis['top3_concentration']:.1f}% of portfolio</td></tr>
        <tr><td>Drawdown Risk</td><td class="risk-high">HIGH</td><td>Avg distance from ATH is {fmt_pct(kpis['avg_drawdown'])} — recovery potential but significant downside exposure</td></tr>
        <tr><td>Liquidity Risk</td><td class="risk-low">LOW</td><td>24h volume-to-MCap ratio of {kpis['volume_mcap_ratio']:.1f}% indicates healthy market depth</td></tr>
        <tr><td>Stablecoin Buffer</td><td class="{'risk-low' if kpis['stablecoin_ratio'] > 10 else 'risk-med' if kpis['stablecoin_ratio'] > 5 else 'risk-high'}">{"ADEQUATE" if kpis['stablecoin_ratio'] > 5 else "LOW"}</td><td>{kpis['stablecoin_ratio']:.1f}% in stablecoins provides {"sufficient" if kpis['stablecoin_ratio'] > 5 else "limited"} downside protection</td></tr>
    </tbody>
</table>

<!-- RECOMMENDATIONS -->
<h1>5. Recommendations & Watch Items</h1>
<div class="exec-box">
    <ol>
        <li><strong>{"Reduce concentration:" if kpis['top3_concentration'] > 70 else "Monitor concentration:"}</strong> Top 3 holdings at {kpis['top3_concentration']:.1f}% — consider {"rebalancing into mid-cap L1s and DeFi protocols" if kpis['top3_concentration'] > 70 else "maintaining current allocation with quarterly review"}</li>
        <li><strong>Volatility management:</strong> With 30d volatility at {kpis['portfolio_volatility']:.1f}%, consider implementing systematic rebalancing triggers at +/- 15% deviation from target weights</li>
        <li><strong>Stablecoin strategy:</strong> {"Current allocation is sufficient for near-term liquidity needs" if kpis['stablecoin_ratio'] > 10 else "Consider increasing stablecoin allocation to 10-15% for risk management"}</li>
        <li><strong>Next review:</strong> Schedule portfolio rebalance for end of Q1 2026 or upon any single holding exceeding 50% portfolio weight</li>
    </ol>
</div>

<!-- METHODOLOGY -->
<h1>6. Methodology & Data Sources</h1>
<table>
    <thead>
        <tr><th>Component</th><th>Detail</th></tr>
    </thead>
    <tbody>
        <tr><td>Data Source</td><td>CoinGecko Markets API (public, no API key)</td></tr>
        <tr><td>Pricing</td><td>USD spot prices, real-time at time of pull</td></tr>
        <tr><td>Weighting</td><td>Market capitalization weighted</td></tr>
        <tr><td>Risk-Free Rate</td><td>4.5% annualized (US 3-month T-bill proxy)</td></tr>
        <tr><td>VaR Method</td><td>Parametric (variance-covariance), 95% confidence</td></tr>
        <tr><td>Sharpe/Sortino</td><td>Annualized from 30-day rolling returns</td></tr>
        <tr><td>HHI</td><td>Herfindahl-Hirschman Index on portfolio weights</td></tr>
        <tr><td>Report Period</td><td>{q_label} (snapshot as of {today})</td></tr>
    </tbody>
</table>

<!-- DISCLAIMER -->
<div class="disclaimer">
    <strong>Disclaimer & Disclosure:</strong> This report uses <strong>live market data sourced from the CoinGecko public API</strong> at the time of generation. "Meridian Digital Assets Fund" is a fictional fund name used for demonstration — all underlying market data is real and independently verifiable at coingecko.com. This report does not constitute financial advice, investment recommendation, or solicitation. Past performance does not guarantee future results. Cryptocurrency investments carry significant risk including potential total loss of principal.
</div>

<div class="footer-attribution">
    Report prepared by Mboya Jeffers | MboyaJeffers9@gmail.com
</div>

</body>
</html>"""
    return html


if __name__ == "__main__":
    print("Fetching crypto market data from CoinGecko (real data only)...")
    coins = fetch_crypto_data()
    print(f"Got {len(coins)} coins from CoinGecko (live data).")

    print("Computing KPIs...")
    kpis = compute_kpis(coins)

    print("Generating HTML...")
    html = generate_html(coins, kpis)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    html_path = os.path.join(output_dir, "Sample_Crypto_Portfolio_Report.html")
    pdf_path = os.path.join(output_dir, "Sample_Crypto_Portfolio_Report.pdf")

    with open(html_path, "w") as f:
        f.write(html)
    print(f"HTML saved: {html_path}")

    print("Generating PDF...")
    HTML(string=html).write_pdf(pdf_path)
    print(f"PDF saved: {pdf_path}")
    print("Done!")
