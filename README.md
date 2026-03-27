<div align="center">

<br/>

```
╔╦╗╦╔╗╔╦  ╔╦╗╔═╗╔╦╗╔═╗  ╔═╗╦  ╔═╗╔╦╗╔═╗╔═╗╦═╗╔╦╗
║║║║║║║║   ║║╠═╣ ║ ╠═╣  ╠═╝║  ╠═╣ ║ ╠╣ ║ ║╠╦╝║║║
╩ ╩╩╝╚╝╩  ═╩╝╩ ╩ ╩ ╩ ╩  ╩  ╩═╝╩ ╩ ╩ ╚  ╚═╝╩╚═╩ ╩
```

**A containerized end-to-end data platform for ingesting, processing,**
**storing, and visualizing e-commerce data using modern data engineering tools.**

<br/>

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=flat-square&logo=apache-airflow&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![MinIO](https://img.shields.io/badge/MinIO-C72E49?style=flat-square&logo=minio&logoColor=white)
![Metabase](https://img.shields.io/badge/Metabase-509EE3?style=flat-square&logo=metabase&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)

<br/>

</div>

---

## Project Overview

### What

Mini Data Platform is a containerized data platform built with Docker Compose that demonstrates how modern data systems work together.

**The platform automatically:**

- Generates sample e-commerce data
- Uploads it to object storage
- Detects and processes new data
- Loads cleaned data into a database
- Visualizes insights through dashboards

**The system integrates several widely used data engineering tools:**

| Tool | Purpose |
|------|---------|
| `PostgreSQL` | Analytical data storage |
| `Apache Airflow` | Workflow orchestration |
| `MinIO` | Object storage (S3 compatible) |
| `Metabase` | Data visualization and dashboards |

---

### Why

Modern data platforms consist of multiple components working together:

| Layer | Example Tool |
|-------|-------------|
| Data Ingestion | Object Storage |
| Workflow Orchestration | Airflow |
| Data Processing | Python ETL |
| Data Warehouse | PostgreSQL |
| Business Intelligence | Metabase |

This project demonstrates how these systems integrate together in a simplified architecture.

**It is ideal for learning:**

- Data engineering fundamentals
- ETL pipeline development
- Workflow orchestration
- Docker based infrastructure
- Data visualization pipelines
- CI/CD for data platforms

---

### How

The system works through an automated pipeline:

```
 01  ──  Data generators create synthetic e-commerce CSV files
 02  ──  Files are uploaded to MinIO object storage
 03  ──  Airflow scans MinIO for new files
 04  ──  ETL pipelines clean and transform the data
 05  ──  Processed data is stored in PostgreSQL
 06  ──  Metabase dashboards visualize insights
```

---

## Architecture Overview
<div align="center">

![architecture](docs/pipeline.drawio.png)

</div>
The entire platform runs inside Docker containers. Components interact through an internal Docker network.

---

### Data Flow

```
 01  ──  Generator → MinIO          Upload CSV files
 02  ──  Airflow  → MinIO          Scan for new files, return file list
 03  ──  Airflow  → ETL            Trigger entity pipelines
 04  ──  ETL      → PostgreSQL     Load cleaned data
 05  ──  PostgreSQL → Metabase     Query datasets
 06  ──  Metabase  → User          Display dashboards
```

---

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| `Docker` | Containerization |
| `Docker Compose` | Multi-service orchestration |
| `PostgreSQL` | Data warehouse |
| `Apache Airflow` | Workflow orchestration |
| `MinIO` | Object storage |
| `Metabase` | Data visualization |
| `Python` | ETL pipelines |
| `GitHub Actions` | CI/CD automation |

---

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| `PostgreSQL` | **5432** | Data warehouse |
| `Airflow Webserver` | **8080** | Workflow UI |
| `MinIO API` | **9000** | Object storage API |
| `MinIO Console` | **9001** | Object storage UI |
| `Metabase` | **3000** | BI dashboards |

### Docker Image

The project builds and deploys the Docker image:

```
percyayimbila/mini-data-platform:latest
```

---

## Project Structure

```
Mini_Data_Platform/
│
├── .github/workflows/
│   └── main.yml
│
├── airflow/
│   └── dags/
│       ├── etl_minio_pipeline_dag.py
│       └── pipeline.py
│
├── data/
│   └── tmp/
│       ├── users/
│       ├── products/
│       ├── orders/
│       └── order_items/
│
├── scripts/
│
├── src/
│   ├── data_generators/
│   ├── detection/
│   ├── etl/
│   │   ├── base_etl.py
│   │   ├── users_etl.py
│   │   ├── products_etl.py
│   │   ├── orders_etl.py
│   │   └── order_items_etl.py
│   │
│   ├── data_quality/
│   ├── scripts/
│   │   └── db_init.sql
│   └── utils/
│
├── tests/
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Prerequisites

Install the following before running the project.

- Docker
- Docker Compose
- Python 3.11+
- Git

---

## Installation and Setup

**Clone the repository**

```bash
git clone https://github.com/PercyAyimbilaNsolemna/Mini_Data_Platform.git
cd Mini_Data_Platform
```

**Create the environment file** — `.env`

```env
# Postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=ecommerce
POSTGRES_PORT=5432

# Airflow
AIRFLOW_ADMIN_USERNAME=username
AIRFLOW_ADMIN_PASSWORD=password
AIRFLOW__CORE__FERNET_KEY=4Jr3mL8Rb5VfGg9k6TQ2jFqM9MZ5wKzN3fPQ2VxGKdM=
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://postgres:password@postgres:5432/ecommerce
AIRFLOW__CORE__LOAD_EXAMPLES=False
AIRFLOW__CORE__ENABLE_XCOM_PICKLING=True
AIRFLOW__LOGGING__LOGGING_LEVEL=INFO

# MinIO
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=${MINIO_ROOT_USER}
MINIO_SECRET_KEY=${MINIO_ROOT_PASSWORD}
MINIO_USE_SSL=false

# Metabase
MB_DB_TYPE=postgres
MB_DB_DBNAME=ecommerce
MB_DB_PORT=5432
MB_DB_USER=postgres
MB_DB_PASS=password
MB_DB_HOST=postgres
MB_JETTY_PORT=3000
```

---

## Running the Platform

Start all services using Docker Compose.

```bash
docker compose up -d
```

Verify running containers.

```bash
docker ps
```

**Accessing Services**

| Service | URL |
|---------|-----|
| Airflow | http://localhost:8080 |
| MinIO Console | http://localhost:9001 |
| Metabase | http://localhost:3000 |
| PostgreSQL | localhost:5432 |

---

## Data Pipeline Explanation

The platform contains two main Airflow pipelines.

---

#### Pipeline 01 — Data Generation Pipeline

> **DAG:** `pipeline.py`

Generates synthetic e-commerce datasets and uploads CSV files to MinIO.

**Entities generated:** Users · Products · Orders · Order Items

---

#### Pipeline 02 — ETL Processing Pipeline

> **DAG:** `etl_minio_pipeline_dag.py` · Runs every **5 minutes**

```
 Step 1  ──  Scan MinIO for new files
 Step 2  ──  Register new files in registry
 Step 3  ──  Fetch pending files
 Step 4  ──  Run ETL by entity type
```

---

### Entity ETL Pipelines

Each dataset has its own ETL module under `src/etl/`

| ETL Module | Purpose |
|-----------|---------|
| `users_etl.py` | Process user data |
| `products_etl.py` | Process product data |
| `orders_etl.py` | Process order data |
| `order_items_etl.py` | Process order item data |

All ETL pipelines extend `base_etl.py`, which provides shared functionality:

- File loading
- Data cleaning
- Data transformation
- PostgreSQL loading
- Logging

---

### MinIO Storage

**Bucket name:** `ecommerce-data`

**Example stored files:**

```
users_2026_03_01.csv
products_2026_03_01.csv
orders_2026_03_01.csv
order_items_2026_03_01.csv
```

---

### Complete Data Flow

```
 01  ──  Data generator creates CSV files
 02  ──  Files are uploaded to MinIO bucket   [ ecommerce-data ]
 03  ──  Airflow scans MinIO every 5 minutes
 04  ──  New files are registered and processed
 05  ──  ETL cleans and transforms the data
 06  ──  Data is loaded into PostgreSQL
 07  ──  Metabase queries PostgreSQL
 08  ──  Dashboards visualize insights
```

---

## Example Use Case

Imagine an e-commerce platform collecting transaction data. This platform can answer questions like:

- Top selling products
- Revenue trends
- Customer growth
- Order frequency

**Metabase dashboards can display:**

- Sales over time
- Product popularity
- Customer distribution
- Order volume

---

### Dashboard Examples

| Screenshot | Description |
|-----------|-------------|
| ![metabase_dashboard](docs/metabase_dashboard.png) | Metabase —  Dashboard |
| ![pgAdmin](docs/pgAdmin.png) | pgAdmin |
| ![etl_pipeline](docs/etl_pipeline_dag.png) | Airflow — ETL DAG |
| ![data_generation](docs/data_generation_dag.png) | Airflow — Data Generation DAG |
| ![minio_bucket](docs/minio_bucket.png) | MinIO — Storage Bucket |
| ![gitHub_action_ci](docs/gitHub_action_ci.png)` | GitHub Actions — CI Pipeline |
| ![gitHub_action_cd](docs/gitHub_action_cd.png)` | GitHub Actions — CD Pipeline |

---

## CI/CD Pipeline

The project uses GitHub Actions.

**Continuous Integration** — On every push:

- Install dependencies
- Run tests
- Build Docker image
- Push image to Docker Hub

**Continuous Deployment** — When merging to main:

- Pull latest Docker image
- Start production stack
- Deploy containers

---

### Data Flow Validation

The pipeline ensures the following flow works correctly:

```
MinIO  ──▶  Airflow  ──▶  ETL  ──▶  PostgreSQL  ──▶  Metabase
```

This guarantees that files are detected, ETL processes run successfully, data reaches PostgreSQL, and dashboards update automatically.

---

## Troubleshooting

**Containers not starting** — Check logs:

```bash
docker compose logs
```

**Airflow not loading DAGs** — Restart Airflow services:

```bash
docker compose restart airflow
```

**PostgreSQL connection errors** — Verify environment variables in `.env`

**MinIO bucket missing** — Create the bucket: `ecommerce-data`

---

## Future Improvements

Potential improvements for the platform:

- Add Kafka for streaming ingestion
- Implement dbt transformations
- Use DuckDB or ClickHouse for analytics
- Add data quality monitoring
- Add data lineage tracking
- Deploy using Kubernetes
- Implement data lake architecture

---

## Contribution Guide

Contributions are welcome.

1. Fork the repository
2. Create a new branch — `feature/your-feature`
3. Commit your changes
4. Submit a Pull Request

---

<div align="center">

**Mini Data Platform** &nbsp;·&nbsp; MIT License

</div>