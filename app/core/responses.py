from typing import Any


def success_response(message: str, data: Any = None) -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": data,
        "errors": [],
    }


def error_response(message: str, errors: list[str] | None = None) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "data": None,
        "errors": errors or [message],
    }
