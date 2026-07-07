"""Seed default bot texts (i18n) for testing."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.bot_text import BotText


def seed_bot_texts():
    """Create default bot texts for all languages."""
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        existing = db.query(BotText).first()
        if existing:
            print("Bot texts already seeded. Skipping.")
            return

        default_texts = [
            # UZ
            BotText(key="start.language_changed", lang="uz", text="✅ Til o'zgartirildi!"),
            BotText(key="main_menu", lang="uz", text="🏠 Asosiy menyu"),
            BotText(key="about.text", lang="uz", text="ℹ️ Myestro — AI yordamida ingliz tini o'rganish platformasi."),
            BotText(key="guide.text", lang="uz", text="📖 Qo'llanma: Botdan foydalanish bo'yicha ko'rsatmalar."),
            BotText(key="language.prompt", lang="uz", text="🌐 Tilni tanlang:"),
            BotText(key="settings.title", lang="uz", text="⚙️ Sozlamalar"),
            BotText(key="settings.logout_done", lang="uz", text="🚪 Tizimdan chiqdingiz."),
            BotText(key="profile.title", lang="uz", text="👤 Profil"),
            BotText(key="profile.edit_prompt", lang="uz", text="Qaysi maydonni o'zgartirmoqchisiz?"),
            BotText(key="profile.updated", lang="uz", text="✅ Ma'lumot yangilandi!"),
            BotText(key="admin.instruction", lang="uz", text="📨 Adminga xabar yuborish. O'zingizni savolingizni yozing:"),
            BotText(key="admin.sent", lang="uz", text="✅ Xabar yuborildi!"),
            BotText(key="admin.sent_inbox", lang="uz", text="✅ Xabaringiz admin panel'ga yuborildi."),
            BotText(key="video.select", lang="uz", text="🎬 Video darslikni tanlang:"),
            BotText(key="video.not_found", lang="uz", text="❌ Hozircha video darsliklar yo'q."),
            BotText(key="file.select", lang="uz", text="📁 File darslikni tanlang:"),
            BotText(key="file.not_found", lang="uz", text="❌ Hozircha file darsliklar yo'q."),
            BotText(key="ai.thinking", lang="uz", text="🤔 O'ylayapman..."),
            BotText(key="ai.error", lang="uz", text="❌ Xatolik yuz berdi. Iltimos, qayta urining."),
            BotText(key="ai.user_off", lang="uz", text="🤖 AI o'chirilgan. Sozlamalarda yoqishingiz mumkin."),
            BotText(key="ai.global_off", lang="uz", text="🤖 AI global o'chirilgan. Admin tomonidan yoqilishi kutilmoqda."),
            BotText(key="channel.required", lang="uz", text="📢 Botdan foydalanish uchun kanalga obuna bo'lishingiz kerak!"),
            BotText(key="back", lang="uz", text="⬅️ Orqaga"),
            BotText(key="error", lang="uz", text="❌ Xatolik yuz berdi."),
            BotText(key="auth.phone_request", lang="uz", text="📱 Telefon raqamingizni ulashing yoki email kiriting:"),
            BotText(key="login.ask_password", lang="uz", text="🔑 Parolni kiriting:"),
            BotText(key="login.success", lang="uz", text="✅ Tizimga kirdingiz!"),
            BotText(key="register.ask_name", lang="uz", text="📝 Ismingizni kiriting:"),
            BotText(key="register.ask_email", lang="uz", text="📧 Email kiriting:"),
            BotText(key="register.ask_password", lang="uz", text="🔑 Parol kiriting (kamida 8 ta belgi):"),
            BotText(key="register.ask_confirm_password", lang="uz", text="🔑 Parolni tasdiqlang:"),
            BotText(key="register.invalid_email", lang="uz", text="❌ Noto'g'ri email. Qayta kiriting:"),
            BotText(key="register.invalid_password", lang="uz", text="❌ Parol juda qisqa. Kamida 8 ta belgi:"),
            BotText(key="register.password_mismatch", lang="uz", text="❌ Parollar mos kelmaydi. Qayta kiriting:"),
            BotText(key="register.confirm", lang="uz", text="📋 Ma'lumotlaringiz:",),
            BotText(key="registration.done", lang="uz", text="✅ Ro'yxatdan o'tdingiz!"),
            BotText(key="registered.welcome_new", lang="uz", text="🎉 Xush kelibsiz! Siz ro'yxatdan o'tdingiz."),
            BotText(key="ai_fallback_teacher", lang="uz", text="👋 Salom! Men Myestro AI o'qituvchisiman. Savolingizni yozing."),
            BotText(key="ai_fallback_reminder", lang="uz", text="📌 Ro'yxatdan o'tishni unutmang!"),
            BotText(key="auth.phone_not_found", lang="uz", text="📱 Raqam topilmadi. Ro'yxatdan o'ting."),
            BotText(key="auth.email_not_found", lang="uz", text="📧 Email topilmadi. Ro'yxatdan o'ting."),
            BotText(key="auth.invalid_phone_or_email", lang="uz", text="❌ Noto'g'ri format. Telefon yoki email kiriting."),

            # RU
            BotText(key="start.language_changed", lang="ru", text="✅ Язык изменен!"),
            BotText(key="main_menu", lang="ru", text="🏠 Главное меню"),
            BotText(key="about.text", lang="ru", text="ℹ️ Myestro — платформа для изучения английского с AI."),
            BotText(key="guide.text", lang="ru", text="📖 Руководство: инструкции по использованию бота."),
            BotText(key="language.prompt", lang="ru", text="🌐 Выберите язык:"),
            BotText(key="settings.title", lang="ru", text="⚙️ Настройки"),
            BotText(key="settings.logout_done", lang="ru", text="🚪 Вы вышли из системы."),
            BotText(key="profile.title", lang="ru", text="👤 Профиль"),
            BotText(key="profile.edit_prompt", lang="ru", text="Какое поле хотите изменить?"),
            BotText(key="profile.updated", lang="ru", text="✅ Данные обновлены!"),
            BotText(key="admin.instruction", lang="ru", text="📨 Напишите сообщение администратору:"),
            BotText(key="admin.sent", lang="ru", text="✅ Сообщение отправлено!"),
            BotText(key="admin.sent_inbox", lang="ru", text="✅ Сообщение отправлено в панель администратора."),
            BotText(key="video.select", lang="ru", text="🎬 Выберите видеоурок:"),
            BotText(key="video.not_found", lang="ru", text="❌ Пока нет видеоуроков."),
            BotText(key="file.select", lang="ru", text="📁 Выберите файл урока:"),
            BotText(key="file.not_found", lang="ru", text="❌ Пока нет файлов уроков."),
            BotText(key="ai.thinking", lang="ru", text="🤔 Думаю..."),
            BotText(key="ai.error", lang="ru", text="❌ Произошла ошибка. Пожалуйста, попробуйте снова."),
            BotText(key="ai.user_off", lang="ru", text="🤖 AI отключен. Вы можете включить его в настройках."),
            BotText(key="ai.global_off", lang="ru", text="🤖 AI глобально отключен. Ожидается включение администратором."),
            BotText(key="channel.required", lang="ru", text="📢 Для использования бота необходимо подписаться на канал!"),
            BotText(key="back", lang="ru", text="⬅️ Назад"),
            BotText(key="error", lang="ru", text="❌ Произошла ошибка."),
            BotText(key="auth.phone_request", lang="ru", text="📱 Поделитесь номером телефона или введите email:"),
            BotText(key="login.ask_password", lang="ru", text="🔑 Введите пароль:"),
            BotText(key="login.success", lang="ru", text="✅ Вы вошли в систему!"),
            BotText(key="register.ask_name", lang="ru", text="📝 Введите имя:"),
            BotText(key="register.ask_email", lang="ru", text="📧 Введите email:"),
            BotText(key="register.ask_password", lang="ru", text="🔑 Введите пароль (минимум 8 символов):"),
            BotText(key="register.ask_confirm_password", lang="ru", text="🔑 Подтвердите пароль:"),
            BotText(key="register.invalid_email", lang="ru", text="❌ Неверный email. Повторите ввод:"),
            BotText(key="register.invalid_password", lang="ru", text="❌ Пароль слишком короткий. Минимум 8 символов:"),
            BotText(key="register.password_mismatch", lang="ru", text="❌ Пароли не совпадают. Повторите ввод:"),
            BotText(key="register.confirm", lang="ru", text="📋 Ваши данные:"),
            BotText(key="registration.done", lang="ru", text="✅ Вы зарегистрировались!"),
            BotText(key="registered.welcome_new", lang="ru", text="🎉 Добро пожаловать! Вы зарегистрировались."),
            BotText(key="ai_fallback_teacher", lang="ru", text="👋 Привет! Я AI учитель Myestro. Напишите ваш вопрос."),
            BotText(key="ai_fallback_reminder", lang="ru", text="📌 Не забудьте зарегистрироваться!"),
            BotText(key="auth.phone_not_found", lang="ru", text="📱 Номер не найден. Зарегистрируйтесь."),
            BotText(key="auth.email_not_found", lang="ru", text="📧 Email не найден. Зарегистрируйтесь."),
            BotText(key="auth.invalid_phone_or_email", lang="ru", text="❌ Неверный формат. Введите телефон или email."),

            # EN
            BotText(key="start.language_changed", lang="en", text="✅ Language changed!"),
            BotText(key="main_menu", lang="en", text="🏠 Main menu"),
            BotText(key="about.text", lang="en", text="ℹ️ Myestro — AI-powered English learning platform."),
            BotText(key="guide.text", lang="en", text="📖 Guide: How to use the bot."),
            BotText(key="language.prompt", lang="en", text="🌐 Select language:"),
            BotText(key="settings.title", lang="en", text="⚙️ Settings"),
            BotText(key="settings.logout_done", lang="en", text="🚪 You have logged out."),
            BotText(key="profile.title", lang="en", text="👤 Profile"),
            BotText(key="profile.edit_prompt", lang="en", text="Which field do you want to edit?"),
            BotText(key="profile.updated", lang="en", text="✅ Information updated!"),
            BotText(key="admin.instruction", lang="en", text="📨 Send a message to admin. Write your question:"),
            BotText(key="admin.sent", lang="en", text="✅ Message sent!"),
            BotText(key="admin.sent_inbox", lang="en", text="✅ Your message has been sent to the admin panel."),
            BotText(key="video.select", lang="en", text="🎬 Select a video lesson:"),
            BotText(key="video.not_found", lang="en", text="❌ No video lessons available yet."),
            BotText(key="file.select", lang="en", text="📁 Select a file lesson:"),
            BotText(key="file.not_found", lang="en", text="❌ No file lessons available yet."),
            BotText(key="ai.thinking", lang="en", text="🤔 Thinking..."),
            BotText(key="ai.error", lang="en", text="❌ An error occurred. Please try again."),
            BotText(key="ai.user_off", lang="en", text="🤖 AI is disabled. You can enable it in settings."),
            BotText(key="ai.global_off", lang="en", text="🤖 AI is globally disabled. Waiting for admin to enable."),
            BotText(key="channel.required", lang="en", text="📢 You must subscribe to the channel to use the bot!"),
            BotText(key="back", lang="en", text="⬅️ Back"),
            BotText(key="error", lang="en", text="❌ An error occurred."),
            BotText(key="auth.phone_request", lang="en", text="📱 Share your phone number or enter email:"),
            BotText(key="login.ask_password", lang="en", text="🔑 Enter password:"),
            BotText(key="login.success", lang="en", text="✅ You have logged in!"),
            BotText(key="register.ask_name", lang="en", text="📝 Enter your name:"),
            BotText(key="register.ask_email", lang="en", text="📧 Enter email:"),
            BotText(key="register.ask_password", lang="en", text="🔑 Enter password (at least 8 characters):"),
            BotText(key="register.ask_confirm_password", lang="en", text="🔑 Confirm password:"),
            BotText(key="register.invalid_email", lang="en", text="❌ Invalid email. Please re-enter:"),
            BotText(key="register.invalid_password", lang="en", text="❌ Password too short. At least 8 characters:"),
            BotText(key="register.password_mismatch", lang="en", text="❌ Passwords do not match. Please re-enter:"),
            BotText(key="register.confirm", lang="en", text="📋 Your information:"),
            BotText(key="registration.done", lang="en", text="✅ You have registered!"),
            BotText(key="registered.welcome_new", lang="en", text="🎉 Welcome! You have registered."),
            BotText(key="ai_fallback_teacher", lang="en", text="👋 Hello! I am Myestro AI teacher. Ask me anything."),
            BotText(key="ai_fallback_reminder", lang="en", text="📌 Don't forget to register!"),
            BotText(key="auth.phone_not_found", lang="en", text="📱 Phone not found. Please register."),
            BotText(key="auth.email_not_found", lang="en", text="📧 Email not found. Please register."),
            BotText(key="auth.invalid_phone_or_email", lang="en", text="❌ Invalid format. Enter phone or email."),
        ]

        for text in default_texts:
            db.add(text)

        db.commit()
        print("=" * 50)
        print("DEFAULT BOT TEXTS SEEDED SUCCESSFULLY")
        print("=" * 50)
        print(f"Items: {len(default_texts)}")
        print("=" * 50)

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_bot_texts()
