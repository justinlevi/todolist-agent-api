from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from src.logger import get_logger
from pydantic import ValidationError
from src.models.chat import ChatCompletionRequest, ChatCompletionResponse
from src.services.chat_service import generate_chat_completion
from src.auth import get_api_key
from src.utils.validators import validate_model_availability
from src.config import settings
import json

router = APIRouter()
logger = get_logger()


@router.post("/v1/chat/completions", dependencies=[Depends(get_api_key)])
async def create_chat_completion(
    request: ChatCompletionRequest, api_key: str = Depends(get_api_key)
):
    """
    Generate a chat completion based on the provided messages and model.

    This endpoint takes a chat completion request containing a model ID and a list of messages,
    and returns a generated response from the specified language model. It supports both streaming
    and non-streaming responses.

    Args:
        request (ChatCompletionRequest): The request containing the model and messages for chat completion.

    Returns:
        Union[ChatCompletionResponse, StreamingResponse]: The generated chat completion response,
        either as a full response or a streaming response.

    Raises:
        HTTPException: If there's an error generating the chat completion or if the requested model
        is not available.

    Security:
        Requires a valid API key to be provided in the Authorization header.

    Example:
        Request body:
        {
            "model": "agent",
            "messages": [
                {"role": "user", "content": "Hello, how are you?"}
            ],
            "stream": false
        }
    """
    # logger.debug(f"Received chat completion request: {request}")
    # logger.debug(f"Current environment: {settings.ENVIRONMENT}")
    # logger.debug(f"API Key: {api_key}")
    # logger.debug(f"Allowed hosts: {settings.ALLOWED_HOSTS}")
    try:
        # logger.info("Chat completion requested")

        response = await generate_chat_completion(request)

        if request.stream:

            async def stream_generator():
                async for chunk in response:
                    yield f"data: {json.dumps(chunk.model_dump())}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(stream_generator(), media_type="text/event-stream")
        else:
            # logger.debug(f"Chat completion response: {response}")
            return JSONResponse(
                content=json.loads(json.dumps(response.model_dump(), indent=2)),
                media_type="application/json",
            )
    except ValidationError as ve:
        logger.error(f"Validation error: {str(ve)}")
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        logger.error(f"Error in chat completion: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
