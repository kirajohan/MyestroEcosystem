from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


class IsRegistered(BaseFilter):
    """✅ Faqat REGISTERED userlar uchun."""

    async def __call__(self, event, state: FSMContext) -> bool:
        user_data = await state.get_data()
        return user_data.get("registration_complete", False) is True


class IsNotRegistered(BaseFilter):
    """🚫 Faqat UNREGISTERED userlar uchun."""

    async def __call__(self, event, state: FSMContext) -> bool:
        user_data = await state.get_data()
        return user_data.get("registration_complete", False) is not True