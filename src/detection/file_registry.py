"""
File Registry

This module manages tracking of files detected in MinIO.
It ensures we only process NEW files and avoid duplicates.

Responsibilities:
1. Check if a file already exists in the tracking table
2. Insert newly detected files
3. Return files that need processing

Author: Data Engineering Team
"""

import os
import psycopg2
from typing import List, Dict

from src.utils.logger import get_logger


logger = get_logger("file_registry")


class FileRegistry:
    """
    Handles interactions with the processed_files tracking table.
    """

    def __init__(self):
        """
        Initialize database connection parameters from environment variables.
        """

        self.db_host = os.getenv("POSTGRES_HOST", "postgres")
        self.db_name = os.getenv("POSTGRES_DB", "ecommerce")
        self.db_user = os.getenv("POSTGRES_USER", "postgres")
        self.db_password = os.getenv("POSTGRES_PASSWORD", "password")
        self.db_port = os.getenv("POSTGRES_PORT", "5432")

    def _get_connection(self):
        """
        Create a PostgreSQL database connection.
        """

        return psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
            port=self.db_port,
        )

    def register_new_files(self, files: List[Dict]) -> List[Dict]:
        """
        Insert new files into the processed_files table.

        Only files that do not already exist will be inserted.

        Returns:
            List[Dict]: files that are newly registered
        """

        new_files = []

        conn = self._get_connection()
        cursor = conn.cursor()

        try:

            for file in files:

                bucket = file["bucket_name"]
                object_name = file["object_name"]
                entity = file["entity_type"]

                # Check if file already exists
                cursor.execute(
                    """
                    SELECT 1 FROM processed_files
                    WHERE object_name = %s
                    """,
                    (object_name,)
                )

                exists = cursor.fetchone()

                if exists:
                    continue

                # Insert new file record
                cursor.execute(
                    """
                    INSERT INTO processed_files
                    (bucket_name, object_name, entity_type, status)
                    VALUES (%s, %s, %s, 'pending')
                    """,
                    (bucket, object_name, entity)
                )

                new_files.append(file)

            conn.commit()

            logger.info(f"Registered {len(new_files)} new files")

        except Exception as e:
            logger.exception("Error registering files")
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

        return new_files

    def fetch_pending_files(self) -> List[Dict]:
        """
        Retrieve files that are pending processing.

        Returns:
            List of files ready for ingestion.
        """

        conn = self._get_connection()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT bucket_name, object_name, entity_type
                FROM processed_files
                WHERE status = 'pending'
                ORDER BY detected_at ASC
                """
            )

            rows = cursor.fetchall()

            files = [
                {
                    "bucket_name": r[0],
                    "object_name": r[1],
                    "entity_type": r[2],
                }
                for r in rows
            ]

            logger.info(f"Fetched {len(files)} pending files")

            return files

        except Exception:
            logger.exception("Failed to fetch pending files")
            raise

        finally:
            cursor.close()
            conn.close()