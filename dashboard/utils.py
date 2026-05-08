"""
Shared utility helpers for data preparation and KPI calculations.
"""

from __future__ import annotations

from typing import Dict, List

import pandas as pd


FREQUENCY_MAP = {
    "Fortnightly": 14,
    "Weekly": 7,
    "Monthly": 30,
    "Quarterly": 90,
    "Bi-Weekly": 14,
    "Annually": 365,
    "Every 3 Months": 90,
}

AGE_LABELS = ["Young Adult", "Adult", "Middle-aged", "Senior"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize incoming table column names to snake_case.
    Reuses logic from your notebook.
    """
    clean_df = df.copy()
    clean_df.columns = clean_df.columns.str.strip().str.lower().str.replace(" ", "_")
    clean_df.columns = clean_df.columns.str.replace(r"[()]", "", regex=True)
    clean_df.columns = clean_df.columns.str.replace("-", "_")
    clean_df = clean_df.rename(columns={"purchase_amount_usd": "purchase_amount"})
    return clean_df


def apply_notebook_transformations(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply core transformations already done in notebook:
    - fill review rating nulls category-wise
    - create age_group
    - map frequency_of_purchases to purchase_frequency_days
    - drop promo_code_used if redundant
    """
    data = normalize_columns(df)

    if "review_rating" in data.columns and "category" in data.columns:
        data["review_rating"] = data.groupby("category")["review_rating"].transform(
            lambda s: s.fillna(s.median())
        )

    if "age" in data.columns and "age_group" not in data.columns:
        data["age_group"] = pd.qcut(data["age"], q=4, labels=AGE_LABELS)

    if "frequency_of_purchases" in data.columns:
        data["purchase_frequency_days"] = data["frequency_of_purchases"].map(FREQUENCY_MAP)

    if "promo_code_used" in data.columns and "discount_applied" in data.columns:
        same_values = (data["discount_applied"] == data["promo_code_used"]).all()
        if same_values:
            data = data.drop(columns=["promo_code_used"])

    return data


def add_customer_segment(df: pd.DataFrame) -> pd.DataFrame:
    """Segment users into New, Returning, Loyal using notebook SQL logic."""
    segmented = df.copy()
    segmented["customer_segment"] = pd.cut(
        segmented["previous_purchases"],
        bins=[0, 1, 10, float("inf")],
        labels=["New", "Returning", "Loyal"],
        include_lowest=True,
    )
    return segmented


def compute_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Compute top KPI metrics for overview cards."""
    total_customers = int(df["customer_id"].nunique()) if not df.empty else 0
    total_revenue = float(df["purchase_amount"].sum()) if not df.empty else 0.0
    avg_purchase = float(df["purchase_amount"].mean()) if not df.empty else 0.0
    avg_rating = float(df["review_rating"].mean()) if not df.empty else 0.0
    repeat_buyers_pct = (
        float((df["previous_purchases"] > 5).mean() * 100) if not df.empty else 0.0
    )
    subscribers_pct = (
        float((df["subscription_status"].str.lower() == "yes").mean() * 100)
        if not df.empty
        else 0.0
    )
    discount_usage_pct = (
        float((df["discount_applied"].str.lower() == "yes").mean() * 100)
        if not df.empty
        else 0.0
    )

    return {
        "total_customers": total_customers,
        "total_revenue": round(total_revenue, 2),
        "avg_purchase_amount": round(avg_purchase, 2),
        "avg_review_rating": round(avg_rating, 2),
        "repeat_buyers_pct": round(repeat_buyers_pct, 2),
        "subscribers_pct": round(subscribers_pct, 2),
        "discount_usage_pct": round(discount_usage_pct, 2),
    }


def get_filter_values(df: pd.DataFrame) -> Dict[str, List[str]]:
    """Get dropdown values for all dashboard filters."""
    return {
        "gender": sorted(df["gender"].dropna().unique().tolist()),
        "age_group": sorted(df["age_group"].dropna().astype(str).unique().tolist()),
        "category": sorted(df["category"].dropna().unique().tolist()),
        "subscription_status": sorted(df["subscription_status"].dropna().unique().tolist()),
        "shipping_type": sorted(df["shipping_type"].dropna().unique().tolist()),
        "discount_applied": sorted(df["discount_applied"].dropna().unique().tolist()),
    }

