from pathlib import Path
import pandas as pd


DATASET_DIR = Path("datasets")


def main():

    orders = pd.read_csv(
        DATASET_DIR / "olist_orders_dataset.csv"
    )

    date_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]

    for column in date_columns:
        orders[column] = pd.to_datetime(
            orders[column],
            errors="coerce"
        )

    print("=" * 80)
    print("ORDER LIFECYCLE VALIDATION")
    print("=" * 80)

    # ---------------------------------------------------------------
    # TIMELINE VALIDATION
    # ---------------------------------------------------------------

    checks = {
        "approved_before_purchase":
            orders["order_approved_at"]
            < orders["order_purchase_timestamp"],

        "carrier_before_approval":
            orders["order_delivered_carrier_date"]
            < orders["order_approved_at"],

        "customer_delivery_before_carrier":
            orders["order_delivered_customer_date"]
            < orders["order_delivered_carrier_date"],

        "estimated_delivery_before_purchase":
            orders["order_estimated_delivery_date"]
            < orders["order_purchase_timestamp"],
    }

    print("\nTimeline violations:")

    for name, condition in checks.items():

        print(
            f"{name}: "
            f"{condition.fillna(False).sum():,}"
        )

    # ---------------------------------------------------------------
    # STATUS / DATE CONSISTENCY
    # ---------------------------------------------------------------

    print("\n" + "-" * 80)
    print("STATUS / DATE CONSISTENCY")
    print("-" * 80)

    delivered_without_date = (
        (orders["order_status"] == "delivered")
        & orders["order_delivered_customer_date"].isna()
    )

    delivered_with_date = (
        (orders["order_status"] == "delivered")
        & orders["order_delivered_customer_date"].notna()
    )

    non_delivered_with_delivery_date = (
        (orders["order_status"] != "delivered")
        & orders["order_delivered_customer_date"].notna()
    )

    print(
        "Delivered status without customer delivery date:",
        delivered_without_date.sum()
    )

    print(
        "Delivered status with customer delivery date:",
        delivered_with_date.sum()
    )

    print(
        "Non-delivered status with customer delivery date:",
        non_delivered_with_delivery_date.sum()
    )

    # ---------------------------------------------------------------
    # CARRIER DATE CONSISTENCY
    # ---------------------------------------------------------------

    print("\n" + "-" * 80)
    print("CARRIER DATE CONSISTENCY")
    print("-" * 80)

    shipped_without_carrier_date = (
        (orders["order_status"] == "shipped")
        & orders["order_delivered_carrier_date"].isna()
    )

    print(
        "Shipped status without carrier date:",
        shipped_without_carrier_date.sum()
    )

    # ---------------------------------------------------------------
    # STATUS COUNTS
    # ---------------------------------------------------------------

    print("\n" + "-" * 80)
    print("STATUS COUNTS")
    print("-" * 80)

    print(
        orders["order_status"]
        .value_counts()
        .to_string()
    )


if __name__ == "__main__":
    main()