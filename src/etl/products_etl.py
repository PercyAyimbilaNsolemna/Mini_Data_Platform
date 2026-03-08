# src/etl/products_etl.py
"""
Products ETL using BaseETL and DataQualityChecks.
"""

from typing import Tuple
import pandas as pd
from psycopg2.extras import execute_batch

from src.etl.base_etl import BaseETL
from src.data_quality.dq_checks import DataQualityChecks
from src.data_quality.validation_rules import PRODUCT_NAME_REGEX


class ProductsETL(BaseETL):
    """ETL pipeline for products entity."""

    def __init__(self) -> None:
        super().__init__("products")

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic cleaning for products."""
        df = df.copy()

        # Clean name safely (preserve nulls)
        if "name" in df.columns:
            df["name"] = df["name"].astype("string").str.strip()

        # Clean description safely
        if "description" in df.columns:
            df["description"] = df["description"].astype("string").str.strip()

        # Normalize null tokens
        df = df.replace({"": pd.NA, "None": pd.NA, "NULL": pd.NA})

        # Remove duplicates by product name
        df, duplicates = DataQualityChecks.remove_duplicates(df, subset=["name"])

        return df

    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Type casting for price and safe defaults."""
        if "price" in df.columns:
            df["price"] = pd.to_numeric(df["price"], errors="coerce")

        return df

    def validate_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Validate required fields and positive price."""
        invalid_parts = []

        # Required fields
        df, invalid = DataQualityChecks.required_fields(df, ["name", "price"])
        invalid_parts.append(invalid)

        # Price must be positive
        df, invalid = DataQualityChecks.positive_value(df, "price")
        invalid_parts.append(invalid)

        # Name regex
        df, invalid = DataQualityChecks.regex_match(
            df,
            "name",
            PRODUCT_NAME_REGEX,
            "invalid_product_name",
        )
        invalid_parts.append(invalid)

        invalid_frames = [p for p in invalid_parts if p is not None and not p.empty]

        if invalid_frames:
            invalid_df = pd.concat(invalid_frames, ignore_index=True)
        else:
            invalid_df = pd.DataFrame()

        if not invalid_df.empty:
            invalid_df = invalid_df.drop_duplicates()

        return df.reset_index(drop=True), invalid_df.reset_index(drop=True)

    def load_to_postgres(self, df: pd.DataFrame) -> None:
        """Bulk insert products. Use ON CONFLICT on name to prevent duplicates."""
        if df is None or df.empty:
            self.logger.info("No valid product rows to insert.")
            return

        cur = self.db_conn.cursor()

        insert_q = """
            INSERT INTO products (name, description, price)
            VALUES (%s, %s, %s)
            ON CONFLICT (name) DO NOTHING
        """

        data = [
            (
                r.name,
                r.description if hasattr(r, "description") else None,
                r.price,
            )
            for r in df.itertuples(index=False)
        ]

        execute_batch(cur, insert_q, data)

        self.db_conn.commit()
        cur.close()

        self.logger.info("Inserted %d products", len(data))