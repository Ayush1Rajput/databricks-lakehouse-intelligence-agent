from pathlib import Path
import pandas as pd


DATASET_DIR = Path("datasets")


def profile_csv(file_path: Path) -> None:
    df = pd.read_csv(file_path)

    print("\n" + "=" * 80)
    print(f"FILE: {file_path.name}")
    print("=" * 80)

    print(f"Rows    : {len(df):,}")
    print(f"Columns : {len(df.columns)}")

    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nData Types:")
    print(df.dtypes.to_string())

    print("\nNull Values:")
    nulls = df.isnull().sum()
    nulls = nulls[nulls > 0]

    if nulls.empty:
        print("  No null values")
    else:
        print(nulls.to_string())

    print("\nDuplicate Rows:")
    print(f"  {df.duplicated().sum():,}")


def main():
    csv_files = sorted(DATASET_DIR.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in datasets/")
        return

    print(f"Found {len(csv_files)} CSV files.")

    for file_path in csv_files:
        profile_csv(file_path)


if __name__ == "__main__":
    main()