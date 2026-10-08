-- name: Ticket volume by month
SELECT Month, COUNT(*) AS Tickets FROM support_tickets GROUP BY Month ORDER BY Month;

-- name: Escalations by issue type and priority
SELECT IssueType, Priority, COUNT(*) AS Tickets, ROUND(100.0*AVG((Escalated='Yes')::INT),1) AS EscalationPct
FROM support_tickets GROUP BY IssueType, Priority HAVING COUNT(*) > 50 ORDER BY EscalationPct DESC LIMIT 10;

-- name: Products generating most tickets
SELECT Product, COUNT(*) AS Tickets, ROUND(AVG(ResolutionHours),2) AS AvgResolutionHours, ROUND(AVG(SatisfactionScore),2) AS AvgCSAT
FROM support_tickets GROUP BY Product ORDER BY Tickets DESC;
