"""EventFlow - Real-time Event Streaming Platform."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from eventflow.core.config import settings
from eventflow.api.routes import router
from eventflow.api.websockets import websocket_manager

logger = logging.getLogger("eventflow.augur")

_augur_client = None


def _init_augur():
    global _augur_client
    hub_url = os.environ.get("AUGUR_URL", "")
    if not hub_url:
        return
    try:
        from augur_client import AugurClient

        _augur_client = AugurClient(
            hub_url=hub_url,
            agent_name=os.environ.get("AUGUR_AGENT_NAME", "eventflow"),
            agent_type=os.environ.get("AUGUR_AGENT_TYPE", "eventflow"),
            api_key=os.environ.get("AUGUR_API_KEY", ""),
            heartbeat_interval=int(os.environ.get("AUGUR_HEARTBEAT_INTERVAL", "30")),
        )
        _augur_client.register(name=_augur_client.agent_name, agent_type=_augur_client.agent_type)
        _augur_client.start_heartbeat()
        logger.info("Registered with Augur hub, heartbeat started")
    except ImportError:
        logger.debug("augur-client not installed")
    except Exception as e:
        logger.warning("Augur init failed: %s", e)


def push_to_augur(event_type, severity, title, payload=None, tags=None):
    if not _augur_client:
        return False
    try:
        _augur_client.push_event(
            event_type=event_type,
            severity=severity,
            source="eventflow",
            title=title,
            payload=payload or {},
            tags=tags or ["eventflow"],
        )
        return True
    except Exception as e:
        logger.debug("Augur push failed: %s", e)
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    _init_augur()
    logging.info("Starting EventFlow...")
    await websocket_manager.connect_redis()
    yield
    logging.info("Shutting down EventFlow...")
    await websocket_manager.disconnect_redis()
    if _augur_client:
        try:
            _augur_client.stop_heartbeat()
        except Exception:
            pass


app = FastAPI(
    title="EventFlow API",
    description="Real-time event streaming and processing platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "EventFlow",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "redis": websocket_manager.redis_connected}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


def run_server():
    """CLI entry point for `eventflow` command."""
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)