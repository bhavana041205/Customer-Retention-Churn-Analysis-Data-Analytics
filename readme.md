# Customer Retention & Churn Analysis

An end-to-end customer analytics project focused on understanding **retention, churn, customer lifetime value (CLTV), and churn prediction** for a subscription-based business.

The project uses **SQL, Python, Machine Learning, and Power BI** to transform customer activity and subscription data into actionable retention insights.

---

## 📌 Project Overview

Customer churn is a major challenge for subscription businesses. Losing customers reduces recurring revenue and increases the cost of acquiring new customers.

This project analyzes a synthetic dataset of **3,000 users** to understand:

* How customer retention changes after signup
* Where users drop off during the onboarding funnel
* Which customer groups have higher churn
* Which acquisition channels generate higher-value customers
* Which users are more likely to churn
* How onboarding performance is associated with customer retention

The goal is not only to describe customer behavior, but to identify **specific areas where a business can take action to improve retention and customer value**.

---

## 📊 Key Results

| Metric                   |                                                        Result |
| ------------------------ | ------------------------------------------------------------: |
| Users analyzed           |                                                     **3,000** |
| Activity events          |                                                     **118K+** |
| Onboarding impact        | **~47% lower Day-30 churn** among users completing onboarding |
| Best acquisition channel |                                                 **Referrals** |
| CLTV advantage           |                           **23% higher CLTV** vs. Paid Social |
| Churn model              |                                       **Logistic Regression** |
| Model performance        |                                              **0.63 ROC-AUC** |
| Main funnel drop-off     |                            **Signup → Onboarding completion** |

### Key Business Insights

**Onboarding:**
Users who completed onboarding showed approximately **47% lower Day-30 churn**, indicating that improving early product activation could be a major retention lever.

**Acquisition:**
Referral users generated approximately **23% higher CLTV than Paid Social users**, suggesting an opportunity to shift part of the acquisition strategy toward referral programs.

**Churn Prediction:**
The Logistic Regression model achieved a **0.63 ROC-AUC** on the held-out test set, demonstrating useful signal for ranking customers by churn risk while leaving room for further model improvement.

**Funnel:**
The largest user drop-off occurs between **signup and onboarding completion**, making this an important stage for product and customer-success improvements.

---

## 🔄 Project Workflow

```text
Synthetic Customer Data
          ↓
   Data Generation
          ↓
   SQL Analysis
          ↓
Retention & Cohort Analysis
          ↓
     Python Analysis
          ↓
  CLTV + Churn Prediction
          ↓
   Business Segmentation
          ↓
     Power BI Dashboard
          ↓
  Retention Recommendations
```

---

## 🗂️ Project Structure

```text
Customer-Retention-Churn-Analysis/
│
├── data/
│   ├── users.csv
│   ├── events.csv
│   └── subscriptions.csv
│
├── python/
│   ├── 01_generate_data.py
│   └── 02_analysis.py
│
├── sql/
│   └── retention_queries.sql
│
├── outputs/
│   ├── cohort_retention_matrix.csv
│   ├── retention_heatmap.png
│   ├── cltv_by_channel.csv
│   ├── churn_risk_scores.csv
│   └── onboarding_impact_estimate.txt
│
├── powerbi/
│   ├── dashboard_preview.png
│   └── HOW_TO_BUILD_PBIX.md
│
├── requirements.txt
└── README.md
```

---

## 🧾 Dataset

The project uses a **synthetically generated dataset of 3,000 users** designed to represent a realistic subscription business.

### Users

`users.csv`

Contains customer-level information such as:

* User ID
* Signup date
* Acquisition channel
* Subscription plan
* Onboarding completion

### Events

`events.csv`

Contains more than **118,000 user activity events**, including:

* Logins
* Feature usage
* Activity dates

These events are used to measure customer engagement and retention.

### Subscriptions

`subscriptions.csv`

Contains subscription and revenue information including:

* Subscription plan
* Payment information
* Cancellation status
* Revenue-related fields

---

## 🐍 Python Analysis

### `01_generate_data.py`

Generates the synthetic customer dataset used throughout the project.

The script creates:

* 3,000 users
* User activity events
* Subscription records

Creating the dataset programmatically makes the analysis **reproducible** and allows the complete project to be regenerated from scratch.

### `02_analysis.py`

Performs the main analytical and machine-learning workflow.

The script:

* Calculates cohort retention
* Generates the retention heatmap
* Calculates CLTV by acquisition channel
* Compares onboarding and churn behavior
* Trains the churn prediction model
* Generates customer-level churn risk scores

---

## 🗄️ SQL Analysis

### `retention_queries.sql`

SQL queries are used to calculate:

* Day 1 retention
* Day 7 retention
* Day 30 retention
* Day 90 retention
* Monthly cohort retention
* Customer Lifetime Value

The SQL analysis demonstrates how customer behavior can be analyzed directly from structured business data.

---

## 🤖 Churn Prediction Model

A **Logistic Regression** model is used to predict the probability of 30-day customer churn.

The model uses information available at signup to avoid **future data leakage**.

### Model workflow

```text
Customer Features
       ↓
Train/Test Split
       ↓
Logistic Regression
       ↓
Churn Probability
       ↓
Customer Risk Score
```

The dataset is divided into:

* **75% training data**
* **25% test data**

The model is evaluated only on the unseen test set.

### Model Performance

**ROC-AUC: 0.63**

An AUC of 0.63 indicates that the model performs better than random classification and provides useful initial signal for identifying customers with higher churn risk.

The resulting customer-level predictions are stored in:

`churn_risk_scores.csv`

---

## 📈 Retention & Cohort Analysis

Customers are grouped into monthly signup cohorts and tracked across:

* Day 1
* Day 7
* Day 30
* Day 90

The resulting cohort matrix is stored in:

`cohort_retention_matrix.csv`

A visual representation is provided in:

`retention_heatmap.png`

This allows retention patterns and early customer drop-offs to be compared across different signup cohorts.

---

## 💰 Customer Lifetime Value

Customer Lifetime Value (CLTV) is calculated to understand the long-term value generated by customers from different acquisition channels.

The results are stored in:

`cltv_by_channel.csv`

The analysis found that **referral customers generated approximately 23% higher CLTV than Paid Social customers**, highlighting the potential value of referral-led acquisition.

---

## 🚀 Onboarding Impact

The project compares customers who completed onboarding with those who did not.

Users completing onboarding showed approximately:

### **47% lower Day-30 churn**

This finding identifies onboarding as a potential high-impact retention lever.

The calculated result is stored in:

`onboarding_impact_estimate.txt`

The result is based on the project dataset rather than an assumed improvement percentage.

---

## 📊 Power BI Dashboard

Power BI is used as the final business intelligence layer to present the analysis in an interactive format.

The dashboard brings together:

* Customer overview
* Retention trends
* Churn analysis
* Cohort performance
* Acquisition-channel performance
* CLTV
* Customer risk information

### Dashboard Preview

![Customer Retention Dashboard](powerbi/dashboard_preview.png)

The `HOW_TO_BUILD_PBIX.md` file contains the steps required to recreate the interactive Power BI dashboard in Power BI Desktop.

---

## 🛠️ Technology Stack

**Data Analysis:** Python, Pandas, NumPy
**Machine Learning:** Scikit-learn, Logistic Regression
**Database Analysis:** SQL
**Visualization:** Matplotlib, Power BI
**Data Storage:** CSV
**Version Control:** GitHub

---

## ▶️ How to Run

Install the required Python libraries:

```bash
pip install -r requirements.txt
```

Generate the datasets:

```bash
python python/01_generate_data.py
```

Run the analysis:

```bash
python python/02_analysis.py
```

The analysis generates the files inside the `outputs/` directory.

---

## 💡 Business Recommendations

Based on the analysis, the project recommends:

1. **Improve onboarding completion** to reduce early-stage customer churn.
2. **Invest in referral acquisition** given its higher observed CLTV compared with Paid Social.
3. **Use churn-risk scores** to prioritize customers for proactive retention campaigns.
4. **Monitor D1/D7/D30/D90 retention** to identify early engagement problems.
5. **Continue improving the prediction model** with additional behavioral and subscription features.

---

## 🎯 Skills Demonstrated

* Customer Retention Analysis
* Churn Analysis
* Cohort Analysis
* Customer Lifetime Value
* Funnel Analysis
* Machine Learning
* Logistic Regression
* SQL Analytics
* Python Analytics
* Power BI Dashboarding
* Business Insight Generation
* Data-Driven Product Recommendations

---

## 👤 Project Focus

This project demonstrates an end-to-end approach to turning customer data into **product and business decisions**:

**Data → Analysis → Prediction → Visualization → Action**

