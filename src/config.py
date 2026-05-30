import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini').lower()
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    TEMPERATURE_RAW = os.getenv('TEMPERATURE', '0.1')
    TEMPERATURE: float = 0.1  # resolved by validate()
    LOG_DIRECTORY = os.getenv('LOG_DIRECTORY', 'logs')
    MEMORY_DIR = os.getenv('MEMORY_DIR', '.memory')
    MAX_ITERATIONS = 10

    @classmethod
    def validate(cls):
        if cls.LLM_PROVIDER == 'gemini' and not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")
        try:
            temperature = float(cls.TEMPERATURE_RAW)
        except ValueError:
            raise ValueError(
                f"TEMPERATURE must be a number, got: {cls.TEMPERATURE_RAW!r}"
            )
        if not (0.0 <= temperature <= 1.0):
            raise ValueError(
                f"TEMPERATURE must be between 0.0 and 1.0, got: {temperature}"
            )
        cls.TEMPERATURE = temperature

    @classmethod
    def get_system_prompt(cls) -> str:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        with open(os.path.join(base_dir, 'system_prompt.txt'), 'r') as f:
            prompt = f.read()
        try:
            with open(os.path.join(base_dir, 'examples.txt'), 'r') as f:
                prompt += '\n\n' + f.read()
        except FileNotFoundError:
            pass
        return prompt
