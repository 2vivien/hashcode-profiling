import hashlib, json
from pathlib import Path
from pydantic import BaseModel

class KnowledgeManifest(BaseModel):
    version:str
    source:str
    date:str
    directions:int
    sha256:str
    item_counts: dict[str,int] = {}
    transformation_rules: list[str] = []

def load_manifest(root:Path)->KnowledgeManifest:
    raw=(root/"manifest.json").read_text(encoding="utf-8")
    data=json.loads(raw)
    content=(root/"directions.json").read_bytes()
    data["sha256"]=hashlib.sha256(content).hexdigest()
    return KnowledgeManifest.model_validate(data)
