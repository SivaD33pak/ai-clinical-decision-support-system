from app.features.auth.repository import AuthRepository
from app.features.auth.service import AuthService
from app.features.prediction.repository import StorageRepository, PredictionRepository
from app.features.prediction.service import PredictionService
from app.features.history.repository import HistoryRepository
from app.features.history.service import HistoryService

# Singletons / Repositories
_auth_repository = AuthRepository()
_storage_repository = StorageRepository()
_prediction_repository = PredictionRepository()
_history_repository = HistoryRepository()

# Service Providers
def get_auth_service() -> AuthService:
    return AuthService(repository=_auth_repository)

def get_prediction_service() -> PredictionService:
    return PredictionService(
        storage_repo=_storage_repository,
        prediction_repo=_prediction_repository
    )

def get_history_service() -> HistoryService:
    return HistoryService(repository=_history_repository)
