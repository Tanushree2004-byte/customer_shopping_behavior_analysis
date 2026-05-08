"""
Filter parsing and dataframe filtering utilities.
"""

from __future__ import annotations

from typing import Dict
import pandas as pd


def parse_filters(args) -> Dict[str, str]:
    """Extract known filter keys from request args."""
    keys = [
        "gender",
        "age_group",
        "category",
        "subscription_status",
        "shipping_type",
        "discount_applied",
        "search",
    ]
    return {key: args.get(key, "").strip() for key in keys}


def apply_filters(df: pd.DataFrame, selected: Dict[str, str]) -> pd.DataFrame:
    """Apply user-selected filters to dataframe."""
    filtered = df.copy()

    for key in [
        "gender",
        "age_group",
        "category",
        "subscription_status",
        "shipping_type",
        "discount_applied",
    ]:
        value = selected.get(key)
        if value:
            filtered = filtered[filtered[key].astype(str) == value]

    # Simple global search over common dimensions.
    search_text = selected.get("search", "")
    if search_text:
        mask = (
            filtered["item_purchased"].astype(str).str.contains(search_text, case=False, na=False)
            | filtered["category"].astype(str).str.contains(search_text, case=False, na=False)
            | filtered["location"].astype(str).str.contains(search_text, case=False, na=False)
        )
        filtered = filtered[mask]

    return filtered

