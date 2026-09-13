"""
Universal AI Agent — OpenRouter Function Calling + Oddiy suhbat
Admin va user uchun — role-based access bilan.
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
    - Admin: 40+ tool (butun DB)
    - User: 5 tool (faqat o'z ma'lumotlari)
    - Oddiy suhbat: tool chaqirmasdan javob beradi
    """

    SYSTEM_PROMPT_ADMIN = """Sen Myestro platformasining AI yordamchisisan — ADMIN uchun.
Sen butun ma'lumotlar bazasiga kirish huquqiga egasan va turli tool'lar (funksiyalar) orqali ma'lumot olish imkoniyating bor.

QOIDALAR:
1. Javoblarni O'ZBEK tilida ber (agar boshqacha so'ralmasa).
2. Admin so'roviga qarab qaror qabul qil:
   - Agar admin platforma statistikasi, foydalanuvchilar, imtihonlar, urinishlar, AI xatoliklari haqida so'rasa → TEGISHLI TOOL'NI CHAQIR
   - Agar oddiy savol (masalan: "Past Simple nima?", "Qanday dasturlash kerak?") → Tool CHAQIRMA, to'g'ridan-to'g'ri javob ber
3. Raqamlarni aniq ko'rsat.
4. Murakkab so'rovlar uchun bir necha tool'ni ketma-ket chaqirish mumkin.
5. Natijalarni chiroyli formatlash: emoji, ro'yxat, jadvallar.
6. Xavfsizlik: Faqat admin uchun mo'ljallangan tool'larni chaqir.
"""

    SYSTEM_PROMPT_USER = """Sen Myestro platformasining AI yordamchisisan — foydalanuvchi uchun.
Sen foydalanuvchining O'Z ma'lumotlarini ko'rish uchun bir necha tool'ga (funksiyaga) egasan.

QOIDALAR:
1. Do'stona va rag'batlantiruvchi ohangda gapir.
2. O'ZBEK tilida javob ber.
3. Foydalanuvchi so'roviga qarab qaror qabul qil:
   - Agar foydalanuvchi O'Z natijalari, urinishlari, profili, progressi haqida so'rasa → TEGISHLI TOOL'NI CHAQIR
   - Agar ingliz tili haqida savol (grammar, vocabulary, speaking tips) → Tool CHAQIRMA, AI Teacher sifatida javob ber
   - Agar platforma haqida umumiy savol → Oddiy javob ber
4. Faqat foydalanuvchining O'Z ma'lumotlari haqida gapir (boshqa userlar haqida emas).
5. Foydalanuvchini rag'batlantir, zaif tomonlarini yumshoq tushuntir.
"""

    def __init__(self, tools_service: AIToolsService, is_admin: bool):
        self.tools_service = tools_service
        self.is_admin = is_admin
        self.tools = ADMIN_TOOLS if is_admin else USER_TOOLS
        self.system_prompt = self.SYSTEM_PROMPT_ADMIN if is_admin else self.SYSTEM_PROMPT_USER

    async def chat(
        self, 
        user_message: str, 
        history: Optional[List[Dict]] = None,
        additional_context: Optional[str] = None,
    ) -> str:
        """
        Foydalanuvchi xabariga javob berish.
        AI o'zi qaror qiladi: tool chaqirish yoki oddiy javob.
        """
        if not OPENROUTER_API_KEY:
            return "❌ AI sozlanmagan. OPENROUTER_API_KEY yo'q."

        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Qo'shimcha kontekst (RAG, CEFR, til)
        if additional_context:
            messages.append({
                "role": "system", 
                "content": f"Qo'shimcha kontekst:\n{additional_context}"
            })
        
        # Suhbat tarixi
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
                            "HTTP-Referer": "https://myestro.uz",
                            "X-Title": "Myestro AI",
                        },
                        json={
                            "model": "openai/gpt-4o-mini",
                            "messages": messages,
                            "tools": self.tools,
                            "tool_choice": "auto",  # ← AI o'zi hal qiladi
                        },
                    )

                if response.status_code != 200:
                    logger.error(f"OpenRouter error: {response.status_code} - {response.text[:500]}")
                    return "⚠️ AI bilan aloqada xatolik. Iltimos qayta urinib ko'ring."

                data = response.json()
                message = data["choices"][0]["message"]

                # ✅ Tool call bo'lmasa — bu yakuniy javob (oddiy suhbat)
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

            except httpx.TimeoutException:
                return "⚠️ AI javob berish uchun juda uzoq vaqt talab qildi. Iltimos qayta urinib ko'ring."
            except Exception as e:
                logger.error(f"AI Agent error: {e}", exc_info=True)
                return f"⚠️ Xatolik yuz berdi: {str(e)[:200]}"

        return "⚠️ Javob olish uchun juda ko'p urinishlar kerak bo'ldi. Iltimos soddaroq savol bering."

    async def _execute_tool(self, fn_name: str, args: Dict) -> Any:
        """Tool'ni nomi bo'yicha chaqirish."""
        method = getattr(self.tools_service, fn_name, None)
        if not method or not callable(method):
            return {"error": f"Tool '{fn_name}' mavjud emas"}

        try:
            return await method(**args)
        except TypeError as e:
            logger.error(f"Tool '{fn_name}' argument error: {e}")
            return {"error": f"Tool argumentlari noto'g'ri: {str(e)}"}
        except Exception as e:
            logger.error(f"Tool '{fn_name}' error: {e}", exc_info=True)
            return {"error": str(e)}