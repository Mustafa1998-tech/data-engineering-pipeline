import json
import time
from kafka import KafkaProducer
import random
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Kafka producer with retries
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    retries=3,
    request_timeout_ms=30000
)

def generate_user_event():
    """Generate a detailed user event"""
    user_actions = ['play', 'pause', 'stop', 'seek', 'like', 'comment', 'rate', 'add_to_watchlist']
    countries = ['US', 'UK', 'CA', 'AU', 'IN', 'BR', 'DE', 'FR', 'ES', 'IT']
    devices = ['web', 'mobile', 'smart_tv', 'tablet']
    
    return {
        'user_id': f'user_{random.randint(1, 1000)}',
        'movie_id': f'movie_{random.randint(1, 10000)}',
        'action': random.choice(user_actions),
        'timestamp': datetime.now().isoformat(),
        'duration_seconds': random.randint(0, 3600),
        'country': random.choice(countries),
        'device': random.choice(devices),
        'platform': random.choice(['android', 'ios', 'web', 'tv']),
        'rating': random.randint(1, 5) if 'rate' in user_actions else None,
        'watchlist_added': True if 'add_to_watchlist' in user_actions else False
    }

def main():
    print("Starting Kafka producer...")
    topic = 'user_events'
    
    try:
        while True:
            try:
                event = generate_user_event()
                producer.send(topic, value=event)
                logging.info(f"Produced event: {event}")
                time.sleep(0.5)  # Produce events every 0.5 seconds
            except Exception as e:
                logging.error(f"Error producing event: {str(e)}")
                time.sleep(1)  # Wait before retry
    except KeyboardInterrupt:
        logging.info("\nStopping producer...")
    finally:
        producer.flush()
        producer.close()

if __name__ == "__main__":
    main()