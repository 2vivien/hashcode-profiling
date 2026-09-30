from fastapi import FastAPI

from orientation.api.routes.assessments import router as assessments_router
from orientation.api.routes.feedback import router as feedback_router
from orientation.api.routes.health import router as health_router
from orientation.api.routes.knowledge import router as knowledge_router
from orientation.api.routes.profiles import router as profiles_router
from orientation.api.routes.recommendations import router as recommendations_router

app = FastAPI(title="Otheloo Orientation Engine", version="1.0.0")

app.include_router(health_router)
app.include_router(profiles_router, prefix="/v1/orientation")
app.include_router(assessments_router, prefix="/v1/orientation")
app.include_router(recommendations_router, prefix="/v1/orientation")
app.include_router(knowledge_router, prefix="/v1/orientation")
app.include_router(feedback_router, prefix="/v1/orientation")
