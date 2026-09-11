from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api.routes import (
    health,
    dashboard,
    stations,
    sections,
    assets,
    maintenance,
    trains,
    windows,
    blocks,
    contracts,
    freight,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize application tables and views safely on startup
    init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# CORS Middleware Setup
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/", summary="Root Endpoint")
def read_root():
    return {"message": "PlanRail API Service", "status": "online"}


# Include API v1 routers
prefix = settings.API_V1_STR
app.include_router(health.router, prefix=prefix, tags=["Health"])
app.include_router(dashboard.router, prefix=prefix, tags=["Dashboard"])
app.include_router(stations.router, prefix=prefix, tags=["Stations"])
app.include_router(sections.router, prefix=prefix, tags=["Sections"])
app.include_router(assets.router, prefix=prefix, tags=["Assets"])
app.include_router(maintenance.router, prefix=prefix, tags=["Maintenance"])
app.include_router(trains.router, prefix=prefix, tags=["Trains"])
app.include_router(windows.router, prefix=prefix, tags=["Windows & Traffic"])
app.include_router(blocks.router, prefix=prefix, tags=["Blocks"])
app.include_router(contracts.router, prefix=prefix, tags=["Advanced Services"])
app.include_router(freight.router, prefix=prefix, tags=["Freight Planning"])
