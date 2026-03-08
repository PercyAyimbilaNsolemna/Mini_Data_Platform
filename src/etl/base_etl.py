# src/etl/base_etl.py
"""
Base ETL framework used by entity-specific ETL classes.

Responsibilities:
- Provide a common `run()` orchestration
- Provide extraction helpers (download/read)
- Provide invalid-record upload and status update helpers
- Expose hooks that child classes override:
    - clean_data
    - transform_data
    - validate_data
    - load_to_postgres

Child classes should implement entity-specific validation and loading logic.
"""

import os
from typing import List, Dict, Tuple
import pandas as pd
import psycopg2

from src.utils.logger import get_logger
from src.utils.minio_utils import client as minio_client, upload_file_to_minio

logger = get_logger("base_etl")


class BaseETL:
    """Base class that implements common ETL operations."""

    # Default temporary directory for downloads (child classes can override)
    TEMP_DIR = "data/tmp"

    def __init__(self, entity_name: str, db_conn=None) -> None:
        """
        Initialize shared resources.

        Args:
            entity_name: logical name of the entity (e.g., "users")
            db_conn: optional external DB connection (useful for tests)
        """

        self.entity_name = entity_name
        self.logger = get_logger(f"{entity_name}_etl")
        self.bucket = os.getenv("MINIO_BUCKET", "ecommerce-data")

        # Ensure temp dir exists for this entity
        self.TEMP_DIR = os.path.join(self.TEMP_DIR, entity_name)
        os.makedirs(self.TEMP_DIR, exist_ok=True)

        # Use injected DB connection if provided (used in tests)
        if db_conn:
            self.db_conn = db_conn
        else:
            self.db_conn = self._create_db_connection()

    # ---------- DB Connection ----------

    def _create_db_connection(self):
        """
        Create database connection.

        During unit tests we allow this to fail gracefully so tests
        can run without requiring a real database.
        """
        try:
            conn = psycopg2.connect(
                host=os.getenv("POSTGRES_HOST", "postgres"),
                database=os.getenv("POSTGRES_DB", "ecommerce"),
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                port=int(os.getenv("POSTGRES_PORT", 5432)),
            )

            logger.info("Database connection established.")
            return conn

        except Exception as e:
            logger.warning(
                "Database connection not available. Running in test mode. Error: %s", e
            )
            return None

    # ---------- Main pipeline ----------

    def run(self, files: List[Dict]) -> None:
        """
        Orchestrate ETL steps for each file metadata passed.

        Args:
            files: list of dicts containing file metadata from scanner
        """
        for file_meta in files:
            object_name = file_meta.get("object_name")
            self.logger.info("Starting ETL for file: %s", object_name)

            try:
                # 1. Download
                local_path = self.download_file(file_meta)

                # 2. Read
                df = self.read_csv(local_path)

                # 3. Clean
                df = self.clean_data(df)

                # 4. Transform
                df = self.transform_data(df)

                # 5. Validate -> returns (valid_df, invalid_df)
                valid_df, invalid_df = self.validate_data(df)

                # 6. Load valid to Postgres
                self.load_to_postgres(valid_df)

                # 7. Upload invalids to MinIO
                self.upload_invalid_records(file_meta, invalid_df)

                # 8. Update tracking table status
                self.update_file_status(file_meta, "processed")

                self.logger.info(
                    "ETL finished for %s | valid=%d invalid=%d",
                    object_name,
                    len(valid_df),
                    len(invalid_df),
                )

            except Exception:
                self.logger.exception("ETL failed for file: %s", object_name)
                try:
                    if self.db_conn:
                        self.db_conn.rollback()  # ← clear aborted transaction
                    self.update_file_status(file_meta, "failed")
                except Exception:
                    self.logger.exception(
                        "Failed to update file status for %s", object_name
                    )
                raise  # ← Airflow must see this as a failure


    # ---------- Extraction helpers ----------

    def download_file(self, file_meta: Dict) -> str:
        """
        Download object from MinIO to a local temp file.
        """
        object_name = file_meta["object_name"]
        local_path = os.path.join(self.TEMP_DIR, os.path.basename(object_name))

        self.logger.debug("Downloading %s to %s", object_name, local_path)

        minio_client.fget_object(self.bucket, object_name, local_path)

        return local_path

    def read_csv(self, local_path: str) -> pd.DataFrame:
        """
        Read CSV into pandas DataFrame.
        """
        self.logger.debug("Reading CSV %s", local_path)
        return pd.read_csv(local_path)

    # ---------- Hooks to override in children ----------

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform basic cleaning. Child classes should override as needed."""
        return df

    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform transformations. Child classes should override as needed."""
        return df

    def validate_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Validate and split df into (valid_df, invalid_df).
        Child classes MUST override this method.
        """
        raise NotImplementedError("Child must implement validate_data")

    def load_to_postgres(self, df: pd.DataFrame) -> None:
        """
        Load the valid dataframe into Postgres.
        Child classes must implement.
        """
        raise NotImplementedError("Child must implement load_to_postgres")

    # ---------- Invalid handling & bookkeeping ----------

    def upload_invalid_records(self, file_meta: Dict, df: pd.DataFrame) -> None:
        """
        Upload invalid records to MinIO under bad_records/<entity>/.
        """
        if df is None or df.empty:
            return

        filename = os.path.basename(file_meta["object_name"])
        temp_file = os.path.join(self.TEMP_DIR, f"invalid_{filename}")

        df.to_csv(temp_file, index=False)

        object_path = f"bad_records/{self.entity_name}/{filename}"

        upload_file_to_minio(temp_file, self.bucket, object_path)

        self.logger.info(
            "Uploaded invalid records to %s/%s", self.bucket, object_path
        )

    def update_file_status(self, file_meta: Dict, status: str) -> None:
        """
        Update processed_files tracking table.
        """

        # Skip if DB connection is unavailable (tests)
        if not self.db_conn:
            self.logger.debug("Skipping file status update (no DB connection).")
            return

        cur = self.db_conn.cursor()

        cur.execute(
            """
            UPDATE processed_files
            SET status=%s, processed_at=NOW()
            WHERE object_name=%s
            """,
            (status, file_meta["object_name"]),
        )

        self.db_conn.commit()
        cur.close()