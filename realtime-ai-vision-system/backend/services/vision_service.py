from backend.services.material_service import MaterialService
from backend.services.question_service import QuestionService


class VisionService:
    def __init__(self):
        self.material_service = MaterialService()
        self.question_service = QuestionService()

    def process_object(self, object_name: str, question: str = ""):
        material = self.material_service.identify_material({"name": object_name})
        answer = self.question_service.answer_question(object_name, material, question)

        return {
            "object_name": object_name,
            "material": material,
            "answer": answer,
        }
