import boto3
from botocore.client import Config
import os

def setup_minio_buckets():
    # Configure MinIO client
    s3 = boto3.client('s3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='minioadmin',
        aws_secret_access_key='minioadmin',
        config=Config(signature_version='s3v4')
    )
    
    # Create buckets
    buckets = ['raw-data', 'processed-data', 'analytics', 'checkpoints']
    
    for bucket in buckets:
        try:
            s3.create_bucket(Bucket=bucket)
            print(f"Created bucket: {bucket}")
        except Exception as e:
            print(f"Error creating bucket {bucket}: {str(e)}")

    # Create initial directories in buckets
    directories = ['user_events', 'movies', 'users', 'ratings']
    
    for bucket in buckets:
        for dir in directories:
            try:
                s3.put_object(Bucket=bucket, Key=f'{dir}/')
                print(f"Created directory {dir} in bucket {bucket}")
            except Exception as e:
                print(f"Error creating directory {dir} in bucket {bucket}: {str(e)}")

if __name__ == "__main__":
    setup_minio_buckets()
