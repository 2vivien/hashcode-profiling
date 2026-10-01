from pathlib import Path
from typing import TypeVar

T = TypeVar("T")


def dump(value: object, filename: str | Path) -> None: ...
def load(filename: str | Path) -> object: ...
