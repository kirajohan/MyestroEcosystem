from aiogram.types import KeyboardButton, InlineKeyboardButton
from typing import Optional, Literal, ClassVar

class StyledKeyboardButton(KeyboardButton):
    """Extended KeyboardButton with proper style support."""
    
    def __init__(
        self,
        text: str,
        style: Optional[Literal["primary", "danger", "success"]] = None,
        request_contact: bool = False,
        request_location: bool = False,
        request_poll: Optional[dict] = None,
    ):
        # Prepend a small emoji/icon according to style so buttons look "colored" in Telegram
        prefix_map = {
            "primary": "",
            "danger": "",
            "success": "",
        }
        display_text = f"{prefix_map.get(style, '')} {text}" if style else text

        # Pass adjusted text to parent
        super().__init__(
            text=display_text,
            request_contact=request_contact,
            request_location=request_location,
            request_poll=request_poll,
        )

        # Keep style attribute for compatibility
        if style:
            self.style = style


class StyledInlineKeyboardButton(InlineKeyboardButton):
    """Extended InlineKeyboardButton with proper style support."""
    
    def __init__(
        self,
        text: str,
        callback_data: Optional[str] = None,
        style: Optional[Literal["primary", "danger", "success"]] = None,
        **kwargs
    ):
        # ✅ Style parametrini qo'llab-quvvatlang
        super().__init__(
            text=text,
            callback_data=callback_data,
            **kwargs
        )
        
        if style:
            self.style = style