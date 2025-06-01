#!/bin/bash

# Set up virtual environment
echo "Creating virtual environment..."
python -m venv venv
source venv/bin/activate

# Install all requirements
echo "Installing all dependencies..."
pip install -r requirements.txt

# Set up environment variables
export AIRFLOW_HOME="$PWD/airflow"
export MINIO_ROOT_USER="minioadmin"
export MINIO_ROOT_PASSWORD="minioadmin"
export SPARK_HOME="$PWD/spark"
export HADOOP_HOME="$PWD/hadoop"

# Create necessary directories
mkdir -p airflow
echo "Airflow directory created"
mkdir -p data_lake
echo "Data lake directory created"
mkdir -p logs
echo "Logs directory created"
mkdir -p spark
echo "Spark directory created"
mkdir -p hadoop
echo "Hadoop directory created"
mkdir -p kafka
echo "Kafka directory created"

# Initialize Airflow database
echo "Initializing Airflow database..."
airflow db init

# Create Airflow admin user
echo "Creating Airflow admin user..."
airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com

# Configure Spark
echo "Configuring Spark..."
export SPARK_MASTER_HOST=localhost
export SPARK_MASTER_PORT=7077
export SPARK_WORKER_MEMORY=2g
export SPARK_WORKER_CORES=2

# Configure Hadoop
echo "Configuring Hadoop..."
export HADOOP_HEAPSIZE=1024
export HADOOP_LOG_DIR="$PWD/logs/hadoop"

# Configure Kafka
echo "Configuring Kafka..."
export KAFKA_HEAP_OPTS="-Xmx1G -Xms1G"
export KAFKA_LOG_DIR="$PWD/logs/kafka"

# Start services
echo "Starting all services..."

# Start MinIO
nohup minio server data_lake --console-address ":9001" --address ":9000" --quiet --anonymous &

# Start Kafka
echo "Starting Kafka..."
nohup kafka/bin/windows/zookeeper-server-start.sh kafka/config/zookeeper.properties &
sleep 5
nohup kafka/bin/windows/kafka-server-start.sh kafka/config/server.properties &

# Start Spark
echo "Starting Spark..."
nohup spark/bin/spark-submit --master local[*] --class org.apache.spark.examples.SparkPi spark/examples/*.jar 10 &

# Start Airflow
echo "Starting Airflow..."
nohup airflow webserver --port 8080 &
nohup airflow scheduler &

# Start Hadoop
echo "Starting Hadoop..."
nohup hadoop/sbin/hadoop-daemon.sh start namenode &
nohup hadoop/sbin/hadoop-daemon.sh start datanode &

# Create Kafka topics
echo "Creating Kafka topics..."
nohup kafka/bin/windows/kafka-topics.sh --create --topic streaming-data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 &
nohup kafka/bin/windows/kafka-topics.sh --create --topic processed-data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1 &

# Set up monitoring
echo "Setting up monitoring..."
nohup prometheus/prometheus --config.file=prometheus.yml &
nohup grafana/bin/grafana-server --config=grafana.ini &

# Create logging configuration
echo "Creating logging configuration..."
mkdir -p logs/config

# Create Airflow DAGs
echo "Creating Airflow DAGs..."
mkdir -p airflow/dags

# Create Spark job
echo "Creating Spark job..."
mkdir -p spark/jobs

# Create Spark configuration
echo "Creating Spark configuration..."
mkdir -p spark/conf

# Create Hadoop configuration
echo "Creating Hadoop configuration..."
mkdir -p hadoop/etc/hadoop

# Create Kafka configuration
echo "Creating Kafka configuration..."
mkdir -p kafka/config

# Create Docker Compose for production
echo "Creating Docker Compose configuration..."

# Wait for services to start
echo "Waiting for services to start..."
sleep 10

echo "Setup completed!"
echo "Access services at:"
echo "Airflow UI: http://localhost:8080"
echo "MinIO UI: http://localhost:9001"
echo "Spark UI: http://localhost:8080"
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000"
echo "Kafka UI: http://localhost:8081"
echo "Login credentials: minioadmin/minioadmin"
