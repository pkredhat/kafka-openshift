import os
import asyncio
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from aiokafka import AIOKafkaConsumer

app = FastAPI(title="Real-Time Kafka Consumer")

# Mount the public folder at /static (to serve CSS, images, etc.)
app.mount("/static", StaticFiles(directory="public"), name="static")

# List to hold active WebSocket connections
active_connections: List[WebSocket] = []

# Global variables for topic management
current_topic = "test-topic"
consumer_task = None

# Function to run the Kafka consumer on a given topic
async def consume_kafka_messages(topic: str):
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        group_id="my-realtime-consumer-group",
        auto_offset_reset="earliest"
    )
    await consumer.start()
    print(f"Kafka consumer started, subscribed to topic='{topic}'")
    try:
        async for msg in consumer:
            message_str = msg.value.decode("utf-8")
            disconnected = []
            for conn in active_connections:
                try:
                    await conn.send_text(message_str)
                except Exception as e:
                    print(f"Failed to send message: {e}")
                    disconnected.append(conn)
            for d in disconnected:
                if d in active_connections:
                    active_connections.remove(d)
    finally:
        await consumer.stop()
        print("Kafka consumer stopped.")

# Data model for the topic change request
class TopicChange(BaseModel):
    topic: str

# Endpoint to change the Kafka topic
@app.post("/change_topic")
async def change_topic(topic_change: TopicChange):
    global current_topic, consumer_task
    new_topic = topic_change.topic.strip()
    if not new_topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty")
    if new_topic == current_topic:
        return {"message": "Topic unchanged"}
    # Cancel the current consumer task if it exists
    if consumer_task:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            print("Previous consumer task cancelled")
    current_topic = new_topic
    consumer_task = asyncio.create_task(consume_kafka_messages(current_topic))
    return {"message": f"Topic changed to {new_topic}"}

# Serve index.html at the root
@app.get("/")
async def read_index():
    from pathlib import Path
    index_file = Path("public") / "index.html"
    if not index_file.exists():
        return HTMLResponse("<h1>index.html not found</h1>", status_code=404)
    return HTMLResponse(index_file.read_text(encoding="utf-8"))

# WebSocket endpoint for real-time messages
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # We don't expect messages from the client here; this keeps the connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# On startup, launch the Kafka consumer
@app.on_event("startup")
async def startup_event():
    global consumer_task
    consumer_task = asyncio.create_task(consume_kafka_messages(current_topic))
    print("Startup event: Kafka consumer task created.")
