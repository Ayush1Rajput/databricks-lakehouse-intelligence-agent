from pathlib import Path
import pandas as pd


DATASET_DIR = Path("datasets")


def load_orders():
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

    return orders


def print_section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main():

    orders = load_orders()

    # ================================================================
    # 1. CARRIER BEFORE APPROVAL
    # ================================================================

    print_section("1. CARRIER BEFORE APPROVAL")

    carrier_before_approval = orders[
        orders["order_delivered_carrier_date"]
        < orders["order_approved_at"]
    ].copy()

    print(
        f"Records: {len(carrier_before_approval):,}"
    )

    print("\nOrder status distribution:")

    print(
        carrier_before_approval["order_status"]
        .value_counts()
        .to_string()
    )

    print("\nMissing approved_at:")

    print(
        carrier_before_approval["order_approved_at"]
        .isna()
        .sum()
    )

    print("\nSample records:")

    print(
        carrier_before_approval[
            [
                "order_id",
                "order_status",
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
            ]
        ]
        .sort_values("order_approved_at")
        .head(20)
        .to_string(index=False)
    )

    # ================================================================
    # 2. CUSTOMER DELIVERY BEFORE CARRIER
    # ================================================================

    print_section("2. CUSTOMER DELIVERY BEFORE CARRIER")

    delivery_before_carrier = orders[
        orders["order_delivered_customer_date"]
        < orders["order_delivered_carrier_date"]
    ].copy()

    print(
        f"Records: {len(delivery_before_carrier):,}"
    )

    print("\nOrder status distribution:")

    print(
        delivery_before_carrier["order_status"]
        .value_counts()
        .to_string()
    )

    print("\nSample records:")

    print(
        delivery_before_carrier[
            [
                "order_id",
                "order_status",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
            ]
        ]
        .to_string(index=False)
    )

    # ================================================================
    # 3. DELIVERED WITHOUT DELIVERY DATE
    # ================================================================

    print_section("3. DELIVERED STATUS WITHOUT DELIVERY DATE")

    delivered_missing_date = orders[
        (orders["order_status"] == "delivered")
        & orders["order_delivered_customer_date"].isna()
    ].copy()

    print(
        f"Records: {len(delivered_missing_date):,}"
    )

    print(
        delivered_missing_date[
            [
                "order_id",
                "order_status",
                "order_purchase_timestamp",
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
            ]
        ].to_string(index=False)
    )

    # ================================================================
    # 4. NON-DELIVERED WITH DELIVERY DATE
    # ================================================================

    print_section("4. NON-DELIVERED STATUS WITH DELIVERY DATE")

    non_delivered_with_date = orders[
        (orders["order_status"] != "delivered")
        & orders["order_delivered_customer_date"].notna()
    ].copy()

    print(
        f"Records: {len(non_delivered_with_date):,}"
    )

    print(
        non_delivered_with_date[
            [
                "order_id",
                "order_status",
                "order_purchase_timestamp",
                "order_delivered_carrier_date",
                "order_delivered_customer_date",
                "order_estimated_delivery_date",
            ]
        ].to_string(index=False)
    )

    # ================================================================
    # 5. COMBINED TIMELINE ANOMALY SUMMARY
    # ================================================================

    print_section("5. COMBINED TIMELINE ANOMALY SUMMARY")

    orders["carrier_before_approval"] = (
        orders["order_delivered_carrier_date"]
        < orders["order_approved_at"]
    )

    orders["delivery_before_carrier"] = (
        orders["order_delivered_customer_date"]
        < orders["order_delivered_carrier_date"]
    )

    orders["delivered_without_date"] = (
        (orders["order_status"] == "delivered")
        & orders["order_delivered_customer_date"].isna()
    )

    orders["non_delivered_with_date"] = (
        (orders["order_status"] != "delivered")
        & orders["order_delivered_customer_date"].notna()
    )

    orders["timeline_anomaly"] = (
        orders["carrier_before_approval"]
        | orders["delivery_before_carrier"]
    )

    print(
        "carrier_before_approval:",
        orders["carrier_before_approval"].fillna(False).sum()
    )

    print(
        "delivery_before_carrier:",
        orders["delivery_before_carrier"].fillna(False).sum()
    )

    print(
        "timeline_anomaly:",
        orders["timeline_anomaly"].fillna(False).sum()
    )

    print(
        "delivered_without_date:",
        orders["delivered_without_date"].sum()
    )

    print(
        "non_delivered_with_date:",
        orders["non_delivered_with_date"].sum()
    )


if __name__ == "__main__":
    main()