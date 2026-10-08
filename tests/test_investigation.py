from analysis.generate_data import generate
from analysis.metrics import connect, load_queries
from analysis.investigation import run
from analysis.segmentation import agent_context


def _con(tmp_path):
    p = tmp_path / "s.csv"; generate(4000).to_csv(p, index=False); return connect(p)


def test_case_detects_decline_and_leads(tmp_path):
    inv = run(_con(tmp_path))
    assert inv["case"]["csat"][1] < inv["case"]["csat"][0]
    assert inv["leads"].iloc[0].breach_change > 0
    assert inv["reopen"].set_index("segment").loc["Yes", "avg_csat"] < inv["reopen"].set_index("segment").loc["No", "avg_csat"]
    assert inv["corr"][0] < 0


def test_agent_context_and_all_sql_run(tmp_path):
    con = _con(tmp_path)
    assert not agent_context(con).empty
    for name, sql in load_queries().items():
        assert len(con.execute(sql).df()) > 0, name
