# Custom image for Mini Data Platform
# Single base image for all services
# Uses Apache Airflow as the foundation with additional Python packages for data processing

FROM apache/airflow:2.8.3-python3.11

USER airflow

# Copy requirements file and install Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /requirements.txt

# Copy scripts and entrypoint in one step
COPY --chmod=755 entrypoint.sh /entrypoint.sh
COPY scripts /opt/airflow/scripts

# Switch to airflow user as per Airflow best practices
#USER airflow

# Set Python environment variables for structured logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Use custom entrypoint to initialize services and start Airflow
ENTRYPOINT ["/entrypoint.sh"]
