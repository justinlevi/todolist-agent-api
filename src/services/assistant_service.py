from typing import Iterator, List, Dict, Any, Optional, Literal
from pydantic import BaseModel
from phi.agent.agent import Agent
from phi.run.response import RunResponse
from phi.model.message import Message as PhiMessage
from phi.model.openai.chat import OpenAIChat
from src.models.chat import Message


class AssistantService:
    def __init__(self):
        self.agent = Agent(
            model=OpenAIChat(id="gpt-4o"),
            markdown=True,
            debug_mode=True,
            telemetry=False,
        )

    def run_conversation(
        self,
        messages: List[Message] = [],
        stream: Literal[True] | Literal[False] = False,
    ) -> RunResponse | Iterator[RunResponse]:
        # convert our messages to phi messages
        phi_messages = [
            PhiMessage(role=msg.role, content=msg.content) for msg in messages
        ]

        return self.agent.run(messages=phi_messages, stream=stream)
