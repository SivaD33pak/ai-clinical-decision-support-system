from fastapi import APIRouter, Depends, status
from app.features.history.schemas import HistoryListResponse, HistoryItemResponse
from app.features.history.service import HistoryService
from app.core.responses import APIResponse
from app.dependencies.deps import get_history_service

router = APIRouter(prefix="/history", tags=["History"])

@router.get("", response_model=APIResponse[HistoryListResponse], status_code=status.HTTP_200_OK)
async def get_history(user_id: str = "user_default_001", service: HistoryService = Depends(get_history_service)):
    result = await service.get_history(user_id)
    return APIResponse.ok(data=result, message="Prediction history retrieved successfully")

@router.get("/{prediction_id}", response_model=APIResponse[HistoryItemResponse], status_code=status.HTTP_200_OK)
async def get_history_detail(prediction_id: str, service: HistoryService = Depends(get_history_service)):
    result = await service.get_history_detail(prediction_id)
    return APIResponse.ok(data=result, message="Prediction details retrieved successfully")
