import os
import sys
from datetime import datetime
from src.data_generators.users_generator import UsersGenerator        
from src.data_generators.products_generator import ProductsGenerator  
from src.data_generators.orders_generator import OrdersGenerator  
from src.data_generators.order_items_generator import OrderItemsGenerator    
from src.utils.logger import get_logger                               
from src.utils.minio_utils import upload_file_to_minio                
import csv

logger = get_logger("generator_runner")

RAW_BASE_PATH = "data/raw"
BAD_BASE_PATH = "data/bad_records"
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "ecommerce-data")


def create_dirs(entity: str):
    """Ensure directories exist for raw and bad records."""
    raw_path = os.path.join(RAW_BASE_PATH, entity)
    bad_path = os.path.join(BAD_BASE_PATH, entity)
    os.makedirs(raw_path, exist_ok=True)
    os.makedirs(bad_path, exist_ok=True)
    return raw_path, bad_path


def write_records_to_csv(records: list, filepath: str) -> bool:
    """
    Write a list of record dicts to a CSV file.
    Returns True if file was written, False otherwise.
    """
    if not records:
        logger.warning(f"No records to write for {filepath}")
        return False

    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    return True


def run_all_generators():
    """Run all data generators and handle CSV outputs and MinIO uploads."""
    try:
        # USERS
        raw_path, bad_path = create_dirs("users")
        users_file = os.path.join(raw_path, f"users_{datetime.now():%Y%m%d_%H%M%S}.csv")
        bad_users_file = os.path.join(bad_path, f"bad_users_{datetime.now():%Y%m%d_%H%M%S}.csv")
        logger.info("Starting users generation...")
        good_users, bad_users = UsersGenerator().generate_records()  
        write_records_to_csv(good_users, users_file)
        if write_records_to_csv(bad_users, bad_users_file):
            logger.info(f"Wrote bad users file: {bad_users_file}")
            upload_file_to_minio(bad_users_file, MINIO_BUCKET, f"bad_records/users/{os.path.basename(bad_users_file)}")
        upload_file_to_minio(users_file, MINIO_BUCKET, f"users/{os.path.basename(users_file)}")
        
        logger.info("Users generation completed.")

        # PRODUCTS
        raw_path, bad_path = create_dirs("products")
        products_file = os.path.join(raw_path, f"products_{datetime.now():%Y%m%d_%H%M%S}.csv")
        bad_products_file = os.path.join(bad_path, f"bad_products_{datetime.now():%Y%m%d_%H%M%S}.csv")
        logger.info("Starting products generation...")
        good_products, bad_products = ProductsGenerator().generate_records()  
        write_records_to_csv(good_products, products_file)
        if write_records_to_csv(bad_products, bad_products_file):
            logger.info(f"Wrote bad products file: {bad_products_file}")
            upload_file_to_minio(bad_products_file, MINIO_BUCKET, f"bad_records/products/{os.path.basename(bad_products_file)}")
        upload_file_to_minio(products_file, MINIO_BUCKET, f"products/{os.path.basename(products_file)}")
        logger.info("Products generation completed.")

        # ORDERS
        raw_path, bad_path = create_dirs("orders")
        orders_file = os.path.join(raw_path, f"orders_{datetime.now():%Y%m%d_%H%M%S}.csv")
        bad_orders_file = os.path.join(bad_path, f"bad_orders_{datetime.now():%Y%m%d_%H%M%S}.csv")
        logger.info("Starting orders generation...")
        good_orders, bad_orders = OrdersGenerator().generate_records()  
        write_records_to_csv(good_orders, orders_file)
        if write_records_to_csv(bad_orders, bad_orders_file):
            logger.info(f"Wrote bad orders file: {bad_orders_file}")
            upload_file_to_minio(bad_orders_file, MINIO_BUCKET, f"bad_records/orders/{os.path.basename(bad_orders_file)}")
        upload_file_to_minio(orders_file, MINIO_BUCKET, f"orders/{os.path.basename(orders_file)}")
        logger.info("Orders generation completed.")

        # ORDER ITEMS
        raw_path, bad_path = create_dirs("order_items")
        order_items_file = os.path.join(raw_path, f"order_items_{datetime.now():%Y%m%d_%H%M%S}.csv")
        bad_order_items_file = os.path.join(bad_path, f"bad_order_items_{datetime.now():%Y%m%d_%H%M%S}.csv")
        logger.info("Starting order items generation...")
        good_order_items, bad_order_items = OrderItemsGenerator().generate_records() 
        write_records_to_csv(good_order_items, order_items_file)
        if write_records_to_csv(bad_order_items, bad_order_items_file):
            logger.info(f"Wrote bad order items file: {bad_order_items_file}")
            upload_file_to_minio(bad_order_items_file, MINIO_BUCKET, f"bad_records/order_items/{os.path.basename(bad_order_items_file)}")
        upload_file_to_minio(order_items_file, MINIO_BUCKET, f"order_items/{os.path.basename(order_items_file)}")
        logger.info("Order items generation completed.")

    except Exception as e:
        # Log full stack trace
        logger.exception(f"Failed to run generators: {e}")
    
        # Re-raise the exception so Airflow handles it properly
        raise


if __name__ == "__main__":
    logger.info("Starting all generators run...")
    run_all_generators()
    logger.info("All generators completed successfully.")