"""FSM States for Myestro Telegram Bot.

Flow:
1. /start → Language selection
2. Language → Main Menu (NOT_REGISTERED_USER_SECTION)
3. Register/Login → Phone request → DB check
4. If found → REGISTERED_USER_SECTION
5. If NOT found → Registration FSM (Name → Birthdate → Level → Confirmation)
"""

from aiogram.fsm.state import State, StatesGroup


class RegistrationStates(StatesGroup):
    """Original registration states (kept for backward compatibility)."""
    select_language = State()
    waiting_name = State()
    waiting_level = State()
    registration_done = State()


class StartSection(StatesGroup):
    """Start section — language selection → main menu."""
    language_selection = State()       # Til tanlash
    main_menu = State()                # Asosiy menyu (NOT_REGISTERED)


class RegistrationFSM(StatesGroup):
    """Eski Registration FSM (backward compatibility)."""
    phone_request = State()            # Telefon raqam so'rash
    phone_verified = State()           # DB tekshirildi
    waiting_name = State()             # Ism-Familiya kiritish
    waiting_email = State()            # Email kiritish (NEW)
    waiting_birthdate = State()        # Tug'ilgan kun (optional)
    waiting_level = State()            # CEFR level tanlash
    confirmation = State()             # Tasdiqlash


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
    contact_admin = State()             # Admin ga xabar yozish
    settings = State()                  # Sozlamalar
    profile = State()                   # Profil
    video_lessons = State()             # Video darsliklar
    file_lessons = State()              # File darsliklar


class RegisteredSection(StatesGroup):
    """Registered user states."""
    main_menu = State()                 # Asosiy menyu (REGISTERED)
    idle = State()                      # Umumiy holat


class InboxState(StatesGroup):
    """User states for inbox interaction (admin messages)."""
    waiting_for_subject = State()       # Xabar mavzusi
    waiting_for_message = State()       # Xabar matni


class LessonsStates(StatesGroup):
    """Lessons FSM states — lesson type selection + content viewing."""
    selecting_type = State()            # Video yoki File tanlash
    viewing_lessons = State()           # Darslarni ko'rish


class TestStates(StatesGroup):
    """Test FSM states — CEFR level selection + answering + results."""
    selecting_level = State()           # CEFR level tanlash (A1-C2)
    answering_questions = State()       # Savollarni javoblash
    viewing_results = State()           # Natijalarni ko'rish
