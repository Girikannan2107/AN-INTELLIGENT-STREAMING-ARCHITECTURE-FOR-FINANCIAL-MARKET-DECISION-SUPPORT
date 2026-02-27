import json
import logging
import threading
from typing import Optional

from fastapi import FastAPI
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable

from pathway_app.config import KAFKA_BOOTSTRAP


# =====================================================
# Logging Configuration
# =====================================================
# Centralized logging setup for structured monitoring.
# Using INFO level for production visibility without verbosity.
# This can be extended to JSON logging in distributed systems.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("PredictionAPI")


# =====================================================
# FastAPI Application Initialization
# =====================================================
# The API acts as a lightweight service layer
# over a Kafka streaming pipeline.
# It exposes the most recent prediction via REST.
app = FastAPI(title="Prediction API")


# =====================================================
# Shared In-Memory State
# =====================================================
# latest_data:
#   Acts as a temporary cache storing the most recent
#   prediction received from Kafka.
#
# NOTE:
#   Since this runs in a single-process FastAPI app
#   with a background thread, this shared variable
#   is safe for simple read/write usage.
#
#   For production-scale systems (multi-worker),
#   Redis or an external cache should be used instead.
latest_data: Optional[dict] = None

# Kafka consumer instance (initialized at startup)
consumer: Optional[KafkaConsumer] = None

# Dedicated background thread for streaming consumption
consumer_thread: Optional[threading.Thread] = None

# Control flag for graceful shutdown
running = True


# =====================================================
# Kafka Consumer Worker
# =====================================================
def consume_predictions() -> None:
    """
    Background worker function responsible for:
    1. Connecting to Kafka
    2. Subscribing to 'prediction_topic'
    3. Continuously consuming streaming predictions
    4. Updating the in-memory cache

    This function runs in a daemon thread so that:
    - It does not block FastAPI's main event loop
    - It terminates automatically when the application exits
    """
    global latest_data, consumer, running

    try:
        # Initialize Kafka Consumer with safe defaults
        consumer = KafkaConsumer(
            "prediction_topic",
            bootstrap_servers=KAFKA_BOOTSTRAP,
            auto_offset_reset="latest",  # Consume only new messages
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            enable_auto_commit=True,     # Automatically commit offsets
            group_id="prediction-api-group",  # Consumer group for scaling
        )

        logger.info("✅ Connected to Kafka at %s", KAFKA_BOOTSTRAP)

        # Continuous polling loop
        # This keeps the API synchronized with real-time predictions
        while running:
            for message in consumer:
                # Update shared state with latest prediction
                latest_data = message.value

                # Structured logging improves observability
                logger.info("Received prediction: %s", latest_data)

                # Graceful shutdown check
                if not running:
                    break

    except NoBrokersAvailable:
        # Explicit handling improves production reliability
        logger.error("❌ Kafka not available at %s", KAFKA_BOOTSTRAP)

    except Exception as e:
        # Catch-all to prevent silent thread crashes
        logger.exception("Kafka consumer error: %s", e)


# =====================================================
# FastAPI Lifecycle Events
# =====================================================

@app.on_event("startup")
def startup_event() -> None:
    """
    Triggered when FastAPI application starts.

    Responsibilities:
    - Spawn Kafka consumer thread
    - Ensure non-blocking startup
    """
    global consumer_thread

    logger.info("🚀 Starting Kafka Consumer Thread")

    consumer_thread = threading.Thread(
        target=consume_predictions,
        daemon=True,  # Ensures thread exits with main process
    )
    consumer_thread.start()


@app.on_event("shutdown")
def shutdown_event() -> None:
    """
    Triggered when application shuts down.

    Responsibilities:
    - Signal background thread to stop
    - Close Kafka connection gracefully
    """
    global running, consumer

    logger.info("🛑 Shutting down API...")
    running = False

    if consumer:
        consumer.close()
        logger.info("Kafka consumer closed successfully")


# =====================================================
# REST API Endpoint
# =====================================================

@app.get("/latest")
def get_latest() -> dict:
    """
    GET /latest

    Returns:
        dict: The most recent prediction received from Kafka.

    Design Pattern:
        - Acts as a thin API layer over streaming backend
        - Avoids heavy computation inside request lifecycle
        - Maintains low response latency
    """
    if latest_data is None:
        # Explicit response improves client clarity
        return {"message": "No prediction received yet"}

    return latest_data
