"""
Generates synthetic data for a Retention & Churn Optimisation project.
Simulates: users, daily activity events, subscriptions/cancellations.
Output: users.csv, events.csv, subscriptions.csv
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

N_USERS = 3000
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 9, 30)
OBSERVATION_END = datetime(2025, 10, 30)  # data collection cutoff (gives room for D30/D90 checks)

CHANNELS = ["Organic Search", "Paid Social", "Referral", "Email Campaign", "App Store"]
CHANNEL_WEIGHTS = [0.30, 0.25, 0.15, 0.15, 0.15]
PLANS = {"Basic": 199, "Standard": 499, "Premium": 999}  # monthly revenue (INR)
PLAN_WEIGHTS = [0.5, 0.35, 0.15]

# ---------- USERS ----------
signup_days = (END_DATE - START_DATE).days
signup_offsets = np.random.randint(0, signup_days, N_USERS)
signup_dates = [START_DATE + timedelta(days=int(o)) for o in signup_offsets]

users = pd.DataFrame({
    "user_id": range(1, N_USERS + 1),
    "signup_date": signup_dates,
    "acquisition_channel": np.random.choice(CHANNELS, N_USERS, p=CHANNEL_WEIGHTS),
    "plan": np.random.choice(list(PLANS.keys()), N_USERS, p=PLAN_WEIGHTS),
    "onboarding_completed": np.random.choice([1, 0], N_USERS, p=[0.62, 0.38]),
})
users["monthly_revenue"] = users["plan"].map(PLANS)
users["signup_month"] = pd.to_datetime(users["signup_date"]).dt.to_period("M").astype(str)

# ---------- CHURN SIMULATION ----------
# Onboarding completion + channel quality drive retention probability (this is the causal
# story your "AI onboarding guide" pitch is based on).
channel_quality = {
    "Organic Search": 0.08, "Referral": 0.10, "Email Campaign": 0.02,
    "Paid Social": -0.05, "App Store": 0.0
}

def simulate_survival(row):
    base_daily_churn = 0.010
    if row["onboarding_completed"]:
        base_daily_churn *= 0.55  # onboarding cuts daily churn risk
    base_daily_churn -= channel_quality[row["acquisition_channel"]] * 0.01
    base_daily_churn = max(base_daily_churn, 0.002)

    max_days = (OBSERVATION_END - row["signup_date"]).days
    day = 0
    while day < max_days:
        day += 1
        if np.random.random() < base_daily_churn:
            return row["signup_date"] + timedelta(days=day)
    return pd.NaT  # still active / right-censored

users["churn_date"] = users.apply(simulate_survival, axis=1)
users["is_active"] = users["churn_date"].isna().astype(int)

# ---------- SUBSCRIPTIONS ----------
subscriptions = users[["user_id", "plan", "monthly_revenue", "signup_date", "churn_date", "is_active"]].copy()
subscriptions["status"] = np.where(subscriptions["is_active"] == 1, "active", "cancelled")

# ---------- EVENTS (login activity) ----------
event_rows = []
for _, u in users.iterrows():
    last_day = (u["churn_date"] - timedelta(days=1)) if pd.notna(u["churn_date"]) else OBSERVATION_END
    active_span = max((last_day - u["signup_date"]).days, 0)
    if active_span == 0:
        continue
    # engaged users log in more frequently
    engagement_rate = 0.55 if u["onboarding_completed"] else 0.30
    n_sessions = int(active_span * engagement_rate * np.random.uniform(0.5, 1.3))
    session_days = np.random.choice(range(active_span + 1), size=min(n_sessions, active_span + 1), replace=False)
    for d in session_days:
        event_rows.append({
            "user_id": u["user_id"],
            "event_date": u["signup_date"] + timedelta(days=int(d)),
            "event_type": np.random.choice(
                ["login", "feature_use", "support_ticket"], p=[0.75, 0.22, 0.03]
            ),
        })

events = pd.DataFrame(event_rows)

# ---------- SAVE ----------
users.drop(columns=["monthly_revenue"]).to_csv("/mnt/user-data/outputs/users.csv", index=False)
events.to_csv("/mnt/user-data/outputs/events.csv", index=False)
subscriptions.to_csv("/mnt/user-data/outputs/subscriptions.csv", index=False)

print("users:", users.shape)
print("events:", events.shape)
print("subscriptions:", subscriptions.shape)
print("Overall churn rate:", round(1 - users['is_active'].mean(), 3))
