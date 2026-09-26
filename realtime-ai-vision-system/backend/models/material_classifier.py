from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np


class MaterialClassifier:
    def __init__(self):
        self.material_classes = [
            "Plastic",
            "Metal",
            "Glass",
            "Wood",
            "Paper",
            "Fabric",
            "Rubber",
            "Unknown",
        ]

    def classify(self, crop: Optional[np.ndarray]) -> str:
        if crop is None or crop.size == 0:
            return "Unknown"

        gray = np.mean(crop)
        if np.isnan(gray):
            return "Unknown"

        if gray < 80:
            return "Plastic"
        if gray < 135:
            return "Metal"
        if gray < 170:
            return "Glass"
        if gray < 210:
            return "Paper"
        return "Unknown"

    def classify_from_object(self, object_data: Dict[str, Any]) -> str:
        crop = object_data.get("crop")
        return self.classify(crop)
