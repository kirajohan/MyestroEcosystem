def channel_subscribe_kb(lang: str = "uz", channel_id: str = "") -> InlineKeyboardMarkup:
    """Channel subscription prompt: Join channel + Check again."""
    from bot.utils.i18n import get_text
    from bot.config import settings
    
    texts = {
        "uz": {"join": "📢 Kanalga obuna bo'lish", "check": "✅ Obunani tekshirish"},
        "ru": {"join": "📢 Подписаться на канал", "check": "✅ Проверить подписку"},
        "en": {"join": "📢 Join channel", "check": "✅ Check subscription"},
    }
    t = texts.get(lang, texts["uz"])
    builder = InlineKeyboardBuilder()
    
    # Use channel URL from settings if available, otherwise construct from channel_id
    channel_url = settings.CHANNEL_URL or f"https://t.me/{channel_id.lstrip('@')}"
    
    builder.button(text=t["join"], url=channel_url)
    builder.button(text=t["check"], callback_data="channel_joined")
    builder.adjust(1)
    return builder.as_markup()
