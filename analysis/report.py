"""PDF investigation report (ReportLab)."""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .metrics import kpis, by_dim, load_queries
from .investigation import run
from .segmentation import agent_context

S = getSampleStyleSheet()


def _tbl(df, cols=None):
    df = df[cols] if cols else df
    t = Table([list(map(str, df.columns))] + df.astype(str).values.tolist(), repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                           ("FONTSIZE", (0, 0), (-1, -1), 7), ("GRID", (0, 0), (-1, -1), .3, colors.grey)]))
    return t


def build_report(con, path):
    inv, k = run(con), kpis(con)
    c = inv["case"]
    seg = ["segment", "tickets", "sla_breach_pct", "avg_resolution_hrs", "avg_csat", "reopen_pct", "escalation_pct"]
    P = lambda s: Paragraph(s, S["BodyText"])
    sec = []
    sec.append(("Executive Summary", [P(f"CSAT moved {c['csat'][0]} -> {c['csat'][1]} while monthly ticket volume changed "
        f"{c['volume_change_pct']:+}% and SLA breach rate moved {c['sla'][0]}% -> {c['sla'][1]}%. The largest worsening was in: "
        f"{inv['findings'][0]['observed']}")]))
    sec.append(("Investigation Question", [P("Why are customer support issues increasing, and where are the operational problems occurring?")]))
    sec.append(("Observed Symptoms", [P(f"Comparison window: {c['before_months'][0]}..{c['before_months'][-1]} (before) vs "
        f"{c['after_months'][0]}..{c['after_months'][-1]} (after). Average resolution {c['resolution'][0]}h -> {c['resolution'][1]}h.")]))
    sec.append(("KPI Overview", [_tbl(__import__("pandas").DataFrame([k]))]))
    sec.append(("SLA Analysis", [_tbl(by_dim(con, "Priority"), seg)]))
    sec.append(("Resolution-Time Analysis", [_tbl(by_dim(con, "IssueType"), seg)]))
    sec.append(("Issue-Type Analysis (largest SLA worsening)", [_tbl(inv["leads"].head(8), ["dimension", "segment", "breach_before", "breach_after", "res_before", "res_after", "csat_before", "csat_after"])]))
    sec.append(("Channel Analysis", [_tbl(by_dim(con, "Channel"), seg)]))
    sec.append(("Customer Satisfaction", [_tbl(by_dim(con, "Region"), seg), P(inv["findings"][2]["observed"] + " " + inv["findings"][2]["interpretation"])]))
    sec.append(("Reopened / Escalated Ticket Analysis", [_tbl(by_dim(con, "Reopened"), seg), Spacer(1, 6), _tbl(by_dim(con, "Escalated"), seg)]))
    sec.append(("SQL Evidence", [P("Queries used (see the sql/ folder): " + "; ".join(load_queries()))]))
    sec.append(("Root-Cause Candidates", [P(f"<b>{f['title']}</b><br/>Observed: {f['observed']}<br/>Interpretation: {f['interpretation']}<br/>Hypothesis: {f['hypothesis']}") for f in inv["findings"]]))
    sec.append(("Alternative Explanations", [P("- " + a) for a in inv["alternatives"]]))
    sec.append(("Recommended Next Tests", [P("- " + f["next_test"]) for f in inv["findings"]]))
    sec.append(("Limitations", [P("Fictional, generated data; observational analysis only; no causal claims; agent comparisons ignore case complexity.")]))
    sec.append(("Methodology", [P("DuckDB SQL over a single ticket table. Periods: last three months vs earlier months. Segments under 100 tickets excluded from leads. SLA thresholds: Critical 8h, High 16h, Medium 24h, Low 48h.")]))
    story = [Paragraph("BUSINESS DETECTIVE", S["Title"]), Paragraph("Customer Support Investigation Report", S["Heading2"])]
    for i, (title, items) in enumerate(sec, 1):
        story += [Spacer(1, 10), Paragraph(f"{i}. {title}", S["Heading3"])] + items
    SimpleDocTemplate(str(path), pagesize=A4).build(story)
    return path
