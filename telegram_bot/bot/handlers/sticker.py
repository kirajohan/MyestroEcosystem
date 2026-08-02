from aiogram import Router, types, F

router = Router()


@router.message(F.sticker)
async def handle_sticker(message: types.Message):
    await message.answer(
        "😔 Kechirasiz, men faqat matn  qabul qila olaman.\n"
        "Пожалуйста, отправьте текст или голосовое сообщение.\n"
        "Please send text or voice messages only."
    )
