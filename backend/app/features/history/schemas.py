from pydantic import BaseModel
from typing import Optional, List

class HistoryItemResponse(BaseModel):
    id: str
    user_id: str
    module: str
    disease: str
    confidence: float
    image_url: str
    heatmap_url: Optional[str] = None
    created_at: str

class HistoryListResponse(BaseModel):
    total_count: int
    items: List[HistoryItemResponse]
