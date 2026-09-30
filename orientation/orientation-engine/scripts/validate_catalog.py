import json
from pathlib import Path
root=Path(__file__).parents[1]/"data"/"knowledge"/"v1"
data=json.loads((root/"directions.json").read_text(encoding="utf-8"))
ids=[item["direction_id"] for item in data]
assert data and len(ids)==len(set(ids))
assert all(item["knowledge_version"]=="v1" for item in data)
print(f"catalog valid: {len(data)} directions")
