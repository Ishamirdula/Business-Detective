-- name: SLA breach by issue type
SELECT IssueType, COUNT(*) AS Tickets,
       SUM(CASE WHEN SLAStatus = 'Breached' THEN 1 ELSE 0 END) AS BreachedTickets,
       ROUND(100.0 * SUM(CASE WHEN SLAStatus = 'Breached' THEN 1 ELSE 0 END) / COUNT(*), 2) AS BreachRate
FROM support_tickets GROUP BY IssueType ORDER BY BreachRate DESC;

-- name: Before vs after by issue type (CTE)
WITH p AS (SELECT *, CASE WHEN Month >= '2026-07' THEN 'After' ELSE 'Before' END AS Period FROM support_tickets)
SELECT IssueType, Period, COUNT(*) AS Tickets, ROUND(AVG(ResolutionHours),2) AS AvgResolution,
       ROUND(100.0*AVG((SLAStatus='Breached')::INT),1) AS BreachPct, ROUND(AVG(SatisfactionScore),2) AS AvgCSAT
FROM p GROUP BY IssueType, Period ORDER BY IssueType, Period DESC;

-- name: Reopened tickets vs satisfaction
SELECT Reopened, COUNT(*) AS Tickets, ROUND(AVG(SatisfactionScore),2) AS AvgCSAT, ROUND(AVG(ResolutionHours),2) AS AvgResolutionHours
FROM support_tickets GROUP BY Reopened;
