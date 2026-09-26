from __future__ import annotations

import base64
from datetime import datetime, timezone
from typing import Any, Dict

import cv2
import numpy as np
from fastapi import APIRouter, HTTPException

from backend.models.material_classifier import MaterialClassifier
from backend.services.detection_service import DetectionService

router = APIRouter(prefix="/api", tags=["detection"])
detector_service = DetectionService()


def _decode_frame(image_payload: str) -> np.ndarray:
    if not image_payload:
        raise ValueError("Missing frame payload")

    encoded = image_payload.split(",", 1)[1] if "," in image_payload else image_payload
    if not encoded:
        raise ValueError("Empty frame payload")

    image_bytes = base64.b64decode(encoded)
    np_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("Unable to decode frame")
    return image


@router.get("/detections")
async def list_detections():
    return []


@router.post("/detect")
async def detect_from_frame(payload: Dict[str, Any]):
    image_payload = payload.get("image") or payload.get("frame")
    if not image_payload:
        raise HTTPException(status_code=400, detail="Image frame is required")

    try:
        frame = _decode_frame(str(image_payload))
        detections = detector_service.detect(frame)
        classifier = MaterialClassifier()
        for detection in detections:
            bbox = detection.get("bbox")
            crop = detector_service.crop_object(frame, bbox)
            detection["material"] = classifier.classify(crop)
        return {
            "type": "detections",
            "detections": detections,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Detection failed: {str(exc)}") from exc
