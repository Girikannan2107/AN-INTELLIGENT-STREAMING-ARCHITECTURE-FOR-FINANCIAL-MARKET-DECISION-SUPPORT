<<<<<<< HEAD
AI-Powered Real-Time Market Intelligence Streaming System
1. Overview

This project is a distributed, real-time market intelligence platform built using Apache Kafka, Pathway, FastAPI, OpenAI, and Docker.

The system ingests live stock market data and streaming news headlines, processes them through a real-time streaming engine, applies AI-driven analytics, and generates predictive insights in an event-driven microservices architecture.

The platform is fully containerized and designed following clean architecture principles to ensure scalability, modularity, and maintainability.

2. Problem Statement

Financial markets generate high-frequency, high-volume data streams. Traditional batch processing systems are not suitable for:

Low-latency analytics

Real-time decision support

Context-aware sentiment analysis

Scalable event-driven processing

This system addresses those challenges by integrating:

Event streaming infrastructure

Real-time computation

AI-powered contextual intelligence

Microservice-based architecture

3. System Architecture
3.1 Core Components

Market Producer – Fetches live stock prices from Alpha Vantage

News Producer – Streams market-related headlines

Apache Kafka – Event streaming backbone

Pathway Engine – Real-time stream processing

Prediction Topic – Stores processed trading signals

FastAPI Service – Exposes REST APIs

RAG Service – GPT-based contextual intelligence

Streamlit Dashboard – Visualization layer

Docker Compose – Service orchestration

3.2 Data Flow

Market Producer fetches stock price data.

News Producer generates headline events.

Producers publish events to Kafka topics.

Pathway consumes Kafka streams and generates predictions.

Predictions are published to the prediction_topic.

FastAPI exposes prediction data via REST endpoints.

RAG service enhances contextual queries using OpenAI GPT.

Streamlit dashboard consumes API endpoints for visualization.

4. Technology Stack

Python 3.10+

Apache Kafka

Pathway Streaming Engine

FastAPI

OpenAI GPT API

Alpha Vantage API

Streamlit

Docker & Docker Compose

Pytest

5. Repository Structure
src/
  api/
    server.py
  pathway_app/
    agents/
    producers/
    services/
    config.py
    main.py
    main_news.py
  rag_service/
    openai_client.py
    rag_pipeline.py
    app.py
  ui/
    services/
    dashboard.py
tests/
docker/
docs/
docker-compose.yml
requirements.txt
README.md
6. Features

Real-time stock data ingestion

News sentiment-driven signal generation

Event-driven Kafka architecture

Pathway streaming computation engine

AI-powered contextual RAG system

REST API integration

Modular microservice design

Fully Dockerized deployment

Unit-tested core components

Clean architecture implementation

7. Environment Configuration

Create a .env file in the root directory:

OPENAI_API_KEY=your_openai_api_key
ALPHA_VANTAGE_KEY=your_alpha_vantage_key
KAFKA_BOOTSTRAP=kafka:9092

Do not commit .env to version control.

An .env.example file is provided for reference.

8. Installation and Execution
8.1 Option 1: Docker Deployment (Recommended)

Build and start all services:

docker-compose up --build

For detached mode:

docker-compose up -d --build

Access services:

FastAPI: http://localhost:8000

FastAPI Docs: http://localhost:8000/docs

Streamlit Dashboard: http://localhost:8501

Stop services:

docker-compose down

Clean restart:

docker-compose down -v
docker-compose build --no-cache
docker-compose up
8.2 Option 2: Local Development

Install dependencies:

pip install -r requirements.txt

Run FastAPI server:

uvicorn src.api.server:app --reload

Run Streamlit dashboard:

streamlit run src/ui/dashboard.py

Run Pathway streaming:

python -m src.pathway_app.main
9. API Documentation
9.1 GET /latest

Returns the most recent prediction.

Example response:

{
  "symbol": "AAPL",
  "price": 287.45,
  "recommendation": "BUY",
  "confidence": 0.82,
  "brokerage_cost": 12.45,
  "timestamp": 1772000123.45
}
9.2 POST /query

Performs GPT-based contextual analysis.

Request:

{
  "text": "Why did Apple stock increase?"
}

Response:

{
  "query": "...",
  "context": [...],
  "answer": "..."
}
10. Testing

Run unit tests:

pytest tests/

Test coverage includes:

Agent prediction logic

Streaming service

RAG pipeline

Core service components

11. Architectural Design Principles

Separation of concerns

Dependency injection

Domain-driven modeling

Service abstraction

Config-driven configuration

Structured logging

Stateless services

Scalable event-driven design

12. Future Enhancements

Vector database integration

Async Kafka consumers (aiokafka)

Streaming GPT responses

Prometheus metrics integration

Kubernetes deployment

CI/CD automation

Performance benchmarking

13. License

This project is licensed under the MIT License.

14. Author

Girikannan M P
=======
# AN-INTELLIGENT-STREAMING-ARCHITECTURE-FOR-FINANCIAL-MARKET-DECISION-SUPPORT
AI-powered real-time market intelligence platform built with Kafka, Pathway, FastAPI, and OpenAI. Streams live stock and news data, performs event-driven analytics, and generates predictive insights using a scalable microservices architecture.
>>>>>>> b48ec76e29b97d596d17458a6555d94d1ddc8b20
