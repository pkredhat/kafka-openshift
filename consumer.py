import os
import asyncio
from aiokafka import AIOKafkaConsumer
import uuid

async def consume():
    # Read environment variable for bootstrap servers.
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = "test-topic"
    #group_id = "test-group"
    group_id = f"test-group-{uuid.uuid4()}"
    
    if not bootstrap_servers:
        print("KAFKA_BOOTSTRAP_SERVERS environment variable is not set.")
        return

    print(f"KAFKA_BOOTSTRAP_SERVERS: {bootstrap_servers}")

    # Create an AIOKafkaConsumer instance with your config.
    consumer = AIOKafkaConsumer(
        topic,
        loop=asyncio.get_event_loop(),
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


# For local testing: run this file directly to start consuming
if __name__ == "__main__":
    try:
        asyncio.run(consume())
    except KeyboardInterrupt:
        pass
