from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
APP_NAME = os.getenv("APP_NAME", "Real-Time AI Vision System")
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/database/vision.db")
MODEL_PATH = os.getenv("MODEL_PATH", "yolov8n.pt")
AI_MODEL = os.getenv("AI_MODEL", "")
AI_API_KEY = os.getenv("AI_API_KEY", "")
DETECTION_FPS = int(os.getenv("DETECTION_FPS", "5"))
DETECTION_CONFIDENCE = float(os.getenv("DETECTION_CONFIDENCE", "0.45"))
