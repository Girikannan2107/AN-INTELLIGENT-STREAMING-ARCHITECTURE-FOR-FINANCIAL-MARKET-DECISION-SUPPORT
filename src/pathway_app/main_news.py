import logging
from pathway_app.config import KAFKA_BOOTSTRAP
from pathway_app.producers.news_producer import (
    KafkaNewsProducer,
    NewsProducerService,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    kafka_producer = KafkaNewsProducer(KAFKA_BOOTSTRAP)
    service = NewsProducerService(producer=kafka_producer)
    service.start()