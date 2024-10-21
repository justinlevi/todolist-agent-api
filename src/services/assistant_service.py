from typing import Iterator, List, Literal
from phi.agent.agent import Agent
from phi.run.response import RunResponse
from phi.model.message import Message as PhiMessage
from phi.model.openai.chat import OpenAIChat
from src.models.chat import Message

from services.todos.todos_service_sync import TodosServiceSync


class AssistantService:
    def __init__(self):
        todos_service = TodosServiceSync("sqlite:///./prisma/dev.db")

        self.agent = Agent(
            model=OpenAIChat(id="gpt-4o-mini"),
            markdown=True,
            debug_mode=True,
            telemetry=False,
            tools=[
                todos_service.get_todos,
                todos_service.create_todo,
                todos_service.update_todo,
                todos_service.toggle_todo,
                todos_service.delete_todo,
                todos_service.filter_todos,
            ],
            description="You are an intelligent assistant specialized in managing a todo list. Your primary function is to help users organize their tasks efficiently.",
            instructions=[
                "Use the provided todo list tools to manage tasks for the user.",
                "When asked about tasks or before performing any action, always use the get_todos tool to fetch the latest information.",
                "Create new tasks using the create_todo tool when the user wants to add an item to their list.",
                "Use the toggle_todo tool to mark individual tasks as complete or incomplete.",
                "Remove tasks from the list using the delete_todo tool when requested.",
                "Always confirm actions taken with the user and provide clear, concise responses.",
                "If asked about task details, provide information on task status, creation date, and any other relevant details.",
                "Offer suggestions for task organization and prioritization when appropriate.",
                "If the user asks for something unrelated to todo list management, politely redirect them to task-related queries or actions.",
                "Always follow up an action with a confirmation message to the user showing the result of the action.",
                "For multi-step operations, follow these guidelines:",
                "  1. To mark all todos as complete or incomplete:",
                "     a. Use get_todos to retrieve all current todos",
                "     b. Extract the IDs of todos that need to be updated",
                "     c. Use toggle_todo for each extracted ID",
                "     d. Confirm the action with a summary of changes",
                "  2. To delete multiple todos:",
                "     a. Use get_todos to retrieve all current todos",
                "     b. Extract the IDs of todos to be deleted based on user criteria",
                "     c. Use delete_todo for each extracted ID",
                "     d. Confirm the action with a summary of deletions",
                "  3. To reorganize or prioritize todos:",
                "     a. Use get_todos to retrieve all current todos",
                "     b. Analyze the list based on user requirements",
                "     c. Suggest a new order or priority",
                "     d. If changes are needed, use appropriate tools to implement them",
                "  4. For date-based queries (e.g., 'show me tasks due this week'):",
                "     a. Use get_todos to retrieve all current todos",
                "     b. Parse the creation dates and filter based on the query",
                "     c. Present the filtered list to the user",
                "  5. For complex searches or filters:",
                "     a. Use get_todos to retrieve all current todos",
                "     b. Apply the necessary filters or search criteria",
                "     c. Present the filtered results to the user",
                "Always break down complex user requests into a series of steps using the available tools.",
                "If a requested action is not directly supported by the tools, explain the limitation to the user and suggest alternative approaches.",
                "When in doubt about a user's intention, ask for clarification before performing any actions.",
                "Maintain context throughout the conversation and refer back to previous interactions when relevant.",
                # "Always display the todo list hierarchically, with children todos indented under their parent todos.",
            ],
            prevent_hallucinations=True,
            # reasoning=True,
            add_datetime_to_instructions=True,
            # show_tool_calls=True,
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
