@echo off
echo Installing required packages...
pip install -r requirements.txt

:check_docker
echo Checking Docker status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker Desktop is not running. Please start Docker Desktop and press any key to continue...
    pause
    goto check_docker
)

:setup_services
echo Setting up services...
python setup_pipeline.py

:setup_kafka
echo Setting up Kafka...
python setup_kafka.py

:start_pipeline
echo Starting pipeline...
python setup_minio.py

:run_airflow
echo Starting Airflow...
start airflow webserver -p 8080
start airflow scheduler

:run_dashboard
echo Starting Streamlit dashboard...
start streamlit run dashboards/app.py

echo All services are running!
echo - Airflow UI: http://localhost:8080
echo - MinIO UI: http://localhost:9001
echo - Streamlit Dashboard: http://localhost:8501

pause
