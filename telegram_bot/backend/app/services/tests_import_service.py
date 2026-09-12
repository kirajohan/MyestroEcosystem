"""
Tests Import Service — JSON orqali quiz yuklash
"""
import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tests import Test, TestQuestion
from app.schemas.tests_import import (
    ImportTestsPayload,
    TestImportValidationError,
    TestImportPreviewResponse,
    TestImportResultResponse,
)

logger = logging.getLogger(__name__)


class TestsImportService:

    async def validate(self, payload: ImportTestsPayload) -> TestImportPreviewResponse:
        """Payload ni validatsiya qiladi"""
        errors: List[TestImportValidationError] = []
        warnings: List[str] = []
        total_questions = 0
        total_options = 0

        for test_idx, test in enumerate(payload.tests):
            if not test.title or not test.title.strip():
                errors.append(TestImportValidationError(
                    test_index=test_idx,
                    location=f"tests[{test_idx}].title",
                    message="title bo'sh bo'lishi mumkin emas"
                ))

            if not test.cefr_level:
                errors.append(TestImportValidationError(
                    test_index=test_idx,
                    location=f"tests[{test_idx}].cefr_level",
                    message="cefr_level majburiy"
                ))

            if len(test.questions) == 0:
                warnings.append(f"tests[{test_idx}] '{test.title}': savollar yo'q")

            for q_idx, question in enumerate(test.questions):
                total_questions += 1

                if not question.question_text or not question.question_text.strip():
                    errors.append(TestImportValidationError(
                        test_index=test_idx,
                        question_index=q_idx,
                        location=f"tests[{test_idx}].questions[{q_idx}].question_text",
                        message="question_text bo'sh"
                    ))

                if question.question_type in ("multiple_choice", "single_choice", "multi_choice"):
                    if len(question.options) < 2:
                        errors.append(TestImportValidationError(
                            test_index=test_idx,
                            question_index=q_idx,
                            location=f"tests[{test_idx}].questions[{q_idx}].options",
                            message=f"kamida 2 ta variant kerak (hozir: {len(question.options)})"
                        ))

                    correct_count = sum(1 for o in question.options if o.is_correct)

                    if question.question_type in ("single_choice", "multiple_choice"):
                        if correct_count != 1:
                            errors.append(TestImportValidationError(
                                test_index=test_idx,
                                question_index=q_idx,
                                location=f"tests[{test_idx}].questions[{q_idx}].options",
                                message=f"aniq 1 ta to'g'ri javob kerak (hozir: {correct_count})"
                            ))
                    elif question.question_type == "multi_choice":
                        if correct_count < 1:
                            errors.append(TestImportValidationError(
                                test_index=test_idx,
                                question_index=q_idx,
                                location=f"tests[{test_idx}].questions[{q_idx}].options",
                                message="kamida 1 ta to'g'ri javob kerak"
                            ))

                    total_options += len(question.options)

        return TestImportPreviewResponse(
            valid=len(errors) == 0,
            tests_count=len(payload.tests),
            total_questions=total_questions,
            total_options=total_options,
            errors=errors,
            warnings=warnings,
        )

    async def save(self, payload: ImportTestsPayload, db: AsyncSession) -> TestImportResultResponse:
        """Ma'lumotlarni DB ga saqlaydi"""
        try:
            tests_created = 0
            questions_created = 0
            options_created = 0
            test_ids: List[int] = []

            for test_data in payload.tests:
                test = Test(
                    title=test_data.title,
                    description=test_data.description or "",
                    cefr_level=test_data.cefr_level or "B1",
                    passing_score=test_data.passing_score or 60,
                    is_active=test_data.is_active if test_data.is_active is not None else True,
                    total_duration=test_data.total_duration or 30,
                    max_score=test_data.max_score,
                    status="draft",
                )
                db.add(test)
                await db.flush()
                tests_created += 1
                test_ids.append(test.id)

                logger.info(f"✅ Test created: id={test.id}, title='{test_data.title}'")

                for q_idx, q_data in enumerate(sorted(test_data.questions, key=lambda q: q.order)):
                    options_json = []
                    correct_answer_label = None

                    for opt_idx, opt_data in enumerate(sorted(q_data.options, key=lambda o: o.order)):
                        label = chr(65 + opt_idx)
                        options_json.append({
                            "label": label,
                            "text": opt_data.text,
                            "is_correct": opt_data.is_correct
                        })

                        if opt_data.is_correct:
                            correct_answer_label = label

                    if not correct_answer_label and len(options_json) > 0:
                        correct_answer_label = "A"

                    question = TestQuestion(
                        test_id=test.id,
                        question_text=q_data.question_text,
                        question_type=q_data.question_type or "multiple_choice",
                        options=options_json,
                        correct_answer=correct_answer_label or "A",
                        explanation=q_data.explanation,
                        points=q_data.points or 1,
                        difficulty=q_data.difficulty or "medium",
                        order_index=q_data.order or q_idx + 1,
                    )
                    db.add(question)
                    questions_created += 1
                    options_created += len(options_json)

            await db.commit()

            logger.info(
                f"✅ Import complete: tests={tests_created}, "
                f"questions={questions_created}, options={options_created}"
            )

            return TestImportResultResponse(
                success=True,
                tests_created=tests_created,
                questions_created=questions_created,
                options_created=options_created,
                test_ids=test_ids,
            )

        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Import failed: {e}", exc_info=True)
            return TestImportResultResponse(
                success=False,
                errors=[str(e)],
            )