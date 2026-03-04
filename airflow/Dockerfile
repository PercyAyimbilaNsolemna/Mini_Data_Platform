FROM apache/airflow:2.8.3-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends curl jq && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
USER airflow
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && pip install --no-cache-dir -r /requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]