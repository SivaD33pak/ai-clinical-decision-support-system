import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logging import logger

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"{request.method} {request.url.path} - Status: {response.status_code} - Duration: {process_time_ms:.2f}ms"
        )
        response.headers["X-Process-Time"] = f"{process_time_ms:.2f}ms"
        return response
