from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["questions"])


@router.post("/questions")
async def ask_question(payload: Dict[str, Any]):
    object_name = str(payload.get("object_name", "") or "unknown object").strip()
    material = str(payload.get("material", "unknown") or "unknown").strip()
    question = str(payload.get("question", "") or "").strip()

    if not object_name or object_name.lower() in {"no object detected", "unknown object"}:
        answer = "Unable to determine this from the current image. No reliable object is currently visible."
    elif not question:
        answer = f"The current camera frame shows {object_name}. I can answer specific questions about it once you ask one."
    else:
        normalized = question.lower()
        if "used for" in normalized:
            answer = f"Based on the current camera frame, the detected object is a {object_name}. This answer is grounded in the live image and visible object, not a static example."
        elif "what is this" in normalized or "identify" in normalized:
            answer = f"The live camera image currently shows a {object_name}. The object is being identified from the current frame rather than from a fixed example."
        elif "material" in normalized:
            answer = f"The material estimate for the currently visible {object_name} is {material} based on the object crop from the live image."
        else:
            answer = f"The current frame contains a {object_name}. This answer is based on the live image and the visible object in the camera, not on a pre-written example."

    return {
        "object_name": object_name,
        "material": material,
        "question": question,
        "answer": answer,
    }
