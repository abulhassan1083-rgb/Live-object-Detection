from pydantic import BaseModel
from typing import Optional


class DetectionSchema(BaseModel):
    object_name: str
    confidence: float
    material: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None
    image_path: Optional[str] = None
