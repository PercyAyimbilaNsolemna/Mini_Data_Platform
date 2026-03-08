# src/data_quality/dq_checks.py
"""
Reusable Data Quality checks for ETL pipelines.

Each function returns a tuple: (clean_df, invalid_df) where invalid_df
contains an added column 'error_reason' describing why rows failed.
"""

import re
from typing import List, Tuple
import pandas as pd


class DataQualityChecks:
    """Collection of static methods implementing common DQ checks."""

    @staticmethod
    def required_fields(df: pd.DataFrame, fields: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Ensure required fields are not null."""
        mask = df[fields].notnull().all(axis=1)
        valid = df[mask].copy()
        invalid = df[~mask].copy()
        if not invalid.empty:
            invalid["error_reason"] = "missing_required_field"
        return valid, invalid

    @staticmethod
    def email_format(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Validate email format using a regex."""
        regex = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        mask = df[column].astype(str).str.match(regex)
        valid = df[mask].copy()
        invalid = df[~mask].copy()
        if not invalid.empty:
            invalid["error_reason"] = "invalid_email"
        return valid, invalid

    @staticmethod
    def positive_value(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Ensure numeric column values are > 0."""
        mask = pd.to_numeric(df[column], errors="coerce") > 0
        valid = df[mask].copy()
        invalid = df[~mask].copy()
        if not invalid.empty:
            invalid["error_reason"] = f"{column}_must_be_positive"
        return valid, invalid

    @staticmethod
    def regex_match(df: pd.DataFrame, column: str, pattern: str, reason: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Generic regex matcher for a column; reason is assigned to invalid rows."""
        mask = df[column].astype(str).str.match(pattern)
        valid = df[mask].copy()
        invalid = df[~mask].copy()
        if not invalid.empty:
            invalid["error_reason"] = reason
        return valid, invalid

    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: List[str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Remove duplicates within the dataframe based on subset columns.
        Returns cleaned dataframe and duplicates (marked invalid).
        """
        dup_mask = df.duplicated(subset=subset, keep="first")
        duplicates = df[dup_mask].copy()
        if not duplicates.empty:
            duplicates["error_reason"] = "duplicate_record"
        cleaned = df[~dup_mask].copy()
        return cleaned, duplicates