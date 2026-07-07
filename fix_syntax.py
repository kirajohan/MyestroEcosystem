import sys

with open('telegram_bot/bot/utils/i18n.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix all instances of literal backslash-n followed by quote and comma
content = content.replace('",\\n        "', '",\n        "')
content = content.replace('",\\n    },', '",\n    },')

with open('telegram_bot/bot/utils/i18n.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed i18n.py syntax errors")
