@echo off
echo Installing required packages...
pip install -r requirements.txt
pip install streamlit

:check_docker
echo Checking Docker status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker Desktop is not running. Please start Docker Desktop and press any key to continue...
    pause
    goto check_docker
)

:check_compose
echo Checking Docker Compose status...
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker Compose is not installed. Please install Docker Desktop and restart.
    exit /b 1
)

:setup_services
echo Starting services...
docker-compose up -d

:wait_for_services
echo Waiting for services to start...
timeout /t 30

:check_services
echo Checking services status...
docker ps -a

:run_producer
echo Starting Kafka producer...
start python scripts/producer.py

timeout /t 5

:run_spark
echo Starting Spark streaming processor...
start python spark/stream_processor.py

timeout /t 5

:run_dashboard
echo Starting Streamlit dashboard...
start python -m streamlit run dashboards/app.py

echo All services are running!
echo - Kafka producer: Generating streaming data
echo - Spark processor: Processing and storing data
echo - Streamlit dashboard: Available at http://localhost:8501
echo - MinIO Web UI: Available at http://localhost:9001 (login: minioadmin/minioadmin)

pause
