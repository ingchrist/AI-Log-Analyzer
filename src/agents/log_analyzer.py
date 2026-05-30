from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, ToolMessage
from ..models.factory import create_model
from ..tools import get_all_tools, requires_approval
from ..utils.response import extract_response_text
from ..config import Config

class LogAnalyzerAgent:
    def __init__(self, incident_context: str = ""):
        self.model = create_model()
        self.tools = get_all_tools()
        self.llm = self.model.get_llm_with_tools(self.tools)

        prompt_text = Config.get_system_prompt()
        if incident_context:
            prompt_text += "\n\n" + incident_context

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_text),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

    def process_query(self, user_input: str, chat_history: list) -> str:
        # Build a set of approved (tool_name, frozen_args) pairs from this message.
        # A bare yes/confirm approves any single pending action in this turn.
        user_lower = user_input.lower().strip()
        global_confirm = user_lower in ["yes", "y", "confirm"]

        # Track per-call approvals keyed by tool_call_id so each destructive
        # action must be individually authorized.
        approved_ids: set = set()

        messages = self.prompt.format_messages(chat_history=chat_history, input=user_input)
        response = self.llm.invoke(messages)

        for _ in range(Config.MAX_ITERATIONS):
            if not getattr(response, "tool_calls", None):
                return extract_response_text(response)

            tool_msgs = []
            pending_approvals = [
                tc for tc in response.tool_calls
                if requires_approval(tc["name"]) and tc["id"] not in approved_ids
            ]

            # If user sent a global confirm and there is exactly one pending
            # destructive action, approve it automatically.
            if global_confirm and len(pending_approvals) == 1:
                approved_ids.add(pending_approvals[0]["id"])
                global_confirm = False  # consume the confirmation

            for tc in response.tool_calls:
                if requires_approval(tc["name"]) and tc["id"] not in approved_ids:
                    res = (
                        f"Action '{tc['name']}' with args {tc['args']} is BLOCKED "
                        f"and requires explicit user confirmation. "
                        f"Please reply 'yes' or 'confirm' to authorize this specific action."
                    )
                else:
                    tool_func = next(
                        (t for t in self.tools if t.name == tc["name"]), None
                    )
                    if tool_func is None:
                        res = f"Error: Tool '{tc['name']}' not found."
                    else:
                        try:
                            res = str(tool_func.invoke(tc["args"]))
                        except Exception as e:
                            res = f"Error executing '{tc['name']}': {e}"

                tool_msgs.append(ToolMessage(content=res, tool_call_id=tc["id"]))

            messages.append(AIMessage(content=response.content, tool_calls=response.tool_calls))
            messages.extend(tool_msgs)
            response = self.llm.invoke(messages)

        return extract_response_text(response)
