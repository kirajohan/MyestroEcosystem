from aiogram import Router, types
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(types.ContentType.VOICE)
async def handle_voice(message: types.Message):
    """Voice messages not supported."""
    await message.answer(
        "❌ <b>Afsuski, faqat matn xabarlarni qabul qila olaman.</b>\n\n"
        "Iltimos, matnli formatda yozing yoki ↩️ <b>Orqaga</b> bosing."
    )

