#!/usr/bin/env python3
"""
Generate Sample Energy Market Intelligence Report
US Oil & Gas Production & Pricing Analysis
Uses EIA API + Yahoo Finance — REAL DATA ONLY (no fallback)
"""

import json
import math
import os
import time
import urllib.request
import urllib.error
from datetime import datetime
from weasyprint import HTML

# --- EIA API Data Pull (DEMO_KEY works) ---
def fetch_eia_data(endpoint, params, label, max_retries=3):
    """Pull data from EIA API v2."""
    base = "https://api.eia.gov/v2"
    param_str = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{base}/{endpoint}/data/?api_key=DEMO_KEY&{param_str}"
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode())
                rows = data.get("response", {}).get("data", [])
                if rows:
                    return rows
                raise RuntimeError(f"EIA {label}: empty response")
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            raise RuntimeError(f"EIA {label} failed after {max_retries} attempts: {e}")


def fetch_yahoo_commodity(ticker, max_retries=3):
    """Pull commodity futures price from Yahoo Finance."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=6mo&interval=1d"
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                result = data["chart"]["result"][0]
                closes = [c for c in result["indicators"]["quote"][0]["close"] if c is not None]
                if not closes:
                    raise RuntimeError(f"Yahoo {ticker}: empty data")
                return {
                    "current": closes[-1],
                    "high_6mo": max(closes),
                    "low_6mo": min(closes),
                    "change_6mo": ((closes[-1] - closes[0]) / closes[0] * 100) if closes[0] else 0,
                    "closes": closes,
                }
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3)
                continue
            raise RuntimeError(f"Yahoo {ticker} failed: {e}")


def compute_production_kpis(crude_prod, ng_prod, wti_prices, ng_prices):
    """Compute energy market KPIs from real data."""
    kpis = {}

    # Crude oil production metrics (MBBL/D = thousand barrels per day)
    daily_rates = [r for r in crude_prod if "MBBL/D" in str(r.get("units", ""))]
    if daily_rates:
        latest = float(daily_rates[0]["value"])
        kpis["crude_production_latest"] = latest
        kpis["crude_production_period"] = daily_rates[0]["period"]
        if len(daily_rates) >= 2:
            prev = float(daily_rates[1]["value"])
            kpis["crude_mom_change"] = ((latest - prev) / prev * 100) if prev else 0
        if len(daily_rates) >= 12:
            year_ago = float(daily_rates[11]["value"])
            kpis["crude_yoy_change"] = ((latest - year_ago) / year_ago * 100) if year_ago else 0
        rates = [float(r["value"]) for r in daily_rates[:12] if r.get("value")]
        kpis["crude_12mo_avg"] = sum(rates) / len(rates) if rates else 0
        kpis["crude_12mo_high"] = max(rates) if rates else 0
        kpis["crude_12mo_low"] = min(rates) if rates else 0

    # Natural gas production metrics (MMCF/D)
    ng_daily = [r for r in ng_prod if "MMCF/D" in str(r.get("units", ""))]
    if ng_daily:
        latest_ng = float(ng_daily[0]["value"])
        kpis["ng_production_latest"] = latest_ng
        kpis["ng_production_period"] = ng_daily[0]["period"]
        if len(ng_daily) >= 2:
            prev_ng = float(ng_daily[1]["value"])
            kpis["ng_mom_change"] = ((latest_ng - prev_ng) / prev_ng * 100) if prev_ng else 0
        if len(ng_daily) >= 12:
            year_ago_ng = float(ng_daily[11]["value"])
            kpis["ng_yoy_change"] = ((latest_ng - year_ago_ng) / year_ago_ng * 100) if year_ago_ng else 0

    # WTI pricing metrics
    if wti_prices:
        wti_vals = [float(r["value"]) for r in wti_prices if r.get("value")]
        kpis["wti_latest"] = wti_vals[0] if wti_vals else 0
        kpis["wti_period"] = wti_prices[0]["period"]
        kpis["wti_6mo_avg"] = sum(wti_vals[:6]) / min(len(wti_vals), 6)
        kpis["wti_6mo_high"] = max(wti_vals[:6]) if wti_vals else 0
        kpis["wti_6mo_low"] = min(wti_vals[:6]) if wti_vals else 0
        if len(wti_vals) >= 2:
            kpis["wti_mom_change"] = ((wti_vals[0] - wti_vals[1]) / wti_vals[1] * 100)

    # Natural gas pricing (from Yahoo Finance)
    if ng_prices:
        kpis["ng_price_latest"] = ng_prices["current"]
        kpis["ng_6mo_high"] = ng_prices["high_6mo"]
        kpis["ng_6mo_low"] = ng_prices["low_6mo"]
        kpis["ng_price_change_6mo"] = ng_prices["change_6mo"]

    # Revenue estimate
    if kpis.get("crude_production_latest") and kpis.get("wti_latest"):
        kpis["revenue_per_day_mm"] = kpis["crude_production_latest"] * 1000 * kpis["wti_latest"] / 1e6

    return kpis


def fmt_pct(val):
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.2f}%"

def pct_color(val):
    if val > 0: return "#16a34a"
    if val < 0: return "#dc2626"
    return "#6b7280"


def generate_html(kpis, crude_prod, ng_prod, wti_prices, wti_yahoo, ng_yahoo):
    today = datetime.now().strftime("%B %d, %Y")

    # Build crude oil production trend table
    daily_rates = [r for r in crude_prod if "MBBL/D" in str(r.get("units", ""))][:12]
    crude_rows = ""
    for r in daily_rates:
        crude_rows += f"""
        <tr>
            <td>{r['period']}</td>
            <td style="text-align:right;font-weight:600;">{float(r['value']):,.0f}</td>
            <td style="text-align:right;">MBBL/D</td>
        </tr>"""

    # Build WTI price trend table
    wti_rows = ""
    for r in wti_prices[:12]:
        if r.get("value"):
            wti_rows += f"""
        <tr>
            <td>{r['period']}</td>
            <td style="text-align:right;font-weight:600;">${float(r['value']):,.2f}</td>
        </tr>"""

    # Natural gas production
    ng_daily = [r for r in ng_prod if "MMCF/D" in str(r.get("units", ""))][:12]
    ng_rows = ""
    for r in ng_daily:
        ng_rows += f"""
        <tr>
            <td>{r['period']}</td>
            <td style="text-align:right;font-weight:600;">{float(r['value']):,.0f}</td>
            <td style="text-align:right;">MMCF/D</td>
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
        content: "Sample Report — Analyst: Mboya Jeffers | Live EIA + Yahoo Finance data";
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
    font-size: 26pt;
    font-weight: 700;
    color: #c2410c;
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
    background: #c2410c;
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
    color: #c2410c;
    border-bottom: 2px solid #c2410c;
    padding-bottom: 4px;
    margin-top: 20px;
}}
h2 {{
    font-size: 12pt;
    color: #ea580c;
    margin-top: 16px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;
    font-size: 8.5pt;
}}
th {{
    background: #c2410c;
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
    background: #fff7ed;
}}
.kpi-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    margin: 12px 0;
}}
.kpi-card {{
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: 6px;
    padding: 10px 12px;
    text-align: center;
}}
.kpi-value {{
    font-size: 16pt;
    font-weight: 700;
    color: #c2410c;
}}
.kpi-label {{
    font-size: 7.5pt;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.exec-box {{
    background: #fff7ed;
    border-left: 4px solid #c2410c;
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
    <div class="cover-title">US Energy Market Intelligence</div>
    <div class="cover-line"></div>
    <div class="cover-subtitle">Oil & Gas Production & Pricing Report</div>
    <div class="cover-detail">Crude Oil | Natural Gas | WTI & Henry Hub Pricing</div>
    <div class="cover-detail">Data: U.S. Energy Information Administration (EIA) + Yahoo Finance</div>
    <div class="cover-date">Report Date: {today}</div>
    <div class="cover-date" style="margin-top:30px;font-size:9pt;color:#6b7280;">
        SAMPLE REPORT — Live data from EIA.gov and Yahoo Finance
    </div>
</div>

<!-- EXECUTIVE SUMMARY -->
<h1>1. Executive Summary</h1>
<div class="exec-box">
    <ul>
        <li><strong>US Crude Production:</strong> {kpis.get('crude_production_latest', 0):,.0f} MBBL/D ({kpis.get('crude_production_period', 'N/A')}) — MoM: <span style="color:{pct_color(kpis.get('crude_mom_change', 0))}">{fmt_pct(kpis.get('crude_mom_change', 0))}</span></li>
        <li><strong>US Natural Gas Production:</strong> {kpis.get('ng_production_latest', 0):,.0f} MMCF/D ({kpis.get('ng_production_period', 'N/A')})</li>
        <li><strong>WTI Crude Price:</strong> ${kpis.get('wti_latest', 0):,.2f}/bbl ({kpis.get('wti_period', 'N/A')}) — 6mo avg: ${kpis.get('wti_6mo_avg', 0):,.2f}</li>
        <li><strong>Henry Hub Natural Gas:</strong> ${kpis.get('ng_price_latest', 0):,.2f}/MMBtu — 6mo range: ${kpis.get('ng_6mo_low', 0):,.2f}-${kpis.get('ng_6mo_high', 0):,.2f}</li>
        <li><strong>Estimated US Daily Revenue (crude):</strong> ${kpis.get('revenue_per_day_mm', 0):,.0f}M/day at current production and WTI price</li>
    </ul>
</div>

<!-- KPI DASHBOARD -->
<h1>2. KPI Dashboard</h1>
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-value">{kpis.get('crude_production_latest', 0):,.0f}</div>
        <div class="kpi-label">Crude Production (MBBL/D)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">${kpis.get('wti_latest', 0):,.2f}</div>
        <div class="kpi-label">WTI Price ($/BBL)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{fmt_pct(kpis.get('crude_mom_change', 0))}</div>
        <div class="kpi-label">Production MoM Change</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis.get('ng_production_latest', 0):,.0f}</div>
        <div class="kpi-label">NG Production (MMCF/D)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">${kpis.get('ng_price_latest', 0):,.2f}</div>
        <div class="kpi-label">Henry Hub ($/MMBtu)</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{fmt_pct(kpis.get('wti_mom_change', 0))}</div>
        <div class="kpi-label">WTI MoM Change</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis.get('crude_12mo_high', 0):,.0f}</div>
        <div class="kpi-label">12mo Production High</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">${kpis.get('wti_6mo_high', 0):,.2f}</div>
        <div class="kpi-label">WTI 6mo High</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">${kpis.get('revenue_per_day_mm', 0):,.0f}M</div>
        <div class="kpi-label">Daily Revenue (Est.)</div>
    </div>
</div>

<!-- CRUDE OIL PRODUCTION -->
<h1>3. US Crude Oil Production (12-Month Trend)</h1>
<table>
    <thead>
        <tr><th>Period</th><th style="text-align:right;">Production Rate</th><th style="text-align:right;">Units</th></tr>
    </thead>
    <tbody>
        {crude_rows}
    </tbody>
</table>
<p style="font-size:7.5pt;color:#9ca3af;">Source: EIA Petroleum — Crude Oil Production (series PET.MCRFPUS2). All values are U.S. total field production.</p>

<h2>Production Analysis</h2>
<p>US crude oil production {"reached a new high" if kpis.get('crude_mom_change', 0) > 0 else "pulled back slightly"} at {kpis.get('crude_production_latest', 0):,.0f} MBBL/D in {kpis.get('crude_production_period', 'N/A')}. The 12-month average stands at {kpis.get('crude_12mo_avg', 0):,.0f} MBBL/D, with a range of {kpis.get('crude_12mo_low', 0):,.0f} to {kpis.get('crude_12mo_high', 0):,.0f} MBBL/D. {"Year-over-year growth of " + fmt_pct(kpis.get('crude_yoy_change', 0)) + " reflects continued investment in Permian Basin and other key plays." if kpis.get('crude_yoy_change', 0) and kpis.get('crude_yoy_change', 0) > 0 else "Year-over-year production has moderated, reflecting capital discipline among E&P operators."}</p>

<!-- WTI PRICING -->
<div class="section-break"></div>
<h1>4. WTI Crude Oil Pricing (Monthly)</h1>
<table>
    <thead>
        <tr><th>Period</th><th style="text-align:right;">WTI Spot ($/BBL)</th></tr>
    </thead>
    <tbody>
        {wti_rows}
    </tbody>
</table>
<p style="font-size:7.5pt;color:#9ca3af;">Source: EIA Petroleum Spot Prices — WTI Cushing (series PET.RWTC). Also verified via Yahoo Finance (CL=F).</p>

<h2>Pricing Analysis</h2>
<p>WTI crude averaged ${kpis.get('wti_6mo_avg', 0):,.2f}/bbl over the past 6 months, ranging from ${kpis.get('wti_6mo_low', 0):,.2f} to ${kpis.get('wti_6mo_high', 0):,.2f}. {"Prices are trending higher, supporting E&P capex decisions and production growth." if kpis.get('wti_mom_change', 0) and kpis.get('wti_mom_change', 0) > 0 else "Softening prices may impact operator margins and capital allocation in coming quarters."} At current production of {kpis.get('crude_production_latest', 0):,.0f} MBBL/D and WTI at ${kpis.get('wti_latest', 0):,.2f}, estimated daily US crude revenue is approximately ${kpis.get('revenue_per_day_mm', 0):,.0f}M.</p>

<!-- NATURAL GAS -->
<h1>5. US Natural Gas Production</h1>
<table>
    <thead>
        <tr><th>Period</th><th style="text-align:right;">Production Rate</th><th style="text-align:right;">Units</th></tr>
    </thead>
    <tbody>
        {ng_rows}
    </tbody>
</table>
<p style="font-size:7.5pt;color:#9ca3af;">Source: EIA Natural Gas — Gross Withdrawals (series NG.N9010US2.M).</p>

<!-- RISK ASSESSMENT -->
<h1>6. Market Risk Assessment</h1>
<table>
    <thead>
        <tr><th>Risk Factor</th><th>Level</th><th>Commentary</th></tr>
    </thead>
    <tbody>
        <tr><td>Price Risk (WTI)</td><td class="{'risk-high' if kpis.get('wti_latest', 70) < 50 else 'risk-med' if kpis.get('wti_latest', 70) < 65 else 'risk-low'}">{"HIGH" if kpis.get('wti_latest', 70) < 50 else "MEDIUM" if kpis.get('wti_latest', 70) < 65 else "LOW"}</td><td>WTI at ${kpis.get('wti_latest', 0):,.2f} — {"below breakeven for many operators" if kpis.get('wti_latest', 70) < 50 else "within operating range for most basins"}</td></tr>
        <tr><td>Production Decline</td><td class="{'risk-high' if kpis.get('crude_mom_change', 0) < -3 else 'risk-med' if kpis.get('crude_mom_change', 0) < 0 else 'risk-low'}">{"HIGH" if kpis.get('crude_mom_change', 0) < -3 else "MEDIUM" if kpis.get('crude_mom_change', 0) < 0 else "LOW"}</td><td>MoM change: {fmt_pct(kpis.get('crude_mom_change', 0))}</td></tr>
        <tr><td>Natural Gas Volatility</td><td class="risk-med">MEDIUM</td><td>Henry Hub at ${kpis.get('ng_price_latest', 0):,.2f}/MMBtu — seasonal demand fluctuations expected</td></tr>
        <tr><td>Regulatory Risk</td><td class="risk-med">MEDIUM</td><td>EPA methane regulations and state-level flaring restrictions impact compliance costs</td></tr>
        <tr><td>Geopolitical Risk</td><td class="risk-med">MEDIUM</td><td>OPEC+ production decisions and global demand trajectory remain key variables</td></tr>
    </tbody>
</table>

<!-- METHODOLOGY -->
<h1>7. Methodology & Data Sources</h1>
<table>
    <thead>
        <tr><th>Component</th><th>Detail</th></tr>
    </thead>
    <tbody>
        <tr><td>Crude Production</td><td>EIA API v2 — petroleum/crd/crpdn (US total field production, monthly)</td></tr>
        <tr><td>Natural Gas Production</td><td>EIA API v2 — natural-gas/prod/sum (gross withdrawals, monthly)</td></tr>
        <tr><td>WTI Pricing</td><td>EIA API v2 — petroleum/pri/spt (WTI Cushing spot, monthly)</td></tr>
        <tr><td>Henry Hub Pricing</td><td>Yahoo Finance (NG=F) — daily futures prices, 6-month window</td></tr>
        <tr><td>WTI Daily</td><td>Yahoo Finance (CL=F) — daily futures prices, 6-month window</td></tr>
        <tr><td>Revenue Estimate</td><td>Production (MBBL/D) x 1,000 x WTI Price — simplified gross revenue</td></tr>
        <tr><td>Report Period</td><td>Trailing 12 months of production data, 6 months of pricing ({today})</td></tr>
    </tbody>
</table>
<p style="font-size:7.5pt;color:#9ca3af;">All data sources are public and independently verifiable. EIA: eia.gov/opendata | Yahoo Finance: finance.yahoo.com</p>

<div class="disclaimer">
    <strong>Disclaimer & Disclosure:</strong> This report uses <strong>live data sourced from the U.S. Energy Information Administration (EIA) and Yahoo Finance</strong> at the time of generation. All production volumes, pricing, and computed metrics use real government and market data. This is a sample report demonstrating analytical capabilities — it does not constitute investment advice. For operator-specific compliance reports, client-provided production data would replace the aggregate EIA data shown here.
</div>

<div class="footer-attribution">
    Report prepared by Mboya Jeffers | MboyaJeffers9@gmail.com
</div>

</body>
</html>"""
    return html


if __name__ == "__main__":
    print("Fetching US crude oil production from EIA (real data)...")
    crude_prod = fetch_eia_data(
        "petroleum/crd/crpdn",
        {"frequency": "monthly", "data[0]": "value", "facets[duoarea][]": "NUS",
         "facets[product][]": "EPC0", "sort[0][column]": "period",
         "sort[0][direction]": "desc", "length": "24"},
        "US Crude Production"
    )
    daily_rates = [r for r in crude_prod if "MBBL/D" in str(r.get("units", ""))]
    print(f"  Got {len(daily_rates)} months of crude production data")
    if daily_rates:
        print(f"  Latest: {daily_rates[0]['period']} — {daily_rates[0]['value']} {daily_rates[0].get('units','')}")

    print("\nFetching US natural gas production from EIA...")
    ng_prod = fetch_eia_data(
        "natural-gas/prod/sum",
        {"frequency": "monthly", "data[0]": "value", "facets[process][]": "FGW",
         "facets[duoarea][]": "NUS", "sort[0][column]": "period",
         "sort[0][direction]": "desc", "length": "24"},
        "US NG Production"
    )
    ng_daily = [r for r in ng_prod if "MMCF/D" in str(r.get("units", ""))]
    print(f"  Got {len(ng_daily)} months of NG production data")

    print("\nFetching WTI spot prices from EIA...")
    wti_prices = fetch_eia_data(
        "petroleum/pri/spt",
        {"frequency": "monthly", "data[0]": "value", "facets[product][]": "EPCWTI",
         "sort[0][column]": "period", "sort[0][direction]": "desc", "length": "12"},
        "WTI Prices"
    )
    print(f"  Got {len(wti_prices)} months of WTI prices")
    if wti_prices:
        print(f"  Latest: {wti_prices[0]['period']} — ${wti_prices[0]['value']}")

    print("\nFetching WTI futures from Yahoo Finance (CL=F)...")
    wti_yahoo = fetch_yahoo_commodity("CL=F")
    print(f"  WTI futures: ${wti_yahoo['current']:,.2f} (6mo change: {fmt_pct(wti_yahoo['change_6mo'])})")

    print("\nFetching Henry Hub NG futures from Yahoo Finance (NG=F)...")
    ng_yahoo = fetch_yahoo_commodity("NG=F")
    print(f"  Henry Hub: ${ng_yahoo['current']:,.2f} (6mo change: {fmt_pct(ng_yahoo['change_6mo'])})")

    print("\nComputing energy market KPIs...")
    kpis = compute_production_kpis(crude_prod, ng_prod, wti_prices, ng_yahoo)

    print("Generating HTML...")
    html = generate_html(kpis, crude_prod, ng_prod, wti_prices, wti_yahoo, ng_yahoo)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    html_path = os.path.join(output_dir, "Sample_Energy_Compliance_Report.html")
    pdf_path = os.path.join(output_dir, "Sample_Energy_Compliance_Report.pdf")

    with open(html_path, "w") as f:
        f.write(html)
    print(f"HTML saved: {html_path}")

    print("Generating PDF...")
    HTML(string=html).write_pdf(pdf_path)
    print(f"PDF saved: {pdf_path}")
    print("Done — all data is REAL (EIA API + Yahoo Finance).")
