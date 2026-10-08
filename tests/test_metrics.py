import pandas as pd
from analysis.metrics import connect, kpis, by_dim, load_queries
import pytest


def _csv(tmp_path):
    df = pd.DataFrame({"TicketID": ["a", "b", "c", "d"], "CreatedDate": ["2026-01-05 10:00:00"] * 4, "Priority": ["High"] * 2 + ["Low"] * 2,
                       "ResolutionHours": [2, 20, 4, 6], "FirstResponseMinutes": [5] * 4, "SatisfactionScore": [5, 2, 4, 5],
                       "Reopened": ["No", "Yes", "No", "No"], "Escalated": ["No"] * 4, "SLAStatus": ["Met", "Breached", "Met", "Met"]})
    p = tmp_path / "t.csv"; df.to_csv(p, index=False); return p


def test_kpis(tmp_path):
    k = kpis(connect(_csv(tmp_path)))
    assert k["tickets"] == 4 and k["sla_breach_pct"] == 25.0 and k["reopen_pct"] == 25.0 and k["avg_csat"] == 4.0


def test_by_dim_and_whitelist(tmp_path):
    con = connect(_csv(tmp_path))
    assert set(by_dim(con, "Priority").segment) == {"High", "Low"}
    with pytest.raises(ValueError):
        by_dim(con, "x; DROP TABLE support_tickets")


def test_sql_files_parse():
    assert len(load_queries()) >= 10
