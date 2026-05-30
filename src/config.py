import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini').lower()
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.1'))
    LOG_DIRECTORY = os.getenv('LOG_DIRECTORY', 'logs')
    MEMORY_DIR = os.getenv('MEMORY_DIR', '.memory')
    MAX_ITERATIONS = 10

    @classmethod
    def validate(cls):
        if cls.LLM_PROVIDER == 'gemini' and not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")

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
