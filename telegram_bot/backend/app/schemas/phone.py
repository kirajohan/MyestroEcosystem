# app/schemas/phone.py
import re
from typing import Optional

def normalize_phone(text: str) -> Optional[str]:
    """Har qanday manbadan (matn yoki Telegram contact.phone_number) kelgan
    raqamni +998XXXXXXXXX formatiga keltiradi."""
    if not text:
        return None
    
    text = text.strip()
    # Remove all non-digits
    digits = re.sub(r'\D', '', text)
    
    if len(digits) < 9:
        return None
    
    # If already starts with 998 or input had +998, format it
    if digits.startswith('998'):
        return '+' + digits
    
    # If it's 9 digits (like 946521323), prepend +998
    if len(digits) == 9:
        return '+998' + digits
    
    # If it's 12 digits starting with 998 (already has +998 included), prepend +
    if len(digits) == 12:
        return '+' + digits
    
    # Default: prepend +998 for anything else
    return '+998' + digits
