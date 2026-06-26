from __future__ import annotations

import json
import random
import sqlite3
from pathlib import Path

import pandas as pd

RANDOM_SEED = 42
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_SAMPLE_DIR = PROJECT_ROOT / "data" / "sample"
SQLITE_DIR = PROJECT_ROOT / "data" / "sqlite"


def build_customers() -> pd.DataFrame:
    random.seed(RANDOM_SEED)
    rows = [
        {
            "customer_id": "C001",
            "first_name": " Ava ",
            "last_name": "MARTIN",
            "email": "ava.martin@example.com",
            "signup_date": "2023-01-15",
            "region": "north",
            "customer_segment": "Enterprise",
            "lifetime_value": 18250.75,
            "churn_risk_score": 0.12,
        },
        {
            "customer_id": "C002",
            "first_name": "liam",
            "last_name": "Chen",
            "email": "",
            "signup_date": "2023-02-04",
            "region": " West ",
            "customer_segment": "mid-market",
            "lifetime_value": None,
            "churn_risk_score": 0.38,
        },
        {
            "customer_id": "C003",
            "first_name": "Noah",
            "last_name": "Patel",
            "email": "not-an-email",
            "signup_date": "2023-03-11",
            "region": "SOUTH",
            "customer_segment": "SMB",
            "lifetime_value": 2450.0,
            "churn_risk_score": 0.65,
        },
        {
            "customer_id": "C004",
            "first_name": "Emma",
            "last_name": "Garcia ",
            "email": "emma.garcia@example.com",
            "signup_date": "2023-04-19",
            "region": "east",
            "customer_segment": "Enterprise",
            "lifetime_value": 22100.25,
            "churn_risk_score": 0.08,
        },
        {
            "customer_id": "C005",
            "first_name": "Olivia",
            "last_name": "Brown",
            "email": "olivia.brown@example",
            "signup_date": "2023-05-22",
            "region": "North",
            "customer_segment": " smb ",
            "lifetime_value": 980.5,
            "churn_risk_score": 0.79,
        },
        {
            "customer_id": "C006",
            "first_name": "Mason",
            "last_name": "Wilson",
            "email": "mason.wilson@example.com",
            "signup_date": "2023-06-30",
            "region": "west",
            "customer_segment": "Mid-Market",
            "lifetime_value": 6750.0,
            "churn_risk_score": 0.29,
        },
    ]
    rows.append(rows[2].copy())
    rows[-1]["email"] = "noah.patel@example.com"
    return pd.DataFrame(rows)


def build_orders() -> pd.DataFrame:
    rows = [
        {
            "order_id": "O1001",
            "customer_id": "C001",
            "order_date": "2024-01-10",
            "product_id": "P100",
            "quantity": 4,
            "unit_price": 120.0,
            "discount": 0.05,
            "order_status": "Complete",
            "sales_channel": "Web",
        },
        {
            "order_id": "O1002",
            "customer_id": "C002",
            "order_date": "2024-01-12",
            "product_id": "P200",
            "quantity": -2,
            "unit_price": 85.5,
            "discount": 0.0,
            "order_status": "completed",
            "sales_channel": " partner ",
        },
        {
            "order_id": "O1003",
            "customer_id": "C003",
            "order_date": "not-a-date",
            "product_id": "",
            "quantity": 1,
            "unit_price": 450.0,
            "discount": 0.1,
            "order_status": "PENDING",
            "sales_channel": "Sales",
        },
        {
            "order_id": "O1004",
            "customer_id": "C004",
            "order_date": "2024-02-03",
            "product_id": "P300",
            "quantity": 6,
            "unit_price": 39.99,
            "discount": 0.0,
            "order_status": "cancelled",
            "sales_channel": "web",
        },
        {
            "order_id": "O1005",
            "customer_id": "C005",
            "order_date": "2024-02-14",
            "product_id": "P400",
            "quantity": 3,
            "unit_price": 199.0,
            "discount": 0.2,
            "order_status": "Shipped ",
            "sales_channel": "Retail",
        },
    ]
    rows.append(rows[0].copy())
    return pd.DataFrame(rows)


def build_products() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "product_id": "P100",
                "product_name": "Analytics Starter Kit",
                "category": "Software",
                "cost": 45.0,
                "list_price": 120.0,
                "supplier": "Northstar Systems",
                "active_flag": True,
            },
            {
                "product_id": "P200",
                "product_name": "Data Quality Add-on",
                "category": "software ",
                "cost": 30.0,
                "list_price": 85.5,
                "supplier": "",
                "active_flag": True,
            },
            {
                "product_id": "P300",
                "product_name": "Warehouse Connector",
                "category": "Integration",
                "cost": 12.0,
                "list_price": 39.99,
                "supplier": "ConnectorWorks",
                "active_flag": False,
            },
            {
                "product_id": "P400",
                "product_name": "Executive Insights Pack",
                "category": "SERVICES",
                "cost": 110.0,
                "list_price": 199.0,
                "supplier": "InsightOps",
                "active_flag": True,
            },
        ]
    )


def build_support_tickets() -> list[dict[str, object]]:
    return [
        {
            "ticket_id": "T5001",
            "customer_id": "C001",
            "created_at": "2024-03-01T09:15:00",
            "channel": "email",
            "priority": "High",
            "status": "Open",
            "issue_type": "billing",
            "satisfaction_score": 4,
            "message": {
                "subject": "Invoice question",
                "body": "Needs invoice split by department.",
            },
        },
        {
            "ticket_id": "T5002",
            "customer_id": "C002",
            "created_at": "2024-03-02T10:45:00",
            "channel": "chat",
            "priority": "low ",
            "status": "resolved",
            "issue_type": "login",
            "satisfaction_score": None,
            "message": {"body": "User could not reset password.", "tags": ["auth", "reset"]},
        },
        {
            "ticket_id": "T5003",
            "customer_id": "C003",
            "created_at": "2024-03-04T14:05:00",
            "channel": "Phone",
            "priority": "URGENT",
            "status": "in progress",
            "issue_type": "data_export",
            "satisfaction_score": 2,
            "message": {"body": "Export failed for a large CSV file.", "attempts": 3},
        },
        {
            "ticket_id": "T5004",
            "customer_id": "C006",
            "created_at": "2024-03-08T16:20:00",
            "channel": "email",
            "priority": "Medium",
            "status": "Closed ",
            "issue_type": "feature_request",
            "satisfaction_score": 5,
            "message": {"body": "Asked for dashboard scheduling support."},
        },
    ]


def build_inventory() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "product_id": "P100",
                "warehouse": "Seattle",
                "stock_on_hand": 125,
                "reorder_point": 30,
                "last_restock_date": "2024-02-18",
            },
            {
                "product_id": "P200",
                "warehouse": " seattle ",
                "stock_on_hand": -4,
                "reorder_point": 25,
                "last_restock_date": "2024-02-20",
            },
            {
                "product_id": "P300",
                "warehouse": "Austin",
                "stock_on_hand": 0,
                "reorder_point": 10,
                "last_restock_date": "",
            },
            {
                "product_id": "P400",
                "warehouse": "AUSTIN",
                "stock_on_hand": 44,
                "reorder_point": 15,
                "last_restock_date": "2024-01-30",
            },
        ]
    )


def cleaned_for_sqlite(frame: pd.DataFrame) -> pd.DataFrame:
    cleaned = frame.copy()
    for column in cleaned.select_dtypes(include="object").columns:
        cleaned[column] = cleaned[column].fillna("").astype(str).str.strip()
    return cleaned.drop_duplicates()


def write_sqlite(customers: pd.DataFrame, orders: pd.DataFrame, products: pd.DataFrame) -> Path:
    sqlite_path = SQLITE_DIR / "company.db"
    if sqlite_path.exists():
        sqlite_path.unlink()

    with sqlite3.connect(sqlite_path) as connection:
        cleaned_for_sqlite(customers).to_sql(
            "customers", connection, if_exists="replace", index=False
        )
        cleaned_for_sqlite(orders).to_sql("orders", connection, if_exists="replace", index=False)
        cleaned_for_sqlite(products).to_sql(
            "products", connection, if_exists="replace", index=False
        )
    return sqlite_path


def generate() -> list[Path]:
    random.seed(RANDOM_SEED)
    DATA_SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    SQLITE_DIR.mkdir(parents=True, exist_ok=True)

    customers = build_customers()
    orders = build_orders()
    products = build_products()
    tickets = build_support_tickets()
    inventory = build_inventory()

    output_paths = [
        DATA_SAMPLE_DIR / "customers.csv",
        DATA_SAMPLE_DIR / "orders.csv",
        DATA_SAMPLE_DIR / "products.parquet",
        DATA_SAMPLE_DIR / "support_tickets.jsonl",
        DATA_SAMPLE_DIR / "inventory.xlsx",
    ]

    customers.to_csv(output_paths[0], index=False)
    orders.to_csv(output_paths[1], index=False)
    products.to_parquet(output_paths[2], index=False)
    with output_paths[3].open("w", encoding="utf-8") as file:
        for ticket in tickets:
            file.write(json.dumps(ticket) + "\n")
    inventory.to_excel(output_paths[4], index=False)
    output_paths.append(write_sqlite(customers, orders, products))

    return output_paths


def main() -> None:
    output_paths = generate()
    print("Generated sample data files:")
    for path in output_paths:
        print(f"- {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
