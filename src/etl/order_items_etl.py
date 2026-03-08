# src/etl/order_items_etl.py
"""
OrderItems ETL using BaseETL and DataQualityChecks.

Checks:
- order_id and product_id exist (helpers to fetch valid ids can be mocked in tests)
- quantity and price are positive
"""

from typing import Tuple, Set
import pandas as pd
from psycopg2.extras import execute_batch

from src.etl.base_etl import BaseETL
from src.data_quality.dq_checks import DataQualityChecks


class OrderItemsETL(BaseETL):
    """ETL pipeline for order_items entity."""

    def __init__(self) -> None:
        super().__init__("order_items")

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic cleaning and null normalization."""
        df = df.replace(
                            {"": pd.NA, "None": pd.NA, "NULL": pd.NA}
                        ).infer_objects(copy=False)
        return df

    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cast numeric types."""
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        return df

    def _fetch_valid_order_ids(self) -> Set[int]:
        cur = self.db_conn.cursor()
        cur.execute("SELECT id FROM orders")
        rows = cur.fetchall()
        cur.close()
        return {r[0] for r in rows}

    def _fetch_valid_product_ids(self) -> Set[int]:
        cur = self.db_conn.cursor()
        cur.execute("SELECT id FROM products")
        rows = cur.fetchall()
        cur.close()
        return {r[0] for r in rows}

    def validate_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Validate order_items for positive quantity/price and foreign keys existence."""
        invalid_parts = []

        # required fields presence
        df, invalid = DataQualityChecks.required_fields(df, ["order_id", "product_id", "quantity", "price"])
        invalid_parts.append(invalid)

        # positive quantity and price
        df, invalid = DataQualityChecks.positive_value(df, "quantity")
        invalid_parts.append(invalid)
        df, invalid = DataQualityChecks.positive_value(df, "price")
        invalid_parts.append(invalid)

        # FK existence checks
        valid_order_ids = self._fetch_valid_order_ids()
        valid_product_ids = self._fetch_valid_product_ids()

        mask = df["order_id"].isin(valid_order_ids) & df["product_id"].isin(valid_product_ids)
        valid = df[mask].copy()
        invalid_fk = df[~mask].copy()
        if not invalid_fk.empty:
            invalid_fk["error_reason"] = "invalid_fk"
        invalid_parts.append(invalid_fk)

        invalid_frames = [p for p in invalid_parts if p is not None and not p.empty]

        if invalid_frames:
            invalid_df = pd.concat(invalid_frames, ignore_index=True)
        else:
            invalid_df = pd.DataFrame()

        if not invalid_df.empty:
            invalid_df = invalid_df.drop_duplicates()

        return valid.reset_index(drop=True), invalid_df.reset_index(drop=True)

    def load_to_postgres(self, df: pd.DataFrame) -> None:
        """Bulk insert order items."""
        if df is None or df.empty:
            self.logger.info("No valid order_items to insert.")
            return

        cur = self.db_conn.cursor()
        insert_q = """
            INSERT INTO order_items (order_id, product_id, quantity, price)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """
        data = [(r.order_id, r.product_id, r.quantity, r.price) for r in df.itertuples(index=False)]
        execute_batch(cur, insert_q, data)
        self.db_conn.commit()
        cur.close()
        self.logger.info("Inserted %d order_items", len(data))