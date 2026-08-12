/* =========================================================
   Retention & Churn Optimisation — SQL layer
   Tables: users(user_id, signup_date, acquisition_channel, plan,
                 onboarding_completed, churn_date, is_active, signup_month)
           events(user_id, event_date, event_type)
           subscriptions(user_id, plan, monthly_revenue, signup_date,
                          churn_date, is_active, status)
   Dialect: SQLite / standard ANSI SQL (works in Postgres/MySQL with
   minor date-function swaps, noted below)
   ========================================================= */

-- 1. D1 / D7 / D30 / D90 RETENTION
-- "Retained on day N" = user had at least one event on exactly signup_date + N
WITH signups AS (
    SELECT user_id, signup_date FROM users
),
checkpoints AS (
    SELECT s.user_id,
           s.signup_date,
           date(s.signup_date, '+1 day')  AS d1_date,
           date(s.signup_date, '+7 day')  AS d7_date,
           date(s.signup_date, '+30 day') AS d30_date,
           date(s.signup_date, '+90 day') AS d90_date
    FROM signups s
)
SELECT
    COUNT(DISTINCT c.user_id) AS total_users,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN e1.user_id IS NOT NULL THEN c.user_id END) / COUNT(DISTINCT c.user_id), 1) AS d1_retention_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN e7.user_id IS NOT NULL THEN c.user_id END) / COUNT(DISTINCT c.user_id), 1) AS d7_retention_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN e30.user_id IS NOT NULL THEN c.user_id END) / COUNT(DISTINCT c.user_id), 1) AS d30_retention_pct,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN e90.user_id IS NOT NULL THEN c.user_id END) / COUNT(DISTINCT c.user_id), 1) AS d90_retention_pct
FROM checkpoints c
LEFT JOIN events e1  ON e1.user_id = c.user_id  AND e1.event_date = c.d1_date
LEFT JOIN events e7  ON e7.user_id = c.user_id  AND e7.event_date = c.d7_date
LEFT JOIN events e30 ON e30.user_id = c.user_id AND e30.event_date = c.d30_date
LEFT JOIN events e90 ON e90.user_id = c.user_id AND e90.event_date = c.d90_date;


-- 2. COHORT RETENTION TABLE (by signup month) — feeds the Power BI heatmap
WITH activity AS (
    SELECT u.user_id,
           u.signup_month,
           u.signup_date,
           e.event_date,
           CAST(julianday(e.event_date) - julianday(u.signup_date) AS INT) AS day_offset
    FROM users u
    JOIN events e ON e.user_id = u.user_id
),
cohort_size AS (
    SELECT signup_month, COUNT(DISTINCT user_id) AS cohort_users
    FROM users GROUP BY signup_month
)
SELECT
    a.signup_month,
    cs.cohort_users,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN day_offset BETWEEN 0 AND 1  THEN a.user_id END) / cs.cohort_users, 1) AS d1,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN day_offset BETWEEN 0 AND 7  THEN a.user_id END) / cs.cohort_users, 1) AS d7,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN day_offset BETWEEN 0 AND 30 THEN a.user_id END) / cs.cohort_users, 1) AS d30,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN day_offset BETWEEN 0 AND 90 THEN a.user_id END) / cs.cohort_users, 1) AS d90
FROM activity a
JOIN cohort_size cs ON cs.signup_month = a.signup_month
GROUP BY a.signup_month, cs.cohort_users
ORDER BY a.signup_month;


-- 3. FUNNEL DROP-OFF: onboarding completion vs churn
SELECT
    onboarding_completed,
    COUNT(*) AS users,
    ROUND(100.0 * SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS churn_rate_pct
FROM users
GROUP BY onboarding_completed;


-- 4. CLTV BY ACQUISITION CHANNEL
-- CLTV = avg monthly revenue x avg customer lifespan (months)
WITH lifespans AS (
    SELECT
        u.user_id,
        u.acquisition_channel,
        s.monthly_revenue,
        ROUND(
            (julianday(COALESCE(u.churn_date, CURRENT_DATE)) - julianday(u.signup_date)) / 30.0
        , 1) AS lifespan_months
    FROM users u
    JOIN subscriptions s ON s.user_id = u.user_id
)
SELECT
    acquisition_channel,
    COUNT(*) AS users,
    ROUND(AVG(monthly_revenue), 0) AS avg_monthly_revenue,
    ROUND(AVG(lifespan_months), 1) AS avg_lifespan_months,
    ROUND(AVG(monthly_revenue) * AVG(lifespan_months), 0) AS estimated_cltv
FROM lifespans
GROUP BY acquisition_channel
ORDER BY estimated_cltv DESC;

/* Postgres/MySQL notes:
   - date(x, '+N day')      -> Postgres: (x + interval 'N day')
   - julianday(a) - julianday(b) -> Postgres: (a - b) as integer days
*/
