# OpsPulse — Automated KPI Monitoring & Reporting System

A Python + MySQL automation tool that monitors business KPIs, detects performance anomalies, generates scheduled operational Excel reports, and feeds a live Power BI dashboard — all without manual effort.

---

## Project Overview

Companies need to monitor key performance indicators continuously, detect issues early, and report results efficiently. Manual reporting is slow and error-prone. OpsPulse automates the entire workflow — from data ingestion to KPI calculation, Excel report generation, and live dashboard updates — simulating a real-world operational BI system.

---

## Live Dashboard

[View Power BI Dashboard](#) <!-- Replace with your published Power BI link -->

---

## Tech Stack

| Layer | Technology |
|---|---|
| Database | MySQL |
| Programming | Python 3 |
| Data Processing | pandas, SQLAlchemy |
| Reporting | openpyxl (Excel) |
| Dashboard | Power BI (via OneDrive/SharePoint) |
| Automation | schedule |
| Configuration | config.yaml (PyYAML) |

---

## Project Structure

```
OpsPulse/
│
├── data/                          # Raw CSV dataset
├── reports/                       # Auto-generated weekly Excel reports
├── scripts/
│   ├── ingestion.py               # Incremental data pipeline
│   ├── kpi_engine.py              # KPI calculation & alert detection
│   ├── reporter.py                # Excel report generation
│   ├── scheduler.py               # Automated weekly pipeline runner
│   └── generate_data.py           # Synthetic data generator for simulation
└── config.yaml                    # Central configuration file
```

---

## Features

**Incremental Data Pipeline** — Tracks the last loaded date in a `pipeline_status` table and only loads new records on each run. No duplicate data, no full reloads.

**KPI Monitoring** — Automatically calculates week-over-week metrics including total revenue, units sold, average order value, customer count, and transaction count.

**Automated Alert Detection** — Flags performance drops based on configurable thresholds. Revenue drop over 10%, units sold drop over 8%, and AOV decline over 5% all trigger alerts in the report.

**Excel Report Generation** — Produces a formatted, color-coded Excel report each week with KPI summary, growth rates, alert status, and top categories by revenue. Each report is saved with a date-stamped filename as a permanent historical record.

**Live Power BI Dashboard** — Exports the full transaction dataset to OneDrive/SharePoint on every pipeline run. Power BI connects directly to this file and refreshes automatically, keeping the dashboard current without any manual steps.

**Scheduled Automation** — Runs the full 4-step pipeline automatically every Monday at 8am using the `schedule` library. In production this would run on a server or via cron job continuously.

**Synthetic Data Generator** — Includes a `generate_data.py` script that appends realistic new weekly transactions to the CSV, simulating a live data feed for testing and demonstration purposes.

**Modular Configuration** — All thresholds, database credentials, file paths, and reporting settings are controlled from a single `config.yaml` file. No hardcoded values in the codebase.

---

## How It Works

Each Monday at 8am the scheduler fires and runs the full pipeline in 4 steps:

1. **Ingestion** — checks `pipeline_status` for the last loaded date and inserts only new transactions into MySQL
2. **KPI Engine** — connects to MySQL via SQLAlchemy, calculates current vs previous week metrics, detects anomalies against configurable thresholds
3. **Reporter** — generates a formatted, color-coded Excel report saved to the `reports/` folder with today's date in the filename
4. **OneDrive Export** — exports the full transaction dataset as a CSV to OneDrive/SharePoint, triggering a Power BI refresh automatically

---

## Architecture Design

The ingestion layer is intentionally **decoupled** from the rest of the pipeline. To connect OpsPulse to a live data source, only `ingestion.py` needs to be updated. The KPI engine, reporter, and scheduler require zero changes regardless of whether data comes from:

- A CSV file (current implementation)
- A live operational database
- A REST API
- A cloud data warehouse like Snowflake or BigQuery

This separation of concerns is a core design principle that makes OpsPulse scalable and maintainable in production environments.

---

## Setup Instructions

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/OpsPulse.git
cd OpsPulse
```

**2. Install dependencies**
```bash
pip install pandas sqlalchemy mysql-connector-python openpyxl schedule pyyaml openai
```

**3. Create the MySQL database**
```sql
CREATE DATABASE ops_pulse_db;
USE ops_pulse_db;

CREATE TABLE transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    invoice_date DATE NOT NULL,
    customer_id VARCHAR(20),
    gender VARCHAR(10),
    age INT,
    category VARCHAR(50),
    quantity INT,
    price DECIMAL(10, 2),
    payment_method VARCHAR(30),
    shopping_mall VARCHAR(50)
);

CREATE TABLE pipeline_status (
    id INT PRIMARY KEY AUTO_INCREMENT,
    last_loaded_date DATE NOT NULL,
    rows_loaded INT,
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**4. Configure config.yaml**
```yaml
database:
  host: localhost
  user: root
  password: YOUR_PASSWORD
  name: ops_pulse_db

pipeline:
  csv_path: data/customer_shopping_data.csv
  date_column: invoice_date

kpi_thresholds:
  revenue_drop_pct: 10
  units_sold_drop_pct: 8
  aov_decline_pct: 5

reporting:
  output_folder: reports/
  frequency: weekly
  top_products_count: 5

onedrive:
  folder: ~/Library/CloudStorage/OneDrive-YourAccount/OpsPulse
  filename: opspulse_export.csv

openai:
  enabled: false
  api_key: YOUR_OPENAI_KEY_HERE
```

**5. Add your dataset**

Place your CSV file in the `data/` folder and update `csv_path` in `config.yaml`. Dataset used: [Customer Shopping Dataset](https://www.kaggle.com/datasets/mehmettahiraslan/customer-shopping-dataset) — 99,457 retail transactions across shopping malls in Istanbul (2021–2023).

**6. (Optional) Generate synthetic data**
```bash
python scripts/generate_data.py
```
This appends 4 weeks of realistic new transactions to the CSV to simulate a live weekly data feed.

**7. Run the pipeline**
```bash
python scripts/scheduler.py
```

---

## Sample Report Output

| KPI | Current Week | Previous Week | Growth % | Status |
|---|---|---|---|---|
| Total Revenue | $2,277,306 | $2,389,533 | -4.7% | 🟢 OK |
| Units Sold | 2,554 | 2,745 | -6.96% | 🟡 WARNING |
| Avg Order Value | $2,635 | $2,655 | -0.73% | 🟢 OK |
| Customer Count | 864 | 900 | — | — |
| Transaction Count | 864 | 900 | — | — |

---

## Real-World Application

In a production environment OpsPulse would be deployed on a cloud server with the scheduler running continuously. The ingestion script would connect to a live operational database or API instead of a CSV. The Power BI dashboard would refresh automatically each week as new data flows in. The only change required would be updating the data source connection in `ingestion.py` — the rest of the system remains identical.