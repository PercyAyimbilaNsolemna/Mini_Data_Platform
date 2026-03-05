# src/etl/orders_etl.py
import os
import pandas as pd
from typing import List, Dict
from src.utils.logger import get_logger
from src.utils.minio_utils import client as minio_client, upload_file_to_minio
import psycopg2

logger = get_logger("orders_etl")

class OrdersETL:
    TEMP_DIR = "data/tmp/orders"

    def __init__(self):
        os.makedirs(self.TEMP_DIR, exist_ok=True)
        self.bucket = os.getenv("MINIO_BUCKET", "ecommerce-data")
        self.db_conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST", "postgres"),
            database=os.getenv("POSTGRES_DB", "ecommerce"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            port=os.getenv("POSTGRES_PORT", 5432),
        )

    def run(self, files: List[Dict]):
        for file_meta in files:
            try:
                local_path = self.download_file(file_meta)
                df = self.read_csv(local_path)
                valid_df, invalid_df = self.validate(df)
                self.load_to_postgres(valid_df)
                self.upload_invalid(file_meta, invalid_df)
                self.update_file_status(file_meta, "processed")
            except Exception as e:
                logger.exception(f"ETL failed for file {file_meta['object_name']}")
                self.update_file_status(file_meta, "failed")

    def download_file(self, file_meta: Dict) -> str:
        local_path = os.path.join(self.TEMP_DIR, os.path.basename(file_meta["object_name"]))
        minio_client.fget_object(self.bucket, file_meta["object_name"], local_path)
        return local_path

    def read_csv(self, local_path: str) -> pd.DataFrame:
        return pd.read_csv(local_path)

    def validate(self, df: pd.DataFrame):
        cur = self.db_conn.cursor()
        cur.execute("SELECT id FROM users")
        valid_user_ids = {r[0] for r in cur.fetchall()}
        cur.close()
        valid = df[df["user_id"].isin(valid_user_ids)]
        invalid = df.drop(valid.index)
        return valid, invalid

    def load_to_postgres(self, df: pd.DataFrame):
        if df.empty:
            return
        cur = self.db_conn.cursor()
        for _, row in df.iterrows():
            cur.execute(
                """
                INSERT INTO orders (user_id, total_amount, status)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                (row["user_id"], row.get("total_amount", 0), row.get("status", "pending")),
            )
        self.db_conn.commit()
        cur.close()

    def upload_invalid(self, file_meta: Dict, df: pd.DataFrame):
        if df.empty:
            return
        temp_file = os.path.join(self.TEMP_DIR, f"bad_{os.path.basename(file_meta['object_name'])}")
        df.to_csv(temp_file, index=False)
        object_path = f"bad_records/orders/{os.path.basename(temp_file)}"
        upload_file_to_minio(temp_file, self.bucket, object_path)

    def update_file_status(self, file_meta: Dict, status: str):
        cur = self.db_conn.cursor()
        cur.execute(
            "UPDATE processed_files SET status=%s, processed_at=NOW() WHERE object_name=%s",
            (status, file_meta["object_name"]),
        )
        self.db_conn.commit()
        cur.close()