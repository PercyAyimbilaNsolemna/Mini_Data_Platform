# airflow/dags/etl_minio_pipeline_dag.py
from datetime import datetime, timedelta
from typing import List, Dict
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup

from src.detection.minio_scanner import MinioScanner
from src.detection.file_registry import FileRegistry

# ETL modules
from src.etl.users_etl import UsersETL
from src.etl.products_etl import ProductsETL
from src.etl.orders_etl import OrdersETL
from src.etl.order_items_etl import OrderItemsETL

from src.utils.logger import get_logger

logger = get_logger("etl_minio_pipeline")

DEFAULT_ARGS = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
    "start_date": datetime(2026, 3, 5),
}

ENTITY_ETL_MAP = {
    "users": UsersETL,
    "products": ProductsETL,
    "orders": OrdersETL,
    "order_items": OrderItemsETL,
}

def scan_minio(**context):
    scanner = MinioScanner()
    files = scanner.scan_bucket()
    context['ti'].xcom_push(key="scanned_files", value=files)
    logger.info(f"Scanned {len(files)} files from MinIO.")

def register_new_files(**context):
    files: List[Dict] = context['ti'].xcom_pull(key="scanned_files")
    registry = FileRegistry()
    new_files = registry.register_new_files(files)
    context['ti'].xcom_push(key="new_files", value=new_files)

def fetch_pending_files(**context):
    registry = FileRegistry()
    pending_files = registry.fetch_pending_files()
    context['ti'].xcom_push(key="pending_files", value=pending_files)

def run_entity_etl(entity: str, **context):
    pending_files: List[Dict] = context['ti'].xcom_pull(key="pending_files")
    entity_files = [f for f in pending_files if f["entity_type"] == entity]

    if not entity_files:
        logger.info(f"No new files to process for entity: {entity}")
        return

    etl_class = ENTITY_ETL_MAP[entity]()
    etl_class.run(entity_files)

with DAG(
    dag_id="etl_minio_pipeline",
    schedule_interval="*/5 * * * *",
    catchup=False,
    default_args=DEFAULT_ARGS,
    max_active_runs=1,
    tags=["minio", "etl", "ecommerce"],
) as dag:

    scan_task = PythonOperator(
        task_id="scan_minio_for_new_files",
        python_callable=scan_minio,
    )

    register_task = PythonOperator(
        task_id="register_new_files",
        python_callable=register_new_files,
    )

    fetch_task = PythonOperator(
        task_id="fetch_pending_files",
        python_callable=fetch_pending_files,
    )

    with TaskGroup("entity_etl_tasks") as entity_etl_tasks:
        users_task = PythonOperator(
            task_id="users_etl",
            python_callable=run_entity_etl,
            op_args=["users"],
        )
        products_task = PythonOperator(
            task_id="products_etl",
            python_callable=run_entity_etl,
            op_args=["products"],
        )
        orders_task = PythonOperator(
            task_id="orders_etl",
            python_callable=run_entity_etl,
            op_args=["orders"],
        )
        order_items_task = PythonOperator(
            task_id="order_items_etl",
            python_callable=run_entity_etl,
            op_args=["order_items"],
        )

    # DAG dependencies
    scan_task >> register_task >> fetch_task >> entity_etl_tasks