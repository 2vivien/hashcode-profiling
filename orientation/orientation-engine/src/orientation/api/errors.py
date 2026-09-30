from fastapi import HTTPException

def insufficient_evidence(detail: str = "insufficient_evidence") -> HTTPException:
    return HTTPException(status_code=422, detail=detail)
