from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.responses import APIResponse
from app.core.exceptions import (
    AppException, app_exception_handler,
    validation_exception_handler, global_exception_handler
)
from app.database.supabase import get_supabase_client
from app.middleware.logging_middleware import RequestLoggingMiddleware

from app.features.auth.router import router as auth_router
from app.features.prediction.router import router as prediction_router
from app.features.history.router import router as history_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Sequence
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    
    # Initialize Supabase client
    supabase_client = get_supabase_client()
    if supabase_client is None:
        logger.info("Database running in local mock fallback mode.")
    
    yield
    
    # Shutdown Sequence
    logger.info(f"Shutting down {settings.APP_NAME}...")

# 1. Health Check Router Definition
health_router = APIRouter(tags=["Health Check"])

@health_router.get("/health", response_model=APIResponse[dict], status_code=status.HTTP_200_OK)
async def health_check():
    supabase_active = get_supabase_client() is not None
    return APIResponse.ok(
        data={
            "backend": "healthy",
            "database": "connected" if supabase_active else "mock_mode",
            "storage": "connected" if supabase_active else "local_disk",
            "ai_inference": "ready",
            "version": settings.APP_VERSION
        },
        message="Application healthy"
    )

@health_router.get("/", response_model=APIResponse[dict], status_code=status.HTTP_200_OK)
async def root_welcome():
    return APIResponse.ok(
        data={
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "api_version": settings.API_VERSION,
            "docs": "/docs"
        },
        message="Welcome to AI-CDSS API"
    )

# 2. FastAPI App Instance Initialization
app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API service for AI-powered Clinical Decision Support System",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 3. Configure Middlewares
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 5. Static files for uploaded images
app.mount("/static/uploads", StaticFiles(directory=settings.UPLOAD_DIRECTORY), name="uploads")

# 6. Register API v1 Routers
api_prefix = f"/api/{settings.API_VERSION}"
app.include_router(health_router, prefix=api_prefix)
app.include_router(auth_router, prefix=api_prefix)
app.include_router(prediction_router, prefix=api_prefix)
app.include_router(history_router, prefix=api_prefix)

# 7. Also expose top-level root & health check
app.include_router(health_router)
