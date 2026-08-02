from aiogram import Router, types, F

router = Router()


@router.message(F.document)
async def handle_document(message: types.Message):
    await message.answer(
        "😔 Kechirasiz, men faqat matn xabarlarni qabul qila olaman.\n"
        "Пожалуйста, отправьте текст или голосовое сообщение.\n"
        "Please send text or voice messages only."
    )
