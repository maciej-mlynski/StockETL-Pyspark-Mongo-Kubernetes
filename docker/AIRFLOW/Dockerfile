FROM apache/airflow:2.10.5-python3.12

USER root

# Install system dependencies
RUN apt-get update && apt-get install -y curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/v1.32.3/bin/linux/amd64/kubectl" && \
    chmod +x kubectl && \
    mv kubectl /usr/local/bin/kubectl

# Crerate logs dir
#RUN mkdir -p /opt/airflow/logs/scheduler

USER airflow

# Copy requirements and install python dependencies
COPY docker/AIRFLOW/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy DAGs into the image
COPY dags/ ${AIRFLOW_HOME}/dags/