/opt/kafka/bin/zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties
/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties/opt/kafka/bin/zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties
/opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.propertiesfrom pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, BooleanType
from pyspark.sql import Window
import sys

# Initialize Spark session with MinIO configuration
spark = SparkSession.builder\
    .appName("NetflixStreamProcessor")\
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,org.apache.hadoop:hadoop-aws:3.3.4")\
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin")\
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin")\
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000")\
    .config("spark.hadoop.fs.s3a.path.style.access", "true")\
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")\
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")\
    .getOrCreate()

# Define schema for incoming data
schema = StructType([
    StructField("user_id", StringType()),
    StructField("movie_id", StringType()),
    StructField("action", StringType()),
    StructField("timestamp", TimestampType()),
    StructField("duration_seconds", IntegerType()),
    StructField("country", StringType()),
    StructField("device", StringType()),
    StructField("platform", StringType()),
    StructField("rating", IntegerType()),
    StructField("watchlist_added", BooleanType())
])

# Read from Kafka
df = spark.readStream\
    .format("kafka")\
    .option("kafka.bootstrap.servers", "localhost:9092")\
    .option("subscribe", "user_events")\
    .option("startingOffsets", "latest")\
    .option("failOnDataLoss", "false")\
    .load()

# Parse JSON data
json_df = df.selectExpr("CAST(value AS STRING)")\
    .select(from_json(col("value"), schema).alias("data"))\
    .select("data.*")

# Process data
windowSpec = Window.partitionBy("user_id", "movie_id").orderBy("timestamp")

processed_df = json_df.withColumn("year", col("timestamp").cast("date"))\
    .withColumn("session_id", when(col("action") == "play", 1).otherwise(0))\
    .withColumn("session_id", sum("session_id").over(windowSpec))\
    .withColumn("session_duration", col("duration_seconds"))\
    .withColumn("country", col("country").cast("string"))\
    .withColumn("device", col("device").cast("string"))

# Aggregate metrics
agg_df = processed_df.groupBy("year", "movie_id", "country", "device")\
    .agg({
        "user_id": "count",
        "duration_seconds": "sum",
        "rating": "avg",
        "watchlist_added": "sum"
    })\
    .withColumnRenamed("count(user_id)", "total_views")\
    .withColumnRenamed("sum(duration_seconds)", "total_duration")\
    .withColumnRenamed("avg(rating)", "avg_rating")\
    .withColumnRenamed("sum(watchlist_added)", "watchlist_count")

# Write to MinIO (configured as S3)
query = agg_df.writeStream\
    .format("parquet")\
    .option("path", "s3a://data-lake/processed/analytics")\
    .option("checkpointLocation", "s3a://data-lake/checkpoints/analytics")\
    .partitionBy("year", "country", "device")\
    .outputMode("append")\
    .option("compression", "snappy")\
    .start()

# Start streaming query
try:
    query.awaitTermination()
except Exception as e:
    print(f"Error in streaming query: {str(e)}")
    sys.exit(1)