# Data Engineering Pipeline Project

This project simulates a real-time data pipeline using:
- Kafka (data ingestion)
- Spark Structured Streaming (processing)
- MinIO as a Data Lake (S3-compatible)
- Airflow (workflow orchestration)
- Streamlit (dashboard)

## Structure
- `scripts/`: Kafka producer
- `spark/`: Spark stream processing
- `airflow/dags/`: Airflow DAGs
- `data_lake/`: Simulated data lake using MinIO
- `dashboards/`: Streamlit visualizations

## Getting Started
See `requirements.txt` for setup dependencies.
