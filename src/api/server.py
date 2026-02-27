import json
import logging
import threading
from typing import Optional

from fastapi import FastAPI
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from pathway_app.config import KAFKA_BOOTSTRAP

# ---------------------------------------
# Logging Configuration
# ---------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("PredictionAPI")

# ---------------------------------------
# FastAPI App
# ---------------------------------------

app = FastAPI(title="Prediction API")

# Shared in-memory state
latest_data: Optional[dict] = None
consumer: Optional[KafkaConsumer] = None
consumer_thread: Optional[threading.Thread] = None
running = True


# ---------------------------------------
# Kafka Consumer Worker
# ---------------------------------------

def consume_predictions() -> None:
    global latest_data, consumer, running

    try:
        consumer = KafkaConsumer(
            "prediction_topic",
            bootstrap_servers=KAFKA_BOOTSTRAP,
            auto_offset_reset="latest",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            enable_auto_commit=True,
            group_id="prediction-api-group",
        )

        logger.info("✅ Connected to Kafka")

        while running:
            for message in consumer:
                latest_data = message.value
                logger.info("Received prediction: %s", latest_data)
                if not running:
                    break

    except NoBrokersAvailable:
        logger.error("❌ Kafka not available at %s", KAFKA_BOOTSTRAP)

    except Exception as e:
        logger.exception("Kafka consumer error: %s", e)


# ---------------------------------------
# FastAPI Lifecycle Events
# ---------------------------------------

@app.on_event("startup")
def startup_event() -> None:
    global consumer_thread
    logger.info("🚀 Starting Kafka Consumer Thread")
    consumer_thread = threading.Thread(target=consume_predictions, daemon=True)
    consumer_thread.start()


@app.on_event("shutdown")
def shutdown_event() -> None:
    global running, consumer
    logger.info("🛑 Shutting down API...")
    running = False
    if consumer:
        consumer.close()


# ---------------------------------------
# API Endpoint
# ---------------------------------------

@app.get("/latest")
def get_latest() -> dict:
    """
    Returns the latest prediction received from Kafka.
    """
    if latest_data is None:
        return {"message": "No prediction received yet"}

    return latest_data