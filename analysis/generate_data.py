"""Generate a fictional support-ticket dataset with investigable patterns.
Planted: from Jul-2026 Technical/Payment tickets resolve slower, Technical reopens rise, Email first response slows."""
import numpy as np, pandas as pd
from pathlib import Path

ISSUES = ["Login", "Delivery", "Technical", "Payment", "Account"]
BASE_HRS = {"Login": 3, "Delivery": 6, "Technical": 10, "Payment": 9, "Account": 4.5}
SLA_HRS = {"Critical": 8, "High": 16, "Medium": 24, "Low": 48}
AGENTS = [f"Agent {c}" for c in "ABCDEFGH"]


def generate(n=8000, seed=11):
    r = np.random.default_rng(seed)
    months = pd.period_range("2026-01", "2026-09", freq="M")
    w = np.linspace(1, 1.9, len(months)); w /= w.sum()
    m = r.choice(len(months), n, p=w)
    created = months.to_timestamp()[m] + pd.to_timedelta(r.integers(0, 28 * 24 * 60, n), "min")
    late = m >= 6
    issue = r.choice(ISSUES, n, p=[.25, .20, .20, .15, .20])
    prio = r.choice(list(SLA_HRS), n, p=[.08, .22, .45, .25])
    channel = r.choice(["Email", "Chat", "Phone"], n, p=[.45, .35, .20])
    region = r.choice(["North", "South", "East", "West"], n, p=[.30, .25, .25, .20])
    agent = r.choice(AGENTS, n)
    hi = np.isin(prio, ["Critical", "High"])
    agent[hi] = r.choice(AGENTS, hi.sum(), p=[.25, .25, .1, .1, .1, .08, .06, .06])  # A,B take more urgent work
    esc = r.random(n) < .04 + .04 * (prio == "Critical") + .04 * (issue == "Technical")
    reopen = r.random(n) < .05 + .12 * (late & (issue == "Technical")) + .03 * esc
    base = pd.Series(issue).map(BASE_HRS).to_numpy()
    res = (base * r.lognormal(0, .45, n) * np.where(late & np.isin(issue, ["Technical", "Payment"]), 1.5, 1)
           * np.where(esc, 1.5, 1) * np.where(region == "South", 1.15, 1) * np.where(channel == "Email", 1.1, 1))
    first = pd.Series(channel).map({"Email": 120, "Chat": 5, "Phone": 3}).to_numpy() * r.lognormal(0, .5, n) \
        * np.where(late & (channel == "Email"), 1.4, 1)
    sla = np.where(res > pd.Series(prio).map(SLA_HRS).to_numpy(), "Breached", "Met")
    csat = 4.4 - .07 * np.minimum(res, 24) - .8 * reopen - .4 * esc - .0015 * first + r.normal(0, .6, n)
    df = pd.DataFrame({
        "TicketID": [f"T{1000 + i}" for i in range(n)], "CustomerID": [f"C{x:05d}" for x in r.integers(1, 4000, n)],
        "CreatedDate": created.round("min"), "ResolvedDate": (created + pd.to_timedelta(res, "h")).round("min"),
        "Channel": channel, "IssueType": issue, "Priority": prio,
        "Product": r.choice(["App", "Web", "Subscription", "Hardware"], n, p=[.35, .3, .2, .15]),
        "CustomerSegment": r.choice(["Consumer", "SMB", "Enterprise"], n, p=[.6, .3, .1]),
        "Region": region, "Agent": agent, "FirstResponseMinutes": first.round(1), "ResolutionHours": res.round(2),
        "SatisfactionScore": np.clip(np.round(csat), 1, 5).astype(int),
        "Reopened": np.where(reopen, "Yes", "No"), "Escalated": np.where(esc, "Yes", "No"), "SLAStatus": sla})
    return df.sort_values("CreatedDate").reset_index(drop=True)


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "data" / "support_tickets.csv"
    d = generate(); d.to_csv(out, index=False); print(f"Wrote {len(d)} tickets to {out}")
