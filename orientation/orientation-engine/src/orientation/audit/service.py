import hashlib
from datetime import datetime, timezone
from orientation.config.versions import CONFIGURATION_VERSION, FEATURE_SCHEMA_VERSION, MODEL_VERSION
from orientation.contracts.audit import AuditSnapshot

class AuditService:
    def build(self,request_id:str,student_id:str,profile_version:str,knowledge_version:str,ranking:list[str],scores:dict[str,float],uncertainty:dict[str,float],candidates:list[str]) -> AuditSnapshot:
        pseudonymous_id=hashlib.sha256(student_id.encode("utf-8")).hexdigest()
        return AuditSnapshot(request_id=request_id,student_id=pseudonymous_id,profile_version=profile_version,assessment_version="v1",knowledge_version=knowledge_version,configuration_version=CONFIGURATION_VERSION,feature_schema_version=FEATURE_SCHEMA_VERSION,model_version=MODEL_VERSION,candidate_set=candidates,ranking=ranking,scores=scores,uncertainty=uncertainty,timestamp=datetime.now(timezone.utc))
