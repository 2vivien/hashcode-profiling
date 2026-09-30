import json
import sys
from pathlib import Path


def load(path: str) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


left, right = load(sys.argv[1]), load(sys.argv[2])
print("identical" if left == right else "different")
