"""
Consumer Shopping Behavior Analytics Dashboard (Flask entrypoint).
"""

from __future__ import annotations

from io import StringIO

from flask import Flask, jsonify, make_response, render_template, request

from dashboard.charts import build_charts
from dashboard.config import settings
from dashboard.database import check_connection, get_engine, load_customer_data
from dashboard.filters import apply_filters, parse_filters
from dashboard.insights import build_insights
from dashboard.utils import apply_notebook_transformations, compute_kpis, get_filter_values


app = Flask(__name__)
app.config["SECRET_KEY"] = settings.secret_key


def get_db_engine():
    """Create engine safely so deployment misconfig does not crash app startup."""
    try:
        return get_engine(), ""
    except Exception as exc:
        return None, str(exc)


def get_prepared_data(engine):
    """Load and transform dataframe from PostgreSQL table."""
    raw_df = load_customer_data(engine)
    return apply_notebook_transformations(raw_df)


@app.route("/")
def index():
    """Main dashboard page."""
    engine, engine_error = get_db_engine()
    if engine is None:
        return render_template(
            "index.html",
            error=(
                "Database engine initialization failed. "
                "Check DATABASE_URL/DB_* deployment variables. "
                f"Details: {engine_error}"
            ),
        )

    db_ok, db_error = check_connection(engine)
    if not db_ok:
        # Keep message user-friendly while still helpful for deployment debugging.
        return render_template(
            "index.html",
            error=(
                "Database connection failed. Verify deployment environment variables "
                "(DATABASE_URL or DB_* values) and ensure the cloud DB is reachable. "
                f"Details: {db_error}"
            ),
        )

    data = get_prepared_data(engine)
    selected = parse_filters(request.args)
    filtered = apply_filters(data, selected)

    context = {
        "kpis": compute_kpis(filtered),
        "charts": build_charts(filtered),
        "insights": build_insights(filtered),
        "filters": get_filter_values(data),
        "selected": selected,
        "error": "",
    }
    return render_template("index.html", **context)


@app.route("/insights")
def insights_page():
    """Dedicated insights page."""
    engine, engine_error = get_db_engine()
    if engine is None:
        return render_template(
            "insights.html",
            insights=[
                {
                    "title": "Database Error",
                    "detail": (
                        "Database engine initialization failed. "
                        f"Details: {engine_error}"
                    ),
                }
            ],
        )

    try:
        data = get_prepared_data(engine)
        filtered = apply_filters(data, parse_filters(request.args))
        return render_template("insights.html", insights=build_insights(filtered))
    except Exception as exc:
        return render_template(
            "insights.html",
            insights=[{"title": "Database Error", "detail": str(exc)}],
        )


@app.route("/api/refresh")
def api_refresh():
    """JSON API endpoint for auto-refresh button."""
    engine, engine_error = get_db_engine()
    if engine is None:
        return jsonify({"error": f"Database engine initialization failed: {engine_error}"}), 500

    try:
        data = get_prepared_data(engine)
        filtered = apply_filters(data, parse_filters(request.args))
        return jsonify(
            {
                "kpis": compute_kpis(filtered),
                "insights": build_insights(filtered),
                "record_count": int(filtered.shape[0]),
            }
        )
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/export/csv")
def export_csv():
    """Export filtered data to CSV."""
    engine, engine_error = get_db_engine()
    if engine is None:
        return jsonify({"error": f"Database engine initialization failed: {engine_error}"}), 500

    try:
        data = get_prepared_data(engine)
        filtered = apply_filters(data, parse_filters(request.args))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    csv_buffer = StringIO()
    filtered.to_csv(csv_buffer, index=False)

    response = make_response(csv_buffer.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=filtered_customer_data.csv"
    response.headers["Content-Type"] = "text/csv"
    return response


if __name__ == "__main__":
    app.run(debug=True)

