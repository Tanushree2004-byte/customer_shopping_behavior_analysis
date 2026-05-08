# Consumer Shopping Behavior Analytics Dashboard

Professional full-stack analytics dashboard built with Flask, PostgreSQL, Pandas, Plotly, Bootstrap, and JavaScript.

## Project Overview

This project converts customer shopping data into a business intelligence dashboard experience similar to modern SaaS analytics tools.  
It reuses and operationalizes the original notebook + SQL analysis into a production-style web app.

## Objective

- Analyze consumer shopping behavior
- Track revenue, product performance, customer segments, shipping trends, and subscription impact
- Provide interactive filtering and insight generation for business decisions

## Technologies Used

- Backend: `Flask`, `SQLAlchemy`, `PostgreSQL`
- Data Processing: `Pandas`
- Visualization: `Plotly`
- Frontend: `HTML5`, `CSS3`, `Bootstrap 5`, `JavaScript`

## Project Architecture

```text
customer_behavior/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── dashboard/
│   ├── __init__.py
│   ├── database.py
│   ├── charts.py
│   ├── insights.py
│   ├── filters.py
│   ├── utils.py
│   └── config.py
├── templates/
├── static/
├── screenshots/
├── notebooks/
└── data/
```

## Key Features

- Overview KPI cards (revenue, customers, spend, ratings, repeat buyers, subscribers, discount usage)
- Revenue, product, customer segment, shipping, and subscription analytics
- 3 heatmap analytics views
- Dynamic filters across all major dimensions
- Search support (product/category/location)
- Export filtered data to CSV
- Auto-refresh button
- Interactive Plotly visualizations with hover and legends
- Responsive modern dashboard UI with dark glassmorphism style

## Data and Existing Analysis Reused

- Original dataset: `data/customer_shopping_behavior.csv`
- Original notebook: `notebooks/analysis.ipynb`
- Original SQL analysis: `data/analysis_queries.sql`

Reused transformations include:
- Column normalization to snake_case
- Missing `review_rating` imputation by category median
- `age_group` creation
- Purchase frequency day mapping
- Customer segmentation (`New`, `Returning`, `Loyal`)

## Setup Instructions

1. Open terminal inside `customer_behavior/`.
2. Create virtual environment (recommended):
   - Windows: `python -m venv .venv && .\.venv\Scripts\activate`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Create `.env` file:

```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=consumer_db
DB_TABLE=customer
SECRET_KEY=replace-with-secure-key
```

5. Ensure PostgreSQL has table `customer` populated with cleaned dataset.
6. Run app:
   - `python app.py`
7. Open browser:
   - `http://127.0.0.1:5000`

## Screenshots

Add dashboard screenshots in `screenshots/` and reference them here for portfolio presentation.

## Business Impact

- Helps teams quickly identify profitable customer groups
- Improves product and discount strategy decisions
- Supports retention and subscription planning
- Reduces manual reporting effort through interactive analytics

## Future Enhancements

- Role-based login for analysts/managers
- Scheduled report emails
- Forecasting module for revenue and demand
- API layer for external BI integrations

