from pathlib import Path
import pandas as pd


DATASET_DIR = Path("datasets")


def load_table(filename):
    return pd.read_csv(DATASET_DIR / filename)


def section(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def main():

    orders = load_table("olist_orders_dataset.csv")
    items = load_table("olist_order_items_dataset.csv")
    payments = load_table("olist_order_payments_dataset.csv")
    reviews = load_table("olist_order_reviews_dataset.csv")
    products = load_table("olist_products_dataset.csv")
    sellers = load_table("olist_sellers_dataset.csv")
    customers = load_table("olist_customers_dataset.csv")

    # ================================================================
    # ORDERS
    # ================================================================

    section("ORDERS - DATA QUALITY")

    print("\nOrder statuses:")
    print(orders["order_status"].value_counts().to_string())

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

    print("\nDate ranges:")

    for column in date_columns:
        print(
            f"{column}: "
            f"{orders[column].min()} -> "
            f"{orders[column].max()}"
        )

    print("\nOrders with delivery before purchase:")
    print(
        (
            orders["order_delivered_customer_date"]
            < orders["order_purchase_timestamp"]
        ).sum()
    )

    print("\nOrders delivered after estimated date:")
    print(
        (
            orders["order_delivered_customer_date"]
            > orders["order_estimated_delivery_date"]
        ).sum()
    )

    # ================================================================
    # ORDER ITEMS
    # ================================================================

    section("ORDER ITEMS - DATA QUALITY")

    print("\nPrice statistics:")
    print(items["price"].describe().to_string())

    print("\nFreight statistics:")
    print(items["freight_value"].describe().to_string())

    print("\nZero price rows:")
    print((items["price"] == 0).sum())

    print("\nNegative price rows:")
    print((items["price"] < 0).sum())

    print("\nZero freight rows:")
    print((items["freight_value"] == 0).sum())

    print("\nNegative freight rows:")
    print((items["freight_value"] < 0).sum())

    # ================================================================
    # PAYMENTS
    # ================================================================

    section("PAYMENTS - DATA QUALITY")

    print("\nPayment types:")
    print(payments["payment_type"].value_counts().to_string())

    print("\nPayment statistics:")
    print(payments["payment_value"].describe().to_string())

    print("\nZero payment values:")
    print((payments["payment_value"] == 0).sum())

    print("\nNegative payment values:")
    print((payments["payment_value"] < 0).sum())

    print("\nInstallment distribution:")
    print(
        payments["payment_installments"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    # ================================================================
    # REVIEWS
    # ================================================================

    section("REVIEWS - DATA QUALITY")

    print("\nReview score distribution:")
    print(
        reviews["review_score"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nReview scores outside 1-5:")
    print(
        (
            (reviews["review_score"] < 1)
            | (reviews["review_score"] > 5)
        ).sum()
    )

    # ================================================================
    # PRODUCTS
    # ================================================================

    section("PRODUCTS - DATA QUALITY")

    product_numeric_columns = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ]

    for column in product_numeric_columns:

        print(f"\n{column}")

        print(
            products[column]
            .describe()
            .to_string()
        )

        print(
            f"Zero values: "
            f"{(products[column] == 0).sum()}"
        )

        print(
            f"Negative values: "
            f"{(products[column] < 0).sum()}"
        )

    print("\nMissing product categories:")
    print(
        products["product_category_name"]
        .isna()
        .sum()
    )

    # ================================================================
    # CUSTOMERS
    # ================================================================

    section("CUSTOMERS - DATA QUALITY")

    print("\nCustomer states:")
    print(
        customers["customer_state"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nCustomer cities:")
    print(
        f"Unique cities: "
        f"{customers['customer_city'].nunique():,}"
    )

    # ================================================================
    # SELLERS
    # ================================================================

    section("SELLERS - DATA QUALITY")

    print("\nSeller states:")
    print(
        sellers["seller_state"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    print("\nSeller cities:")
    print(
        f"Unique cities: "
        f"{sellers['seller_city'].nunique():,}"
    )


if __name__ == "__main__":
    main()