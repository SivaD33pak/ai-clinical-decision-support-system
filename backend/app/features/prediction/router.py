from fastapi import APIRouter, Depends, UploadFile, File, status
from app.features.prediction.schemas import UploadResponse, PredictionRequest, PredictionResponse
from app.features.prediction.service import PredictionService
from app.core.responses import APIResponse
from app.dependencies.deps import get_prediction_service

router = APIRouter(prefix="/prediction", tags=["Prediction"])

@router.post("/upload", response_model=APIResponse[UploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(...), service: PredictionService = Depends(get_prediction_service)):
    result = await service.upload_image(file)
    return APIResponse.ok(data=result, message="Image uploaded successfully")

@router.post("", response_model=APIResponse[PredictionResponse], status_code=status.HTTP_200_OK)
async def create_prediction(request: PredictionRequest, service: PredictionService = Depends(get_prediction_service)):
    result = await service.predict(request)
    return APIResponse.ok(data=result, message="Disease prediction analysis completed")
