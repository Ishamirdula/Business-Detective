"""Agent view with workload context. Deliberately not a leaderboard."""
from .metrics import by_dim


def agent_context(con, gap_pts=5.0):
    df = by_dim(con, "Agent").rename(columns={"segment": "agent"})
    hi = con.execute("SELECT Agent, 100.0*AVG((Priority IN ('Critical','High'))::INT) FROM support_tickets GROUP BY 1").df()
    hi.columns = ["agent", "high_priority_pct"]
    overall = con.execute("SELECT 100.0*AVG((Priority IN ('Critical','High'))::INT) FROM support_tickets").fetchone()[0]
    df = df.merge(hi, on="agent").round({"high_priority_pct": 1})

    def note(p):
        if p - overall > gap_pts:
            return f"Handles more urgent work ({p:.0f}% vs {overall:.0f}% avg); raw comparison may be misleading."
        if overall - p > gap_pts:
            return f"Handles less urgent work ({p:.0f}% vs {overall:.0f}% avg); raw comparison may be misleading."
        return "Workload mix close to average."
    df["context"] = df.high_priority_pct.map(note)
    return df
