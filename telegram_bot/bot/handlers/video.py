from aiogram import Router, types, F

router = Router()


@router.message(F.video)
async def handle_video(message: types.Message):
    await message.answer(
        "😔 Kechirasiz, men faqat matn  qabul qila olaman.\n"
        "Пожалуйста, отправьте текст или голосовое сообщение.\n"
        "Please send text or voice messages only."
    )
