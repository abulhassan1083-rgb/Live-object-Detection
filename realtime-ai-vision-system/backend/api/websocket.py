from __future__ import annotations

import base64
import json
from datetime import datetime, timezone

import cv2
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.models.material_classifier import MaterialClassifier
from backend.services.detection_service import DetectionService

router = APIRouter()
detector_service = DetectionService()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON payload"})
                continue

            image_payload = payload.get("image") or payload.get("frame")
            if not image_payload:
                await websocket.send_json({"type": "status", "message": "Waiting for camera frames"})
                continue

            try:
                encoded = image_payload.split(",", 1)[1] if "," in image_payload else image_payload
                image_bytes = base64.b64decode(encoded)
                np_array = np.frombuffer(image_bytes, dtype=np.uint8)
                frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
                if frame is None:
                    raise ValueError("Frame decode failed")

                detections = detector_service.detect(frame)
                classifier = MaterialClassifier()
                for detection in detections:
                    crop = detector_service.crop_object(frame, detection.get("bbox"))
                    detection["material"] = classifier.classify(crop)
                await websocket.send_json(
                    {
                        "type": "detections",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "detections": detections,
                    }
                )
            except Exception as exc:
                await websocket.send_json({"type": "error", "message": str(exc)})
    except WebSocketDisconnect:
        pass
