# src/etl/orders_etl.py
"""
Orders ETL using BaseETL and DataQualityChecks.

Orders validation requires checking that `user_id` exists in users table.
We provide a helper `_fetch_valid_user_ids()` which can be mocked in tests.
"""

from typing import Tuple, Set
import pandas as pd
from psycopg2.extras import execute_batch

from src.etl.base_etl import BaseETL
from src.data_quality.dq_checks import DataQualityChecks


class OrdersETL(BaseETL):
    """ETL pipeline for orders."""

    def __init__(self) -> None:
        super().__init__("orders")

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean strings and ensure numeric types where needed."""
        if "status" in df.columns:
            df["status"] = df["status"].astype(str).str.strip().fillna("pending")
        df = df.replace(
                            {"": pd.NA, "None": pd.NA, "NULL": pd.NA}
                        ).infer_objects(copy=False)
        return df

    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Cast numeric types and convert timestamps."""
        if "total_amount" in df.columns:
            df["total_amount"] = pd.to_numeric(df["total_amount"], errors="coerce")
        if "created_at" in df.columns:
            df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        return df

    def _fetch_valid_user_ids(self) -> Set[int]:
        """
        Query DB for valid user IDs. Separated into helper for easier testing/mocking.
        """
        cur = self.db_conn.cursor()
        cur.execute("SELECT id FROM users")
        rows = cur.fetchall()
        cur.close()
        return {r[0] for r in rows}

    def validate_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Validate orders: required user_id, positive total_amount, and existing users."""
        invalid_parts = []

        # required fields
        df, invalid = DataQualityChecks.required_fields(df, ["user_id", "total_amount"])
        invalid_parts.append(invalid)

        # positive amount
        df, invalid = DataQualityChecks.positive_value(df, "total_amount")
        invalid_parts.append(invalid)

        # user existence: use helper which can be monkeypatched in tests
        valid_user_ids = self._fetch_valid_user_ids()
        mask = df["user_id"].isin(valid_user_ids)
        valid = df[mask].copy()
        invalid_user = df[~mask].copy()
        if not invalid_user.empty:
            invalid_user["error_reason"] = "invalid_user_id"
        invalid_parts.append(invalid_user)

        invalid_frames = [p for p in invalid_parts if p is not None and not p.empty]

        if invalid_frames:
            invalid_df = pd.concat(invalid_frames, ignore_index=True)
        else:
            invalid_df = pd.DataFrame()

        if not invalid_df.empty:
            invalid_df = invalid_df.drop_duplicates()

        return valid.reset_index(drop=True), invalid_df.reset_index(drop=True)

    def load_to_postgres(self, df: pd.DataFrame) -> None:
        """Bulk insert orders."""
        if df is None or df.empty:
            self.logger.info("No valid orders to insert.")
            return

        cur = self.db_conn.cursor()
        insert_q = """
            INSERT INTO orders (user_id, total_amount, status)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING
        """
        data = [(r.user_id, r.total_amount, getattr(r, "status", "pending")) for r in df.itertuples(index=False)]
        execute_batch(cur, insert_q, data)
        self.db_conn.commit()
        cur.close()
        self.logger.info("Inserted %d orders", len(data))