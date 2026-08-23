# bot/states/test_states.py
"""
Test (Quiz) moduli uchun FSM holatlari.
"""

from aiogram.fsm.state import State, StatesGroup


class TestSection(StatesGroup):
    """Test bo'limi holatlari."""
    
    # CEFR daraja tanlash
    cefr_selection = State()
    
    # Testlar ro'yxati
    test_list = State()
    
    # Test topshirish jarayoni (Telegram Quiz Poll)
    taking_quiz = State()