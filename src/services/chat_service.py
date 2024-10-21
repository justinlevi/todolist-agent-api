import time
import uuid
from src.logger import get_logger
from typing import List, Optional, AsyncGenerator, Union
from src.models.chat import (
    Model,
    ChatCompletionRequest,
    ChatCompletionResponse,
    Message,
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionChunkDelta,
    ChatCompletionUsage,
    ChatCompletionChoice,
)
from src.services.assistant_service import AssistantService
from src.utils.input_validation import validate_input

logger = get_logger()

assistant_service = AssistantService()


async def get_models() -> List[Model]:
    return [
        Model(id="agent", object="model", created=1677610602, owned_by="justinlevi"),
    ]


async def get_model_by_id(model_id: str) -> Optional[Model]:
    models = await get_models()
    return next((model for model in models if model.id == model_id), None)


def create_chat_completion_chunk(
    model: str,
    content: Optional[str] = None,
    role: Optional[str] = None,
    finish_reason: Optional[str] = None,
) -> ChatCompletionChunk:
    return ChatCompletionChunk(
        id=str(uuid.uuid4()),
        object="chat.completion.chunk",
        created=int(time.time()),
        model=model,
        choices=[
            ChatCompletionChunkChoice(
                index=0,
                delta=ChatCompletionChunkDelta(content=content, role=role),
                finish_reason=finish_reason,
            )
        ],
    )


async def generate_chat_completion(
    request: ChatCompletionRequest,
) -> Union[ChatCompletionResponse, AsyncGenerator[ChatCompletionChunk, None]]:
    messages = request.messages

    # Apply input guardrails
    is_valid, reason = validate_input(messages[-1].content)
    logger.info(f"Input validation: {is_valid}, reason: {reason}")

    if request.stream:

        async def stream_response():

            if not is_valid:
                content = (
                    "I'm sorry, due to system guardrails, I can't process that request. Please rephrase or ask something else related to medical office tasks."
                    if reason == "jailbreak"
                    else "I'm sorry, we've detected language that's not appropriate for this service. Please rephrase or ask something else related to medical office tasks."
                )
                yield create_chat_completion_chunk(
                    request.model, content=content, role="assistant"
                )
            else:
                response = assistant_service.run_conversation(messages, stream=True)
                for chunk in response:
                    yield create_chat_completion_chunk(
                        request.model, content=chunk.content, role="assistant"
                    )

            # Final chunk to indicate completion
            yield create_chat_completion_chunk(request.model, finish_reason="stop")

        return stream_response()
    else:
        if not is_valid:
            content = (
                "I'm sorry, due to system guardrails, I can't process that request. Please rephrase or ask something else appropriate for this service."
                if reason == "jailbreak"
                else "I'm sorry, we've detected language that's not appropriate for this service. Please rephrase or ask something else appropriate for this service."
            )
        else:
            response = assistant_service.run_conversation(messages)
            content = response.messages[-1].content
        return ChatCompletionResponse(
            id=str(uuid.uuid4()),
            object="chat.completion",
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=Message(
                        role="assistant",
                        content=content,
                    ),
                    finish_reason="stop",
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=0,
                completion_tokens=0,
                total_tokens=0,
                prompt_tokens_details={"cached_tokens": 0},
                completion_tokens_details={"reasoning_tokens": 0},
            ),
        )


async def chat_completion(
    request: ChatCompletionRequest,
) -> Union[ChatCompletionResponse, AsyncGenerator[ChatCompletionChunk, None]]:
    return await generate_chat_completion(request)
