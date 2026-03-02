import pandas as pd
import numpy as np
import random
import yaml
from datetime import datetime, timedelta

# Load config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

csv_path = config["pipeline"]["csv_path"]

# Load existing data
df = pd.read_csv(csv_path, dayfirst=True)
df["invoice_date"] = pd.to_datetime(df["invoice_date"], dayfirst=True)

# Get the last date in the dataset
last_date = df["invoice_date"].max()
print(f"Last date in dataset: {last_date.date()}")

# Reference values from existing data
categories = df["category"].unique().tolist()
genders = df["gender"].unique().tolist()
payment_methods = df["payment_method"].unique().tolist()
shopping_malls = df["shopping_mall"].unique().tolist()
price_ranges = {
    "Clothing": (300, 2000),
    "Shoes": (500, 3500),
    "Technology": (1000, 8000),
    "Cosmetics": (50, 500),
    "Toys": (20, 300),
    "Food & Beverage": (10, 200),
    "Books": (10, 150),
    "Souvenir": (10, 100)
}

# Generate new rows
def generate_invoice_no(existing):
    while True:
        num = f"I{random.randint(100000, 999999)}"
        if num not in existing:
            return num

def generate_customer_id():
    return f"C{random.randint(100000, 999999)}"

existing_invoices = set(df["invoice_no"].tolist())
new_rows = []

# Generate 4 weeks of new data
weeks_to_generate = 4
rows_per_week = random.randint(800, 1200)

for week in range(1, weeks_to_generate + 1):
    week_start = last_date + timedelta(weeks=week)
    for _ in range(rows_per_week):
        invoice_date = week_start + timedelta(days=random.randint(0, 6))
        category = random.choice(categories)
        price_min, price_max = price_ranges.get(category, (100, 1000))
        quantity = random.randint(1, 5)
        price = round(random.uniform(price_min, price_max), 2)
        age = random.randint(18, 70)
        invoice_no = generate_invoice_no(existing_invoices)
        existing_invoices.add(invoice_no)

        new_rows.append({
            "invoice_no": invoice_no,
            "customer_id": generate_customer_id(),
            "gender": random.choice(genders),
            "age": age,
            "category": category,
            "quantity": quantity,
            "price": price,
            "payment_method": random.choice(payment_methods),
            "invoice_date": invoice_date.strftime("%d/%m/%Y"),
            "shopping_mall": random.choice(shopping_malls)
        })

new_df = pd.DataFrame(new_rows)
print(f"Generated {len(new_df)} new rows from {last_date.date()} to {(last_date + timedelta(weeks=weeks_to_generate)).date()}")

# Append to existing CSV
combined = pd.concat([df.assign(invoice_date=df["invoice_date"].dt.strftime("%d/%m/%Y")), new_df], ignore_index=True)
combined.to_csv(csv_path, index=False)
print(f"CSV updated. Total rows: {len(combined)}")