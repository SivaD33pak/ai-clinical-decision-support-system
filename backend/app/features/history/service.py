from app.features.history.repository import HistoryRepository
from app.features.history.schemas import HistoryItemResponse, HistoryListResponse
from app.core.exceptions import NotFoundException

class HistoryService:
    def __init__(self, repository: HistoryRepository):
        self.repository = repository

    async def get_history(self, user_id: str = "user_default_001") -> HistoryListResponse:
        items_data = await self.repository.get_user_history(user_id)
        items = [HistoryItemResponse(**item) for item in items_data]
        return HistoryListResponse(total_count=len(items), items=items)

    async def get_history_detail(self, prediction_id: str) -> HistoryItemResponse:
        item_data = await self.repository.get_prediction_by_id(prediction_id)
        if not item_data:
            raise NotFoundException(f"Prediction record '{prediction_id}' not found.")
        return HistoryItemResponse(**item_data)
