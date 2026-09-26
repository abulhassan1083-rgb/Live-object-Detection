from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes.health import router as health_router
from backend.api.routes.detection import router as detection_router
from backend.api.routes.questions import router as question_router
from backend.api.websocket import router as websocket_router
from backend.services.detection_service import DetectionService

app = FastAPI(title="Real-Time AI Vision System")

app.state.detection_service = DetectionService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(detection_router)
app.include_router(question_router)
app.include_router(websocket_router)


@app.get("/")
async def root():
    return {"message": "Real-Time AI Vision System API is running"}
