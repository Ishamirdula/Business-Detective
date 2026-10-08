"""DuckDB access + KPI helpers. All SQL runs against the `support_tickets` table."""
import re
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parent.parent
DIMS = ["IssueType", "Priority", "Channel", "Product", "Region", "CustomerSegment", "Agent", "Month",
        "SLAStatus", "Reopened", "Escalated"]
COLS = """COUNT(*) AS tickets,
  ROUND(100.0*AVG((SLAStatus='Breached')::INT),1) AS sla_breach_pct,
  ROUND(AVG(ResolutionHours),2) AS avg_resolution_hrs,
  ROUND(AVG(SatisfactionScore),2) AS avg_csat,
  ROUND(100.0*AVG((Reopened='Yes')::INT),1) AS reopen_pct,
  ROUND(100.0*AVG((Escalated='Yes')::INT),1) AS escalation_pct,
  ROUND(AVG(FirstResponseMinutes),1) AS avg_first_response_min"""


def connect(csv=None):
    csv = str(csv or ROOT / "data" / "support_tickets.csv").replace("'", "''")
    con = duckdb.connect()
    con.execute(f"""CREATE TABLE support_tickets AS
        SELECT *, strftime(CreatedDate, '%Y-%m') AS Month FROM read_csv_auto('{csv}', header=true, types={{'Reopened': 'VARCHAR', 'Escalated': 'VARCHAR'}})""")
    return con


def kpis(con, where=""):
    return con.execute(f"SELECT {COLS} FROM support_tickets {where}").df().iloc[0].to_dict()


def by_dim(con, dim, where=""):
    if dim not in DIMS:
        raise ValueError(f"Unknown dimension: {dim}")
    return con.execute(f"SELECT {dim} AS segment, {COLS} FROM support_tickets {where} GROUP BY 1 ORDER BY 1").df()


def load_queries():
    """Parse sql/*.sql files; each query starts with a '-- name: ...' comment."""
    out = {}
    for f in sorted((ROOT / "sql").glob("*.sql")):
        for block in re.split(r"(?m)^-- name:\s*", f.read_text())[1:]:
            name, _, sql = block.partition("\n")
            out[f"{f.stem}: {name.strip()}"] = sql.strip()
    return out
