# src/utils/minio_utils.py
import os
from minio import Minio
from minio.error import S3Error
from src.utils.logger import get_logger
import time

logger = get_logger("minio_utils")

# Create MinIO client from environment variables
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
USE_SSL = os.getenv("MINIO_USE_SSL", "false").lower() == "true"

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=USE_SSL
)

def upload_file_to_minio(file_path: str, bucket: str, object_name: str, max_retries: int = 3):
    """Uploads a file to MinIO with retry and logging.

    Args:
        file_path (str): Local path to the file.
        bucket (str): Bucket name in MinIO.
        object_name (str): Object path in the bucket.
        max_retries (int, optional): Number of retries on failure. Defaults to 3.

    Raises:
        Exception: If upload fails after retries.
    """
    for attempt in range(1, max_retries + 1):
        try:
            # Ensure bucket exists
            if not client.bucket_exists(bucket):
                logger.info(f"Bucket '{bucket}' not found. Creating it...")
                client.make_bucket(bucket)

            # Upload file
            client.fput_object(bucket, object_name, file_path)
            logger.info(f"Successfully uploaded '{file_path}' to '{bucket}/{object_name}'")
            return
        except S3Error as e:
            logger.warning(f"Attempt {attempt}/{max_retries} failed to upload '{file_path}': {e}")
            time.sleep(2 ** attempt)  # Exponential backoff
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            time.sleep(2 ** attempt)

    # If all retries failed
    logger.error(f"Failed to upload '{file_path}' to MinIO after {max_retries} attempts.")
    raise Exception(f"Upload failed: {file_path}")