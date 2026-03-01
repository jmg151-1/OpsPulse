# OpsPulse — Automated KPI Monitoring & Reporting System

A Python + MySQL automation tool that monitors business KPIs, detects performance anomalies, and generates scheduled operational Excel reports without manual effort.

---

## Project Overview

Companies need to monitor key performance indicators continuously, detect issues early, and report results efficiently. Manual reporting is slow and error-prone. OpsPulse automates the entire workflow — from data ingestion to KPI calculation to report generation — simulating a real-world operational BI system.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Database | MySQL |
| Programming | Python 3 |
| Data Processing | pandas, SQLAlchemy |
| Reporting | openpyxl (Excel) |
| Automation | schedule |
| Configuration | config.yaml (PyYAML) |

---

## Project Structure
```
OpsPulse/
│
├── data/                          # Raw CSV dataset
├── reports/                       # Auto-generated Excel reports
├── scripts/
│   ├── ingestion.py               # Incremental data pipeline
│   ├── kpi_engine.py              # KPI calculation & alert detection
│   ├── reporter.py                # Excel report generation
│   └── scheduler.py              # Automated weekly pipeline runner
└── config.yaml                    # Central configuration file
```

---

## Features

**Incremental Data Pipeline** — Tracks the last loaded date in a pipeline_status table and only loads new records on each run. No duplicate data, no full reloads.

**KPI Monitoring** — Automatically calculates week-over-week metrics including total revenue, units sold, average order value, customer count, and transaction count.

**Automated Alert Detection** — Flags performance drops based on configurable thresholds. Revenue drop over 10%, units sold drop over 8%, and AOV decline over 5% all trigger alerts in the report.

**Excel Report Generation** — Produces a formatted, color-coded Excel report with KPI summary, growth rates, alert status, and top categories by revenue.

**Scheduled Automation** — Runs the full pipeline automatically every Monday at 8am using the schedule library. In production this would run on a server or via cron job continuously.

**Modular Configuration** — All thresholds, database credentials, file paths, and reporting settings are controlled from a single config.yaml file. No hardcoded values in the codebase.

---

## How It Works

1. The scheduler triggers the pipeline every Monday at 8am
2. The ingestion script checks the last loaded date and pulls only new transactions
3. The KPI engine connects to MySQL, calculates current vs previous week metrics, and detects anomalies
4. The reporter generates a formatted Excel file saved to the reports folder
5. The pipeline_status table is updated with the new last loaded date

---

## Setup Instructions

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/OpsPulse.git
cd OpsPulse
```

**2. Install dependencies**
```bash
pip install pandas sqlalchemy mysql-connector-python openpyxl schedule pyyaml
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
```

**5. Add your dataset**

Place your CSV file in the `data/` folder and update the `csv_path` in `config.yaml`.

**6. Run the pipeline**
```bash
python scripts/scheduler.py
```

---

## Sample Report Output

| KPI | Current Week | Previous Week | Growth % | Status |
|---|---|---|---|---|
| Total Revenue | 2,277,306 | 2,389,533 | -4.7% | 🟢 OK |
| Units Sold | 2,554 | 2,745 | -6.96% | 🟡 WARNING |
| Avg Order Value | 2,635 | 2,655 | -0.73% | 🟢 OK |

---

## Real-World Scalability

The ingestion layer is intentionally decoupled from the rest of the pipeline. To connect OpsPulse to a live data source, only `ingestion.py` needs to be updated. The KPI engine and reporter require zero changes regardless of whether data comes from a CSV, a live database, an API, or a cloud data warehouse like Snowflake or BigQuery.

---

## Dataset

Customer Shopping Dataset from Kaggle — 99,457 retail transactions across shopping malls in Istanbul (2021–2023).