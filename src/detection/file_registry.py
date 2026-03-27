import os
import psycopg2
from psycopg2.extras import execute_values
from typing import List, Dict

from src.utils.logger import get_logger

logger = get_logger("file_registry")


class FileRegistry:

    def __init__(self):
        self.db_host = os.getenv("POSTGRES_HOST", "postgres")
        self.db_name = os.getenv("POSTGRES_DB", "ecommerce")
        self.db_user = os.getenv("POSTGRES_USER", "postgres")
        self.db_password = os.getenv("POSTGRES_PASSWORD", "password")
        self.db_port = os.getenv("POSTGRES_PORT", "5432")

    def _get_connection(self):
        return psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
            port=self.db_port,
        )

    # 1. BULK REGISTER FILES (FAST + SAFE)
    def register_new_files(self, files: List[Dict]) -> List[Dict]:
        """
        Insert files in bulk using ON CONFLICT.
        Returns only newly inserted files.
        """

        if not files:
            return []

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            values = [
                (f["bucket_name"], f["object_name"], f["entity_type"])
                for f in files
            ]

            query = """
                INSERT INTO processed_files (bucket_name, object_name, entity_type)
                VALUES %s
                ON CONFLICT (object_name) DO NOTHING
                RETURNING bucket_name, object_name, entity_type;
            """

            execute_values(cursor, query, values)

            inserted_rows = cursor.fetchall()

            conn.commit()

            new_files = [
                {
                    "bucket_name": r[0],
                    "object_name": r[1],
                    "entity_type": r[2],
                }
                for r in inserted_rows
            ]

            logger.info(f"Registered {len(new_files)} new files (bulk)")

            return new_files

        except Exception:
            logger.exception("Error registering files")
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    # 2. FETCH FILES SAFELY FOR PROCESSING (NO DUPLICATES)
    def fetch_pending_files(self, batch_size: int = 10) -> List[Dict]:
        """
        Fetch a batch of pending files and lock them for processing.
        Prevents multiple workers from picking same files.
        """

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            query = """
                SELECT id, bucket_name, object_name, entity_type
                FROM processed_files
                WHERE status = 'pending'
                ORDER BY detected_at ASC
                LIMIT %s
                FOR UPDATE SKIP LOCKED
            """

            cursor.execute(query, (batch_size,))
            rows = cursor.fetchall()

            if not rows:
                conn.commit()
                return []

            ids = [r[0] for r in rows]

            # Mark as processing
            cursor.execute(
                """
                UPDATE processed_files
                SET status = 'processing'
                WHERE id = ANY(%s)
                """,
                (ids,)
            )

            conn.commit()

            files = [
                {
                    "id": r[0],
                    "bucket_name": r[1],
                    "object_name": r[2],
                    "entity_type": r[3],
                }
                for r in rows
            ]

            logger.info(f"Fetched {len(files)} files for processing")

            return files

        except Exception:
            logger.exception("Failed to fetch pending files")
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()