#!/usr/bin/env python3
"""
Generate Sample Sports/Betting Analytics Report
Baseline Sports Analytics — NFL Season Performance Report
Uses ESPN public API — REAL DATA ONLY (no fallback)
"""

import json
import math
import os
import time
import urllib.request
from datetime import datetime
from weasyprint import HTML

# --- ESPN Data Pull (no key needed) ---
def fetch_nfl_standings(max_retries=3):
    """Pull NFL standings from ESPN public API. All 32 teams."""
    url = "https://site.api.espn.com/apis/v2/sports/football/nfl/standings"
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                teams = []
                for child in data.get("children", []):
                    conf_name = child.get("name", "")
                    # ESPN structure: conferences may have divisions under 'children'
                    # or standings directly under 'standings'
                    standings_sources = []
                    if "children" in child:
                        for div in child["children"]:
                            div_name = div.get("name", "")
                            entries = div.get("standings", {}).get("entries", [])
                            standings_sources.append((div_name, entries))
                    if "standings" in child:
                        entries = child.get("standings", {}).get("entries", [])
                        standings_sources.append((conf_name, entries))
                    for source_name, entries in standings_sources:
                        for entry in entries:
                            team_info = entry.get("team", {})
                            stats = {s["name"]: s.get("value", s.get("displayValue", "")) for s in entry.get("stats", [])}
                            teams.append({
                                "name": team_info.get("displayName", ""),
                                "abbr": team_info.get("abbreviation", ""),
                                "conference": conf_name,
                                "division": source_name,
                                "wins": int(float(stats.get("wins", 0))),
                                "losses": int(float(stats.get("losses", 0))),
                                "ties": int(float(stats.get("ties", 0))),
                                "win_pct": float(stats.get("winPercent", 0)),
                                "points_for": float(stats.get("pointsFor", 0)),
                                "points_against": float(stats.get("pointsAgainst", 0)),
                                "point_diff": float(stats.get("pointDifferential", 0)),
                                "streak": stats.get("streak", ""),
                            })
                if teams:
                    return teams
                raise RuntimeError("ESPN API returned no teams")
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise RuntimeError(f"ESPN API failed after {max_retries} attempts: {e}")


def compute_kpis(teams):
    """Compute league-wide and team-level analytics."""
    kpis = {}
    n = len(teams)
    kpis["total_teams"] = n

    # League averages
    total_pf = sum(t["points_for"] for t in teams)
    total_pa = sum(t["points_against"] for t in teams)
    total_games = sum(t["wins"] + t["losses"] + t["ties"] for t in teams) / 2
    kpis["avg_points_per_game"] = total_pf / total_games if total_games else 0
    kpis["total_games_played"] = int(total_games)

    # Pythagorean wins (NFL exponent = 2.37)
    exp = 2.37
    for t in teams:
        pf = t["points_for"]
        pa = t["points_against"]
        games = t["wins"] + t["losses"] + t["ties"]
        if pf + pa > 0 and games > 0:
            pyth = pf**exp / (pf**exp + pa**exp)
            t["pyth_wins"] = pyth * games
            t["pyth_diff"] = t["wins"] - t["pyth_wins"]  # positive = overperforming
        else:
            t["pyth_wins"] = 0
            t["pyth_diff"] = 0

    # Conference analysis
    afc = [t for t in teams if "American" in t.get("conference", "")]
    nfc = [t for t in teams if "National" in t.get("conference", "")]
    kpis["afc_avg_wins"] = sum(t["wins"] for t in afc) / len(afc) if afc else 0
    kpis["nfc_avg_wins"] = sum(t["wins"] for t in nfc) / len(nfc) if nfc else 0
    kpis["afc_avg_pf"] = sum(t["points_for"] for t in afc) / len(afc) if afc else 0
    kpis["nfc_avg_pf"] = sum(t["points_for"] for t in nfc) / len(nfc) if nfc else 0

    # Win percentage distribution
    win_pcts = [t["win_pct"] for t in teams]
    kpis["league_parity"] = 1 - (max(win_pcts) - min(win_pcts)) if win_pcts else 0
    kpis["win_pct_stdev"] = math.sqrt(sum((w - 0.5)**2 for w in win_pcts) / len(win_pcts)) if win_pcts else 0

    # Top/bottom performers (sort by wins then point diff — matches standings table)
    sorted_teams = sorted(teams, key=lambda t: (-t["wins"], -t["point_diff"]))
    best = sorted_teams[0]
    worst = sorted_teams[-1]
    # Count teams sharing best/worst record
    best_count = sum(1 for t in teams if t["wins"] == best["wins"] and t["losses"] == best["losses"])
    worst_count = sum(1 for t in teams if t["wins"] == worst["wins"] and t["losses"] == worst["losses"])
    kpis["best_record"] = f"{best['name']} ({best['wins']}-{best['losses']})" + (f" and {best_count - 1} other{'s' if best_count > 2 else ''}" if best_count > 1 else "")
    kpis["worst_record"] = f"{worst['name']} ({worst['wins']}-{worst['losses']})" + (f" and {worst_count - 1} other{'s' if worst_count > 2 else ''}" if worst_count > 1 else "")

    # Biggest overperformer/underperformer (Pythagorean)
    by_pyth = sorted(teams, key=lambda t: t.get("pyth_diff", 0), reverse=True)
    kpis["biggest_overperformer"] = f"{by_pyth[0]['name']} (+{by_pyth[0]['pyth_diff']:.1f} wins vs expected)"
    kpis["biggest_underperformer"] = f"{by_pyth[-1]['name']} ({by_pyth[-1]['pyth_diff']:.1f} wins vs expected)"

    # Scoring trends
    kpis["highest_scoring"] = max(teams, key=lambda t: t["points_for"])["name"]
    kpis["best_defense"] = min(teams, key=lambda t: t["points_against"])["name"]
    kpis["highest_pf"] = max(t["points_for"] for t in teams)
    kpis["lowest_pa"] = min(t["points_against"] for t in teams)

    return kpis


def fmt_pct(val):
    sign = "+" if val > 0 else ""
    return f"{sign}{val:.2f}%"

def pct_color(val):
    if val > 0: return "#16a34a"
    if val < 0: return "#dc2626"
    return "#6b7280"


def generate_html(teams, kpis):
    today = datetime.now().strftime("%B %d, %Y")

    # Sort teams by wins for standings table
    sorted_teams = sorted(teams, key=lambda t: (-t["wins"], -t["point_diff"]))

    standings_rows = ""
    for i, t in enumerate(sorted_teams, 1):
        pyth_color = pct_color(t.get("pyth_diff", 0))
        standings_rows += f"""
        <tr>
            <td style="text-align:center;">{i}</td>
            <td style="font-weight:600;">{t['name']}</td>
            <td>{t['conference']}</td>
            <td style="text-align:center;">{t['wins']}-{t['losses']}{'-' + str(t['ties']) if t['ties'] else ''}</td>
            <td style="text-align:center;">{t['win_pct']:.3f}</td>
            <td style="text-align:right;">{t['points_for']:.0f}</td>
            <td style="text-align:right;">{t['points_against']:.0f}</td>
            <td style="text-align:right;color:{pct_color(t['point_diff'])}">{'+' if t['point_diff'] > 0 else ''}{t['point_diff']:.0f}</td>
            <td style="text-align:center;">{t.get('pyth_wins', 0):.1f}</td>
            <td style="text-align:center;color:{pyth_color}">{'+' if t.get('pyth_diff', 0) > 0 else ''}{t.get('pyth_diff', 0):.1f}</td>
        </tr>"""

    # Top 5 overperformers and underperformers
    by_pyth = sorted(teams, key=lambda t: t.get("pyth_diff", 0), reverse=True)
    over_rows = ""
    for t in by_pyth[:5]:
        over_rows += f"<tr><td>{t['name']}</td><td style='text-align:center;'>{t['wins']}-{t['losses']}</td><td style='text-align:center;'>{t['pyth_wins']:.1f}</td><td style='text-align:center;color:#16a34a;font-weight:600;'>+{t['pyth_diff']:.1f}</td></tr>"
    under_rows = ""
    for t in by_pyth[-5:]:
        under_rows += f"<tr><td>{t['name']}</td><td style='text-align:center;'>{t['wins']}-{t['losses']}</td><td style='text-align:center;'>{t['pyth_wins']:.1f}</td><td style='text-align:center;color:#dc2626;font-weight:600;'>{t['pyth_diff']:.1f}</td></tr>"

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
@page {{
    size: letter landscape;
    margin: 0.5in 0.6in;
    @bottom-center {{
        content: "Sample Report — Analyst: Mboya Jeffers | Live ESPN data";
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
    font-size: 9pt;
    line-height: 1.4;
    color: #1f2937;
}}
.cover {{
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 6in;
    text-align: center;
}}
.cover-title {{
    font-size: 28pt;
    font-weight: 700;
    color: #16a34a;
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
    background: #16a34a;
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
    font-size: 15pt;
    color: #16a34a;
    border-bottom: 2px solid #16a34a;
    padding-bottom: 4px;
    margin-top: 18px;
}}
h2 {{
    font-size: 11pt;
    color: #15803d;
    margin-top: 14px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
    font-size: 7.5pt;
}}
th {{
    background: #16a34a;
    color: white;
    padding: 5px 6px;
    text-align: left;
    font-weight: 600;
    font-size: 7pt;
}}
td {{
    padding: 4px 6px;
    border-bottom: 1px solid #e5e7eb;
}}
tr:nth-child(even) {{
    background: #f0fdf4;
}}
.kpi-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 8px;
    margin: 10px 0;
}}
.kpi-card {{
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 6px;
    padding: 8px 10px;
    text-align: center;
}}
.kpi-value {{
    font-size: 14pt;
    font-weight: 700;
    color: #16a34a;
}}
.kpi-label {{
    font-size: 6.5pt;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.exec-box {{
    background: #f0fdf4;
    border-left: 4px solid #16a34a;
    padding: 10px 14px;
    margin: 10px 0;
    border-radius: 0 6px 6px 0;
}}
.disclaimer {{
    margin-top: 20px;
    padding: 10px;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 4px;
    font-size: 7pt;
    color: #6b7280;
}}
.section-break {{
    page-break-before: always;
}}
.footer-attribution {{
    text-align: center;
    font-size: 7.5pt;
    color: #9ca3af;
    margin-top: 20px;
    border-top: 1px solid #e5e7eb;
    padding-top: 6px;
}}
ul, ol {{ padding-left: 16px; }}
li {{ margin-bottom: 3px; }}
.two-col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}}
</style>
</head>
<body>

<!-- COVER PAGE -->
<div class="cover">
    <div class="cover-title">Baseline Sports Analytics</div>
    <div class="cover-line"></div>
    <div class="cover-subtitle">NFL Season Performance Report</div>
    <div class="cover-detail">All {kpis['total_teams']} Teams | Pythagorean Win Analysis | Conference Breakdown</div>
    <div class="cover-detail">Data: ESPN public API (live standings)</div>
    <div class="cover-date">Report Date: {today}</div>
    <div class="cover-date" style="margin-top:30px;font-size:9pt;color:#6b7280;">
        SAMPLE REPORT — Live data from ESPN.com
    </div>
</div>

<!-- EXECUTIVE SUMMARY -->
<h1>1. Executive Summary</h1>
<div class="exec-box">
    <ul>
        <li><strong>League Overview:</strong> {kpis['total_teams']} teams, {kpis['total_games_played']} games played, {kpis['avg_points_per_game']:.1f} points per game league average</li>
        <li><strong>Best Record:</strong> {kpis['best_record']} | <strong>Worst:</strong> {kpis['worst_record']}</li>
        <li><strong>Pythagorean Overperformer:</strong> {kpis['biggest_overperformer']}</li>
        <li><strong>Pythagorean Underperformer:</strong> {kpis['biggest_underperformer']}</li>
        <li><strong>Conference Balance:</strong> AFC avg {kpis['afc_avg_wins']:.1f} wins ({kpis['afc_avg_pf']:.0f} PPG) | NFC avg {kpis['nfc_avg_wins']:.1f} wins ({kpis['nfc_avg_pf']:.0f} PPG)</li>
        <li><strong>Highest Scoring:</strong> {kpis['highest_scoring']} ({kpis['highest_pf']:.0f} pts) | <strong>Best Defense:</strong> {kpis['best_defense']} ({kpis['lowest_pa']:.0f} pts allowed)</li>
    </ul>
</div>

<!-- KPI DASHBOARD -->
<h1>2. KPI Dashboard</h1>
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-value">{kpis['total_teams']}</div>
        <div class="kpi-label">Teams Tracked</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['avg_points_per_game']:.1f}</div>
        <div class="kpi-label">Avg Points/Game</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['win_pct_stdev']:.3f}</div>
        <div class="kpi-label">Win% Std Dev</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value">{kpis['league_parity']:.2f}</div>
        <div class="kpi-label">Parity Index</div>
    </div>
</div>

<!-- FULL STANDINGS -->
<div class="section-break"></div>
<h1>3. Complete NFL Standings with Pythagorean Analysis</h1>
<p style="font-size:7.5pt;color:#6b7280;">Pythagorean wins use exponent 2.37 (NFL standard). Pyth Diff = Actual Wins - Expected Wins. Positive = overperforming, negative = regression candidate.</p>
<table>
    <thead>
        <tr>
            <th style="text-align:center;">Rank</th>
            <th>Team</th>
            <th>Conf</th>
            <th style="text-align:center;">Record</th>
            <th style="text-align:center;">Win%</th>
            <th style="text-align:right;">PF</th>
            <th style="text-align:right;">PA</th>
            <th style="text-align:right;">Diff</th>
            <th style="text-align:center;">Pyth W</th>
            <th style="text-align:center;">Pyth Diff</th>
        </tr>
    </thead>
    <tbody>
        {standings_rows}
    </tbody>
</table>
<p style="font-size:7pt;color:#9ca3af;">Source: ESPN public API. PF = Points For, PA = Points Against, Diff = Point Differential, Pyth W = Pythagorean Expected Wins.</p>

<!-- PYTHAGOREAN ANALYSIS -->
<div class="section-break"></div>
<h1>4. Pythagorean Win Analysis — Regression Candidates</h1>
<p>Teams with large Pythagorean differentials are statistically likely to regress toward their expected win total. Overperformers may decline; underperformers may improve.</p>

<div class="two-col">
    <div>
        <h2>Top 5 Overperformers (Regression Risk)</h2>
        <table>
            <thead><tr><th>Team</th><th style="text-align:center;">Actual</th><th style="text-align:center;">Expected</th><th style="text-align:center;">Diff</th></tr></thead>
            <tbody>{over_rows}</tbody>
        </table>
        <p style="font-size:7pt;color:#6b7280;">These teams won more games than their point differential suggests. May regress next season.</p>
    </div>
    <div>
        <h2>Top 5 Underperformers (Bounce-Back Candidates)</h2>
        <table>
            <thead><tr><th>Team</th><th style="text-align:center;">Actual</th><th style="text-align:center;">Expected</th><th style="text-align:center;">Diff</th></tr></thead>
            <tbody>{under_rows}</tbody>
        </table>
        <p style="font-size:7pt;color:#6b7280;">These teams underperformed their point differential. Likely to improve next season.</p>
    </div>
</div>

<!-- METHODOLOGY -->
<h1>5. Methodology & Data Sources</h1>
<table>
    <thead>
        <tr><th>Component</th><th>Detail</th></tr>
    </thead>
    <tbody>
        <tr><td>Data Source</td><td>ESPN public API — site.api.espn.com (no authentication required)</td></tr>
        <tr><td>Teams</td><td>All {kpis['total_teams']} NFL teams with current season standings</td></tr>
        <tr><td>Pythagorean Wins</td><td>PF^2.37 / (PF^2.37 + PA^2.37) x Games — NFL standard exponent per Football Outsiders</td></tr>
        <tr><td>Parity Index</td><td>1 - (max win% - min win%) — higher = more competitive league</td></tr>
        <tr><td>Win% Std Dev</td><td>Standard deviation of win percentages from 0.500 — lower = more parity</td></tr>
        <tr><td>Report Period</td><td>Current NFL season standings as of {today}</td></tr>
    </tbody>
</table>
<p style="font-size:7pt;color:#9ca3af;">All data is live from ESPN and independently verifiable at espn.com/nfl/standings.</p>

<div class="disclaimer">
    <strong>Disclaimer & Disclosure:</strong> This report uses <strong>live standings data from the ESPN public API</strong> at the time of generation. "Baseline Sports Analytics" is a fictional brand name used for demonstration — all underlying NFL data is real and independently verifiable at espn.com. This report does not constitute gambling advice. Pythagorean win analysis is a well-established statistical methodology used by Football Outsiders, FiveThirtyEight, and major sports analytics firms.
</div>

<div class="footer-attribution">
    Report prepared by Mboya Jeffers | MboyaJeffers9@gmail.com
</div>

</body>
</html>"""
    return html


if __name__ == "__main__":
    print("Fetching NFL standings from ESPN (real data only)...")
    teams = fetch_nfl_standings()
    print(f"Got {len(teams)} teams from ESPN (live data).")

    # Print a few for verification
    sorted_t = sorted(teams, key=lambda t: -t["wins"])
    for t in sorted_t[:5]:
        print(f"  {t['name']}: {t['wins']}-{t['losses']} ({t['points_for']:.0f} PF, {t['points_against']:.0f} PA)")

    print("\nComputing NFL analytics KPIs...")
    kpis = compute_kpis(teams)

    print("Generating HTML...")
    html = generate_html(teams, kpis)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "..", "output")
    os.makedirs(output_dir, exist_ok=True)
    html_path = os.path.join(output_dir, "Sample_Sports_Analytics_Report.html")
    pdf_path = os.path.join(output_dir, "Sample_Sports_Analytics_Report.pdf")

    with open(html_path, "w") as f:
        f.write(html)
    print(f"HTML saved: {html_path}")

    print("Generating PDF...")
    HTML(string=html).write_pdf(pdf_path)
    print(f"PDF saved: {pdf_path}")
    print("Done — all data is REAL (ESPN public API).")
