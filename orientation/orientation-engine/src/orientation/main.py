from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from orientation.api.routes.assessment_v1 import router as assessment_v1_router
from orientation.api.routes.assessments import router as assessments_router
from orientation.api.routes.atlas import router as atlas_router
from orientation.api.routes.feedback import router as feedback_router
from orientation.api.routes.health import router as health_router
from orientation.api.routes.home import router as home_router
from orientation.api.routes.knowledge import router as knowledge_router
from orientation.api.routes.occupation_v2 import router as occupation_v2_router
from orientation.api.routes.profiles import router as profiles_router
from orientation.api.routes.rag import router as rag_router
from orientation.api.routes.recommendations import router as recommendations_router
from orientation.api.routes.system import router as system_router
from orientation.api.security import ApiKeyMiddleware, SecurityHeadersMiddleware

app = FastAPI(title="Otheloo Orientation Engine", version="1.0.0")

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ApiKeyMiddleware)

_STATIC = Path(__file__).resolve().parent / "api" / "static"
app.mount("/assets", StaticFiles(directory=_STATIC), name="assets")

app.include_router(health_router)
app.include_router(home_router)
app.include_router(system_router, prefix="/v1/orientation")
app.include_router(profiles_router, prefix="/v1/orientation")
app.include_router(assessments_router, prefix="/v1/orientation")
app.include_router(assessment_v1_router, prefix="/v1/orientation")
app.include_router(occupation_v2_router, prefix="/v1/orientation")
app.include_router(recommendations_router, prefix="/v1/orientation")
app.include_router(knowledge_router, prefix="/v1/orientation")
app.include_router(feedback_router, prefix="/v1/orientation")
app.include_router(rag_router, prefix="/v1/orientation")
app.include_router(atlas_router, prefix="/v1/orientation")
