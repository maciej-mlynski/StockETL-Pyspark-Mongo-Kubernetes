FROM python:3.10-bullseye AS spark-base

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      sudo \
      curl \
      vim \
      unzip \
      openjdk-17-jdk \
      build-essential \
      software-properties-common \
      ssh && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies (for Jupyter and others if needed)
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Set environment variables for Spark
ENV SPARK_HOME="/opt/spark"
ENV PYTHONPATH=$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.7-src.zip:$PYTHONPATH
ENV SPARK_VERSION=3.5.5

WORKDIR ${SPARK_HOME}

# Download and install Apache Spark
RUN mkdir -p ${SPARK_HOME} \
 && curl -fSL "https://dlcdn.apache.org/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop3.tgz" -o spark-${SPARK_VERSION}-bin-hadoop3.tgz \
 && tar xvzf spark-${SPARK_VERSION}-bin-hadoop3.tgz --directory ${SPARK_HOME} --strip-components 1 \
 && rm -rf spark-${SPARK_VERSION}-bin-hadoop3.tgz

# Create spark events directory
RUN mkdir -p ${SPARK_HOME}/spark-events

# Copy spark configuration file
COPY spark-defaults.conf "$SPARK_HOME/conf"
ENV PATH="/opt/spark/sbin:/opt/spark/bin:${PATH}"

RUN chmod u+x /opt/spark/sbin/* && \
    chmod u+x /opt/spark/bin/*

# Copy entrypoint.sh into /app and make it executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Stage 2: Build final image with application code
FROM spark-base AS final

WORKDIR /app

# Re-create the spark-events directory in final stage to ensure it exists
RUN mkdir -p ${SPARK_HOME}/spark-events

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy all project files into /app
COPY . .

# Expose the FastAPI port
EXPOSE 8000

# Default command: Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
