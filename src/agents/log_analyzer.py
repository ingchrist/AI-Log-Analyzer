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

    def process_query(self, user_input: str, chat_history: list, callbacks=None) -> str:
        approval_granted = user_input.lower().strip() in ["yes", "y", "confirm"]
        messages = self.prompt.format_messages(chat_history=chat_history, input=user_input)
        response = self.llm.invoke(messages)

        for _ in range(Config.MAX_ITERATIONS):
            if not getattr(response, "tool_calls", None):
                return extract_response_text(response)

            tool_msgs = []
            for tc in response.tool_calls:
                if requires_approval(tc["name"]) and not approval_granted:
                    res = f"Action '{tc['name']}' BLOCKED. Ask user to confirm."
                else:
                    tool_func = next(t for t in self.tools if t.name == tc["name"])
                    res = str(tool_func.invoke(tc["args"]))
                tool_msgs.append(ToolMessage(content=res, tool_call_id=tc["id"]))

            messages.append(AIMessage(content=response.content, tool_calls=response.tool_calls))
            messages.extend(tool_msgs)
            response = self.llm.invoke(messages)

        return extract_response_text(response)
