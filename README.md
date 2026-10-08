# Business Detective: Customer Support & Service Investigation
Root-cause analysis for customer experience and operations.

**Core question:** Why are customer support issues increasing, and where are the operational problems occurring?

## What it does
- **Case Board:** operational KPIs plus an auto-generated case (CSAT, volume, SLA symptoms).
- **Investigation:** compares the last 3 months with earlier months, ranks the segments whose SLA breach rate worsened most, and writes each finding as Observed / Interpretation / Hypothesis / Next test. Pick any of 11 dimensions to drill in.
- **Operations Explorer, SLA & Customer Experience:** volume, resolution distribution, CSAT, SLA split, resolution vs CSAT with Pearson r.
- **Agents (with context):** no leaderboard; each agent's high-priority workload share is shown next to their metrics.
- **SQL Lab:** 12 saved DuckDB queries (CTEs, window functions, CASE, HAVING) you can edit and run.
- **Report:** 16-section PDF in `reports/`.

## Findings on the generated data (yours may differ slightly)
- CSAT 3.70 -> 3.56, SLA breach 5.2% -> 11.2%, monthly volume +35%.
- Largest worsening: Technical tickets (breach 13.7% -> 32.1%, reopen 6.0% -> 15.4%), then Payment.
- Reopened tickets average CSAT 2.72 vs 3.70. Resolution time vs CSAT r = -0.50.
- These are associations; the data cannot prove cause.

## Limitations
observational only; agent comparisons ignore case complexity; fixed SLA thresholds (Critical 8h, High 16h, Medium 24h, Low 48h).



