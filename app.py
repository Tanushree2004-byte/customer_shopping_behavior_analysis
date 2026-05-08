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

engine = get_engine()


def get_prepared_data():
    """Load and transform dataframe from PostgreSQL table."""
    raw_df = load_customer_data(engine)
    return apply_notebook_transformations(raw_df)


@app.route("/")
def index():
    """Main dashboard page."""
    db_ok = check_connection(engine)
    if not db_ok:
        return render_template("index.html", error="Database connection failed. Check your .env values.")

    data = get_prepared_data()
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
    data = get_prepared_data()
    filtered = apply_filters(data, parse_filters(request.args))
    return render_template("insights.html", insights=build_insights(filtered))


@app.route("/api/refresh")
def api_refresh():
    """JSON API endpoint for auto-refresh button."""
    data = get_prepared_data()
    filtered = apply_filters(data, parse_filters(request.args))
    return jsonify(
        {
            "kpis": compute_kpis(filtered),
            "insights": build_insights(filtered),
            "record_count": int(filtered.shape[0]),
        }
    )


@app.route("/export/csv")
def export_csv():
    """Export filtered data to CSV."""
    data = get_prepared_data()
    filtered = apply_filters(data, parse_filters(request.args))

    csv_buffer = StringIO()
    filtered.to_csv(csv_buffer, index=False)

    response = make_response(csv_buffer.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=filtered_customer_data.csv"
    response.headers["Content-Type"] = "text/csv"
    return response


if __name__ == "__main__":
    app.run(debug=True)

