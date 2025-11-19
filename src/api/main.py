"""
FastAPI application for Tournament Director.

Provides REST API for tournament management across multiple TCG formats,
with focus on Magic: The Gathering Pauper tournaments.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routers import (
    formats,
    health,
    matches,
    players,
    registrations,
    rounds,
    tournaments,
    venues,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager for startup and shutdown events.

    Handles initialization and cleanup of resources like database connections.
    """
    # Startup
    print("🚀 Tournament Director API starting...")

    # TODO: Initialize database connection pool when database backend is implemented
    # await app.state.db.connect()

    yield

    # Shutdown
    print("👋 Tournament Director API shutting down...")

    # TODO: Close database connections when database backend is implemented
    # await app.state.db.disconnect()


# Create FastAPI application
app = FastAPI(
    title="Tournament Director API",
    description=(
        "REST API for tournament management supporting multiple TCG formats. "
        "Built with async-first architecture and type-safe Pydantic models."
    ),
    version="0.1.0",
    contact={
        "name": "Vibe-Coder",
        "email": "vibecoder.1.z3r0@gmail.com",
    },
    license_info={
        "name": "MIT / Vibe-Coder License (VCL-0.1-Experimental)",
        "url": "https://github.com/vibecoder-1z3r0/tournament-director/blob/main/LICENSE",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(players.router, prefix="/players", tags=["Players"])
app.include_router(venues.router, prefix="/venues", tags=["Venues"])
app.include_router(formats.router, prefix="/formats", tags=["Formats"])
app.include_router(tournaments.router, tags=["Tournaments"])
app.include_router(registrations.router, tags=["Registrations"])
app.include_router(rounds.router, tags=["Rounds"])
app.include_router(matches.router, tags=["Matches"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions gracefully."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type": type(exc).__name__,
                "message": str(exc),
                "detail": "An internal server error occurred",
            }
        },
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Tournament Director API",
        "version": "0.1.0",
        "description": "REST API for tournament management",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }
