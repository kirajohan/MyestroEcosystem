from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.command import Command
from bot.utils.i18n import get_text
from bot.utils.helpers import clean_telegram_text
from bot.config import settings
import httpx

router = Router()

# Backend API URL
BACKEND_URL = settings.BACKEND_URL

class ChatStates(StatesGroup):
    selecting_thread = State()
    chatting = State()

@router.message(Command("chat"), F.chat.type == "private")
async def start_chat(message: types.Message, state: FSMContext):
    """Chat menu — thread'larni ko'rsatish"""
    user_id = message.from_user.id
    
    # Backend'dan thread'larni ol
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BACKEND_URL}/conversations/threads",
            params={"user_id": user_id}
        )
        threads = response.json()
    
    # Keyboard'ni yaratish (Max 10 ta)
    builder = types.InlineKeyboardBuilder()
    
    for thread in threads[:10]:
        builder.button(
            text=f"💬 {thread['title']} ({len(thread.get('messages', []))} msg)",
            callback_data=f"thread_{thread['id']}"
        )
    
    builder.button(text="➕ Yangi suhbat", callback_data="new_thread")
    builder.adjust(1)
    
    await message.answer(
        "🎯 <b>O'z suhbatlarini tanlang:</b>\n\n(Max 10 ta thread mavjud)",
        reply_markup=builder.as_markup()
    )
    await state.set_state(ChatStates.selecting_thread)

@router.callback_query(F.data.startswith("thread_"))
async def select_thread(callback: types.CallbackQuery, state: FSMContext):
    """Thread'ni tanlash"""
    thread_id = int(callback.data.split("_")[1])
    
    await state.update_data(thread_id=thread_id)
    await state.set_state(ChatStates.chatting)
    
    await callback.message.edit_text(
        "✍️ <b>Xabar yozing va Enter bosing:</b>\n"
        "(Qaytish uchun /menu)"
    )

@router.message(ChatStates.chatting, F.chat.type == "private")
async def process_chat_message(message: types.Message, state: FSMContext):
    """Xabarni backend'ga yuborish va AI javobini olish"""
    data = await state.get_data()
    thread_id = data["thread_id"]
    user_id = message.from_user.id

    # ═══════════════════════════════════════════════════════════
    # SECURITY: Check registration status
    # ═══════════════════════════════════════════════════════════
    if not data.get("registration_complete"):
        lang = data.get("lang", "uz")
        await message.answer(get_text("ai.not_registered", lang))
        return

    # ═══════════════════════════════════════════════════════════
    # SECURITY: Input sanitization
    # ═══════════════════════════════════════════════════════════
    user_text = message.text or ""
    user_text = clean_telegram_text(user_text)
    if not user_text:
        await message.answer("Iltimos, matnli xabar yozing.")
        return
    
    # Typing indicator
    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing"
    )
    
    # Backend'ga xabar yuborish
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/conversations/threads/{thread_id}/messages",
            json={
                "user_id": user_id,
                "content": user_text
            }
        )
        result = response.json()
    
    # AI javobini ko'rsatish
    ai_response = result["assistant_message"]["content"]
    
    await message.answer(
        f"🤖 <b>Javob:</b>\n\n{ai_response}\n\n"
        f"<i>(Davom etish uchun xabar yozing yoki /menu bosing)</i>"
    )

@router.callback_query(F.data == "new_thread")
async def create_new_thread(callback: types.CallbackQuery, state: FSMContext):
    """Yangi thread yaratish"""
    await callback.message.edit_text(
        "📝 <b>Suhbat sarlavhasini kiriting:</b>\n"
        "(Misol: <code>Business English</code>)"
    )
    await state.set_state(ChatStates.selecting_thread)  # Vaqtincha holat

@router.message(ChatStates.selecting_thread, F.chat.type == "private")
async def save_thread_title(message: types.Message, state: FSMContext):
    """Yangi thread yaratish va saqlash"""
    user_id = message.from_user.id
    title = message.text or ""

    # ═══════════════════════════════════════════════════════════
    # SECURITY: Input sanitization for title
    # ═══════════════════════════════════════════════════════════
    title = clean_telegram_text(title)
    if len(title) > 100:
        title = title[:100]
    if not title:
        title = "New Chat"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BACKEND_URL}/conversations/threads",
            json={
                "user_id": user_id,
                "title": title,
                "cefr_level": "A1"
            }
        )
        thread = response.json()
    
    await state.update_data(thread_id=thread["id"])
    await state.set_state(ChatStates.chatting)
    
    await message.answer(
        f"✅ Suhbat <b>{title}</b> yaratildi!\n"
        f"Endi xabar yozing:"
    )