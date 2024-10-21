from fastapi import APIRouter, HTTPException, Depends
from src.logger import get_logger
from src.models.chat import Model, ModelList
from src.services.chat_service import get_models, get_model_by_id
from src.config import settings
from src.auth import get_api_key

router = APIRouter()
logger = get_logger()

@router.get("/v1/models", dependencies=[Depends(get_api_key)], response_model=ModelList)
async def list_models():
    """
    Retrieve a list of all available language models.

    This endpoint returns information about all language models that are available for use with the API.

    Returns:
        ModelList: A list of Model objects containing information about each available model.

    Raises:
        HTTPException: If there's an error retrieving the list of models.

    Security:
        Requires a valid API key to be provided in the Authorization header.
    """
    try:
        logger.info("Models list requested")
        logger.debug(f"Current environment: {settings.ENVIRONMENT}")
        logger.debug(f"Allowed hosts: {settings.ALLOWED_HOSTS}")
        models = await get_models()
        logger.debug(f"Retrieved models: {models}")
        return ModelList(data=models)
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/v1/models/{model_id}", dependencies=[Depends(get_api_key)], response_model=Model)
async def get_model(model_id: str):
    """
    Retrieve details of a specific language model.

    Args:
        model_id (str): The ID of the model to retrieve.

    Returns:
        Model: Detailed information about the requested model.

    Raises:
        HTTPException: If the model is not found or there's an error retrieving the model details.
    """
    try:
        logger.info(f"Model details requested for {model_id}")
        model = await get_model_by_id(model_id)
        if model is None:
            raise HTTPException(status_code=404, detail="Model not found")
        return model
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving model {model_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
