import schedule
import time
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from ingestion import run_ingestion
from kpi_engine import run_kpi_engine
from reporter import run_reporter

def run_pipeline():
    print(f"\n{'='*50}")
    print(f"OpsPulse Pipeline Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    print("\n[1/3] Running ingestion...")
    run_ingestion()

    print("\n[2/3] Running KPI engine...")
    kpi_results = run_kpi_engine()

    print("\n[3/3] Generating report...")
    run_reporter(kpi_results)

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