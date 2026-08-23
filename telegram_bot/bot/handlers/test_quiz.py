# bot/handlers/test_quiz.py
"""
Telegram Quiz Poll orqali test topshirish tizimi.
Telegram'ning o'ziga xos "quiz" poll turidan foydalanadi.
"""

import logging
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from bot.states.test_states import TestSection
from bot.utils.api_client import fetch_test_questions, submit_test_attempt
from bot.utils.i18n import get_text
from bot.keyboards.inline import cefr_level_selection_with_back, registered_menu_kb

logger = logging.getLogger(__name__)
router = Router()

def _get_lang(state_data: dict) -> str:
    return state_data.get("lang", "uz")

# ══════════════════════════════════════════════════════════════
# TESTNI BOSHLASH (Inline tugma bosilganda)
# ══════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("start_test:"))
async def start_test_quiz(callback: types.CallbackQuery, state: FSMContext):
    """Foydalanuvchi testni boshlash tugmasini bosdi."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    try:
        test_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("❌ Xatolik", show_alert=True)
        return
    
    # Loading ko'rsatish
    await callback.answer()
    loading_msg = await callback.message.answer(
        get_text("test.loading_questions", lang),
        parse_mode="HTML"
    )
    
    try:
        # Backenddan savollarni olish
        test_data = await fetch_test_questions(test_id)
        
        if not test_data or not test_data.get("questions"):
            await loading_msg.edit_text(
                get_text("test.no_questions", lang),
                parse_mode="HTML"
            )
            await callback.message.answer(
                get_text("test.return_to_menu", lang),
                reply_markup=registered_menu_kb(lang),  # ✅ TO'G'RI
                parse_mode="HTML"
            )
            await state.clear()
            return
        
        # FSM ga saqlash
        await state.update_data(
            current_test_id=test_id,
            test_title=test_data.get("title", "Test"),
            passing_score=test_data.get("passing_score", 60),
            questions=test_data["questions"],
            current_question_index=0,
            score=0,
            total_questions=len(test_data["questions"])
        )
        await state.set_state(TestSection.taking_quiz)
        
        # Loading xabarni o'chirish
        await loading_msg.delete()
        
        # Birinchi savolni yuborish
        await send_next_poll_question(callback.message, state, lang)
        
    except Exception as e:
        logger.error(f"Testni boshlashda xatolik: {e}")
        await loading_msg.edit_text(
            get_text("test.error_loading", lang),
            parse_mode="HTML"
        )
        await state.clear()

# bot/handlers/test_quiz.py yoki menu.py ichiga qo'shing

@router.callback_query(F.data.startswith("test_back_to_cefr:"))
async def handle_test_back_to_cefr(callback: types.CallbackQuery, state: FSMContext):
    """Testlar ro'yxatidan CEFR tanlashga qaytish."""
    cefr_level = callback.data.split(":")[1]
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    # State'ni qayta o'rnatish
    await state.set_state(TestSection.cefr_selection)
    
    await callback.message.edit_text(
        get_text("test.select_cefr", lang),
        reply_markup=cefr_level_selection_with_back(lang),
        parse_mode="HTML"
    )
    await callback.answer()
    
# ══════════════════════════════════════════════════════════════
# SAVOLNI TELEGRAM QUIZ POLL SIFATIDA YUBORISH
# ══════════════════════════════════════════════════════════════

async def send_next_poll_question(message: types.Message, state: FSMContext, lang: str = "uz"):
    """Keyingi savolni Telegram Quiz Poll sifatida yuboradi."""
    data = await state.get_data()
    questions = data.get("questions", [])
    current_idx = data.get("current_question_index", 0)
    total = data.get("total_questions", len(questions))
    
    # Agar savollar tugagan bo'lsa — testni yakunlash
    if current_idx >= len(questions):
        await finish_test(message, state, lang)
        return
    
    q = questions[current_idx]
    
    # Savol raqamini ko'rsatish
    progress_text = f"📝 <b>Savol {current_idx + 1}/{total}</b>"
    await message.answer(progress_text, parse_mode="HTML")
    
    # Telegram Quiz Poll yuborish
    try:
        await message.answer_poll(
            question=q["question_text"],
            options=q["options"],  # ["variant1", "variant2", "variant3", "variant4"]
            type="quiz",  # ⭐ Eng muhimi: Telegram o'zi to'g'ri/noto'g'riligini ko'rsatadi
            correct_option_id=q["correct_option_index"],  # 0, 1, 2 yoki 3
            explanation=q.get("explanation", ""),  # Javob bergandan keyin chiqadigan izoh
            is_anonymous=False,  # poll_answer handler ishlashi uchun
            open_period=None,  # Cheksiz vaqt
        )
    except Exception as e:
        logger.error(f"Poll yuborishda xatolik: {e}")
        await message.answer(
            get_text("test.poll_error", lang),
            parse_mode="HTML"
        )
        await finish_test(message, state, lang)


# ══════════════════════════════════════════════════════════════
# FOYDALANUVCHI JAVOBINI QABUL QILISH (poll_answer)
# ══════════════════════════════════════════════════════════════

@router.poll_answer()
async def handle_poll_answer(poll_answer: types.PollAnswer, state: FSMContext, bot: Bot):
    """Foydalanuvchi Telegram Quiz Poll'da javob berdi."""
    data = await state.get_data()
    
    # Agar foydalanuvchi test topshirmayotgan bo'lsa — e'tiborsiz qoldirish
    if not data.get("current_test_id"):
        return
    
    questions = data.get("questions", [])
    current_idx = data.get("current_question_index", 0)
    
    # Xavfsizlik: agar indeks savollar sonidan oshib ketsa
    if current_idx >= len(questions):
        return
    
    current_q = questions[current_idx]
    user_answer = poll_answer.option_ids[0] if poll_answer.option_ids else None
    
    # Javob to'g'riligini tekshirish
    if user_answer == current_q["correct_option_index"]:
        new_score = data.get("score", 0) + 1
        await state.update_data(score=new_score)
    
    # FSM dagi indeksni 1 ga oshirish
    await state.update_data(current_question_index=current_idx + 1)
    
    # Foydalanuvchiga xabar yuborish (keyingi savol yoki test yakuni)
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    # Foydalanuvchiga shaxsiy xabar yuborish uchun user obyektini olish
    user = poll_answer.user
    
    # Kichik kechikuv (Telegram rate limit uchun)
    import asyncio
    await asyncio.sleep(1)
    
    # Keyingi savolni yuborish yoki testni yakunlash
    # Eslatma: poll_answer'da message yo'q, shuning uchun bot.send_message ishlatamiz
    try:
        # Progress xabari
        next_idx = current_idx + 1
        total = data.get("total_questions", len(questions))
        
        if next_idx < total:
            # Hali savollar bor — progress ko'rsatish
            await bot.send_message(
                chat_id=user.id,
                text=f"✅ <b>{next_idx}/{total}</b> savolga o'tdingiz",
                parse_mode="HTML"
            )
            await asyncio.sleep(1)
        
        # Keyingi savolni yuborish (send_next_poll_question bot.send_message ishlatadi)
        # Lekin bu yerda message obyekti yo'q, shuning uchun maxsus funksiya kerak
        await send_next_poll_question_for_user(bot, user.id, state, lang)
        
    except Exception as e:
        logger.error(f"Keyingi savolni yuborishda xatolik: {e}")


async def send_next_poll_question_for_user(bot:Bot, chat_id: int, state: FSMContext, lang: str):
    """poll_answer handler ichidan keyingi savolni yuborish uchun maxsus funksiya."""
    data = await state.get_data()
    questions = data.get("questions", [])
    current_idx = data.get("current_question_index", 0)
    total = data.get("total_questions", len(questions))
    
    # Agar savollar tugagan bo'lsa — testni yakunlash
    if current_idx >= len(questions):
        await finish_test_for_user(bot, chat_id, state, lang)
        return
    
    q = questions[current_idx]
    
    # Savol raqamini ko'rsatish
    progress_text = f"📝 <b>Savol {current_idx + 1}/{total}</b>"
    await bot.send_message(chat_id=chat_id, text=progress_text, parse_mode="HTML")
    
    # Telegram Quiz Poll yuborish
    try:
        await bot.send_poll(
            chat_id=chat_id,
            question=q["question_text"],
            options=q["options"],
            type="quiz",
            correct_option_id=q["correct_option_index"],
            explanation=q.get("explanation", ""),
            is_anonymous=False,
        )
    except Exception as e:
        logger.error(f"Poll yuborishda xatolik (user {chat_id}): {e}")
        await bot.send_message(
            chat_id=chat_id,
            text=get_text("test.poll_error", lang),
            parse_mode="HTML"
        )
        await finish_test_for_user(bot, chat_id, state, lang)


# ══════════════════════════════════════════════════════════════
# TESTNI YAKUNLASH
# ══════════════════════════════════════════════════════════════

async def finish_test(message: types.Message, state: FSMContext, lang: str):
    """Test tugadi — natijani hisoblash va ko'rsatish (message orqali)."""
    data = await state.get_data()
    await _process_test_result(message, data, lang)
    await state.clear()


async def finish_test_for_user(bot:Bot, chat_id: int, state: FSMContext, lang: str):
    """Test tugadi — natijani hisoblash va ko'rsatish (chat_id orqali)."""
    data = await state.get_data()
    
    score = data.get("score", 0)
    total = data.get("total_questions", 0)
    percentage = int((score / total) * 100) if total > 0 else 0
    passing_score = data.get("passing_score", 60)
    passed = percentage >= passing_score
    
    # Natija xabari
    if passed:
        result_text = get_text("test.passed", lang).format(
            score=score,
            total=total,
            percentage=percentage
        )
    else:
        result_text = get_text("test.failed", lang).format(
            score=score,
            total=total,
            percentage=percentage,
            passing_score=passing_score
        )
    
    await bot.send_message(
        chat_id=chat_id,
        text=result_text,
        parse_mode="HTML",
        reply_markup=registered_menu_kb(lang)
    )
    
    # Backendga natijani yuborish
    try:
        await submit_test_attempt(
            user_id=chat_id,
            test_id=data.get("current_test_id"),
            score=score,
            total_questions=total,
            percentage=percentage,
            passed=passed
        )
    except Exception as e:
        logger.error(f"Natijani backendga yuborishda xatolik: {e}")
    
    await state.clear()


async def _process_test_result(message: types.Message, data: dict, lang: str):
    """Test natijasini hisoblash va ko'rsatish."""
    score = data.get("score", 0)
    total = data.get("total_questions", 0)
    percentage = int((score / total) * 100) if total > 0 else 0
    passing_score = data.get("passing_score", 60)
    passed = percentage >= passing_score
    
    # Natija xabari
    if passed:
        result_text = get_text("test.passed", lang).format(
            score=score,
            total=total,
            percentage=percentage
        )
    else:
        result_text = get_text("test.failed", lang).format(
            score=score,
            total=total,
            percentage=percentage,
            passing_score=passing_score
        )
    
    await message.answer(
        result_text,
        parse_mode="HTML",
        reply_markup=registered_menu_kb(lang)
    )
    
    # Backendga natijani yuborish
    try:
        await submit_test_attempt(
            user_id=message.from_user.id,
            test_id=data.get("current_test_id"),
            score=score,
            total_questions=total,
            percentage=percentage,
            passed=passed
        )
    except Exception as e:
        logger.error(f"Natijani backendga yuborishda xatolik: {e}")


# ══════════════════════════════════════════════════════════════
# TESTNI BEKOR QILISH (agar foydalanuvchi chiqib ketsa)
# ══════════════════════════════════════════════════════════════

@router.message(StateFilter(TestSection.taking_quiz), F.text.in_(["❌ Bekor qilish", "❌ Отменить"]))
async def cancel_test(message: types.Message, state: FSMContext):
    """Foydalanuvchi testni bekor qildi."""
    user_data = await state.get_data()
    lang = _get_lang(user_data)
    
    await message.answer(
        get_text("test.cancelled", lang),
        parse_mode="HTML",
        reply_markup=registered_menu_kb(lang)
    )
    await state.clear()