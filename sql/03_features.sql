-- Building the unified feature table for the XGBoost model

SELECT 
    m.msno AS user_id,
    m.city,
    m.bd AS age,
    m.registered_via,
    t.is_churn,
    
    -- Transaction Features
    MAX(tr.is_auto_renew) AS auto_renew_flag,
    MAX(tr.is_cancel) AS cancel_flag,
    SUM(tr.actual_amount_paid) AS total_lifetime_spend,
    
    -- Engagement Features (from logs)
    SUM(ul.num_100) AS total_songs_completed,
    SUM(ul.total_secs) AS total_listening_seconds

FROM 
    kk_members m
JOIN 
    kk_train t ON m.msno = t.msno
LEFT JOIN 
    kk_transactions tr ON m.msno = tr.msno
LEFT JOIN 
    kk_user_logs_sample ul ON m.msno = ul.msno
GROUP BY 
    m.msno;