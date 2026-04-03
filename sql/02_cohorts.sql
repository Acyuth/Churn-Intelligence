-- What is the overall churn rate by Acquisition Channel?

SELECT 
    m.registered_via AS acquisition_channel,
    COUNT(m.msno) AS total_users,
    SUM(t.is_churn) AS churned_users,
    ROUND(CAST(SUM(t.is_churn) AS FLOAT) / COUNT(m.msno) * 100, 2) AS churn_rate_pct
FROM 
    kk_members m
JOIN 
    kk_train t ON m.msno = t.msno
GROUP BY 
    m.registered_via
ORDER BY 
    total_users DESC;