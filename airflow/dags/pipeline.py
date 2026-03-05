"""
Airflow DAG to orchestrate e-commerce data generation.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator  # ✅ Fix 1: import EmptyOperator
import logging

from src.data_generators.run_generators import run_all_generators

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email': ['check@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2026, 3, 4),
}

logger = logging.getLogger("airflow.task")

with DAG(
    'ecommerce_data_generation',
    default_args=default_args,
    description='Generates CSV data for ecommerce entities and uploads to MinIO',
    schedule_interval='@hourly',
    catchup=False,
    max_active_runs=1
) as dag:

    start = EmptyOperator(task_id="start")       # ✅ Fix 3: defined once

    generate_data_task = PythonOperator(
        task_id='generate_ecommerce_data',
        python_callable=run_all_generators,
    )

    end = EmptyOperator(task_id="end")           # ✅ Fix 2: end task defined

    start >> generate_data_task >> end