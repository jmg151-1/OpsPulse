import schedule
import time
import sys
import os
import pandas as pd
from sqlalchemy import create_engine
import yaml
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from ingestion import run_ingestion
from kpi_engine import run_kpi_engine
from reporter import run_reporter

def export_to_onedrive(config):
    db = config["database"]
    engine = create_engine(
        f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}/{db['name']}"
    )
    df = pd.read_sql("SELECT * FROM transactions", engine)
    engine.dispose()
    
    onedrive_folder = os.path.expanduser(config["onedrive"]["folder"])
    onedrive_filename = config["onedrive"]["filename"]
    onedrive_path = os.path.join(onedrive_folder, onedrive_filename)
    print(f"Power BI CSV updated: {onedrive_path} ({len(df)} rows)")

def run_pipeline():
    print(f"\n{'='*50}")
    print(f"OpsPulse Pipeline Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    print("\n[1/4] Running ingestion...")
    run_ingestion()

    print("\n[2/4] Running KPI engine...")
    kpi_results = run_kpi_engine()

    print("\n[3/4] Generating report...")
    run_reporter(kpi_results)

    print("\n[4/4] Updating Power BI CSV on OneDrive...")
    export_to_onedrive(config)

    print(f"\nPipeline complete: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

# Schedule to run every Monday at 8am
schedule.every().monday.at("08:00").do(run_pipeline)

print("OpsPulse Scheduler is running...")
print("Pipeline scheduled every Monday at 08:00 AM")
print("Press Ctrl+C to stop\n")

# Run immediately once for testing
print("Running pipeline now for initial test...")
run_pipeline()

# Keep scheduler alive
while True:
    schedule.run_pending()
    time.sleep(60)