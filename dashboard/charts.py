"""
Plotly chart generation layer.
"""

from __future__ import annotations

from typing import Dict

import pandas as pd
import plotly.express as px

from dashboard.utils import add_customer_segment


PLOTLY_THEME = "plotly_dark"
CHART_BG = "rgba(19, 25, 45, 0.6)"
PAPER_BG = "rgba(0, 0, 0, 0)"


def _style(fig, title: str):
    """Apply consistent modern styling to all charts."""
    fig.update_layout(
        template=PLOTLY_THEME,
        title=title,
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=CHART_BG,
        legend_title_text="",
        margin=dict(l=20, r=20, t=55, b=20),
    )
    return fig


def build_charts(df: pd.DataFrame) -> Dict[str, str]:
    """Build all dashboard chart HTML snippets."""
    charts = {}

    # Revenue Analytics
    fig = px.bar(df.groupby("gender", as_index=False)["purchase_amount"].sum(), x="gender", y="purchase_amount", color="gender")
    charts["revenue_by_gender"] = _style(fig, "Revenue by Gender").to_html(full_html=False, config={"displaylogo": False})

    fig = px.line(df.groupby("age_group", as_index=False)["purchase_amount"].sum(), x="age_group", y="purchase_amount", markers=True)
    charts["revenue_by_age"] = _style(fig, "Revenue by Age Group").to_html(full_html=False, config={"displaylogo": False})

    fig = px.pie(df.groupby("subscription_status", as_index=False)["purchase_amount"].sum(), names="subscription_status", values="purchase_amount", hole=0.55)
    charts["revenue_by_subscription"] = _style(fig, "Revenue by Subscription Status").to_html(full_html=False, config={"displaylogo": False})

    fig = px.bar(df.groupby("category", as_index=False)["purchase_amount"].sum().sort_values("purchase_amount", ascending=False), x="category", y="purchase_amount", color="category")
    charts["revenue_by_category"] = _style(fig, "Revenue by Category").to_html(full_html=False, config={"displaylogo": False})

    # Product Analytics
    top_rated = (
        df.groupby("item_purchased", as_index=False)
        .agg(avg_rating=("review_rating", "mean"))
        .sort_values("avg_rating", ascending=False)
        .head(10)
    )
    fig = px.bar(top_rated, x="avg_rating", y="item_purchased", orientation="h", color="avg_rating", color_continuous_scale="Tealrose")
    charts["top_rated_products"] = _style(fig, "Top Rated Products").to_html(full_html=False, config={"displaylogo": False})

    top_purchased = (
        df.groupby("item_purchased", as_index=False)["customer_id"]
        .count()
        .rename(columns={"customer_id": "orders"})
        .sort_values("orders", ascending=False)
        .head(10)
    )
    fig = px.pie(top_purchased, names="item_purchased", values="orders")
    charts["top_purchased_products"] = _style(fig, "Top Purchased Products").to_html(full_html=False, config={"displaylogo": False})

    category_orders = (
        df.groupby("category", as_index=False)["customer_id"]
        .count()
        .rename(columns={"customer_id": "orders"})
    )
    fig = px.treemap(category_orders, path=["category"], values="orders", color="orders", color_continuous_scale="Blues")
    charts["category_purchases"] = _style(fig, "Category-wise Purchases").to_html(full_html=False, config={"displaylogo": False})

    discount_stack = (
        df.groupby(["category", "discount_applied"], as_index=False)["customer_id"]
        .count()
        .rename(columns={"customer_id": "orders"})
    )
    fig = px.bar(discount_stack, x="category", y="orders", color="discount_applied", barmode="stack")
    charts["discounted_product_analysis"] = _style(fig, "Discounted Product Analysis").to_html(full_html=False, config={"displaylogo": False})

    # Segmentation
    segmented = add_customer_segment(df)
    segment_dist = (
        segmented.groupby("customer_segment", as_index=False)["customer_id"]
        .count()
        .rename(columns={"customer_id": "customers"})
    )
    fig = px.pie(segment_dist, names="customer_segment", values="customers", hole=0.5)
    charts["customer_segments"] = _style(fig, "Customer Segment Distribution").to_html(full_html=False, config={"displaylogo": False})

    segment_revenue = segmented.groupby("customer_segment", as_index=False)["purchase_amount"].sum()
    fig = px.bar(segment_revenue, x="customer_segment", y="purchase_amount", color="customer_segment")
    charts["segment_revenue"] = _style(fig, "Revenue by Customer Segment").to_html(full_html=False, config={"displaylogo": False})

    # Shipping
    shipping_metrics = df.groupby("shipping_type", as_index=False).agg(
        avg_spending=("purchase_amount", "mean"),
        total_orders=("customer_id", "count"),
    )
    fig = px.bar(shipping_metrics, x="shipping_type", y="avg_spending", color="shipping_type")
    charts["shipping_avg_spending"] = _style(fig, "Shipping Type vs Avg Spending").to_html(full_html=False, config={"displaylogo": False})

    fig = px.bar(shipping_metrics, x="shipping_type", y="total_orders", color="shipping_type")
    charts["shipping_total_orders"] = _style(fig, "Shipping Type vs Total Orders").to_html(full_html=False, config={"displaylogo": False})

    # Subscription
    sub_count = (
        df.groupby("subscription_status", as_index=False)["customer_id"]
        .count()
        .rename(columns={"customer_id": "customers"})
    )
    fig = px.pie(sub_count, names="subscription_status", values="customers", hole=0.45)
    charts["subscribers_vs_non"] = _style(fig, "Subscribers vs Non-Subscribers").to_html(full_html=False, config={"displaylogo": False})

    repeat_sub = (
        df.assign(is_repeat=df["previous_purchases"] > 5)
        .groupby(["subscription_status", "is_repeat"], as_index=False)["customer_id"]
        .count()
        .rename(columns={"customer_id": "customers"})
    )
    fig = px.bar(repeat_sub, x="subscription_status", y="customers", color="is_repeat", barmode="group")
    charts["repeat_vs_subscribers"] = _style(fig, "Repeat Buyers vs Subscription").to_html(full_html=False, config={"displaylogo": False})

    sub_rev = df.groupby("subscription_status", as_index=False)["purchase_amount"].sum()
    fig = px.bar(sub_rev, x="subscription_status", y="purchase_amount", color="subscription_status")
    charts["subscription_revenue"] = _style(fig, "Revenue Contribution by Subscription").to_html(full_html=False, config={"displaylogo": False})

    # Heatmaps
    pivot_age_category = pd.pivot_table(
        df,
        values="purchase_amount",
        index="age_group",
        columns="category",
        aggfunc="sum",
        fill_value=0,
    )
    fig = px.imshow(pivot_age_category, text_auto=True, aspect="auto", color_continuous_scale="Viridis")
    charts["heatmap_age_category"] = _style(fig, "Heatmap: Age Group vs Category").to_html(full_html=False, config={"displaylogo": False})

    pivot_gender_category = pd.pivot_table(
        df,
        values="purchase_amount",
        index="gender",
        columns="category",
        aggfunc="sum",
        fill_value=0,
    )
    fig = px.imshow(pivot_gender_category, text_auto=True, aspect="auto", color_continuous_scale="Magma")
    charts["heatmap_gender_category"] = _style(fig, "Heatmap: Gender vs Category").to_html(full_html=False, config={"displaylogo": False})

    pivot_discount_behavior = pd.pivot_table(
        df,
        values="purchase_amount",
        index="discount_applied",
        columns="subscription_status",
        aggfunc="mean",
        fill_value=0,
    )
    fig = px.imshow(pivot_discount_behavior, text_auto=True, aspect="auto", color_continuous_scale="Cividis")
    charts["heatmap_discount_behavior"] = _style(fig, "Heatmap: Discount vs Purchase Behavior").to_html(full_html=False, config={"displaylogo": False})

    return charts

