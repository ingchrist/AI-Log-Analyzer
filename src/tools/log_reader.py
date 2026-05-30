import os
from pathlib import Path
from langchain.tools import tool
from ..config import Config

@tool
def read_log_file(filename: str) -> str:
    """Read contents of a log file from the logs directory."""
    log_path = Path(Config.LOG_DIRECTORY) / filename
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            return f"File: {filename}\n\n{f.read()}"
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def list_log_files() -> str:
    """List all available log files."""
    log_dir = Path(Config.LOG_DIRECTORY)
    files = [f.name for f in log_dir.glob("*.log")]
    return f"Logs: {', '.join(files)}" if files else "No logs found."
