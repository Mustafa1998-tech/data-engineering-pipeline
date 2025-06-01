from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.kafka.operators.kafka import KafkaProducerOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
import os

def start_producer():
    """Start the Kafka producer"""
    os.system("python ../scripts/producer.py")

def start_spark_processor():
    """Start the Spark streaming processor"""
    os.system("python ../spark/stream_processor.py")

def start_dashboard():
    """Start the Streamlit dashboard"""
    os.system("streamlit run ../dashboards/app.py")

def create_dag():
    dag = DAG(
        'netflix_data_pipeline',
        description='Netflix data pipeline DAG',
        schedule_interval=timedelta(days=1),
        start_date=datetime(2025, 6, 1),
        catchup=False
    )

    # Define tasks
    producer_task = PythonOperator(
        task_id='start_producer',
        python_callable=start_producer,
        dag=dag
    )

    spark_task = PythonOperator(
        task_id='start_spark_processor',
        python_callable=start_spark_processor,
        dag=dag
    )

    dashboard_task = PythonOperator(
        task_id='start_dashboard',
        python_callable=start_dashboard,
        dag=dag
    )

    # Set task dependencies
    producer_task >> spark_task >> dashboard_task

    return dag

# Create and return the DAG
dag = create_dag()
