from pathlib import Path
import json
import sys

def load(path:str)->object:
    return json.loads(Path(path).read_text(encoding="utf-8"))

left,right=load(sys.argv[1]),load(sys.argv[2])
print("identical" if left==right else "different")
