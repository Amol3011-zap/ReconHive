from typing import Any, List, Optional, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope."""
    success: bool = True
    data: Optional[T] = None
    error: Optional[str] = None
    message: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response envelope."""
    total: int
    skip: int
    limit: int
    data: List[T]


def success_response(data: Any = None, message: str = None) -> dict:
    """Create a success response."""
    return {
        "success": True,
        "data": data,
        "message": message,
    }


def error_response(error: str, message: str = None) -> dict:
    """Create an error response."""
    return {
        "success": False,
        "error": error,
        "message": message,
    }


def paginated_response(items: List[Any], total: int, skip: int, limit: int) -> dict:
    """Create a paginated response."""
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": items,
    }
