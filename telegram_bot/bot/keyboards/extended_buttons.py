

from aiogram.types import KeyboardButton
from typing import Optional, Literal


class StyledKeyboardButton(KeyboardButton):
    """Extended KeyboardButton with style support for reply keyboards.
    
    Styles:
    - "primary": Blue (default button style)
    - "success": Green (positive action)
    - "danger": Red (destructive action)
    """
    
    def __init__(
        self,
        text: str,
        style: Optional[Literal["primary", "danger", "success"]] = None,
        request_contact: bool = False,
        request_location: bool = False,
        request_poll: Optional[dict] = None,
    ):
        super().__init__(
            text=text,
            request_contact=request_contact,
            request_location=request_location,
            request_poll=request_poll,
        )
        if style:
            self.style = style


