# EventFlow

A production-ready real-time event streaming and processing platform built with FastAPI, Redis, and PostgreSQL.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal?logo=fastapi&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-4169E1?logo=postgresql&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green)

---

## Overview

EventFlow is an event-driven data processing platform designed for real-time event ingestion, streaming, and analytics. It provides a scalable architecture for handling high-volume event streams with WebSocket support for live updates.

### Key Features

- **Real-time Event Ingestion** - POST events to the API for immediate processing
- **WebSocket Streaming** - Live event updates pushed to connected clients
- **Redis Pub/Sub** - Fast message broadcasting between services
- **PostgreSQL Storage** - Persistent event storage with async operations
- **Event Statistics** - Real-time metrics on event throughput and status

---

## Architecture

```
┌─────────┐     ┌──────────┐     ┌─────────────┐
│  Client │────▶│  FastAPI │────▶│  PostgreSQL │
│ (REST)  │     │   API    │     │  (Storage)  │
└─────────┘     └────┬─────┘     └─────────────┘
                     │
              ┌──────┴──────┐
              │   Redis     │
              │  Pub/Sub   │
              └──────┬──────┘
                     │
              ┌──────┴──────┐
              │  WebSocket │
              │  Clients   │
              └────────────┘
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/events` | Create a new event |
| GET | `/api/events` | List events |
| GET | `/api/events/{id}` | Get specific event |
| GET | `/api/stats` | Event statistics |
| WS | `/ws/{client_id}` | WebSocket for real-time updates |

---

## Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose

### Configuration

```bash
cp .env.example .env
# Edit .env with your settings
```

### Docker Compose

```bash
docker compose up -d
```

Access:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql://eventflow:eventflow@localhost:5432/eventflow |
| REDIS_URL | Redis connection string | redis://localhost:6379/0 |
| SECRET_KEY | JWT secret key | change-me-in-production |
| CORS_ORIGINS | Allowed CORS origins | * |

---

## Example Usage

### Create an Event

```bash
curl -X POST http://localhost:8000/api/events \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "user_action",
    "payload": {"action": "click", "page": "/home"},
    "user_id": "user123"
  }'
```

### Get Statistics

```bash
curl http://localhost:8000/api/stats
```

### WebSocket Connection

```python
import asyncio
import websockets

async def listen():
    async with websockets.connect("ws://localhost:8000/ws/client1") as ws:
        async for message in ws:
            print(message)

asyncio.run(listen())
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| API | FastAPI, Python 3.10+ |
| Database | PostgreSQL 16 |
| Cache/PubSub | Redis 7 |
| Auth | JWT (python-jose) |
| Deployment | Docker Compose |

---

## Project Structure

```
eventflow/
├── src/eventflow/
│   ├── api/          # Routes and WebSocket
│   ├── core/         # Configuration
│   ├── ingestion/    # Event management
│   └── models/       # Pydantic schemas
├── tests/            # Unit tests
├── docker/           # Docker configuration
└── pyproject.toml   # Dependencies
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.