from pathway_app.producers.market_producer import MarketProducer
import logging
from pathway_app.agents.news_agent import NewsAgent
from pathway_app.services.streaming_service import StreamingService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    agent = NewsAgent()
    service = StreamingService(agent)
    producer = MarketProducer()
    service.start()
    producer.start()
