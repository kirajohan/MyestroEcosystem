from fastapi import APIRouter
from app.api.exam_v2.admin_import import router as admin_import_router

from app.api.exam_v2 import auth, admin, exams, attempts, answers, media

exam_v2_router = APIRouter(prefix="/api/v2/exam")

exam_v2_router.include_router(auth.router, prefix="/auth", tags=["Exam Auth"])
exam_v2_router.include_router(exams.router, prefix="/exams", tags=["Exam Exams"])
exam_v2_router.include_router(attempts.router, prefix="/attempts", tags=["Exam Attempts"])
exam_v2_router.include_router(answers.router, prefix="/attempts", tags=["Exam Answers"])
exam_v2_router.include_router(admin.router, prefix="/admin", tags=["Exam Admin"])
exam_v2_router.include_router(media.router, prefix="/admin/media", tags=["Exam Media"])  # ← YANGI
exam_v2_router.include_router(admin_import_router)