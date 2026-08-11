from pydantic import BaseModel, Field
from typing import Optional, List

class UploadResponse(BaseModel):
    upload_id: str
    filename: str
    file_path: str
    public_url: Optional[str] = None
    file_size_bytes: int

class PredictionRequest(BaseModel):
    upload_id: str
    user_id: Optional[str] = "user_default_001"
    module: str = Field(default="XRAY", description="Diagnostic module: XRAY, BLOOD, or SYMPTOMS")

class PredictionBreakdown(BaseModel):
    disease: str
    confidence: float

class PredictionResponse(BaseModel):
    prediction_id: str
    user_id: str
    module: str
    disease: str
    prediction: Optional[str] = None
    confidence: float
    confidence_formatted: Optional[str] = None
    model: Optional[str] = "Chest X-ray Model v1.0"
    disclaimer: Optional[str] = "⚠️ AI-assisted result. This system is not a replacement for professional medical diagnosis."
    image_url: str
    heatmap_url: Optional[str] = None
    predictions_breakdown: List[PredictionBreakdown] = Field(default_factory=list)
    created_at: str
