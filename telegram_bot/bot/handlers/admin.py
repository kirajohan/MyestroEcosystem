from aiogram import Router, types, F
from aiogram.filters import Command

router = Router()


@router.message(Command("admin"))
async def admin_broadcast(message: types.Message):
    """Admin panel — broadcast and stats."""
    if message.from_user.id not in getattr(message.bot, "admin_ids", []):
        await message.answer("Access denied.")
        return

    await message.answer(
        "🛠 Admin Panel\n\n"
        "Commands:\n"
        "/stats — view bot statistics\n"
        "/broadcast <text> — send message to all users"
    )


@router.message(Command("stats"))
async def admin_stats(message: types.Message):
    await message.answer("📊 Bot Statistics\n\nComing soon.")
