"""
Business insight generator for cards and narrative section.
"""

from __future__ import annotations

from typing import List, Dict
import pandas as pd

from dashboard.utils import add_customer_segment


def build_insights(df: pd.DataFrame) -> List[Dict[str, str]]:
    """Generate concise insights from filtered data."""
    if df.empty:
        return [{"title": "No Data", "detail": "No records match selected filters."}]

    insights = []

    spend_by_gender = df.groupby("gender")["purchase_amount"].sum().sort_values(ascending=False)
    top_gender = spend_by_gender.index[0]
    insights.append(
        {
            "title": "Top Spending Gender",
            "detail": f"{top_gender} customers generate the highest revenue (${spend_by_gender.iloc[0]:,.0f}).",
        }
    )

    top_product = (
        df.groupby("item_purchased")
        .agg(avg_rating=("review_rating", "mean"), orders=("customer_id", "count"))
        .sort_values(["avg_rating", "orders"], ascending=[False, False])
        .head(1)
    )
    if not top_product.empty:
        product_name = top_product.index[0]
        insights.append(
            {
                "title": "High Performing Product",
                "detail": f"{product_name} leads with strong rating ({top_product['avg_rating'].iloc[0]:.2f}) and demand.",
            }
        )

    segmented = add_customer_segment(df)
    segment_rev = (
        segmented.groupby("customer_segment", observed=False)["purchase_amount"]
        .sum()
        .sort_values(ascending=False)
    )
    best_segment = segment_rev.index[0]
    insights.append(
        {
            "title": "Most Profitable Segment",
            "detail": f"{best_segment} customers contribute the highest segment revenue (${segment_rev.iloc[0]:,.0f}).",
        }
    )

    discount_yes = df[df["discount_applied"] == "Yes"]["purchase_amount"].mean()
    discount_no = df[df["discount_applied"] == "No"]["purchase_amount"].mean()
    verdict = "increase" if discount_yes > discount_no else "reduce"
    insights.append(
        {
            "title": "Discount Effectiveness",
            "detail": f"Discounted purchases {verdict} average spend (${discount_yes:.2f} vs ${discount_no:.2f}).",
        }
    )

    repeat_rate = (df["previous_purchases"] > 5).mean() * 100
    sub_repeat_rate = (
        (df[df["subscription_status"] == "Yes"]["previous_purchases"] > 5).mean() * 100
    )
    insights.append(
        {
            "title": "Retention and Subscription Trend",
            "detail": f"Overall repeat buyers: {repeat_rate:.1f}%. Among subscribers: {sub_repeat_rate:.1f}%.",
        }
    )

    return insights

