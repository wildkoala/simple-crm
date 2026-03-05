import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import engine, SessionLocal
from app.models.models import Base
from app.routers import auth, contacts, communications, contracts, contacts_followup, users
from app.seed_data import seed_database

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Pretorin CRM API",
    description="API for managing sales contacts and government contract opportunities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
    )

# Disable favicon
@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return {"detail": "Not Found"}

# Configure CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
allowed_origins = [frontend_url]
extra_origins = os.getenv("EXTRA_CORS_ORIGINS", "")
if extra_origins:
    allowed_origins.extend(o.strip() for o in extra_origins.split(",") if o.strip())
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Include routers - specific paths before parameterized ones
app.include_router(auth.router)
app.include_router(contacts_followup.router)
app.include_router(contacts.router)
app.include_router(communications.router)
app.include_router(contracts.router)
app.include_router(users.router)


@app.get("/")
def root():
    """API root endpoint"""
    return {
        "message": "Pretorin CRM API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
