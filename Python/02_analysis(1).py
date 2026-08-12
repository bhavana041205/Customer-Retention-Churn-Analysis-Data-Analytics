"""
Retention & Churn Optimisation — analysis layer
Reads users.csv / events.csv / subscriptions.csv
Produces: cohort_retention_matrix.csv, cltv_by_channel.csv,
          churn_risk_scores.csv, retention_heatmap.png,
          onboarding_impact_estimate.txt
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report

OUT = "/mnt/user-data/outputs/"

users = pd.read_csv(OUT + "users.csv", parse_dates=["signup_date", "churn_date"])
events = pd.read_csv(OUT + "events.csv", parse_dates=["event_date"])
subs = pd.read_csv(OUT + "subscriptions.csv", parse_dates=["signup_date", "churn_date"])

# ---------- 1. COHORT RETENTION MATRIX ----------
ev = events.merge(users[["user_id", "signup_date", "signup_month"]], on="user_id")
ev["day_offset"] = (ev["event_date"] - ev["signup_date"]).dt.days

cohort_sizes = users.groupby("signup_month")["user_id"].nunique()

def pct_active_by(day_max):
    active = ev[ev["day_offset"].between(0, day_max)].groupby("signup_month")["user_id"].nunique()
    return (active / cohort_sizes * 100).round(1)

cohort_matrix = pd.DataFrame({
    "cohort_users": cohort_sizes,
    "D1": pct_active_by(1),
    "D7": pct_active_by(7),
    "D30": pct_active_by(30),
    "D90": pct_active_by(90),
}).fillna(0)
cohort_matrix.to_csv(OUT + "cohort_retention_matrix.csv")

# heatmap for the portfolio / dashboard preview
fig, ax = plt.subplots(figsize=(8, 5))
data = cohort_matrix[["D1", "D7", "D30", "D90"]]
im = ax.imshow(data.values, cmap="YlGnBu", aspect="auto")
ax.set_xticks(range(len(data.columns))); ax.set_xticklabels(data.columns)
ax.set_yticks(range(len(data.index))); ax.set_yticklabels(data.index)
for i in range(data.shape[0]):
    for j in range(data.shape[1]):
        ax.text(j, i, f"{data.values[i,j]:.0f}%", ha="center", va="center", fontsize=8)
ax.set_title("Cohort Retention Heatmap (%)")
plt.colorbar(im, ax=ax, label="% retained")
plt.tight_layout()
plt.savefig(OUT + "retention_heatmap.png", dpi=150)
plt.close()

# ---------- 2. CLTV BY CHANNEL ----------
lifespan = users.merge(subs[["user_id", "monthly_revenue"]], on="user_id")
lifespan["end_date"] = lifespan["churn_date"].fillna(pd.Timestamp("2025-10-30"))
lifespan["lifespan_months"] = (lifespan["end_date"] - lifespan["signup_date"]).dt.days / 30

cltv = lifespan.groupby("acquisition_channel").agg(
    users=("user_id", "count"),
    avg_monthly_revenue=("monthly_revenue", "mean"),
    avg_lifespan_months=("lifespan_months", "mean"),
).reset_index()
cltv["estimated_cltv"] = (cltv["avg_monthly_revenue"] * cltv["avg_lifespan_months"]).round(0)
cltv = cltv.sort_values("estimated_cltv", ascending=False)
cltv.to_csv(OUT + "cltv_by_channel.csv", index=False)

# ---------- 3. CHURN-RISK MODEL (the "AI" in "AI onboarding guide") ----------
# Features available at/near signup time — no future leakage
feat = users.copy()
feat["days_since_signup"] = (pd.Timestamp("2025-10-30") - feat["signup_date"]).dt.days
feat = pd.get_dummies(feat, columns=["acquisition_channel", "plan"], drop_first=True)

# only score users with enough history to have a real D30 outcome
eligible = feat[feat["days_since_signup"] >= 30].copy()
eligible["churned_by_d30"] = (
    (eligible["churn_date"].notna()) &
    ((eligible["churn_date"] - eligible["signup_date"]).dt.days <= 30)
).astype(int)

drop_cols = ["user_id", "signup_date", "churn_date", "signup_month", "is_active", "churned_by_d30"]
X = eligible.drop(columns=drop_cols)
y = eligible["churned_by_d30"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
model = LogisticRegression(max_iter=1000, class_weight="balanced")
model.fit(X_train, y_train)

y_prob = model.predict_proba(X_test)[:, 1]
auc = roc_auc_score(y_test, y_prob)

# score everyone, output risk list for the "personalized insights" feature
X_all = eligible.drop(columns=[c for c in drop_cols if c in eligible.columns])
eligible["churn_risk_score"] = model.predict_proba(X_all)[:, 1].round(3)
risk_output = eligible[["user_id", "onboarding_completed", "churn_risk_score"]].sort_values(
    "churn_risk_score", ascending=False
)
risk_output.to_csv(OUT + "churn_risk_scores.csv", index=False)

# ---------- 4. ONBOARDING IMPACT ESTIMATE (backs the "20% reduction" claim) ----------
completed = eligible[eligible["onboarding_completed"] == 1]["churned_by_d30"].mean()
not_completed = eligible[eligible["onboarding_completed"] == 0]["churned_by_d30"].mean()
relative_reduction = (not_completed - completed) / not_completed * 100

summary = f"""ONBOARDING IMPACT — model-backed estimate
=========================================
Model AUC (D30 churn prediction): {auc:.3f}

D30 churn rate, onboarding completed:     {completed*100:.1f}%
D30 churn rate, onboarding NOT completed: {not_completed*100:.1f}%
Observed relative reduction in churn:     {relative_reduction:.1f}%

Interpretation for your resume/report:
Users who complete onboarding churn at a {relative_reduction:.0f}% lower rate by Day 30
in this dataset. This is the number to cite instead of an unverified "20%" —
swap in your real dataset's numbers when you run this against actual data.
"""
with open(OUT + "onboarding_impact_estimate.txt", "w") as f:
    f.write(summary)

print(summary)
print("Cohort matrix:\n", cohort_matrix)
print("\nCLTV by channel:\n", cltv)
