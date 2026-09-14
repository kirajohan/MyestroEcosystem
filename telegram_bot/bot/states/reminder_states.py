"""FSM States uchun Eslatmalar (Reminders)."""
from aiogram.fsm.state import State, StatesGroup


class ReminderFSM(StatesGroup):
    """Eslatma yaratish FSM oqimi."""
    waiting_ai_choice = State()     # ⭐ YANGI: AI yoki statik?
    waiting_ai_prompt = State()     # ⭐ YANGI: AI prompt
    waiting_text = State()          # Matn kiritish
    waiting_type = State()       
    waiting_date = State()      # ⭐ YANGI: Bir martalik uchun kun tanlash
    waiting_time = State()          # Vaqt kiritish (HH:MM)
    waiting_day = State()           # Haftalik uchun kun tanlash
    waiting_datetime = State()      # Bir martalik uchun aniq sana+vaqt
    confirm = State()               # Tasdiqlash