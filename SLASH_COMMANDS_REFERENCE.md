# Myestro Slash Commands Reference

> **Status:** Phase 1 Complete ✅  
> **Last Updated:** 2024-07  
> **BotFather Command:** Use this list with `/setcommands` in BotFather

---

## 📋 All Available Commands

| Slash Command | Handler File | Description | State | UI Text |
|---|---|---|---|---|
| `/start` | `start.py` | Start bot / Main menu | **PUBLIC** | — |
| `/register` | `register.py` | Register new user | PUBLIC | `📝 Ro'yxatdan o'tish` |
| `/login` | `register.py` | Login existing user | PUBLIC | `🔐 Tizimga kirish` |
| `/profile` | `profile.py` | View user profile | REGISTERED | `👤 Profil` |
| `/settings` | `menu.py` | Settings & preferences | REGISTERED | `⚙️ Sozlamalar` |
| `/guide` | `menu.py` | User guide | PUBLIC | `📖 Qo'llanma` |
| `/about` | `menu.py` | About Myestro | PUBLIC | `ℹ️ Biz haqimizda` |
| `/admin` | `menu.py` | Contact admin | PUBLIC | `📨 Admin ga xabar` |
| `/video` | `menu.py` | Video lessons | REGISTERED | `🎬 Video Darslik` |
| `/file` | `menu.py` | File lessons | REGISTERED | `📁 File Darsliklar` |
| `/language` | `menu.py` | Change language | PUBLIC | `🌐 Til/Language` |
| `/logout` | `profile.py` | Logout | REGISTERED | — |
| `/ai` | `ai_agent.py` | AI teacher chat | REGISTERED | — |
| `/exam` | `exam.py` | Start exam | REGISTERED | — |
| `/referral` | `referral.py` | Referral program | REGISTERED | — |

---

## 🔄 Implementation Status

### ✅ Completed (Command + F.text.in_ filters)
- `/start` ← already Command("start")
- `/register` ← already Command("register") & Command("login")
- `/profile` ← added Command("profile")
- `/settings` ← added Command("settings")
- `/guide` ← added Command("guide")
- `/about` ← added Command("about")
- `/admin` ← added Command("admin")
- `/video` ← added Command("video")
- `/file` ← added Command("file")
- `/language` ← added Command("language")

### ⏳ To Do (Need Command filter + testing)
- `/logout` ← Check `profile.py` for handler
- `/ai` ← Check `ai_agent.py` for handler  
- `/exam` ← Check `exam.py` for handler
- `/referral` ← Check `referral.py` for handler

---

## 🤖 BotFather /setcommands Format

Copy this list and paste into BotFather with `/setcommands`:

```
start - Botni ishga tushirish
register - Ro'yxatdan o'tish
login - Tizimga kirish
profile - Profil
settings - Sozlamalar va preferences
guide - Foydalanuvchi qo'llanmasi
about - Myestro haqida
admin - Admin bilan aloqa
video - Video darsliklar
file - File darsliklar
language - Tilni o'zgartirish
logout - Tizimdan chiqish
ai - AI o'qituvchi
exam - Imtihon
referral - Referral dasturi
```

---

## 📝 Handler Pattern (Updated)

All menu handlers now support **both** button taps and slash commands:

```python
@router.message((F.text.in_(["⚙️ Sozlamalar", ...])) | Command("settings"))
async def msg_settings(message: types.Message, state: FSMContext):
    """Works from both reply keyboard AND /settings slash command."""
    ...
```

**Filter breakdown:**
- `F.text.in_([...])` ← User tapped reply keyboard button
- `|` ← OR operator
- `Command("settings")` ← User typed `/settings` slash command

---

## 🔐 Access Control

| Level | Commands |
|---|---|
| **PUBLIC** | `/start`, `/register`, `/login`, `/guide`, `/about`, `/admin`, `/language` |
| **REGISTERED** | `/profile`, `/settings`, `/video`, `/file`, `/logout`, `/ai`, `/exam`, `/referral` |
| **ADMIN-ONLY** | *To be implemented in Phase 5* |

---

## ✨ Next Steps

1. **Test slash commands** in Telegram for all updated handlers
2. **Update remaining handlers** (`logout`, `ai`, `exam`, `referral`) with Command filters
3. **Register with BotFather** using `/setcommands` list above
4. **Move to Phase 2:** Channel Check middleware + Bot Settings

---

**Phase 1 Completion:** 10/10 handlers updated ✅
