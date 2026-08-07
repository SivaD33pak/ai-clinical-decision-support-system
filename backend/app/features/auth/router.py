from fastapi import APIRouter, Depends, status
from app.features.auth.schemas import LoginRequest, RegisterRequest, AuthResponse
from app.features.auth.service import AuthService
from app.core.responses import APIResponse
from app.dependencies.deps import get_auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=APIResponse[AuthResponse], status_code=status.HTTP_200_OK)
async def login(request: LoginRequest, service: AuthService = Depends(get_auth_service)):
    result = await service.login(request)
    return APIResponse.ok(data=result, message="Authentication successful")

@router.post("/register", response_model=APIResponse[AuthResponse], status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    result = await service.register(request)
    return APIResponse.ok(data=result, message="User registration successful")
