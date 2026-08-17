"""Test (QUIZ) handler for Telegram bot."""
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import httpx
from bot.config import API_BASE_URL, BOT_TOKEN
from bot.keyboards.reply import registered_menu_kb
from bot.states.registration import QuizSection
from bot.utils.i18n import get_text
from bot.states.registrations_filter import IsRegistered, IsNotRegistered


router = Router()


# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════

def _get_lang(state_data: dict) -> str:
    return state_data.get("lang", "uz")


async def fetch_public_exams(cefr_level: str, limit: int = 10, offset: int = 0):
    """Backend'dan published testlarni olish."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{API_BASE_URL}/exams/public/list",
                params={"cefr_level": cefr_level, "limit": limit, "offset": offset}
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        print(f"[EXAM FETCH ERROR] {e}")
    return []


def exam_list_inline_kb(exams: list, page: int = 0, cefr_level: str = "A1") -> InlineKeyboardMarkup:
    """Testlar ro'yxati inline keyboard (pagination)."""
    buttons = []
    
    for exam in exams:
        buttons.append([
            InlineKeyboardButton(
                text=f"📝 {exam['title']}",
                callback_data=f"exam_start:{exam['id']}"
            )
        ])
    
    # Pagination (hozircha sodda)
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="◀️ Old", callback_data=f"exam_page:{page-1}:{cefr_level}"))
    nav_row.append(InlineKeyboardButton(text=f"Sahifa {page+1}", callback_data="noop"))
    if len(exams) == 10:  # Agar 10 ta bo'lsa, keyingi sahifa bor
        nav_row.append(InlineKeyboardButton(text="Next ▶️", callback_data=f"exam_page:{page+1}:{cefr_level}"))
    
    if nav_row:
        buttons.append(nav_row)
    
    buttons.append([
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="exam_back_to_menu")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def question_inline_kb(question: dict, current: int, total: int, attempt_id: int) -> InlineKeyboardMarkup:
    """Savol uchun inline keyboard (variantlar + navigation)."""
    buttons = []
    
    # Variantlar (A, B, C, D)
    options = question.get("options", [])
    if options:
        for opt in options:
            label = opt.get("label", "")
            buttons.append([
                InlineKeyboardButton(
                    text=label,
                    callback_data=f"exam_answer:{attempt_id}:{question['id']}:{label}"
                )
            ])
    
    # Navigation
    nav_row = []
    if current > 1:
        nav_row.append(InlineKeyboardButton(text="◀️ Old", callback_data=f"exam_prev:{attempt_id}:{current-1}"))
    nav_row.append(InlineKeyboardButton(text=f"{current}/{total}", callback_data="noop"))
    if current < total:
        nav_row.append(InlineKeyboardButton(text="Next ▶️", callback_data=f"exam_next:{attempt_id}:{current+1}"))
    
    if nav_row:
        buttons.append(nav_row)
    
    buttons.append([
        InlineKeyboardButton(text="✅ Yakunlash", callback_data=f"exam_finish:{attempt_id}")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ══════════════════════════════════════════════════════════════
# TEST RO'YXATI (Inline Keyboard)
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("exam_page:"))
async def exam_page_callback(callback: types.CallbackQuery, state: FSMContext):
    """Testlar ro'yxati pagination."""
    parts = callback.data.split(":")
    page = int(parts[1])
    cefr_level = parts[2]
    
    exams = await fetch_public_exams(cefr_level, limit=10, offset=page*10)
    
    if not exams:
        await callback.message.edit_text(
            f"❌ <b>{cefr_level}</b> darajasida testlar topilmadi",
            parse_mode="HTML"
        )
        return
    
    await callback.message.edit_text(
        f"📊 <b>{cefr_level}</b> darajasidagi testlar:\n\n"
        f"Testni tanlang:",
        parse_mode="HTML",
        reply_markup=exam_list_inline_kb(exams, page, cefr_level)
    )
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# TEST BOSHLASH
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("exam_start:"))
async def exam_start_callback(callback: types.CallbackQuery, state: FSMContext):
    """Testni boshlash."""
    exam_id = int(callback.data.split(":")[1])
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    await callback.message.edit_text("⏳ Test boshlanmoqda...")
    
    # Backend'da attempt yaratish
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Token olish (user state'dan)
            token = user_data.get("access_token")
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            
            resp = await client.post(
                f"{API_BASE_URL}/exams/{exam_id}/start",
                headers=headers
            )
            
            if resp.status_code != 200:
                await callback.message.edit_text(
                    f"❌ {resp.json().get('detail', 'Xatolik')}",
                    parse_mode="HTML"
                )
                return
            
            attempt = resp.json()
            attempt_id = attempt["id"]
            
            # Savollarni olish
            questions_resp = await client.get(
                f"{API_BASE_URL}/exams/{exam_id}/questions",
                headers=headers
            )
            
            if questions_resp.status_code != 200:
                await callback.message.edit_text("❌ Savollarni yuklashda xatolik")
                return
            
            questions = questions_resp.json()
            
            if not questions:
                await callback.message.edit_text("❌ Bu testda savollar yo'q")
                return
            
            # State'ga saqlash
            await state.update_data(
                exam_attempt_id=attempt_id,
                exam_questions=questions,
                exam_current_question=1,
                exam_answers={}
            )
            await state.set_state(QuizSection.quiz_active)
            
            # Birinchi savolni ko'rsatish
            await show_question(callback.message, state, 1)
    
    except Exception as e:
        print(f"[EXAM START ERROR] {e}")
        await callback.message.edit_text(f"❌ Xatolik: {str(e)}")


# ══════════════════════════════════════════════════════════════
# SAVOL KO'RSATISH
# ══════════════════════════════════════════════════════════════

async def show_question(message: types.Message, state: FSMContext, question_num: int):
    """Savolni ko'rsatish."""
    user_data = await state.get_data()
    questions = user_data.get("exam_questions", [])
    attempt_id = user_data.get("exam_attempt_id")
    
    if question_num < 1 or question_num > len(questions):
        return
    
    question = questions[question_num - 1]
    
    text = (
        f"❓ <b>Savol {question_num}/{len(questions)}</b>\n\n"
        f"{question['question_text']}\n\n"
    )
    
    await message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=question_inline_kb(question, question_num, len(questions), attempt_id)
    )


# ══════════════════════════════════════════════════════════════
# JAVOB BERISH
# ══════════════════════════════════════════════════════════════

@router.callback_query(QuizSection.quiz_active, F.data.startswith("exam_answer:"))
async def exam_answer_callback(callback: types.CallbackQuery, state: FSMContext):
    """Foydalanuvchi javob berdi."""
    parts = callback.data.split(":")
    attempt_id = int(parts[1])
    question_id = int(parts[2])
    answer = parts[3]
    
    user_data = await state.get_data()
    answers = user_data.get("exam_answers", {})
    current_question = user_data.get("exam_current_question", 1)
    questions = user_data.get("exam_questions", [])
    
    # Javobni saqlash
    answers[str(question_id)] = answer
    await state.update_data(exam_answers=answers)
    
    # Keyingi savolga o'tish
    if current_question < len(questions):
        next_question = current_question + 1
        await state.update_data(exam_current_question=next_question)
        await show_question(callback.message, state, next_question)
    else:
        # Oxirgi savol — yakunlash taklifi
        await callback.message.edit_text(
            "✅ Barcha savollarga javob berdingiz!\n\n"
            "Testni yakunlash uchun '✅ Yakunlash' tugmasini bosing.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Yakunlash", callback_data=f"exam_finish:{attempt_id}")],
                [InlineKeyboardButton(text="🔙 Orqaga", callback_data=f"exam_prev:{attempt_id}:{current_question-1}")]
            ])
        )
    
    await callback.answer("✅ Javob saqlandi")


@router.callback_query(QuizSection.quiz_active, F.data.startswith("exam_prev:"))
async def exam_prev_callback(callback: types.CallbackQuery, state: FSMContext):
    """Oldingi savol."""
    parts = callback.data.split(":")
    question_num = int(parts[2])
    
    await state.update_data(exam_current_question=question_num)
    await show_question(callback.message, state, question_num)
    await callback.answer()


@router.callback_query(QuizSection.quiz_active, F.data.startswith("exam_next:"))
async def exam_next_callback(callback: types.CallbackQuery, state: FSMContext):
    """Keyingi savol."""
    parts = callback.data.split(":")
    question_num = int(parts[2])
    
    await state.update_data(exam_current_question=question_num)
    await show_question(callback.message, state, question_num)
    await callback.answer()


# ══════════════════════════════════════════════════════════════
# TESTNI YAKUNLASH
# ══════════════════════════════════════════════════════════════

@router.callback_query(QuizSection.quiz_active, F.data.startswith("exam_finish:"))
async def exam_finish_callback(callback: types.CallbackQuery, state: FSMContext):
    """Testni yakunlash va natijani ko'rsatish."""
    attempt_id = int(callback.data.split(":")[1])
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    answers = user_data.get("exam_answers", {})
    exam_id = user_data.get("exam_id")
    
    await callback.message.edit_text("⏳ Natija hisoblanmoqda...")
    
    # Backend'ga javoblarni yuborish
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            token = user_data.get("access_token")
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            
            # Javoblarni formatlash
            answers_list = [
                {"question_id": int(qid), "user_answer": ans}
                for qid, ans in answers.items()
            ]
            
            resp = await client.post(
                f"{API_BASE_URL}/exams/{exam_id}/submit",
                headers=headers,
                json={
                    "attempt_id": attempt_id,
                    "answers": answers_list
                }
            )
            
            if resp.status_code != 200:
                await callback.message.edit_text(
                    f"❌ Xatolik: {resp.text}",
                    parse_mode="HTML"
                )
                return
            
            result = resp.json()
            
            # Natijani ko'rsatish
            attempt = result["attempt"]
            total = result["total_questions"]
            correct = result["correct_answers"]
            percentage = result["score_percentage"]
            passed = attempt.get("passed")
            
            status_emoji = "✅" if passed else "❌"
            status_text = "O'TDINGIZ!" if passed else "O'TMADINGIZ"
            
            text = (
                f"{status_emoji} <b>Test yakunlandi!</b>\n\n"
                f"📊 <b>Natija:</b>\n"
                f"• To'g'ri javoblar: <b>{correct}/{total}</b>\n"
                f"• Foiz: <b>{percentage:.1f}%</b>\n"
                f"• Holat: <b>{status_text}</b>\n\n"
                f"🎯 <b>Umumiy ball:</b> {attempt.get('total_score', 0)}\n"
            )
            
            await callback.message.edit_text(
                text,
                parse_mode="HTML",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="exam_back_to_menu")]
                ])
            )
            
            await state.set_state(QuizSection.quiz_results)
    
    except Exception as e:
        print(f"[EXAM FINISH ERROR] {e}")
        await callback.message.edit_text(f"❌ Xatolik: {str(e)}")


# ══════════════════════════════════════════════════════════════
# ORQAGA
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data == "exam_back_to_menu")
async def exam_back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Asosiy menyuga qaytish."""
    await state.clear()
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    await callback.message.delete()
    await callback.message.answer(
        get_text("main_menu", lang),
        reply_markup=registered_menu_kb(lang)
    )
    await callback.answer()