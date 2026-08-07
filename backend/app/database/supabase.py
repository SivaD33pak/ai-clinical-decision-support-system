from typing import Optional
from supabase import create_client, Client
from app.core.config import settings
from app.core.logging import logger

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Optional[Client]:
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY or "your-project" in settings.SUPABASE_URL:
        logger.info("Supabase credentials not configured in .env. Running persistence in Mock Fallback Mode.")
        return None

    try:
        _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        logger.info("Successfully initialized Supabase client connection.")
        return _supabase_client
    except Exception as e:
        logger.warning(f"Failed to connect to Supabase: {e}. Falling back to Mock Persistence Mode.")
        return None
