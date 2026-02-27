System Architecture Documentation
1. Introduction

This document describes the architectural design of the AI-Powered Real-Time Market Intelligence Streaming System.

The system follows a distributed, event-driven microservices architecture designed for scalability, modularity, and real-time processing.

The architecture separates ingestion, processing, intelligence, and presentation layers to maintain clean separation of concerns.

2. Architectural Style

The system is built using:

Event-Driven Architecture

Microservices Architecture

Stream Processing Model

Clean Architecture Principles

Core design characteristics:

Loosely coupled services

Stateless processing components

Independent deployment units

Config-driven configuration

Service abstraction layers

3. High-Level Architecture
Market Producer ──┐
                  ├──► Kafka Topics ───► Pathway Engine ───► Prediction Topic
News Producer  ───┘                                │
                                                    ▼
                                              FastAPI Service
                                                    │
                                                    ▼
                                              Streamlit Dashboard

RAG Service (OpenAI GPT) ─────────────────────────► API Layer
4. Component Overview
4.1 Market Producer

Fetches stock price data from Alpha Vantage API

Publishes events to Kafka market_topic

Runs as an independent service

Responsibilities:

External API communication

Event formatting

Publishing to Kafka

4.2 News Producer

Streams market-related headlines

Publishes events to Kafka news_topic

Responsibilities:

Event generation

Topic publishing

Message serialization

4.3 Apache Kafka

Kafka serves as the event backbone.

Topics:

market_topic

news_topic

prediction_topic

Responsibilities:

Decoupling producers and consumers

High-throughput event streaming

Horizontal scalability

4.4 Pathway Streaming Engine

Consumes Kafka topics and performs:

Real-time transformation

Agent-based prediction logic

Signal generation

Outputs:

Prediction events to prediction_topic

Responsibilities:

Stream ingestion

Data transformation

Real-time analytics

Prediction generation

4.5 Agents Layer

Agents encapsulate business logic.

Examples:

NewsAgent (prediction logic)

VolatilityAgent (volatility scoring)

Design Principles:

Stateless computation

Domain modeling with dataclasses

Strong typing

Single responsibility

4.6 RAG Service

Implements Retrieval-Augmented Generation using OpenAI GPT.

Pipeline:

Query embedding

Context retrieval

GPT-based response generation

Responsibilities:

Contextual financial reasoning

Intelligent query handling

Integration with OpenAI API

4.7 FastAPI Service

Exposes REST endpoints:

GET /latest

POST /query

Responsibilities:

API routing

Request validation

Response formatting

Service orchestration

4.8 Streamlit Dashboard

Provides visualization for:

Live predictions

Confidence scores

RAG query responses

Responsibilities:

User interaction

API consumption

Metric display

5. Data Flow Sequence
Step 1: Data Ingestion

Market Producer fetches stock price.

News Producer generates headline event.

Events published to Kafka.

Step 2: Stream Processing

Pathway consumes Kafka topics.

Applies agent logic.

Generates prediction output.

Publishes to prediction_topic.

Step 3: API Exposure

FastAPI consumes prediction topic.

Exposes latest prediction via REST.

Step 4: Contextual Query

User submits query.

RAG service retrieves context.

GPT generates contextual answer.

Step 5: Visualization

Dashboard fetches API endpoints.

Displays predictions and AI responses.

6. Deployment Architecture

Deployment is managed via Docker Compose.

Services:

kafka

zookeeper

market_producer

news_producer

pathway_engine

api

rag_service

ui

Each service runs in its own container.

Benefits:

Isolation

Reproducibility

Environment consistency

Easy scaling

7. Design Principles Applied
7.1 Separation of Concerns

Each service handles one responsibility.

7.2 Dependency Injection

Services receive dependencies via constructor injection.

7.3 Domain Modeling

Use of dataclasses for strong typing and immutability.

7.4 Config-Driven Architecture

Environment variables control behavior.

7.5 Observability

Structured logging across services.

8. Scalability Considerations

The architecture supports horizontal scaling:

Kafka partitions for parallelism

Stateless API services

Independent scaling of producers

Independent scaling of RAG service

Future enhancements:

Vector database integration

Async Kafka consumers

Kubernetes orchestration

Load balancing layer

9. Security Considerations

Environment-based secret management

No hardcoded API keys

Container isolation

Stateless services

Future improvements:

API authentication

Rate limiting

HTTPS termination

Secret management integration
