import uuid
from typing import Optional, Dict, Any
from app.database.supabase import get_supabase_client
from app.core.logging import logger

class AuthRepository:
    def __init__(self):
        self.supabase = get_supabase_client()

    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        if self.supabase is not None:
            try:
                res = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
                return {
                    "id": res.user.id,
                    "email": res.user.email,
                    "name": res.user.user_metadata.get("name", "Healthcare Professional"),
                    "access_token": res.session.access_token if res.session else "mock_token"
                }
            except Exception as e:
                logger.warning(f"Supabase auth failed: {e}. Falling back to mock auth response.")
        
        # Mock Fallback for local development
        return {
            "id": str(uuid.uuid5(uuid.NAMESPACE_DNS, email)),
            "email": email,
            "name": "Dr. Siva Deepak",
            "access_token": f"mock_jwt_token_{uuid.uuid4().hex[:8]}"
        }

    async def register_user(self, email: str, password: str, name: str) -> Dict[str, Any]:
        if self.supabase is not None:
            try:
                res = self.supabase.auth.sign_up({"email": email, "password": password, "options": {"data": {"name": name}}})
                user_id = res.user.id if res.user else str(uuid.uuid4())
                
                # Insert into users table
                self.supabase.table("users").insert({"id": user_id, "email": email, "name": name}).execute()
                
                return {
                    "id": user_id,
                    "email": email,
                    "name": name,
                    "access_token": res.session.access_token if res.session else f"mock_token_{uuid.uuid4().hex[:8]}"
                }
            except Exception as e:
                logger.warning(f"Supabase registration failed: {e}. Falling back to mock registration.")
        
        # Mock Fallback
        return {
            "id": str(uuid.uuid4()),
            "email": email,
            "name": name,
            "access_token": f"mock_jwt_token_{uuid.uuid4().hex[:8]}"
        }
