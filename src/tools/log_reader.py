import os
from pathlib import Path
from langchain.tools import tool
from ..config import Config

@tool
def read_log_file(filename: str) -> str:
    """Read contents of a log file from the logs directory."""
    # Reject absolute paths and normalize away any traversal sequences
    if os.path.isabs(filename):
        return "Error: Absolute paths are not allowed."
    filename = os.path.normpath(filename)
    if filename.startswith(".."):
        return "Error: Path traversal is not allowed."

    base_dir = Path(Config.LOG_DIRECTORY).resolve()
    candidate = (base_dir / filename).resolve()

    if not candidate.is_relative_to(base_dir):
        return "Error: Access outside the log directory is not permitted."

    try:
        with open(candidate, 'r', encoding='utf-8') as f:
            return f"File: {filename}\n\n{f.read()}"
    except FileNotFoundError:
        return f"Error: File not found: {filename}"
    except PermissionError:
        return f"Error: Permission denied: {filename}"
    except IsADirectoryError:
        return f"Error: Path is a directory, not a file: {filename}"
    except UnicodeDecodeError:
        return f"Error: File is not valid UTF-8 text: {filename}"
    except OSError as e:
        return f"Error reading file: {e}"

@tool
def list_log_files() -> str:
    """List all available log files."""
    log_dir = Path(Config.LOG_DIRECTORY)
    files = [f.name for f in log_dir.glob("*.log")]
    return f"Logs: {', '.join(files)}" if files else "No logs found."
