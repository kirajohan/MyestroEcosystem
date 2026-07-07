from aiogram import Router, types, F

router = Router()


@router.callback_query(F.data == "menu_academy")
async def show_academy(callback: types.CallbackQuery):
    await callback.message.answer(
        "🏫 Myestro Academy\n\n"
        "Online English learning platform\n"
        "• AI-powered teacher\n"
        "• IELTS/TOEFL/CEFR preparation\n"
        "• Personalized learning path\n"
        "• 24/7 available\n\n"
        "Learn more: @myestro_academy"
    )
    await callback.answer()
