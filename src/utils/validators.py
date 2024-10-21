from typing import List
from src.services.chat_service import get_models
from src.models.chat import Model
from src.config import settings

async def validate_model_availability(model_id: str) -> bool:
    """
    Validate if the requested model is available.

    Args:
        model_id (str): The ID of the model to validate.

    Returns:
        bool: True if the model is available, False otherwise.
    """
    if settings.ENVIRONMENT == "test":
        return True
    available_models: List[Model] = await get_models()
    return any(model.id == model_id for model in available_models)