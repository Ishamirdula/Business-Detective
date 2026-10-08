"""Business Detective: Customer Support Investigation Platform. Run: streamlit run app.py"""
import pandas as pd, plotly.express as px, streamlit as st
from analysis.metrics import ROOT, connect, kpis, by_dim, load_queries, DIMS
from analysis.investigation import run
from analysis.segmentation import agent_context
from analysis.report import build_report

st.set_page_config(page_title="Business Detective", layout="wide")


@st.cache_resource
def get_con():
    csv = ROOT / "data" / "support_tickets.csv"
    if not csv.exists():
        from analysis.generate_data import generate
        generate().to_csv(csv, index=False)
    return connect()


con = get_con()
inv = run(con)
c = inv["case"]
st.sidebar.title("BUSINESS DETECTIVE")
page = st.sidebar.radio("Go to", ["Case Board", "Investigation", "Operations Explorer", "SLA & Customer Experience",
                                  "Agents (with context)", "SQL Lab", "Report"])
st.title(page)

if page == "Case Board":
    k = kpis(con)
    cols = st.columns(6)
    for col, (label, v) in zip(cols, [("Total tickets", f"{k['tickets']:,}"), ("SLA breach", f"{k['sla_breach_pct']}%"),
            ("Avg resolution", f"{k['avg_resolution_hrs']} h"), ("Avg CSAT", f"{k['avg_csat']} / 5"),
            ("Reopen rate", f"{k['reopen_pct']}%"), ("Escalation rate", f"{k['escalation_pct']}%")]):
        col.metric(label, v)
    st.error(f"**CASE #001: Customer Experience Investigation**  \n"
             f"Symptom: CSAT {c['csat'][0]} -> {c['csat'][1]} | Ticket volume {c['volume_change_pct']:+}% per month | "
             f"SLA breach {c['sla'][0]}% -> {c['sla'][1]}%  \nStatus: **{c['status']}**")
    m = by_dim(con, "Month")
    st.plotly_chart(px.bar(m, x="segment", y="tickets", title="Tickets per month"), use_container_width=True)
    st.plotly_chart(px.line(m, x="segment", y="avg_csat", markers=True, title="Average CSAT per month"), use_container_width=True)

elif page == "Investigation":
    st.subheader("Where did SLA performance worsen? (last 3 months vs earlier)")
    st.dataframe(inv["leads"].head(10), use_container_width=True)
    for f in inv["findings"]:
        with st.expander(f["title"], expanded=True):
            st.markdown(f"**Observed:** {f['observed']}\n\n**Interpretation:** {f['interpretation']}\n\n"
                        f"**Hypothesis:** {f['hypothesis']}\n\n**Next test:** {f['next_test']}")
    st.info("We do not claim causation: these are associations in observational data.")
    st.subheader("Alternative explanations")
    for a in inv["alternatives"]:
        st.write("- " + a)
    dim = st.selectbox("Investigate by dimension", DIMS)
    d = by_dim(con, dim)
    st.dataframe(d, use_container_width=True)
    st.plotly_chart(px.bar(d, x="segment", y="sla_breach_pct", title=f"SLA breach % by {dim}"), use_container_width=True)

elif page == "Operations Explorer":
    df = con.execute("SELECT * FROM support_tickets").df()
    a, b = st.columns(2)
    a.plotly_chart(px.histogram(df, x="ResolutionHours", nbins=50, title="Resolution time distribution"), use_container_width=True)
    b.plotly_chart(px.bar(by_dim(con, "IssueType"), x="segment", y="avg_csat", title="CSAT by issue type"), use_container_width=True)
    a.plotly_chart(px.bar(by_dim(con, "Priority"), x="segment", y="tickets", title="Tickets by priority"), use_container_width=True)
    b.plotly_chart(px.bar(by_dim(con, "Channel"), x="segment", y="avg_resolution_hrs", title="Resolution by channel"), use_container_width=True)
    st.dataframe(by_dim(con, "IssueType"), use_container_width=True)

elif page == "SLA & Customer Experience":
    df = con.execute("SELECT * FROM support_tickets").df()
    a, b = st.columns(2)
    a.plotly_chart(px.pie(df, names="SLAStatus", hole=.5, title="SLA performance"), use_container_width=True)
    b.plotly_chart(px.histogram(df, x="SatisfactionScore", title="CSAT distribution"), use_container_width=True)
    st.plotly_chart(px.scatter(df.sample(1500, random_state=1), x="ResolutionHours", y="SatisfactionScore", opacity=.3,
                               title="Resolution hours vs CSAT (sample)"), use_container_width=True)
    st.write(f"Pearson r, resolution vs CSAT: **{inv['corr'][0]:.2f}**; first response vs CSAT: **{inv['corr'][1]:.2f}**. "
             "Correlation does not establish causation.")

elif page == "Agents (with context)":
    st.caption("No leaderboard: agents handle different ticket mixes, so raw metrics are shown with workload context.")
    st.dataframe(agent_context(con), use_container_width=True)

elif page == "SQL Lab":
    qs = load_queries()
    name = st.selectbox("Saved query", list(qs))
    sql = st.text_area("SQL (SELECT only)", qs[name], height=200)
    if st.button("Run"):
        if sql.strip().lower().startswith(("select", "with")):
            try:
                st.dataframe(con.execute(sql).df(), use_container_width=True)
            except Exception as e:
                st.error(str(e))
        else:
            st.error("Only SELECT queries are allowed.")

else:
    if st.button("Generate PDF report"):
        p = build_report(con, ROOT / "reports" / "investigation_report.pdf")
        st.download_button("Download report", open(p, "rb").read(), "investigation_report.pdf", "application/pdf")
