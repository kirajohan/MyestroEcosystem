"""FSM States for Myestro Telegram Bot.

Flow:
1. /start → Language selection
2. Language → Main Menu (NOT_REGISTERED_USER_SECTION)
3. Register/Login → Phone request → DB check
4. If found → REGISTERED_USER_SECTION
5. If NOT found → Registration FSM (Name → Birthdate → Level → Confirmation)
"""

from aiogram.fsm.state import State, StatesGroup
# bot/filters/registration.py
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

class IsRegisteredFilter(BaseFilter):
    """Filter for registered users only."""
    def __init__(self, is_registered: bool):
        self.is_registered = is_registered

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        user_data = await state.get_data()
        registration_complete = user_data.get("registration_complete", False)
        return registration_complete == self.is_registered

class QuizSection(StatesGroup):
    """Test's (English QUIZ) — maxsus bo'lim, boshqalardan alohida."""
    cefr_selection = State()    # CEFR daraja tanlash (reply keyboard)
    quiz_list = State()         # Testlar ro'yxati (inline keyboard — pagination)
    quiz_active = State()       # Test jarayoni (inline keyboard — javob berish)
    quiz_results = State()      # Natijani ko'rsatish

class StartSection(StatesGroup):
    """Start section — language selection → main menu."""
    language_selection = State()       # Til tanlash
    main_menu = State()                # Asosiy menyu (NOT_REGISTERED)


class RegistrationFSM(StatesGroup):
    """Registration FSM — Phone → Name → Password → Level → Confirmation."""
    waiting_phone = State()        # Telefon kontaktini kutish
    waiting_name = State()         # Ism kutish
    waiting_password = State()     # Parol kutish
    waiting_level = State()        # Ingliz tili darajasini kutish
    waiting_confirmation = State() # Tasdiqlash


class AuthFSM(StatesGroup):
    """Bitta Auth FSM — Register/Login bitta oqim."""
    requesting_contact = State()       # Telefon raqam so'raydi (contact share yoki text)
    waiting_password = State()         # Login paroli (DB da topilgan foydalanuvchi)
    waiting_name = State()             # Registratsiya ismi
    waiting_email = State()            # Registratsiya email
    waiting_password_new = State()     # Registratsiya paroli
    waiting_confirm_password = State() # Parolni tasdiqlash
    confirmation = State()             # Tasdiqlash


class RegisterFSM(StatesGroup):
    """Yangi Register FSM — Ism → Email → Parol → Tasdiqlash. (Eskirgan, AuthFSM ishlatiladi)"""
    waiting_name = State()             # Ism-Familiya
    waiting_email = State()            # Email
    waiting_password = State()         # Parol
    waiting_confirm_password = State() # Parolni tasdiqlash
    confirmation = State()             # Tasdiqlash


class LoginFSM(StatesGroup):
    """Login FSM — Contact/Email → Parol. (Eskirgan, AuthFSM ishlatiladi)"""
    waiting_contact_or_email = State() # Contact share yoki email matn
    waiting_password = State()         # Parol so'rash


class MenuSection(StatesGroup):
    """Menu section states — sub-menu navigatsiya."""
    idle = State()                      # Asosiy menyuda
    language_selection = State()        # Til o'zgartirish
    about_us = State()                  # About us sub-menu
    guide = State()                     # Qo'llanma sub-menu
    contact_admin = State()             # Admin ga xabar yozish
    settings = State()                  # Sozlamalar
    profile = State()                   # Profil
    video_lessons = State()             # Video darsliklar
    file_lessons = State()              # File darsliklar


class RegisteredSection(StatesGroup):
    """Registered user states."""
    main_menu = State()                 # Asosiy menyu (REGISTERED)
    idle = State()                      # Umumiy holat
