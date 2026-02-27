import os

# Kafka
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
MARKET_TOPIC = os.getenv("MARKET_TOPIC", "market_topic")

# Alpha Vantage
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")

# Producer Settings
MARKET_FETCH_INTERVAL = 20