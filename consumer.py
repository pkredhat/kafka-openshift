import os
import asyncio
import argparse
from aiokafka import AIOKafkaConsumer
import uuid

async def consume(topic: str):
    # Read environment variable for bootstrap servers.
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    
    # Use a unique group id for each run
    group_id = f"test-group-{uuid.uuid4()}"
    
    if not bootstrap_servers:
        print("KAFKA_BOOTSTRAP_SERVERS environment variable is not set.")
        return

    print(f"KAFKA_BOOTSTRAP_SERVERS: {bootstrap_servers}")

    # Create an AIOKafkaConsumer instance with your config.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_offset_reset='earliest'
    )

    # Start the consumer to connect to Kafka.
    await consumer.start()
    try:
        print(f"Subscribed to {topic}, waiting for messages (async)...")
        # `async for` automatically polls for new messages in the background.
        async for msg in consumer:
            print(f"Received: {msg.value.decode('utf-8')}")
    finally:
        # This ensures offsets are committed (if enabled) and resources closed.
        await consumer.stop()
        print("Kafka consumer stopped.")

if __name__ == "__main__":
    # Prompt the user for a Kafka topic. If none is entered, default to 'test-topic'.
    user_topic = input("Enter Kafka topic (default 'test-topic'): ")
    topic = user_topic.strip() or "test-topic"
    try:
        asyncio.run(consume(topic))
    except KeyboardInterrupt:
        pass