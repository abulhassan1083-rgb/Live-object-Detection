from __future__ import annotations

from typing import Any, Dict, List, Optional

import cv2
import numpy as np

from backend.core.config import DETECTION_CONFIDENCE
from backend.models.object_detector import ObjectDetector


class DetectionService:
    def __init__(self, model_path: str = "yolov8n.pt", confidence_threshold: Optional[float] = None):
        self.model_path = model_path
        self.confidence_threshold = (
            confidence_threshold if confidence_threshold is not None else float(DETECTION_CONFIDENCE)
        )
        self.detector = ObjectDetector(model_path=model_path, confidence_threshold=self.confidence_threshold)

    def preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        if frame is None:
            return np.zeros((1, 1, 3), dtype=np.uint8)

        image = frame.copy()
        if image.ndim == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        return image

    def crop_object(self, frame: np.ndarray, bbox: Dict[str, int]) -> Optional[np.ndarray]:
        if frame is None or bbox is None:
            return None

        height, width = frame.shape[:2]
        x1 = max(0, int(bbox.get("x1", 0)))
        y1 = max(0, int(bbox.get("y1", 0)))
        x2 = min(width, int(bbox.get("x2", width)))
        y2 = min(height, int(bbox.get("y2", height)))

        if x2 <= x1 or y2 <= y1:
            return None

        return frame[y1:y2, x1:x2]

    def detect(self, frame: Any) -> List[Dict[str, Any]]:
        if frame is None:
            return []

        processed = self.preprocess_frame(frame)
        detections = self.detector.detect(processed)

        filtered: List[Dict[str, Any]] = []
        for detection in detections:
            conf = float(detection.get("confidence", 0.0))
            if conf < self.confidence_threshold:
                continue

            filtered.append(detection)

        return filtered
