from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
from ultralytics import YOLO


class ObjectDetector:
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: float = 0.45):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = YOLO(model_path)

    def detect(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        if frame is None:
            return []

        results = self.model(frame, conf=self.confidence_threshold, verbose=False)
        detections: List[Dict[str, Any]] = []

        if not results:
            return detections

        result = results[0]
        names = getattr(result, "names", {}) or {}
        boxes = getattr(result, "boxes", None)

        if boxes is None:
            return detections

        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = str(names.get(class_id, "object")).strip().lower()

            detections.append(
                {
                    "class_name": class_name,
                    "confidence": confidence,
                    "bbox": {
                        "x1": int(round(x1)),
                        "y1": int(round(y1)),
                        "x2": int(round(x2)),
                        "y2": int(round(y2)),
                    },
                }
            )

        return detections
