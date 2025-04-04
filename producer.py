import os
import sys
import asyncio
from aiokafka import AIOKafkaProducer

async def produce():
    print("Starting Kafka Producer...")
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")
    topic = "test-topic"

    if not bootstrap_servers:
        print("KAFKA_BOOTSTRAP_SERVERS environment variable is not set.")
        return

    print(f"KAFKA_BOOTSTRAP_SERVERS: {bootstrap_servers}")

    # Create and start the Kafka producer.
    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    await producer.start()
    try:
        print(f"Producing messages to Kafka topic: {topic}")
        print("Type your message and press Enter (type 'exit' to quit):")
        loop = asyncio.get_running_loop()
        while True:
            # Use run_in_executor to avoid blocking the event loop with input().
            print("> ", end="", flush=True)
            message = await loop.run_in_executor(None, sys.stdin.readline)
            message = message.strip()
            if not message:
                continue  # Ignore empty input.
            if message.lower() == "exit":
                break

            try:
                # Send the message asynchronously. Encode the string to bytes.
                result = await producer.send_and_wait(topic, message.encode('utf-8'))
                print(f"✅ Delivered message to {result.topic}-{result.partition}@{result.offset}")
            except Exception as e:
                print(f"❌ Delivery failed: {e}")
    finally:
        # Stop the producer to flush any pending messages.
        await producer.stop()
        print("Kafka producer stopped.")

if __name__ == "__main__":
    asyncio.run(produce())
