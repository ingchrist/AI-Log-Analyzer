from ..config import Config

def create_model():
    provider = Config.LLM_PROVIDER
    if provider == "gemini":
        from .gemini import GeminiModel
        return GeminiModel()
    raise ValueError(f"Unknown LLM_PROVIDER '{provider}'")
