-- name: Satisfaction by channel
SELECT Channel, COUNT(*) AS Tickets, ROUND(AVG(SatisfactionScore),2) AS AvgCSAT FROM support_tickets GROUP BY Channel ORDER BY AvgCSAT;

-- name: CSAT by resolution-time band
SELECT CASE WHEN ResolutionHours < 4 THEN '1: <4h' WHEN ResolutionHours < 8 THEN '2: 4-8h'
            WHEN ResolutionHours < 16 THEN '3: 8-16h' ELSE '4: 16h+' END AS ResolutionBand,
       COUNT(*) AS Tickets, ROUND(AVG(SatisfactionScore),2) AS AvgCSAT
FROM support_tickets GROUP BY 1 ORDER BY 1;

-- name: Lowest-satisfaction regions
SELECT Region, COUNT(*) AS Tickets, ROUND(AVG(SatisfactionScore),2) AS AvgCSAT FROM support_tickets GROUP BY Region ORDER BY AvgCSAT;
