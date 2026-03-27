# airflow/dags/etl_minio_pipeline_observable_dag.py
from datetime import datetime, timedelta
from typing import List, Dict
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup

from src.detection.minio_scanner import MinioScanner
from src.detection.file_registry import FileRegistry
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

def etl_step(entity_name: str, step: str, **context):
    """
    Generic ETL step runner:
    step: 'extract', 'read', 'clean', 'transform', 'validate', 'load', 'finalize'
    """
    pending_files: List[Dict] = context['ti'].xcom_pull(key="pending_files")
    entity_files = [f for f in pending_files if f["entity_type"] == entity_name]
    if not entity_files:
        logger.info(f"No files to process for {entity_name} at step {step}")
        return

    etl = ENTITY_ETL_MAP[entity_name]()
    for file_meta in entity_files:
        object_name = file_meta["object_name"]
        try:
            # Extract
            if step == "extract":
                local_path = etl.download_file(file_meta)
                context['ti'].xcom_push(key=f"{entity_name}_{object_name}_local_path", value=local_path)

            # Read
            elif step == "read":
                local_path = context['ti'].xcom_pull(key=f"{entity_name}_{object_name}_local_path")
                df = etl.read_csv(local_path)
                df_path = f"{etl.TEMP_DIR}/df_{object_name.replace('/', '_')}.csv"
                df.to_csv(df_path, index=False)
                context['ti'].xcom_push(key=f"{entity_name}_{object_name}_df_path", value=df_path)

            # Clean
            elif step == "clean":
                df_path = context['ti'].xcom_pull(key=f"{entity_name}_{object_name}_df_path")
                df = pd.read_csv(df_path)
                df_clean = etl.clean_data(df)
                df_clean_path = f"{etl.TEMP_DIR}/df_clean_{object_name.replace('/', '_')}.csv"
                df_clean.to_csv(df_clean_path, index=False)
                context['ti'].xcom_push(key=f"{entity_name}_{object_name}_df_clean_path", value=df_clean_path)

            # Transform
            elif step == "transform":
                df_clean_path = context['ti'].xcom_pull(key=f"{entity_name}_{object_name}_df_clean_path")
                df_clean = pd.read_csv(df_clean_path)
                df_trans = etl.transform_data(df_clean)
                df_trans_path = f"{etl.TEMP_DIR}/df_trans_{object_name.replace('/', '_')}.csv"
                df_trans.to_csv(df_trans_path, index=False)
                context['ti'].xcom_push(key=f"{entity_name}_{object_name}_df_trans_path", value=df_trans_path)

            # Validate
            elif step == "validate":
                df_trans_path = context['ti'].xcom_pull(key=f"{entity_name}_{object_name}_df_trans_path")
                df_trans = pd.read_csv(df_trans_path)
                valid_df, invalid_df = etl.validate_data(df_trans)
                valid_path = f"{etl.TEMP_DIR}/df_valid_{object_name.replace('/', '_')}.csv"
                invalid_path = f"{etl.TEMP_DIR}/df_invalid_{object_name.replace('/', '_')}.csv"
                valid_df.to_csv(valid_path, index=False)
                invalid_df.to_csv(invalid_path, index=False)
                context['ti'].xcom_push(key=f"{entity_name}_{object_name}_valid_path", value=valid_path)
                context['ti'].xcom_push(key=f"{entity_name}_{object_name}_invalid_path", value=invalid_path)

                # Upload invalids immediately
                etl.upload_invalid_records(file_meta, invalid_df)

            # Load
            elif step == "load":
                valid_path = context['ti'].xcom_pull(key=f"{entity_name}_{object_name}_valid_path")
                valid_df = pd.read_csv(valid_path)
                etl.load_to_postgres(valid_df)

            # Finalize
            elif step == "finalize":
                etl.update_file_status(file_meta, "processed")

        except Exception:
            logger.exception(f"ETL failed for {entity_name} file {object_name} at step {step}")
            raise

with DAG(
    dag_id="etl_minio_pipeline",
    schedule_interval="*/5 * * * *",
    catchup=False,
    default_args=DEFAULT_ARGS,
    max_active_runs=1,
    tags=["minio", "etl", "ecommerce", "observable"],
) as dag:

    # Top-level tasks
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

    # Create TaskGroups per entity with observable ETL steps
    entity_taskgroups = {}
    for entity in ENTITY_ETL_MAP.keys():
        with TaskGroup(group_id=f"{entity}_etl") as tg:
            extract = PythonOperator(
                task_id=f"{entity}_extract",
                python_callable=etl_step,
                op_args=[entity, "extract"],
            )
            read = PythonOperator(
                task_id=f"{entity}_read",
                python_callable=etl_step,
                op_args=[entity, "read"],
            )
            clean = PythonOperator(
                task_id=f"{entity}_clean",
                python_callable=etl_step,
                op_args=[entity, "clean"],
            )
            transform = PythonOperator(
                task_id=f"{entity}_transform",
                python_callable=etl_step,
                op_args=[entity, "transform"],
            )
            validate = PythonOperator(
                task_id=f"{entity}_validate",
                python_callable=etl_step,
                op_args=[entity, "validate"],
            )
            load = PythonOperator(
                task_id=f"{entity}_load",
                python_callable=etl_step,
                op_args=[entity, "load"],
            )
            finalize = PythonOperator(
                task_id=f"{entity}_finalize",
                python_callable=etl_step,
                op_args=[entity, "finalize"],
            )

            extract >> read >> clean >> transform >> validate >> load >> finalize
        entity_taskgroups[entity] = tg

    # DAG dependencies
    scan_task >> register_task >> fetch_task
    fetch_task >> list(entity_taskgroups.values())