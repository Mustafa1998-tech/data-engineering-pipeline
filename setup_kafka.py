import os
import subprocess
import time

def setup_kafka():
    print("Starting Kafka setup...")
    
    # Create Kafka logs directory
    kafka_logs = os.path.join(os.getcwd(), "kafka", "logs")
    os.makedirs(kafka_logs, exist_ok=True)
    
    # Create Kafka configuration files
    with open("kafka\server.properties", "w") as f:
        f.write("broker.id=0\n"
                "listeners=PLAINTEXT://localhost:9092\n"
                "zookeeper.connect=localhost:2181\n"
                "log.dirs={}\n"
                "num.partitions=3\n"
                "delete.topic.enable=true\n"
                "auto.create.topics.enable=true\n"
                "offsets.topic.replication.factor=1\n"
                "transaction.state.log.replication.factor=1\n"
                "transaction.state.log.min.isr=1\n"
                "log.retention.hours=168\n"
                "log.segment.bytes=1073741824\n"
                "zookeeper.connection.timeout.ms=6000\n"
                "group.initial.rebalance.delay.ms=0\n"
                "confluent.support.customer.id=anonymous\n"
                "confluent.support.metrics.enable=false\n"
                .format(kafka_logs))
    
    with open("kafka\zookeeper.properties", "w") as f:
        f.write("dataDir={}/zookeeper\n"
                "clientPort=2181\n"
                "maxClientCnxns=0\n"
                "tickTime=2000\n"
                "initLimit=5\n"
                "syncLimit=2\n"
                .format(os.path.join(os.getcwd(), "kafka")))
    
    print("Kafka configuration files created successfully!")

def start_kafka():
    print("Starting Zookeeper...")
    subprocess.Popen(["kafka\bin\windows\zookeeper-server-start.bat", "kafka\zookeeper.properties"])\n    time.sleep(5)
    
    print("Starting Kafka broker...")
    subprocess.Popen(["kafka\bin\windows\kafka-server-start.bat", "kafka\server.properties"])\n    time.sleep(5)
    
    print("Kafka services started successfully!")

def create_topic():
    print("Creating Kafka topic...")
    subprocess.run(["kafka\bin\windows\kafka-topics.bat", 
                   "--create", 
                   "--topic", "user_events", 
                   "--bootstrap-server", "localhost:9092", 
                   "--partitions", "3", 
                   "--replication-factor", "1"])\n    print("Kafka topic created successfully!")

if __name__ == "__main__":
    setup_kafka()
    start_kafka()
    create_topic()
