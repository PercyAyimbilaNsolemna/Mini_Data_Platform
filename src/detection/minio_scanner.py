"""
MinIO File Scanner

This module scans a MinIO bucket for newly uploaded files and returns
structured metadata about each object.

Responsibilities:
1. Connect to the MinIO server
2. List objects inside the bucket
3. Filter out unwanted folders (e.g., bad_records)
4. Extract file metadata
5. Return a clean list of files ready for processing

This module does NOT write to the database. It only detects files.

Author: Data Engineering Team
"""

import os
from typing import List, Dict

from minio import Minio
from minio.error import S3Error

from src.utils.logger import get_logger


logger = get_logger("minio_scanner")


class MinioScanner:
    """
    Scans a MinIO bucket for new files.

    This class encapsulates the logic for detecting files stored
    in MinIO while excluding directories that should not be monitored.
    """

    def __init__(self):
        """
        Initialize MinIO client using environment variables.
        """

        self.endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        self.access_key = os.getenv("MINIO_ROOT_USER")
        self.secret_key = os.getenv("MINIO_ROOT_PASSWORD")
        self.bucket = os.getenv("MINIO_BUCKET", "ecommerce-data")

        if not self.access_key or not self.secret_key:
            raise ValueError("MinIO credentials are missing from environment variables.")

        # Create MinIO client
        self.client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=False,
        )

        logger.info("MinIO Scanner initialized successfully")

    def scan_bucket(self) -> List[Dict]:
        """
        Scan the configured MinIO bucket for files.

        Returns:
            List[Dict]: List of file metadata dictionaries
        """

        files = []

        try:
            logger.info(f"Scanning bucket: {self.bucket}")

            # List all objects recursively
            objects = self.client.list_objects(self.bucket, recursive=True)

            for obj in objects:

                object_name = obj.object_name

                # Ignore bad records folder
                if object_name.startswith("bad_records/"):
                    continue

                # Ignore directories
                if object_name.endswith("/"):
                    continue

                # Extract entity type from path
                entity_type = object_name.split("/")[0]

                file_metadata = {
                    "bucket_name": self.bucket,
                    "object_name": object_name,
                    "entity_type": entity_type,
                    "file_size": obj.size,
                    "etag": obj.etag,
                    "last_modified": obj.last_modified,
                }

                files.append(file_metadata)

            logger.info(f"Detected {len(files)} valid files in bucket")

        except S3Error as e:
            logger.exception(f"MinIO scanning error: {str(e)}")
            raise

        except Exception as e:
            logger.exception(f"Unexpected scanning failure: {str(e)}")
            raise

        return files