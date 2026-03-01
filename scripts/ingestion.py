import pandas as pd
import mysql.connector
import yaml
from datetime import datetime

def run_ingestion():
    # Load config
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    db = config["database"]
    pipeline = config["pipeline"]

    # Connect to MySQL
    conn = mysql.connector.connect(
        host=db["host"],
        user=db["user"],
        password=db["password"],
        database=db["name"]
    )
    cursor = conn.cursor()

    # Check last loaded date
    cursor.execute("SELECT last_loaded_date FROM pipeline_status ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    last_loaded_date = row[0] if row else None
    print(f"Last loaded date: {last_loaded_date}")

    # Read CSV
    df = pd.read_csv(pipeline["csv_path"], dayfirst=True)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"], dayfirst=True)

    # Filter only new rows
    if last_loaded_date:
        df = df[df["invoice_date"] > pd.Timestamp(last_loaded_date)]

    print(f"Rows to insert: {len(df)}")

    # Insert rows
    inserted = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO transactions 
                (transaction_id, invoice_date, customer_id, gender, age, category, quantity, price, payment_method, shopping_mall)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row["invoice_no"],
                row["invoice_date"].date(),
                row["customer_id"],
                row["gender"],
                int(row["age"]),
                row["category"],
                int(row["quantity"]),
                float(row["price"]),
                row["payment_method"],
                row["shopping_mall"]
            ))
            inserted += 1
        except mysql.connector.errors.IntegrityError:
            pass

    conn.commit()

    # Update pipeline_status
    max_date = df["invoice_date"].max().date() if not df.empty else last_loaded_date
    cursor.execute("""
        INSERT INTO pipeline_status (last_loaded_date, rows_loaded)
        VALUES (%s, %s)
    """, (max_date, inserted))
    conn.commit()

    print(f"Ingestion complete. {inserted} rows inserted. Last date: {max_date}")
    cursor.close()
    conn.close()

if __name__ == "__main__":
    run_ingestion()