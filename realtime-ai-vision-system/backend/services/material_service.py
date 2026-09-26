from typing import Any, Dict, Optional

import numpy as np

from backend.models.material_classifier import MaterialClassifier


class MaterialService:
    def __init__(self):
        self.classifier = MaterialClassifier()

    def identify_material(self, detected_object: Dict[str, Any]) -> str:
        crop: Optional[np.ndarray] = detected_object.get("crop")
        if crop is None:
            return "Unknown"
        return self.classifier.classify(crop)
