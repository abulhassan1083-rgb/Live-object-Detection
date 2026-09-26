from sqlalchemy.orm import Session

from backend.database.models import DetectionRecord


class DetectionRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_detection(self, object_name: str, confidence: float, material: str, question: str = "", answer: str = "", image_path: str = ""):
        record = DetectionRecord(
            object_name=object_name,
            confidence=confidence,
            material=material,
            question=question,
            answer=answer,
            image_path=image_path,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_detections(self):
        return self.db.query(DetectionRecord).order_by(DetectionRecord.timestamp.desc()).all()
