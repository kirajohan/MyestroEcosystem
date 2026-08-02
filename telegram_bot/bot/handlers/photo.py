from aiogram import Router, types, F

router = Router()


@router.message(F.photo)
async def handle_photo(message: types.Message):
    """Handle photo messages — not supported yet."""
    await message.answer(
        "😔 Kechirasiz, men faqat matn  qabul qila olaman.\n"
        "Пожалуйста, отправьте текст или голосовое сообщение.\n"
        "Please send text or voice messages only."
    )
