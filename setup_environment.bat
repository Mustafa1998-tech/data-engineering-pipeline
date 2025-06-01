@echo off
:: Set up virtual environment
echo Creating virtual environment...
python -m venv venv

:: Activate virtual environment
call venv\Scripts\activate

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt

:: Set up environment variables
setx AIRFLOW_HOME "%cd%\airflow"
setx MINIO_ROOT_USER "minioadmin"
setx MINIO_ROOT_PASSWORD "minioadmin"

:: Create necessary directories
mkdir airflow
echo Airflow directory created
mkdir data_lake
echo Data lake directory created

:: Initialize Airflow database
echo Initializing Airflow database...
airflow db init

:: Create Airflow admin user
echo Creating Airflow admin user...
airflow users create --username admin --firstname Admin --lastname User --role Admin --email admin@example.com

:: Start MinIO
echo Starting MinIO...
start minio.exe server data_lake --console-address ":9001" --address ":9000" --quiet --anonymous

echo Setup completed!
echo Airflow UI will be available at http://localhost:8080
echo MinIO UI will be available at http://localhost:9001
echo Login credentials: minioadmin/minioadmin

pause
