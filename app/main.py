# app/main.py

from fastapi import FastAPI
from app.core.config import settings
import uvicorn
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware 

# --- IMPORTS FOR RATE LIMITING ---
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

# Import routers and DB tools
from app.database.database import create_db_and_tables
from app.api.v1.agent_router import router as agent_router 
from app.api.v1.auth_router import router as auth_router

# --- Application Lifespan Context ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events.
    Startup: Ensures database tables are created.
    """
    print("[STARTUP] Checking database tables...")
    create_db_and_tables() 
    print("[STARTUP] Database readiness complete.")
    yield

# --- FastAPI Application Initialization ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version="1.0.0",
    debug=settings.DEBUG_MODE,
    lifespan=lifespan 
)

# --- REGISTER LIMITER AND EXCEPTION HANDLER ---
# This connects the limiter to the app state
app.state.limiter = limiter 
# This tells FastAPI what to do when a limit is hit (return 429 error)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS MIDDLEWARE CONFIGURATION ---
origins = [
    "http://localhost",
    "http://localhost:8000",
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routers ---
app.include_router(agent_router, prefix=settings.API_V1_STR, tags=["agent"])
app.include_router(auth_router, prefix=settings.API_V1_STR + "/auth", tags=["auth"])

# --- Uvicorn Server Runner ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)