from typing import List, Dict, Any, Optional
from app.database.supabase import get_supabase_client
from app.features.prediction.repository import _local_predictions_store
from app.core.logging import logger

class HistoryRepository:
    def __init__(self):
        self.supabase = get_supabase_client()

    async def get_user_history(self, user_id: str = "user_default_001") -> List[Dict[str, Any]]:
        if self.supabase is not None:
            try:
                res = self.supabase.table("predictions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
                if res.data is not None:
                    return res.data
            except Exception as e:
                logger.warning(f"Supabase history query failed: {e}. Falling back to local predictions store.")

        # Local fallback store + default mock items if empty
        user_items = [p for p in _local_predictions_store if p.get("user_id") == user_id or user_id == "user_default_001"]
        if not user_items:
            # Provide initial seed item for Phase 2 demonstration
            user_items = [
                {
                    "id": "pred_demo_001",
                    "user_id": user_id,
                    "module": "XRAY",
                    "disease": "Normal",
                    "confidence": 0.9450,
                    "image_url": "/static/uploads/sample_xray.png",
                    "heatmap_url": "/static/uploads/sample_xray.png?heatmap=true",
                    "created_at": "2026-08-06T10:00:00Z"
                }
            ]
        return user_items

    async def get_prediction_by_id(self, prediction_id: str) -> Optional[Dict[str, Any]]:
        if self.supabase is not None:
            try:
                res = self.supabase.table("predictions").select("*").eq("id", prediction_id).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
            except Exception as e:
                logger.warning(f"Supabase prediction lookup failed: {e}.")

        for p in _local_predictions_store:
            if p.get("id") == prediction_id:
                return p
        if prediction_id == "pred_demo_001":
            return {
                "id": "pred_demo_001",
                "user_id": "user_default_001",
                "module": "XRAY",
                "disease": "Normal",
                "confidence": 0.9450,
                "image_url": "/static/uploads/sample_xray.png",
                "heatmap_url": "/static/uploads/sample_xray.png?heatmap=true",
                "created_at": "2026-08-06T10:00:00Z"
            }
        return None
