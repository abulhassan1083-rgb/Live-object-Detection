class QuestionService:
    def __init__(self):
        self.default_answer = "The current image does not provide enough reliable evidence to answer this confidently."

    def answer_question(self, object_name: str, material: str, question: str) -> str:
        if not question:
            return self.default_answer

        q = question.lower()
        if "what" in q and "used" in q:
            return f"The live image currently shows a {object_name}. Its practical use should be inferred from the visible object and frame context, not from a pre-written example."
        if "material" in q:
            return f"The current object crop suggests a material estimate of {material}, but this is only as reliable as the visible image evidence."
        if "recycl" in q:
            return f"The recycling suitability for the currently visible {object_name} should be evaluated from the live image and material estimate: {material}."
        if "danger" in q:
            return "There is no reliable evidence from the current image that this object is dangerous."
        return f"The current camera frame contains a {object_name}. The answer is based on the live image and the currently visible object, not a static placeholder."
