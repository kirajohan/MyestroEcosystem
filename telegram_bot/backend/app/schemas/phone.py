# bot/utils/phone.py
import re
from typing import Optional

def normalize_phone(text: str) -> Optional[str]:
    """Har qanday manbadan (matn yoki Telegram contact.phone_number) kelgan
    raqamni +998XXXXXXXXX formatiga keltiradi."""
    if not text:
        return None
    text = text.strip()
    has_plus = text.startswith('+')
    digits = re.sub(r'\D', '', text)
    if len(digits) >= 9:
        if has_plus or digits.startswith('998'):
            if not digits.startswith('+'):
                digits = '+' + digits
        else:
            digits = '+998' + digits
        return digits
    return None