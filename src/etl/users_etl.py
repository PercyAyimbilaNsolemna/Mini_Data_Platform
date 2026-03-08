# src/etl/users_etl.py
"""
Users ETL implementation using BaseETL and DataQualityChecks.

This file contains:
- cleaning
- transformation
- validation (dq checks)
- batch load into Postgres
"""

import re
from typing import Tuple
import pandas as pd
from psycopg2.extras import execute_batch

from src.etl.base_etl import BaseETL
from src.data_quality.dq_checks import DataQualityChecks
from src.data_quality.validation_rules import USER_USERNAME_REGEX


class UsersETL(BaseETL):
    """ETL pipeline for users entity."""

    def __init__(self) -> None:
        """Initialize the UsersETL by delegating to BaseETL."""
        super().__init__("users")

    # ---------- cleaning ----------
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean user DataFrame:
        - strip whitespace
        - normalize empty strings to NaN
        - normalize case
        - remove duplicates within batch
        """

        df = df.copy()

        # Trim whitespace
        df["username"] = df.get("username", pd.Series()).astype(str).str.strip()
        df["email"] = df.get("email", pd.Series()).astype(str).str.strip()

        # Normalize case
        df["username"] = df["username"].str.lower()
        df["email"] = df["email"].str.lower()

        # Normalize common null tokens
        df = df.replace(
                            {"": pd.NA, "None": pd.NA, "NULL": pd.NA}
                        ).infer_objects(copy=False)

        # Remove duplicates
        df, duplicates = DataQualityChecks.remove_duplicates(df, subset=["username", "email"])

        if not duplicates.empty:
            # append reason for visibility if used downstream
            duplicates["error_reason"] = "duplicate_record"

        return df

    # ---------- transform ----------
    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform fields to canonical types/formats:
        - lowercase username and email
        """
        if "username" in df.columns:
            df["username"] = df["username"].str.lower()
        if "email" in df.columns:
            df["email"] = df["email"].str.lower()
        return df

    # ---------- validate ----------
    def validate_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Apply validations and produce (valid_df, invalid_df).
        Steps:
        - required_fields
        - email_format
        - username regex
        """
        invalid_parts = []

        # required fields
        df, invalid = DataQualityChecks.required_fields(df, ["username", "email"])
        invalid_parts.append(invalid)

        # email format
        df, invalid = DataQualityChecks.email_format(df, "email")
        invalid_parts.append(invalid)

        # username regex
        df, invalid = DataQualityChecks.regex_match(df, "username", USER_USERNAME_REGEX, "invalid_username")
        invalid_parts.append(invalid)

        # Concatenate all invalid partitions (if any); keep unique invalid rows
        invalid_frames = [p for p in invalid_parts if p is not None and not p.empty]

        if invalid_frames:
            invalid_df = pd.concat(invalid_frames, ignore_index=True)
        else:
            invalid_df = pd.DataFrame()

        # Drop duplicates from invalid_df (some rows may fail multiple checks)
        if not invalid_df.empty:
            invalid_df = invalid_df.drop_duplicates()

        return df.reset_index(drop=True), invalid_df.reset_index(drop=True)

    # ---------- load ----------
    def load_to_postgres(self, df: pd.DataFrame) -> None:
        """
        Bulk insert valid users into users table using psycopg2.execute_batch.
        INSERT ignores conflicts on email to maintain idempotency.
        """
        if df is None or df.empty:
            self.logger.info("No valid user rows to insert.")
            return

        cur = self.db_conn.cursor()

        insert_query = """
            INSERT INTO users (username, email)
            VALUES (%s, %s)
            ON CONFLICT (email) DO NOTHING
        """

        # Build parameter list
        data = [(row.username, row.email) for row in df.itertuples(index=False)]

        # Execute in a batch for better performance
        execute_batch(cur, insert_query, data)

        self.db_conn.commit()
        cur.close()
        self.logger.info("Inserted %d users into DB", len(data))