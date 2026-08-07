from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None
    errors: Optional[list[Any]] = Field(default_factory=list)

    @classmethod
    def ok(cls, data: Optional[T] = None, message: str = "Success") -> "APIResponse[T]":
        return cls(success=True, message=message, data=data, errors=[])

    @classmethod
    def error(cls, message: str = "An error occurred", errors: Optional[list[Any]] = None) -> "APIResponse[Any]":
        return cls(success=False, message=message, data=None, errors=errors or [])
