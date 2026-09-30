from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def model_response(value: T) -> T:
    return value
