import pandas as pd
import yaml
from sqlalchemy import create_engine

def run_kpi_engine():
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    db = config["database"]
    thresholds = config["kpi_thresholds"]
    top_n = config["reporting"]["top_products_count"]

    # Connect to MySQL using SQLAlchemy
    engine = create_engine(
        f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}/{db['name']}"
    )

    # Pull data into pandas
    query = "SELECT * FROM transactions"
    df = pd.read_sql(query, engine)
    engine.dispose()

    # Convert date column
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])

    # Calculate revenue
    df["revenue"] = df["quantity"] * df["price"]

    # Get current and previous week
    max_date = df["invoice_date"].max()
    current_week_start = max_date - pd.Timedelta(days=6)
    previous_week_start = current_week_start - pd.Timedelta(days=7)
    previous_week_end = current_week_start - pd.Timedelta(days=1)

    current = df[df["invoice_date"] >= current_week_start]
    previous = df[(df["invoice_date"] >= previous_week_start) &
                  (df["invoice_date"] <= previous_week_end)]

    # Calculate KPIs
    def calc_kpis(data):
        return {
            "total_revenue": round(data["revenue"].sum(), 2),
            "units_sold": int(data["quantity"].sum()),
            "aov": round(data["revenue"].mean(), 2) if len(data) > 0 else 0,
            "customer_count": data["customer_id"].nunique(),
            "transaction_count": len(data)
        }

    current_kpis = calc_kpis(current)
    previous_kpis = calc_kpis(previous)

    # Growth rates
    def growth_rate(current_val, previous_val):
        if previous_val == 0:
            return 0
        return round(((current_val - previous_val) / previous_val) * 100, 2)

    growth = {
        "revenue_growth": growth_rate(current_kpis["total_revenue"], previous_kpis["total_revenue"]),
        "units_growth": growth_rate(current_kpis["units_sold"], previous_kpis["units_sold"]),
        "aov_growth": growth_rate(current_kpis["aov"], previous_kpis["aov"])
    }

    # Top products
    top_products = (
        current.groupby("category")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    top_products.columns = ["Category", "Revenue"]
    top_products["Revenue"] = top_products["Revenue"].round(2)

    # Alerts
    alerts = []
    if growth["revenue_growth"] <= -thresholds["revenue_drop_pct"]:
        alerts.append(f"ALERT: Revenue dropped {abs(growth['revenue_growth'])}% vs last week")
    if growth["units_growth"] <= -thresholds["units_sold_drop_pct"]:
        alerts.append(f"ALERT: Units sold dropped {abs(growth['units_growth'])}% vs last week")
    if growth["aov_growth"] <= -thresholds["aov_decline_pct"]:
        alerts.append(f"ALERT: AOV declined {abs(growth['aov_growth'])}% vs last week")

    if not alerts:
        alerts.append("No alerts — all KPIs within normal range.")

    return {
        "current_kpis": current_kpis,
        "previous_kpis": previous_kpis,
        "growth": growth,
        "top_products": top_products,
        "alerts": alerts,
        "current_week_start": current_week_start.date(),
        "max_date": max_date.date()
    }

if __name__ == "__main__":
    results = run_kpi_engine()
    print("\n--- CURRENT WEEK KPIs ---")
    for k, v in results["current_kpis"].items():
        print(f"  {k}: {v}")
    print("\n--- GROWTH RATES ---")
    for k, v in results["growth"].items():
        print(f"  {k}: {v}%")
    print("\n--- ALERTS ---")
    for alert in results["alerts"]:
        print(f"  {alert}")