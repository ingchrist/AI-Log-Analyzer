from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, ToolMessage
from ..models.factory import create_model
from ..tools import get_all_tools, requires_approval
from ..utils.response import extract_response_text
from ..config import Config
import json


def _action_token(tool_name: str, args: dict) -> str:
    """Stable, human-readable token for a (tool_name, args) pair.

    Used in blocked-action messages so the user can confirm a specific action
    by echoing the token back (e.g. 'confirm restart_kubernetes_pod:backend-pod').
    """
    args_str = json.dumps(args, sort_keys=True, separators=(",", ":"))
    return f"{tool_name}:{args_str}"


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
        user_lower = user_input.lower().strip()

        # approved_tokens: set of _action_token strings the user has confirmed.
        # Populated when the user replies with 'yes'/'confirm' (approves all
        # pending actions in that turn) or includes a specific token string.
        approved_tokens: set = set()

        messages = self.prompt.format_messages(chat_history=chat_history, input=user_input)
        response = self.llm.invoke(messages)

        for _ in range(Config.MAX_ITERATIONS):
            if not getattr(response, "tool_calls", None):
                return extract_response_text(response)

            # Build token→call_id map for all approval-required calls this round.
            pending: dict[str, str] = {
                _action_token(tc["name"], tc["args"]): tc["id"]
                for tc in response.tool_calls
                if requires_approval(tc["name"])
            }

            # Global 'yes'/'confirm' approves every pending action in this turn.
            if user_lower in ("yes", "y", "confirm"):
                approved_tokens.update(pending.keys())

            # Also approve any pending token that appears verbatim in the message.
            for token in pending:
                if token in user_input:
                    approved_tokens.add(token)

            tool_msgs = []
            for tc in response.tool_calls:
                token = _action_token(tc["name"], tc["args"])
                if requires_approval(tc["name"]) and token not in approved_tokens:
                    res = (
                        f"Action '{tc['name']}' is BLOCKED and requires confirmation.\n"
                        f"To approve only this action, reply with:\n"
                        f"  confirm {token}\n"
                        f"Or reply 'yes' / 'confirm' to approve all pending actions."
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
