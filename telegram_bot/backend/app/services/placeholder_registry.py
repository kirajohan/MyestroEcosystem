"""Placeholder registry — defines all available placeholders for broadcast messages.

Each placeholder can be used in broadcast message content and will be replaced
with actual user data when sending.
"""

PLACEHOLDER_REGISTRY = [
    {"key": "{id}", "label": "User ID", "example": "123"},
    {"key": "{email}", "label": "Email", "example": "aziz@mail.com"},
    {"key": "{full_name}", "label": "To'liq ism", "example": "Aziz Karimov"},
    {"key": "{role}", "label": "Rol", "example": "student"},
    {"key": "{cefr_level}", "label": "CEFR darajasi", "example": "B1"},
    {"key": "{target_level}", "label": "Maqsad daraja", "example": "C1"},
    {"key": "{avatar_url}", "label": "Avatar URL", "example": "https://example.com/avatar.jpg"},
    {"key": "{phone}", "label": "Telefon raqam", "example": "+998901234567"},
    {"key": "{lang}", "label": "Interfeys tili", "example": "uz"},
    {"key": "{learning_lang}", "label": "O'rganilayotgan til", "example": "en"},
    {"key": "{telegram_id}", "label": "Telegram ID", "example": "123456789"},
    {"key": "{telegram_username}", "label": "Telegram username", "example": "@aziz_dev"},
    {"key": "{auth_provider}", "label": "Auth provider", "example": "email"},
    {"key": "{provider_user_id}", "label": "Provider user ID", "example": "google_123"},
    {"key": "{is_active}", "label": "Faol holat", "example": "true"},
    {"key": "{is_verified}", "label": "Tasdiqlangan", "example": "true"},
    {"key": "{profile_completed}", "label": "Profil to'ldirilgan", "example": "true"},
    {"key": "{last_login_at}", "label": "Oxirgi kirish", "example": "2024-01-15 10:30:00"},
    {"key": "{location}", "label": "Manzil", "example": "Tashkent"},
    {"key": "{ai_enabled}", "label": "AI yoqilgan", "example": "true"},
    {"key": "{created_at}", "label": "Yaratilgan sana", "example": "2024-01-01 00:00:00"},
    {"key": "{updated_at}", "label": "Yangilangan sana", "example": "2024-01-15 10:30:00"},
]


def get_placeholders() -> list[dict]:
    """Return the placeholder registry."""
    return PLACEHOLDER_REGISTRY


def get_safe_user_fields() -> list[str]:
    """Return list of safe user field names for placeholders.
    
    Excludes sensitive fields: password_hash, deleted_at
    """
    return [p["key"].strip("{}") for p in PLACEHOLDER_REGISTRY]