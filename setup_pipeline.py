import os
import subprocess
import time
import logging
import sys
from datetime import datetime
import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('PipelineSetup')

def monitor_resources():
    """Monitor system resources and log them"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    logger.info(f"System Resources: CPU: {cpu_percent}%, Memory: {memory.percent}%, Disk: {disk.percent}%")
    return cpu_percent, memory.percent, disk.percent

def setup_minio():
    """Setup MinIO server with enhanced error handling"""
    logger.info("Starting MinIO setup...")
    try:
        # Create data directory
        data_dir = os.path.join(os.getcwd(), 'data_lake')
        os.makedirs(data_dir, exist_ok=True)
        
        # Start MinIO with enhanced configuration
        minio_cmd = [
            "minio.exe", "server", 
            data_dir,
            "--console-address", ":9001",
            "--address", ":9000",
            "--quiet",
            "--anonymous"
        ]
        
        logger.info("Starting MinIO server...")
        minio_process = subprocess.Popen(minio_cmd)
        time.sleep(5)
        
        if minio_process.poll() is None:
            logger.info("MinIO started successfully!")
            return True
        else:
            logger.error("Failed to start MinIO")
            return False
            
    except Exception as e:
        logger.error(f"Error during MinIO setup: {str(e)}")
        return False

def setup_airflow():
    """Setup Airflow with enhanced error handling"""
    logger.info("Setting up Airflow...")
    try:
        # Initialize Airflow database
        result = subprocess.run(
            ["airflow", "db", "init"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Failed to initialize Airflow database: {result.stderr}")
            return False
            
        # Create admin user
        result = subprocess.run(
            ["airflow", "users", "create", 
             "--username", "admin", 
             "--firstname", "Admin", 
             "--lastname", "User", 
             "--role", "Admin", 
             "--email", "admin@example.com"],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            logger.error(f"Failed to create admin user: {result.stderr}")
            return False
            
        logger.info("Airflow setup completed!")
        return True
        
    except Exception as e:
        logger.error(f"Error during Airflow setup: {str(e)}")
        return False

def main():
    try:
        # Monitor initial system state
        logger.info("Starting data pipeline setup...")
        monitor_resources()
        
        # Setup components
        minio_success = setup_minio()
        airflow_setup_success = setup_airflow()
        
        if minio_success and airflow_setup_success:
            logger.info("\nData pipeline setup completed!")
            logger.info("Access Airflow UI at http://localhost:8080")
            logger.info("MinIO UI at http://localhost:9001")
            logger.info("(Login credentials: minioadmin/minioadmin)")
            
        else:
            logger.error("Setup failed - check logs for details")
            
    except Exception as e:
        logger.error(f"Critical error during setup: {str(e)}")

if __name__ == "__main__":
    main()
