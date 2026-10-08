"""Structured investigation: symptom -> where -> observed / interpretation / hypothesis / next test."""
import pandas as pd
from .metrics import kpis, by_dim

LEAD_DIMS = ["IssueType", "Channel", "Region", "Priority", "Product", "CustomerSegment"]
ALTERNATIVES = [
    "Ticket mix changed (more complex issues), not agent or process performance.",
    "Staffing or scheduling changes reduced capacity during the period.",
    "A product release or policy change created new problem types.",
    "Survey response behaviour changed, so CSAT shifted without service changing.",
]


def _where(ms):
    return "WHERE Month IN (%s)" % ",".join(f"'{m}'" for m in ms)


def run(con, min_tickets=100):
    months = [r[0] for r in con.execute("SELECT DISTINCT Month FROM support_tickets ORDER BY 1").fetchall()]
    after, before = months[-3:], months[:-3]
    kb, ka = kpis(con, _where(before)), kpis(con, _where(after))
    case = {"before_months": before, "after_months": after, "status": "UNDER INVESTIGATION",
            "csat": (kb["avg_csat"], ka["avg_csat"]), "sla": (kb["sla_breach_pct"], ka["sla_breach_pct"]),
            "resolution": (kb["avg_resolution_hrs"], ka["avg_resolution_hrs"]),
            "volume_change_pct": round(((ka["tickets"] / len(after)) / (kb["tickets"] / len(before)) - 1) * 100, 1)}
    rows = []
    for dim in LEAD_DIMS:
        b, a = by_dim(con, dim, _where(before)).set_index("segment"), by_dim(con, dim, _where(after)).set_index("segment")
        for seg in a.index.intersection(b.index):
            if a.loc[seg, "tickets"] < min_tickets:
                continue
            rows.append({"dimension": dim, "segment": seg, "tickets_after": int(a.loc[seg, "tickets"]),
                         "breach_before": b.loc[seg, "sla_breach_pct"], "breach_after": a.loc[seg, "sla_breach_pct"],
                         "res_before": b.loc[seg, "avg_resolution_hrs"], "res_after": a.loc[seg, "avg_resolution_hrs"],
                         "csat_before": b.loc[seg, "avg_csat"], "csat_after": a.loc[seg, "avg_csat"],
                         "reopen_before": b.loc[seg, "reopen_pct"], "reopen_after": a.loc[seg, "reopen_pct"]})
    leads = pd.DataFrame(rows)
    leads["breach_change"] = (leads.breach_after - leads.breach_before).round(1)
    leads = leads.sort_values("breach_change", ascending=False).reset_index(drop=True)
    ro = by_dim(con, "Reopened").set_index("segment")
    c_res, c_first = con.execute("SELECT corr(ResolutionHours, SatisfactionScore), "
                                 "corr(FirstResponseMinutes, SatisfactionScore) FROM support_tickets").fetchone()
    t = leads.iloc[0]
    findings = [
        {"title": "Where SLA performance worsened most",
         "observed": f"{t.dimension} = {t.segment}: SLA breach {t.breach_before}% -> {t.breach_after}%, avg resolution "
                     f"{t.res_before}h -> {t.res_after}h, CSAT {t.csat_before} -> {t.csat_after}.",
         "interpretation": "This segment shows the largest worsening and is the strongest lead for the overall decline.",
         "hypothesis": f"A capacity, complexity or process change affecting {t.segment} tickets after {after[0]}.",
         "next_test": f"Check staffing, ticket complexity, releases and policy changes touching {t.segment}."},
        {"title": "Reopened tickets and satisfaction",
         "observed": f"Reopened tickets average CSAT {ro.loc['Yes', 'avg_csat']} vs {ro.loc['No', 'avg_csat']} for others.",
         "interpretation": "Reopened tickets are associated with poorer customer experience in this dataset.",
         "hypothesis": "Incomplete first-contact resolution may be contributing to lower satisfaction.",
         "next_test": "Examine first-response time, issue complexity and agent/team assignment for reopened tickets."},
        {"title": "Resolution time and satisfaction",
         "observed": f"Pearson r (resolution hours vs CSAT) = {c_res:.2f}; (first response vs CSAT) = {c_first:.2f}.",
         "interpretation": "Longer resolution is associated with lower CSAT. Correlation does not establish causation.",
         "hypothesis": "Waiting time itself may reduce satisfaction, or hard issues drive both long times and low CSAT.",
         "next_test": "Compare CSAT at equal issue type and priority across resolution-time bands."}]
    return {"case": case, "leads": leads, "reopen": ro.reset_index(), "corr": (c_res, c_first),
            "findings": findings, "alternatives": ALTERNATIVES}
