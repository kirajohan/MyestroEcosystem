#!/usr/bin/env python
"""Add channel.required keys to i18n.py"""

import re

# Read the file
with open('bot/utils/i18n.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and add for uz
content = re.sub(
    r'("admin\.sent": "✅ Xabaringiz admin ga yuborildi! Tez orada javob olasiz\.",)\n\n        # ─── REGISTRATION',
    r'\1\n\n        # ─── CHANNEL SUBSCRIPTION ────────────────────────────\n        "channel.required": "📢 Kanal obunasi talab qilinadi!\\n\\n{channel_url}\\n\\nKanalga obuna bo\'ling, keyin qayta urinib ko\'ring.",\n\n        # ─── REGISTRATION',
    content
)

# Find and add for ru
content = re.sub(
    r'("admin\.sent": "✅ Ваше сообщение отправлено администратору! Вы получите ответ в ближайшее время\.",)\n\n        "registration\.phone_request"',
    r'\1\n\n        # ─── CHANNEL SUBSCRIPTION ────────────────────────────\n        "channel.required": "📢 Требуется подписка на канал!\\n\\n{channel_url}\\n\\nПодпишитесь на канал и попробуйте снова.",\n\n        "registration.phone_request"',
    content
)

# Find and add for en
content = re.sub(
    r'("admin\.sent": "✅ Your message has been sent to admin! You will receive a reply soon\.",)\n\n        "registration\.phone_request"',
    r'\1\n\n        # ─── CHANNEL SUBSCRIPTION ────────────────────────────\n        "channel.required": "📢 Channel subscription required!\\n\\n{channel_url}\\n\\nSubscribe to the channel, then try again.",\n\n        "registration.phone_request"',
    content
)

# Write back
with open('bot/utils/i18n.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Added channel.required keys to i18n.py')
