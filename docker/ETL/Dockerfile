FROM bitnami/spark:3.5.5

USER 0
RUN groupadd -g 1001 spark && \
    useradd -r -u 1001 -g spark spark && \
    mkdir -p /home/spark && \
    chown -R spark:spark /home/spark

ENV HOME=/home/spark
ENV USER=spark

ENV PYSPARK_PYTHON=/opt/bitnami/python/bin/python3 \
    PYSPARK_DRIVER_PYTHON=/opt/bitnami/python/bin/python3

WORKDIR /etl
COPY docker/ETL/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ETL ./ETL
COPY ./utils ./utils
COPY ./db ./db
COPY etl_main.py /etl/etl_main.py

USER spark
ENTRYPOINT ["python", "etl_main.py"]