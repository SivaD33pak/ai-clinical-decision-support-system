from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.responses import APIResponse
from app.core.logging import logger

class AppException(Exception):
    def __init__(self, message: str = "An internal error occurred", status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)

class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST)

class AuthenticationException(AppException):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED)

class InferenceException(AppException):
    def __init__(self, message: str = "AI inference execution failed"):
        super().__init__(message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def app_exception_handler(request: Request, exc: AppException):
    logger.error(f"AppException on {request.method} {request.url}: {exc.message}")
    response = APIResponse.error(message=exc.message)
    return JSONResponse(status_code=exc.status_code, content=response.model_dump())

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"ValidationError on {request.method} {request.url}: {exc.errors()}")
    errors = [f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()]
    response = APIResponse.error(message="Invalid request payload", errors=errors)
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=response.model_dump())

async def global_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Unhandled Exception on {request.method} {request.url}: {str(exc)}", exc_info=True)
    response = APIResponse.error(message="An unexpected server error occurred.")
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response.model_dump())
