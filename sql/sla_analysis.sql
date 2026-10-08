-- name: Average resolution by priority
SELECT Priority, COUNT(*) AS Tickets, ROUND(AVG(ResolutionHours),2) AS AvgResolutionHours
FROM support_tickets GROUP BY Priority ORDER BY AvgResolutionHours DESC;

-- name: Monthly breach rate with change (window function)
WITH m AS (SELECT Month, ROUND(100.0*AVG((SLAStatus='Breached')::INT),2) AS BreachPct FROM support_tickets GROUP BY Month)
SELECT Month, BreachPct, ROUND(BreachPct - LAG(BreachPct) OVER (ORDER BY Month),2) AS ChangeVsPrev FROM m ORDER BY Month;

-- name: Breach rate by region and priority
SELECT Region, Priority, COUNT(*) AS Tickets, ROUND(100.0*AVG((SLAStatus='Breached')::INT),1) AS BreachPct
FROM support_tickets GROUP BY Region, Priority HAVING COUNT(*) > 50 ORDER BY BreachPct DESC;
