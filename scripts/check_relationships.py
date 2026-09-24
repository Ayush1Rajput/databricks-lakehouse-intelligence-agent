from pathlib import Path
import pandas as pd


DATASET_DIR = Path("datasets")


def load_table(filename):
    return pd.read_csv(DATASET_DIR / filename)


def check_unique(df, columns, table_name):
    duplicate_count = df.duplicated(subset=columns).sum()

    if duplicate_count == 0:
        print(f"[PASS] {table_name}: {columns} are unique")
    else:
        print(
            f"[FAIL] {table_name}: {columns} have "
            f"{duplicate_count:,} duplicate rows"
        )


def check_foreign_key(
    child_df,
    child_column,
    parent_df,
    parent_column,
    relationship_name,
):
    child_values = set(child_df[child_column].dropna().unique())
    parent_values = set(parent_df[parent_column].dropna().unique())

    missing_values = child_values - parent_values

    if not missing_values:
        print(f"[PASS] {relationship_name}")
    else:
        print(
            f"[FAIL] {relationship_name}: "
            f"{len(missing_values):,} values not found in parent table"
        )


def main():
    print("=" * 80)
    print("OLIST KEY & RELATIONSHIP VALIDATION")
    print("=" * 80)

    customers = load_table("olist_customers_dataset.csv")
    orders = load_table("olist_orders_dataset.csv")
    order_items = load_table("olist_order_items_dataset.csv")
    payments = load_table("olist_order_payments_dataset.csv")
    reviews = load_table("olist_order_reviews_dataset.csv")
    products = load_table("olist_products_dataset.csv")
    sellers = load_table("olist_sellers_dataset.csv")
    translations = load_table(
        "product_category_name_translation.csv"
    )

    # ------------------------------------------------------------------
    # PRIMARY KEY / COMPOSITE KEY CHECKS
    # ------------------------------------------------------------------

    print("\n" + "-" * 80)
    print("KEY UNIQUENESS")
    print("-" * 80)

    check_unique(
        customers,
        ["customer_id"],
        "customers.customer_id",
    )

    check_unique(
        customers,
        ["customer_unique_id"],
        "customers.customer_unique_id",
    )

    check_unique(
        orders,
        ["order_id"],
        "orders.order_id",
    )

    check_unique(
        order_items,
        ["order_id", "order_item_id"],
        "order_items.(order_id, order_item_id)",
    )

    check_unique(
        payments,
        ["order_id", "payment_sequential"],
        "payments.(order_id, payment_sequential)",
    )

    check_unique(
        reviews,
        ["review_id"],
        "reviews.review_id",
    )

    check_unique(
        products,
        ["product_id"],
        "products.product_id",
    )

    check_unique(
        sellers,
        ["seller_id"],
        "sellers.seller_id",
    )

    check_unique(
        translations,
        ["product_category_name"],
        "category_translation.product_category_name",
    )

    # ------------------------------------------------------------------
    # FOREIGN KEY CHECKS
    # ------------------------------------------------------------------

    print("\n" + "-" * 80)
    print("FOREIGN KEY VALIDATION")
    print("-" * 80)

    check_foreign_key(
        orders,
        "customer_id",
        customers,
        "customer_id",
        "orders.customer_id -> customers.customer_id",
    )

    check_foreign_key(
        order_items,
        "order_id",
        orders,
        "order_id",
        "order_items.order_id -> orders.order_id",
    )

    check_foreign_key(
        order_items,
        "product_id",
        products,
        "product_id",
        "order_items.product_id -> products.product_id",
    )

    check_foreign_key(
        order_items,
        "seller_id",
        sellers,
        "seller_id",
        "order_items.seller_id -> sellers.seller_id",
    )

    check_foreign_key(
        payments,
        "order_id",
        orders,
        "order_id",
        "payments.order_id -> orders.order_id",
    )

    check_foreign_key(
        reviews,
        "order_id",
        orders,
        "order_id",
        "reviews.order_id -> orders.order_id",
    )

    check_foreign_key(
        translations,
        "product_category_name",
        products,
        "product_category_name",
        "translation.category -> products.category",
    )


if __name__ == "__main__":
    main()