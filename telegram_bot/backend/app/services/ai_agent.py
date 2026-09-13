"""
Universal AI Agent — OpenRouter Function Calling orqali tool'larni chaqiradi.
"""
import json
import logging
import os
from typing import Any, Dict, List, Optional

import httpx

from app.services.admin_ai_service import (
    AIToolsService,
    ADMIN_TOOLS,
    USER_TOOLS,
)

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


class AIAgent:
    """
    Universal AI Agent.
    Admin va user uchun bir xil ishlaydi, lekin tool'lar ro'yxati har xil.
    """

    SYSTEM_PROMPT_ADMIN = """Sen Myestro platformasining AI yordamchisisan — ADMIN uchun.
Sen butun ma'lumotlar bazasiga kirish huquqiga egasan.

VAZIFALAR:
- Admin so'rovlariga aniq va tushunarli javob berish
- Statistikalarni tahlil qilish
- Muammolarni aniqlash (masalan: xatoliklar, past ballar)
- Tavsiyalar berish

QOIDALAR:
1. Javoblarni O'ZBEK tilida ber (agar boshqacha so'ralmasa).
2. Raqamlarni aniq ko'rsat.
3. Agar ma'lumot yetarli bo'lmasa, qo'shimcha tool chaqir.
4. Murakkab so'rovlar uchun bir necha tool'ni ketma-ket chaqirish mumkin.
5. Natijalarni chiroyli formatlash: emoji, ro'yxat, jadvallar.
"""

    SYSTEM_PROMPT_USER = """Sen Myestro platformasining AI yordamchisisan — foydalanuvchi uchun.
Sen faqat foydalanuvchining O'Z ma'lumotlarini ko'ra olasan.

VAZIFALAR:
- Foydalanuvchining natijalarini tushuntirish
- Progress haqida ma'lumot berish
- Keyingi qadamlar bo'yicha tavsiyalar
- Zaif tomonlarni aniqlash va maslahat berish

QOIDALAR:
1. Do'stona va rag'batlantiruvchi ohangda gapir.
2. O'ZBEK tilida javob ber.
3. Faqat o'z ma'lumotlari haqida gapir (boshqa userlar haqida emas).
"""

    def __init__(self, tools_service: AIToolsService, is_admin: bool):
        self.tools_service = tools_service
        self.is_admin = is_admin
        self.tools = ADMIN_TOOLS if is_admin else USER_TOOLS
        self.system_prompt = self.SYSTEM_PROMPT_ADMIN if is_admin else self.SYSTEM_PROMPT_USER

    async def chat(self, user_message: str, history: List[Dict] = None) -> str:
        """Foydalanuvchi xabariga javob berish (tool calling loop bilan)."""
        if not OPENROUTER_API_KEY:
            return "❌ AI sozlanmagan. OPENROUTER_API_KEY yo'q."

        messages = [{"role": "system", "content": self.system_prompt}]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_message})

        # Tool calling loop (max 5 marta)
        for iteration in range(5):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        OPENROUTER_URL,
                        headers={
                            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": "openai/gpt-4o-mini",
                            "messages": messages,
                            "tools": self.tools,
                            "tool_choice": "auto",
                        },
                    )

                if response.status_code != 200:
                    logger.error(f"OpenRouter error: {response.status_code} - {response.text}")
                    return "⚠️ AI bilan aloqada xatolik."

                data = response.json()
                message = data["choices"][0]["message"]

                # Tool call bo'lmasa — bu yakuniy javob
                if not message.get("tool_calls"):
                    return message.get("content", "Javob yo'q.")

                # Tool call bor — bajaramiz
                messages.append(message)

                for tool_call in message["tool_calls"]:
                    fn_name = tool_call["function"]["name"]
                    try:
                        fn_args = json.loads(tool_call["function"]["arguments"])
                    except json.JSONDecodeError:
                        fn_args = {}

                    logger.info(f"🔧 Calling tool: {fn_name}({fn_args})")

                    # Tool'ni chaqirish
                    result = await self._execute_tool(fn_name, fn_args)

                    # Natijani messages'ga qo'shish
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": json.dumps(result, ensure_ascii=False, default=str),
                    })

            except Exception as e:
                logger.error(f"AI Agent error: {e}", exc_info=True)
                return f"⚠️ Xatolik: {str(e)}"

        return "⚠️ Javob olish uchun juda ko'p urinishlar kerak bo'ldi."

    async def _execute_tool(self, fn_name: str, args: Dict) -> Any:
        """Tool'ni nomi bo'yicha chaqirish."""
        method = getattr(self.tools_service, fn_name, None)
        if not method or not callable(method):
            return {"error": f"Tool '{fn_name}' mavjud emas"}

        try:
            return await method(**args)
        except Exception as e:
            logger.error(f"Tool '{fn_name}' error: {e}", exc_info=True)
            return {"error": str(e)}