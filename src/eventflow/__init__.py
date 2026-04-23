"""EventFlow - Real-time Event Streaming Platform."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from eventflow.core.config import settings
from eventflow.api.routes import router
from eventflow.api.websockets import websocket_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logging.info("Starting EventFlow...")
    await websocket_manager.connect_redis()
    yield
    logging.info("Shutting down EventFlow...")
    await websocket_manager.disconnect_redis()


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