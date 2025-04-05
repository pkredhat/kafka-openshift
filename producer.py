import os
import sys
import asyncio
import argparse
from aiokafka import AIOKafkaProducer

async def produce(topic: str):
    print("Starting Kafka Producer...")
    bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS")

    if not bootstrap_servers:
        print("KAFKA_BOOTSTRAP_SERVERS environment variable is not set.")
        return

    print(f"KAFKA_BOOTSTRAP_SERVERS: {bootstrap_servers}")
    print(f"Producing messages to Kafka topic: {topic}")

    producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
    await producer.start()
    try:
        print("Type your message and press Enter (type 'exit' to quit):")
        loop = asyncio.get_running_loop()
        while True:
            print("> ", end="", flush=True)
            message = await loop.run_in_executor(None, sys.stdin.readline)
            message = message.strip()
            if not message:
                continue
            if message.lower() == "exit":
                break
            try:
                result = await producer.send_and_wait(topic, message.encode('utf-8'))
                print(f"✅ Delivered message to {result.topic}-{result.partition}@{result.offset}")
            except Exception as e:
                print(f"❌ Delivery failed: {e}")
    finally:
        await producer.stop()
        print("Kafka producer stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Async Kafka producer")
    parser.add_argument("--topic", "-t", required=True, help="Kafka topic to produce to")
    args = parser.parse_args()

    asyncio.run(produce(args.topic))