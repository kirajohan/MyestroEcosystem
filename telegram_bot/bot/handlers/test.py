"""Test handler — CEFR level test (A1-C2).

Flow:
1. User presses ✅ Test → level selection grid
2. User selects level → confirmation prompt
3. User confirms → questions are fetched from backend API
4. User answers questions one by one
5. Results are shown with score, percentage, and level
"""

from aiogram import Router, types, F
from aiogram.filters import Command, or_f
from aiogram.fsm.context import FSMContext
from bot.states.registration import TestStates, RegisteredSection
from bot.keyboards.inline import (
    test_level_kb,
    test_confirm_kb,
    test_question_kb,
    test_results_kb,
)
from bot.utils.i18n import get_text
from bot.config import API_BASE_URL
import httpx

router = Router()

# ─── Helpers ─────────────────────────────────────────────────

def _get_lang(state_data: dict) -> str:
    return state_data.get("lang", "uz")


async def fetch_test_questions(level: str):
    """Fetch test questions for a given CEFR level from backend API.

    Returns: list of question dicts or empty list on error.
    Each question dict: {id, question, options: [{label, is_correct}], level}
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{API_BASE_URL}/exams/test/questions?level={level}"
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        print(f"[TEST FETCH ERROR] {e}")
    return []


async def save_test_attempt(user_id: int, level: str, correct: int, total: int, percent: float):
    """Save test attempt to backend."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            payload = {
                "user_id": user_id,
                "level": level,
                "correct_answers": correct,
                "total_questions": total,
                "percentage": percent,
            }
            resp = await client.post(f"{API_BASE_URL}/exams/test/attempts", json=payload)
            return resp.status_code in (200, 201)
    except Exception as e:
        print(f"[TEST SAVE ERROR] {e}")
    return False


# ─── Reply Keyboard Handler ──────────────────────────────────

@router.message(or_f(
    F.text.in_(["✅ Test", "✅ Тест"]),
    Command("test"),
))
async def test_menu(message: types.Message, state: FSMContext):
    """Handle ✅ Test button — show CEFR level selection grid."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(TestStates.selecting_level)

    await message.answer(
        get_text("test.title", lang) + "\n\n" + get_text("test.prompt", lang),
        reply_markup=test_level_kb(lang),
    )


# ─── Level Selection ─────────────────────────────────────────

@router.callback_query(F.data == "menu_test")
async def menu_test(callback: types.CallbackQuery, state: FSMContext):
    """Handle Test button from main menu — show CEFR level selection grid."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(TestStates.selecting_level)

    await callback.message.edit_text(
        get_text("test.title", lang) + "\n\n" + get_text("test.prompt", lang),
        reply_markup=test_level_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "test_select_level")
async def test_select_level(callback: types.CallbackQuery, state: FSMContext):
    """Back to level selection from confirmation or results."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    await state.set_state(TestStates.selecting_level)

    await callback.message.edit_text(
        get_text("test.title", lang) + "\n\n" + get_text("test.prompt", lang),
        reply_markup=test_level_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("test_level_"))
async def test_level_selected(callback: types.CallbackQuery, state: FSMContext):
    """User selected a CEFR level — show confirmation prompt."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    level = callback.data.replace("test_level_", "")

    await state.update_data(test_level=level)
    await state.set_state(TestStates.selecting_level)

    level_text = get_text(f"test.level.{level}", lang)
    await callback.message.edit_text(
        get_text("test.confirm_start", lang, level=level_text),
        reply_markup=test_confirm_kb(lang, level),
    )
    await callback.answer()


# ─── Test Start ──────────────────────────────────────────────

@router.callback_query(F.data.startswith("test_start_"))
async def test_start(callback: types.CallbackQuery, state: FSMContext):
    """User confirmed test start — fetch questions and show first question."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    level = callback.data.replace("test_start_", "")

    # Fetch questions from backend
    questions = await fetch_test_questions(level)

    if not questions:
        await callback.message.edit_text(get_text("test.no_questions", lang))
        await callback.answer()
        return

    # Store test data in state
    await state.update_data(
        test_questions=questions,
        test_current=0,
        test_correct=0,
        test_total=len(questions),
        test_level=level,
    )
    await state.set_state(TestStates.answering_questions)

    # Show first question
    await _show_question(callback.message, state, lang)
    await callback.answer()


async def _show_question(message: types.Message, state: FSMContext, lang: str):
    """Show current question to user."""
    user_data = await state.get_data()
    questions = user_data.get("test_questions", [])
    current = user_data.get("test_current", 0)
    total = user_data.get("test_total", len(questions))

    if current >= total:
        # All questions answered — show results
        await _show_results(message, state, lang)
        return

    question = questions[current]
    question_text = question.get("question", "???")
    options = question.get("options", [])
    question_id = question.get("id", current)

    # Build options list for keyboard
    opt_list = [(opt.get("label", f"Option {i+1}"), opt.get("is_correct", False)) for i, opt in enumerate(options)]

    text = get_text("test.question", lang, current=current + 1, total=total, question=question_text)
    keyboard = test_question_kb(opt_list, question_id, lang)

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


# ─── Answer Handling ─────────────────────────────────────────

@router.callback_query(F.data.startswith("test_answer_"))
async def test_answer(callback: types.CallbackQuery, state: FSMContext):
    """Handle user's answer to a test question."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)

    # Parse callback data: test_answer_{question_id}_{option_index}
    parts = callback.data.split("_")
    option_index = int(parts[-1])

    questions = user_data.get("test_questions", [])
    current = user_data.get("test_current", 0)
    correct_count = user_data.get("test_correct", 0)

    if current >= len(questions):
        await callback.answer()
        return

    question = questions[current]
    options = question.get("options", [])

    if option_index < len(options):
        is_correct = options[option_index].get("is_correct", False)

        if is_correct:
            correct_count += 1
            await state.update_data(test_correct=correct_count)
            feedback = get_text("test.correct", lang)
        else:
            # Find correct answer label
            correct_label = "???"
            for opt in options:
                if opt.get("is_correct", False):
                    correct_label = opt.get("label", "???")
                    break
            feedback = get_text("test.incorrect", lang, correct_answer=correct_label)

        # Show feedback briefly
        await callback.answer(feedback, show_alert=True)

    # Move to next question
    current += 1
    await state.update_data(test_current=current)

    # Show next question or results
    await _show_question(callback.message, state, lang)


# ─── Results ─────────────────────────────────────────────────

async def _show_results(message: types.Message, state: FSMContext, lang: str):
    """Show test results to user."""
    user_data = await state.get_data()
    correct = user_data.get("test_correct", 0)
    total = user_data.get("test_total", 0)
    level = user_data.get("test_level", "A1")
    db_user_id = user_data.get("id")

    percent = round((correct / total * 100), 1) if total > 0 else 0

    # Determine result message
    if percent >= 80:
        msg_key = "test.results.excellent"
    elif percent >= 60:
        msg_key = "test.results.good"
    elif percent >= 40:
        msg_key = "test.results.average"
    else:
        msg_key = "test.results.poor"

    level_text = get_text(f"test.level.{level}", lang)
    result_text = get_text(
        "test.results",
        lang,
        correct=correct,
        total=total,
        percent=percent,
        level=level_text,
        message=get_text(msg_key, lang),
    )

    # Save attempt to backend
    if db_user_id:
        await save_test_attempt(db_user_id, level, correct, total, percent)

    await state.set_state(TestStates.viewing_results)

    await message.answer(result_text, reply_markup=test_results_kb(lang), parse_mode="HTML")