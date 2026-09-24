from pathlib import Path
import pandas as pd


DATASET_DIR = Path("datasets")


def load_table(filename):
    return pd.read_csv(DATASET_DIR / filename)


def main():

    customers = load_table("olist_customers_dataset.csv")
    reviews = load_table("olist_order_reviews_dataset.csv")

    # ================================================================
    # CUSTOMER UNIQUE ID INVESTIGATION
    # ================================================================

    print("=" * 80)
    print("CUSTOMER UNIQUE ID INVESTIGATION")
    print("=" * 80)

    customer_identity = (
        customers
        .groupby("customer_unique_id")
        .agg(
            customer_ids=("customer_id", "nunique"),
            cities=("customer_city", "nunique"),
            states=("customer_state", "nunique"),
            total_records=("customer_id", "count"),
        )
        .reset_index()
    )

    print("\nCustomers with more than one customer_id:")
    print(
        customer_identity[
            customer_identity["customer_ids"] > 1
        ]
        .sort_values("customer_ids", ascending=False)
        .head(20)
        .to_string(index=False)
    )

    print("\nSummary:")
    print(
        customer_identity[
            ["customer_ids", "cities", "states", "total_records"]
        ]
        .describe()
        .to_string()
    )

    # ================================================================
    # REVIEW ID INVESTIGATION
    # ================================================================

    print("\n" + "=" * 80)
    print("REVIEW ID INVESTIGATION")
    print("=" * 80)

    review_id_counts = reviews["review_id"].value_counts()

    duplicate_review_ids = review_id_counts[
        review_id_counts > 1
    ].index

    duplicate_reviews = reviews[
        reviews["review_id"].isin(duplicate_review_ids)
    ].sort_values("review_id")

    print(
        f"\nDuplicate review IDs: "
        f"{len(duplicate_review_ids):,}"
    )

    print(
        f"Rows belonging to duplicate review IDs: "
        f"{len(duplicate_reviews):,}"
    )

    # Are duplicate review IDs associated with multiple orders?
    review_order_counts = (
        duplicate_reviews
        .groupby("review_id")["order_id"]
        .nunique()
    )

    print("\nDuplicate review IDs associated with multiple orders:")
    print(
        (review_order_counts > 1).value_counts()
        .to_string()
    )

    # Are the duplicate rows exact duplicates?
    exact_duplicate_rows = duplicate_reviews.duplicated().sum()

    print(
        f"\nExact duplicate rows among duplicate review IDs: "
        f"{exact_duplicate_rows:,}"
    )

    # Show sample duplicate review IDs
    print("\nSample duplicate review records:")
    print(
        duplicate_reviews.head(20).to_string(index=False)
    )


if __name__ == "__main__":
    main()