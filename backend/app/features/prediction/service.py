from fastapi import UploadFile
from app.features.prediction.repository import StorageRepository, PredictionRepository
from app.features.prediction.schemas import (
    UploadResponse, PredictionRequest, PredictionResponse, PredictionBreakdown
)
from ai_core.serving.inference_manager import inference_manager
from app.core.exceptions import ValidationException, NotFoundException, InferenceException

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

class PredictionService:
    def __init__(self, storage_repo: StorageRepository, prediction_repo: PredictionRepository):
        self.storage_repo = storage_repo
        self.prediction_repo = prediction_repo

    async def upload_image(self, file: UploadFile) -> UploadResponse:
        if not file.filename:
            raise ValidationException("File must have a valid filename")
            
        ext = f".{file.filename.split('.')[-1].lower()}" if "." in file.filename else ""
        if ext not in ALLOWED_EXTENSIONS:
            raise ValidationException(f"Unsupported file format '{ext}'. Allowed: JPEG, PNG.")

        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise ValidationException(f"File size exceeds maximum limit of 10MB.")

        upload_record = await self.storage_repo.save_uploaded_file(file.filename, contents)
        return UploadResponse(**upload_record)

    async def predict(self, request: PredictionRequest) -> PredictionResponse:
        upload_record = await self.storage_repo.get_upload_record(request.upload_id)
        if not upload_record:
            raise NotFoundException(f"Upload ID '{request.upload_id}' not found. Please upload image first.")

        image_path = upload_record["file_path"]
        
        # Call AI Inference Manager
        try:
            inference_result = await inference_manager.predict_xray(image_path)
        except Exception as e:
            raise InferenceException(f"Prediction engine failed: {str(e)}")

        prediction_data = {
            "user_id": request.user_id or "user_default_001",
            "module": request.module,
            "disease": inference_result.get("disease", "Normal"),
            "confidence": float(inference_result.get("confidence", 0.95)),
            "image_url": upload_record.get("public_url", ""),
            "heatmap_url": upload_record.get("public_url", "") + "?heatmap=true" if inference_result.get("heatmap_generated") else None
        }

        saved_record = await self.prediction_repo.save_prediction(prediction_data)

        breakdown = [
            PredictionBreakdown(disease=b["disease"], confidence=b["confidence"])
            for b in inference_result.get("predictions_breakdown", [])
        ]

        return PredictionResponse(
            prediction_id=saved_record["id"],
            user_id=saved_record["user_id"],
            module=saved_record["module"],
            disease=saved_record["disease"],
            confidence=saved_record["confidence"],
            image_url=saved_record["image_url"],
            heatmap_url=saved_record["heatmap_url"],
            predictions_breakdown=breakdown,
            created_at=saved_record["created_at"]
        )
