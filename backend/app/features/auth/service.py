from app.features.auth.repository import AuthRepository
from app.features.auth.schemas import LoginRequest, RegisterRequest, AuthResponse, AuthUser
from app.core.exceptions import AuthenticationException

class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def login(self, request: LoginRequest) -> AuthResponse:
        user_data = await self.repository.authenticate_user(request.email, request.password)
        if not user_data:
            raise AuthenticationException("Invalid email or password")
            
        user = AuthUser(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"]
        )
        return AuthResponse(user=user, access_token=user_data.get("access_token"))

    async def register(self, request: RegisterRequest) -> AuthResponse:
        user_data = await self.repository.register_user(request.email, request.password, request.name)
        user = AuthUser(
            id=user_data["id"],
            email=user_data["email"],
            name=user_data["name"]
        )
        return AuthResponse(user=user, access_token=user_data.get("access_token"))
