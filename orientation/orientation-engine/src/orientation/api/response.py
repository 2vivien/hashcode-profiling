from pydantic import BaseModel


def model_response[T: BaseModel](value: T) -> T:
    return value
