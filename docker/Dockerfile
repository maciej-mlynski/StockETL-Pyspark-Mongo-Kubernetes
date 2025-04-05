FROM python:3.12-bookworm

# Install jdk -> requied for spark
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-17-jdk \
        wget \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create user and group with UID/GID 1001
RUN groupadd -g 1001 spark && \
    useradd -m -u 1001 -g spark -s /bin/bash spark

# Create logs dir & assign to spark user
RUN mkdir -p /tmp/spark-events && \
    chown -R spark:spark /tmp/spark-events

# Set working dir
WORKDIR /app

# Download requirements
COPY docker/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Coppy all files from root dir
COPY .. .

USER spark

# Expose port & set CMD command
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]