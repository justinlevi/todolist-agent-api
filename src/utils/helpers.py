import time
from typing import Dict, Any

def get_current_timestamp() -> int:
    """
    Get the current Unix timestamp.

    Returns:
        int: The current Unix timestamp.
    """
    return int(time.time())

def format_error_response(status_code: int, detail: str) -> Dict[str, Any]:
    """
    Format an error response.

    Args:
        status_code (int): The HTTP status code.
        detail (str): The error detail message.

    Returns:
        Dict[str, Any]: A formatted error response dictionary.
    """
    return {
        "error": {
            "status_code": status_code,
            "detail": detail
        }
    }

