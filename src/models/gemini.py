from langchain_google_genai import ChatGoogleGenerativeAI
from ..config import Config

class GeminiModel:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=Config.GEMINI_MODEL,
            google_api_key=Config.GEMINI_API_KEY,
            temperature=Config.TEMPERATURE
        )

    def get_llm_with_tools(self, tools: list):
        return self.llm.bind_tools(tools)
