"""
Maestro Exam — umumiy router agregator.

Barcha exam_v2 sub-routerlarni birlashtiradi va
main.py ga ulash uchun yagona `exam_v2_router` ni eksport qiladi.
"""

from fastapi import APIRouter

from app.api.exam_v2 import auth

exam_v2_router = APIRouter(prefix="/api/v2/exam")

# Auth
exam_v2_router.include_router(auth.router, prefix="/auth", tags=["Exam Auth"])

# Keyingi qadamlarda qo'shiladi:
# from app.api.exam_v2 import exams, attempts, answers, admin
# exam_v2_router.include_router(exams.router, prefix="/exams", tags=["Exams"])
# exam_v2_router.include_router(attempts.router, prefix="/attempts", tags=["Attempts"])
# exam_v2_router.include_router(answers.router, prefix="/answers", tags=["Answers"])
# exam_v2_router.include_router(admin.router, prefix="/admin", tags=["Exam Admin"])