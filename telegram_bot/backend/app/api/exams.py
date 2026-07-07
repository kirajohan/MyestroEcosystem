from fastapi import APIRouter

router = APIRouter(prefix="/exams", tags=["exams"])


@router.get("/")
def get_exams():
    """Get all exams."""
    return {"exams": []}


@router.get("/{exam_id}")
def get_exam(exam_id: int):
    """Get exam by ID."""
    return {"exam_id": exam_id}
