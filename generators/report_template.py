#!/usr/bin/env python3
"""
Shared Report Template Module — Enterprise Showcase Suite
Matches CMS Official PDF Template (cms_pdf_generator.py / pdf_generator_template.py)

Author: Mboya Jeffers (MboyaJeffers9@gmail.com)
System: Clean Metrics Studio (CMS)
"""
from datetime import datetime

AUTHOR = "Mboya Jeffers"
EMAIL = "MboyaJeffers9@gmail.com"
SYSTEM = "Clean Metrics Studio (CMS)"


def get_base_css(color_primary, color_light=None, color_accent=None):
    """Return CMS-standard CSS for all report types."""
    if not color_accent:
        color_accent = color_primary
    return f"""
@page {{
    size: letter;
    margin: 0.6in;
    @bottom-center {{
        content: "Page " counter(page) " of " counter(pages);
        font-size: 10px;
        color: #666;
    }}
}}

body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #333;
    line-height: 1.5;
    font-size: 11px;
    orphans: 3;
    widows: 3;
}}

p {{
    margin: 0 0 8px 0;
    orphans: 3;
    widows: 3;
}}

/* ===== HEADER (Cover Page) ===== */
.header {{
    border-bottom: 3px solid {color_primary};
    padding-bottom: 10px;
    margin-bottom: 15px;
}}
.header h1 {{
    color: #1a1a2e;
    margin: 0;
    font-size: 24px;
    line-height: 1.2;
}}
.header .subtitle {{
    color: #666;
    font-size: 12px;
    margin-top: 3px;
}}
.header .date {{
    color: {color_primary};
    font-size: 11px;
    font-weight: bold;
}}

/* ===== CONTENT SECTIONS ===== */
h1 {{
    color: {color_primary};
    font-size: 16px;
    font-weight: 700;
    border-bottom: 2px solid {color_primary};
    padding-bottom: 5px;
    margin: 18px 0 10px 0;
    page-break-after: avoid;
}}
.section {{
    margin: 15px 0;
}}
.section h2, h2.section-title {{
    color: {color_primary};
    font-size: 14px;
    border-bottom: 2px solid {color_primary};
    padding-bottom: 5px;
    margin: 15px 0 8px 0;
    page-break-after: avoid;
}}
.section h3, h3 {{
    color: #1a1a2e;
    font-size: 12px;
    font-weight: 600;
    margin: 10px 0 5px 0;
    page-break-after: avoid;
}}

/* ===== TABLES ===== */
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
    font-size: 10px;
}}
th {{
    background: {color_primary};
    color: white;
    padding: 8px 6px;
    text-align: left;
    font-size: 10px;
    font-weight: 600;
}}
td {{
    padding: 6px;
    border-bottom: 1px solid #eee;
    vertical-align: top;
}}
tr {{
    page-break-inside: avoid;
}}
tr:nth-child(even) {{
    background: #f8f9fa;
}}
thead {{
    display: table-header-group;
}}

/* ===== KPI GRID ===== */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin: 10px 0;
}}
.kpi-card {{
    background: #f8f9fa;
    border-radius: 6px;
    padding: 10px;
    text-align: center;
    border-left: 3px solid {color_primary};
    page-break-inside: avoid;
}}
.kpi-card .label {{
    font-size: 9px;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}
.kpi-card .value {{
    font-size: 16px;
    font-weight: bold;
    color: #1a1a2e;
    margin: 3px 0;
}}
.kpi-card .value.positive {{ color: #10b981; }}
.kpi-card .value.negative {{ color: #ef4444; }}

/* ===== HIGHLIGHT BOXES ===== */
.highlight-box {{
    background: #f0fdf4;
    border-left: 4px solid {color_primary};
    padding: 10px;
    margin: 10px 0;
    font-size: 11px;
    page-break-inside: avoid;
}}
.highlight-box.warning {{
    background: #fef3c7;
    border-color: #f59e0b;
}}
.highlight-box.success {{
    background: #dcfce7;
    border-color: #10b981;
}}
.highlight-box.info {{
    background: #eff6ff;
    border-color: #3b82f6;
}}

/* ===== DATA BADGES ===== */
.data-badge {{
    background: {color_primary};
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: bold;
    display: inline-block;
    margin: 2px;
}}

/* ===== TAGS ===== */
.tag {{
    display: inline-block;
    background: #e5e7eb;
    color: #374151;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 9px;
    margin: 1px;
}}
.tag.primary {{
    background: {color_primary};
    color: white;
}}
.tag.success {{
    background: #dcfce7;
    color: #166534;
}}
.tag.warning {{
    background: #fef3c7;
    color: #92400e;
}}

/* ===== RISK LEVELS ===== */
.risk-high {{ color: #dc2626; font-weight: 600; }}
.risk-med {{ color: #d97706; font-weight: 600; }}
.risk-low {{ color: #16a34a; font-weight: 600; }}

/* ===== LISTS ===== */
ul, ol {{
    margin: 5px 0;
    padding-left: 20px;
}}
li {{
    margin: 3px 0;
    line-height: 1.5;
}}

/* ===== TWO COLUMN ===== */
.two-col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
}}

/* ===== FOOTER ===== */
.footer {{
    margin-top: 20px;
    padding-top: 10px;
    border-top: 1px solid #eee;
    font-size: 10px;
    color: #999;
    text-align: center;
}}
.footer .author {{
    color: {color_primary};
    font-weight: bold;
}}

/* ===== PAGE BREAKS ===== */
.page-break {{
    page-break-before: always;
}}
h2, h3 {{
    page-break-after: avoid;
}}

/* ===== METHODOLOGY ===== */
.methodology {{
    background: #f8f9fa;
    padding: 10px;
    border-radius: 6px;
    font-size: 10px;
    color: #666;
    margin-top: 15px;
}}

/* ===== ML SIGNALS ===== */
.ml-signal {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 9px;
    font-weight: 600;
}}
.ml-bullish {{ background: #dcfce7; color: #166534; }}
.ml-bearish {{ background: #fee2e2; color: #991b1b; }}
.ml-neutral {{ background: #f3f4f6; color: #4b5563; }}
"""


# ============================================================================
# FORMATTERS
# ============================================================================

def fmt_pct(val):
    sign = "+" if val > 0 else ""
    return "%s%.2f%%" % (sign, val)


def fmt_usd(val):
    if abs(val) >= 1e12: return "$%.2fT" % (val / 1e12)
    if abs(val) >= 1e9: return "$%.2fB" % (val / 1e9)
    if abs(val) >= 1e6: return "$%.2fM" % (val / 1e6)
    if abs(val) >= 1e3: return "$%.1fK" % (val / 1e3)
    return "${:,.2f}".format(val)


def pct_color(val):
    if val > 0: return "#10b981"
    if val < 0: return "#ef4444"
    return "#666"


def trend_arrow(val):
    if val > 0: return "&#9650;"
    if val < 0: return "&#9660;"
    return "&#9644;"


def risk_class(level):
    return {"HIGH": "risk-high", "MEDIUM": "risk-med", "LOW": "risk-low"}.get(level, "risk-med")


# ============================================================================
# CMS STANDARD HTML COMPONENTS
# ============================================================================

def header_block(title, subtitle="Generated Report", date_str=None):
    """CMS standard header block — top-left title, subtitle, date, 3px colored rule.
    Used as cover page (page 1) with page break after."""
    if not date_str:
        date_str = datetime.now().strftime("%B %d, %Y")
    return """
<div class="header">
    <h1>%s</h1>
    <div class="subtitle">%s</div>
    <div class="date">%s</div>
</div>
""" % (title, subtitle, date_str)


def cover_page(title, subtitle="Generated Report", date_str=None):
    """CMS standard cover page — header block followed by page break."""
    return header_block(title, subtitle, date_str) + '<div class="page-break"></div>\n'


def content_start():
    """'Content' section divider that starts page 2."""
    return '<h2 class="section-title">Content</h2>\n'


def exec_summary(text_or_bullets):
    """Executive Summary section — CMS standard with bullet points."""
    html = '<h2 class="section-title">Executive Summary</h2>\n'
    if isinstance(text_or_bullets, list):
        html += "<ul>\n"
        for b in text_or_bullets:
            html += "    <li>%s</li>\n" % b
        html += "</ul>\n"
    else:
        html += "<p>%s</p>\n" % text_or_bullets
    return html


def section(title, content=""):
    """Standard section with h2 header."""
    return """
<div class="section">
    <h2>%s</h2>
    %s
</div>
""" % (title, content)


def subsection(title):
    """H3 subsection header."""
    return '<h3>%s</h3>\n' % title


def kpi_grid(kpis):
    """CMS KPI card grid. kpis = list of (value, label) tuples."""
    cards = ""
    for val, label in kpis:
        cards += """
    <div class="kpi-card">
        <div class="label">%s</div>
        <div class="value">%s</div>
    </div>""" % (label, val)
    return '<div class="kpi-grid">%s\n</div>\n' % cards


def kpi_table(rows):
    """KPI table with name/formula/interpretation. rows = list of (name, formula_or_value, interpretation)."""
    tbody = ""
    for name, val, interp in rows:
        tbody += """
        <tr><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>""" % (name, val, interp)
    return """
<table>
    <thead>
        <tr><th>KPI</th><th>Formula / Value</th><th>Interpretation</th></tr>
    </thead>
    <tbody>%s
    </tbody>
</table>""" % tbody


def make_table(headers, rows):
    """Generic table builder. headers = list of strings, rows = list of lists."""
    h_html = "".join("<th>%s</th>" % h for h in headers)
    r_html = ""
    for row in rows:
        r_html += "<tr>" + "".join("<td>%s</td>" % cell for cell in row) + "</tr>\n"
    return """<table>
    <thead><tr>%s</tr></thead>
    <tbody>%s</tbody>
</table>""" % (h_html, r_html)


def risk_table(risks):
    """Risk assessment table. risks = list of (factor, level, commentary)."""
    tbody = ""
    for factor, level, commentary in risks:
        cls = risk_class(level)
        tbody += """
        <tr><td><strong>%s</strong></td><td class="%s">%s</td><td>%s</td></tr>""" % (factor, cls, level, commentary)
    return """
<table>
    <thead>
        <tr><th>Risk Factor</th><th>Level</th><th>Commentary</th></tr>
    </thead>
    <tbody>%s
    </tbody>
</table>""" % tbody


def methodology_table(methods):
    """Two-column methodology table. methods = list of (component, detail)."""
    tbody = ""
    for comp, detail in methods:
        tbody += """
        <tr><td><strong>%s</strong></td><td>%s</td></tr>""" % (comp, detail)
    return """
<table>
    <thead>
        <tr><th>Component</th><th>Detail</th></tr>
    </thead>
    <tbody>%s
    </tbody>
</table>""" % tbody


def highlight_box(content, box_type=""):
    """CMS highlight box. box_type: '', 'warning', 'success', 'info'."""
    return '<div class="highlight-box %s">%s</div>\n' % (box_type, content)


def data_lineage_section(sources, total_rows):
    """Data lineage as a standard section with table."""
    rows_html = ""
    for src in sources:
        rows_html += """
        <tr>
            <td><strong>%s</strong></td>
            <td>%s</td>
            <td style="text-align:right;">%s</td>
            <td>%s</td>
            <td>%s</td>
        </tr>""" % (src["source"], src["table"], "{:,}".format(src["rows"]),
                     src["date_range"], src["pull_date"])
    return """
<h2 class="section-title">Data Lineage</h2>
<p>Generated from <strong>%s</strong> rows of real, traceable public data.</p>
<table>
    <thead>
        <tr><th>Source</th><th>Table</th><th style="text-align:right;">Rows</th><th>Date Range</th><th>Pull Date</th></tr>
    </thead>
    <tbody>%s
    </tbody>
</table>
""" % ("{:,}".format(total_rows), rows_html)


def methodology_section(data_source, metric_defs=None, limitations=None):
    """CMS-standard Methodology section with subsections."""
    html = '<h2 class="section-title">Methodology</h2>\n'
    html += '<h3>Data Source</h3>\n'
    if isinstance(data_source, list):
        html += "<ul>\n"
        for item in data_source:
            html += "    <li>%s</li>\n" % item
        html += "</ul>\n"
    else:
        html += "<p>%s</p>\n" % data_source

    if metric_defs:
        html += '<h3>Metric Definitions</h3>\n<ul>\n'
        for item in metric_defs:
            html += "    <li>%s</li>\n" % item
        html += "</ul>\n"

    if limitations:
        html += '<h3>Limitations</h3>\n<ul>\n'
        for item in limitations:
            html += "    <li>%s</li>\n" % item
        html += "</ul>\n"

    return html


def verification_section(links):
    """Verification section with source documentation links."""
    html = '<h2 class="section-title">Verification</h2>\n<ul>\n'
    for label, url in links:
        html += '    <li><strong>%s:</strong> %s</li>\n' % (label, url)
    html += "</ul>\n"
    return html


def disclaimer(client_name, data_sources_text):
    """Disclaimer text — inline, not boxed."""
    return """
<p style="font-size:10px;color:#666;margin-top:15px;">
    <em>This report uses <strong>%s</strong>.
    "%s" is a fictional firm name used for demonstration &mdash; all underlying market data
    is real and independently verifiable. This report does not constitute financial advice,
    investment recommendation, or solicitation. Past performance does not guarantee future results.</em>
</p>
""" % (data_sources_text, client_name)


def footer(data_source="PostgreSQL"):
    """CMS standard footer with author attribution and branding."""
    return """
<div class="footer">
    Report prepared by <span class="author">%s</span> | %s<br>
    Data Source: %s | Processing: %s
</div>
""" % (AUTHOR, EMAIL, data_source, SYSTEM)


def cms_branding():
    """'Clean Metrics Studio' branding line at end of document."""
    return """
<div style="text-align:center;margin-top:20px;padding-top:10px;border-top:1px solid #eee;">
    <strong style="color:#2d9596;">Clean Metrics Studio</strong>
</div>
"""


# Legacy aliases for backward compatibility during migration
def footer_attribution(total_rows=None):
    """Legacy — use footer() instead. Kept for migration."""
    src = "PostgreSQL"
    if total_rows:
        src = "PostgreSQL ({:,}+ rows)".format(total_rows)
    return footer(src) + cms_branding()


def section_break():
    return '<div class="page-break"></div>\n'


def ml_signal_badge(signal):
    """Return HTML for an ML signal badge (bullish/bearish/neutral)."""
    cls = {"bullish": "ml-bullish", "bearish": "ml-bearish"}.get(signal.lower(), "ml-neutral")
    return '<span class="ml-signal %s">%s</span>' % (cls, signal.upper())


def wrap_html(css, body):
    """Wrap body HTML with doctype, head, and base structure."""
    return """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
%s
</style>
</head>
<body>
%s
</body>
</html>""" % (css, body)
