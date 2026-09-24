from pathlib import Path
import pandas as pd


DATASET_DIR = Path("datasets")


def load_table(filename):
    return pd.read_csv(DATASET_DIR / filename)


def print_distribution(series, name):
    print(f"\n{name}")
    print("-" * 60)

    print(f"Minimum : {series.min()}")
    print(f"Maximum : {series.max()}")
    print(f"Average : {series.mean():.2f}")
    print(f"Median  : {series.median():.2f}")

    print("\nFrequency distribution:")
    print(series.value_counts().sort_index().to_string())


def main():

    print("=" * 80)
    print("OLIST CARDINALITY ANALYSIS")
    print("=" * 80)

    customers = load_table("olist_customers_dataset.csv")
    orders = load_table("olist_orders_dataset.csv")
    order_items = load_table("olist_order_items_dataset.csv")
    payments = load_table("olist_order_payments_dataset.csv")
    reviews = load_table("olist_order_reviews_dataset.csv")
    products = load_table("olist_products_dataset.csv")
    sellers = load_table("olist_sellers_dataset.csv")

    # ---------------------------------------------------------------
    # CUSTOMER IDENTITY
    # ---------------------------------------------------------------

    print("\n" + "-" * 80)
    print("CUSTOMER IDENTITY")
    print("-" * 80)

    customer_id_per_unique = (
        customers
        .groupby("customer_unique_id")["customer_id"]
        .nunique()
    )

    print_distribution(
        customer_id_per_unique,
        "customer_unique_id -> customer_id"
    )

    # ---------------------------------------------------------------
    # CUSTOMER -> ORDERS
    # ---------------------------------------------------------------

    print("\n" + "-" * 80)
    print("CUSTOMER -> ORDERS")
    print("-" * 80)

    orders_per_customer = (
        orders
        .groupby("customer_id")["order_id"]
        .nunique()
    )

    print_distribution(
        orders_per_customer,
        "customer_id -> order_id"
    )

    # ---------------------------------------------------------------
    # ORDER -> ITEMS
    # ---------------------------------------------------------------

    print("\n" + "-" * 80)
    print("ORDER -> ITEMS")
    print("-" * 80)

    items_per_order = (
        order_items
        .groupby("order_id")["order_item_id"]
        .nunique()
    )

    print_distribution(
        items_per_order,
        "order_id -> order_item_id"
    )

    # ---------------------------------------------------------------
    # ORDER -> PAYMENTS
    # ---------------------------------------------------------------

    print("\n" + "-" * 80)
    print("ORDER -> PAYMENTS")
    print("-" * 80)

    payments_per_order = (
        payments
        .groupby("order_id")["payment_sequential"]
        .nunique()
    )

    print_distribution(
        payments_per_order,
        "order_id -> payment_sequential"
    )

    # ---------------------------------------------------------------
    # ORDER -> REVIEWS
    # ---------------------------------------------------------------

    print("\n" + "-" * 80)
    print("ORDER -> REVIEWS")
    print("-" * 80)

    reviews_per_order = (
        reviews
        .groupby("order_id")["review_id"]
        .nunique()
    )

    print_distribution(
        reviews_per_order,
        "order_id -> review_id"
    )

    # ---------------------------------------------------------------
    # PRODUCT -> ORDER ITEMS
    # ---------------------------------------------------------------

    print("\n" + "-" * 80)
    print("PRODUCT -> ORDER ITEMS")
    print("-" * 80)

    items_per_product = (
        order_items
        .groupby("product_id")["order_id"]
        .nunique()
    )

    print_distribution(
        items_per_product,
        "product_id -> order_id"
    )

    # ---------------------------------------------------------------
    # SELLER -> ORDER ITEMS
    # ---------------------------------------------------------------

    print("\n" + "-" * 80)
    print("SELLER -> ORDER ITEMS")
    print("-" * 80)

    items_per_seller = (
        order_items
        .groupby("seller_id")["order_id"]
        .nunique()
    )

    print_distribution(
        items_per_seller,
        "seller_id -> order_id"
    )


if __name__ == "__main__":
    main()