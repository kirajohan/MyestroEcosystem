from aiogram import Router
from aiogram import types, F
from aiogram.fsm.context import FSMContext
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text, F.chat.type == "private")
async def debug_text(message: types.Message, state: FSMContext):
    """Debug handler: logs incoming private text messages. Does not block propagation."""
    try:
        state_name = await state.get_state()
        user_data = await state.get_data()
    except Exception:
        state_name = None
        user_data = {}

    log_msg = f"[DEBUG_HANDLER] user={message.from_user.id} text='{(message.text or '')[:200]}' state={state_name} user_data_keys={list(user_data.keys())}"
    logger.info(log_msg)
    print(log_msg)
    # Do not return None explicitly; allow other handlers to run
    return
