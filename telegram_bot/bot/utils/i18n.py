"""Internationalization — uz, ru, en languages.

Key naming convention: section.subsection.element
"""

TRANSLATIONS = {
    "uz": {
        # ═══════════════════════════════════════════════════════════
        #  START
        # ═══════════════════════════════════════════════════════════
        "start.welcome": (
            "👋 <b>Xush kelibsiz!</b>\n\n"
            "Siz <b>Myestro Teacher</b> — "
            "<a href='https://t.me/myestro_ecosystem'>Myestro Ecosystem</a> "
            "ekosistemasining AI-powered ingliz tili o'qitish platformasidasiz.\n\n"
            "🎯 <b>Platforma imkoniyatlari:</b>\n"
            "• 🤖 <b>AI Teacher</b> — ingliz tilida suhbatlashib, amaliy ko'nikmalarni oshiring\n"
            "• 📝 <b>Myestro Exam</b> — bilim darajangizni obyektiv baholang\n"
            "• 📚 <b>Myestro Academy</b> — o'quv materiallari va kurslar\n"
            "• 🎓 <b>100% bepul</b> — barcha funksiyalar ochiq va bepul\n\n"
            "🚀 Ingliz tilini o'rganishni bugun boshlang!"
        ),
        "start.language_prompt": "🌍 Iltimos, platforma tilini tanlang:",
        "start.language_changed": (
            "✅ <b>Til o'zgartirildi!</b>\n\n"
            "Endi barcha xabarlar va AI suhbatlari <b>o'zbek tilida</b> bo'ladi.\n"
            "Tilni istalgan vaqtda ⚙️ <b>Sozlamalar</b> bo'limidan o'zgartirishingiz mumkin."
        ),

        # ═══════════════════════════════════════════════════════════
        #  ABOUT
        # ═══════════════════════════════════════════════════════════
        "about.title": "ℹ️ <b>Biz haqimizda</b>",
        "about.text": (
            "<b>Myestro</b> — O'zbekiston va Markaziy Osiyo bozoriga mo'ljallangan "
            "zamonaviy, <b>AI-powered</b> ingliz tili o'rganish platformasi.\n\n"
            "🎯 <b>Asosiy yo'nalishlar:</b>\n"
            "• Ingliz tilini noldan o'rganish\n"
            "• Xalqaro imtihonlarga (IELTS, TOEFL, CEFR) tayyorgarlik\n"
            "• AI bilan amaliy suhbat orqali til ko'nikmalarini oshirish\n\n"
            "🏢 <b>Myestro Ecosystem</b> doirasida ishlaydigan mahsulotlar:\n"
            "• <b>Myestro Teacher</b> — AI o'qituvchi (shu bot)\n"
            "• <b>Myestro Exam</b> — Onlayn imtihon tizimi\n"
            "• <b>Myestro Academy</b> — Video va file darsliklar bazasi\n\n"
            "📍 <b>Joylashuv:</b> Toshkent, O'zbekiston\n"
            "⚖️ <b>Yuridik shakl:</b> MCHJ «Myestro Ecosystem»"
        ),
        "about.links": (
            "🔗 <b>Foydali havolalar:</b>\n\n"
            "• 💬 Qo'llab-quvvatlash: <a href='https://t.me/myestro_support'>@myestro_support</a>\n"
            "• 📢 Yangiliklar kanali: <a href='https://t.me/myestro_news'>@myestro_news</a>\n"
            "• 🌐 Veb-sayt: <a href='https://myestro.uz'>myestro.uz</a>\n"
            "• 📧 Email: <a href='mailto:support@myestro.uz'>support@myestro.uz</a>"
        ),
        "about.ecosystem": (
            "🌐 <b>Myestro Ecosystem</b> — bu bitta ekosistema, bir nechta mahsulot:\n\n"
            "🤖 <b>Myestro Teacher</b>\n"
            "   Telegram bot | AI suhbat | Grammatika tuzatish\n\n"
            "📝 <b>Myestro Exam</b>\n"
            "   Onlayn imtihon | IELTS/TOEFL/CEFR | Natijalar tahlili\n\n"
            "📚 <b>Myestro Academy</b>\n"
            "   Video darsliklar | File materiallar | Daraja bo'yicha taqsimot\n\n"
            "⚙️ <b>Admin Panel</b>\n"
            "   Foydalanuvchilar boshqaruvi | Kontent | Statistika"
        ),
        "about.faq": (
            "❓ <b>Ko'p beriladigan savollar (FAQ)</b>\n\n"
            "<b>1. Bu platforma bepulmi?</b>\n"
            "   → Ha, <b>100% bepul</b>. Barcha asosiy funksiyalar — AI Teacher, "
            "imtihonlar, darsliklar — hech qanday to'lovsiz.\n\n"
            "<b>2. Qanday imtihonlar mavjud?</b>\n"
            "   → Hozirda <b>CEFR</b> darajalash imtihoni mavjud. "
            "Tez orada <b>IELTS</b> va <b>TOEFL</b> mock imtihonlari qo'shiladi.\n\n"
            "<b>3. AI Teacher qanday ishlaydi?</b>\n"
            "   → <b>OpenRouter</b> orqali GPT-4, Gemini, Claude va Mistral "
            "modellari yordamida. AI sizning darajangizga moslashadi, "
            "xatolaringizni tuzatadi va ovozli xabarlarni qabul qiladi.\n\n"
            "<b>4. Ma'lumotlarim xavfsizmi?</b>\n"
            "   → Albatta. Barcha ma'lumotlar shifrlanadi va "
            "O'zbekiston qonunlariga muvofiq saqlanadi."
        ),

        # ═══════════════════════════════════════════════════════════
        #  GUIDE
        # ═══════════════════════════════════════════════════════════
        "guide.title": "📖 <b>Qo'llanma</b>",
        "guide.text": (
            "<b>Myestro Teacher</b> — bu sizning shaxsiy AI yordamchingiz.\n\n"
            "🎯 <b>Nima qilish mumkin?</b>\n"
            "• Istagan mavzuda ingliz tilida suhbatlashish\n"
            "• Grammatik va leksik xatolaringizni real vaqtda tuzatish\n"
            "• Ovozli xabarlar orqali talaffuzni mashq qilish\n"
            "• CEFR darajangizni aniqlash imtihonini topshirish\n\n"
            "👇 <b>Quyidagi bo'limlardan birini tanlang:</b>"
        ),
        "guide.bot": (
            "🤖 <b>Bot bo'yicha batafsil</b>\n\n"
            "<b>Tillar:</b> O'zbek, Rus, Ingliz (3 ta til)\n\n"
            "<b>Asosiy funksiyalar:</b>\n"
            "• <b>AI Teacher</b> — Sun'iy intellekt bilan bemuloqot suhbat\n"
            "• <b>Imtihonlar</b> — CEFR darajalash (tez orada IELTS/TOEFL)\n"
            "• <b>Eslatmalar</b> — Kunlik mashqlar va dars vaqti eslatmalari\n"
            "• <b>Referral</b> — Do'stlaringizni taklif qilib, bonuslar yutib oling\n\n"
            "⚙️ <b>Sozlamalar</b> orqali tilni, AI rejimini va profilni boshqarish mumkin."
        ),
        "guide.ai": (
            "🧠 <b>AI Teacher qanday ishlaydi?</b>\n\n"
            "<b>Texnologiya:</b> OpenRouter orqali quyidagi modellarga ulanadi:\n"
            "• GPT-4 (OpenAI)\n"
            "• Gemini (Google)\n"
            "• Claude (Anthropic)\n"
            "• Mistral\n\n"
            "<b>Xususiyatlar:</b>\n"
            "• Sizning <b>CEFR darajangiz</b> (A1–C2) ga moslashadi\n"
            "• Grammatik xatolarni <b>real vaqtda</b> tuzatadi\n"
            "• 3 ta til (uz, ru, en) da javob beradi\n"
            "• Ovozli xabarlarni matnga aylantiradi va tahlil qiladi\n\n"
            "💡 <b>Maslahat:</b> AI bilan har kuni kamida 10 daqiqa suhbatlashish "
            "— til o'rganishning eng samarali usuli."
        ),

        # ═══════════════════════════════════════════════════════════
        #  LANGUAGE
        # ═══════════════════════════════════════════════════════════
        "language.prompt": "🌐 <b>Platforma tilini tanlang:</b>\n\nTilni istalgan vaqtda o'zgartirishingiz mumkin.",

        # ═══════════════════════════════════════════════════════════
        #  REGISTER (legacy flow — eski ro'yxatdan o'tish)
        # ═══════════════════════════════════════════════════════════
        "register.ask_name": (
            "📝 <b>Ro'yxatdan o'tish</b>\n\n"
            "Iltimos, <b>ism-familiyangizni</b> to'liq kiriting:\n"
            "<i>Misol: Azizbek Karimov</i>"
        ),
        "register.ask_email": (
            "📧 Endi <b>email manzilingizni</b> kiriting:\n"
            "<i>Misol: azizbek@gmail.com</i>\n\n"
            "Email orqali tizimga kirish va xabarnomalar yuboriladi."
        ),
        "register.ask_password": (
            "🔐 <b>Xavfsiz parol</b> yarating:\n\n"
            "• Kamida <b>8 ta belgi</b>\n"
            "• Kamida <b>1 ta katta harf</b>\n"
            "• Kamida <b>1 ta raqam</b>\n\n"
            "<i>Misol: Myestro2024!</i>"
        ),
        "register.invalid_email": (
            "❌ <b>Noto'g'ri email formati</b>\n\n"
            "Iltimos, qayta kiriting. Email quyidagi ko'rinishda bo'lishi kerak:\n"
            "<code>ism@domen.com</code>\n\n"
            "<i>Misol: support@myestro.uz</i>"
        ),
        "register.invalid_password": (
            "❌ <b>Juda oddiy parol</b>\n\n"
            "Parol quyidagi talablarga javob berishi kerak:\n"
            "• Kamida 8 ta belgi\n"
            "• 1 ta katta harf\n"
            "• 1 ta raqam\n\n"
            "Iltimos, murakkabroq parol yarating."
        ),
        "register.ask_phone": (
            "📱 <b>Telefon raqamingizni</b> ulashing:\n\n"
            "Quyidagi tugmani bosish orqali raqamingizni avtomatik yuboring "
            "yoki qo'lda kiriting: <code>+998901234567</code>"
        ),
        "register.invalid_phone": (
            "❌ <b>Noto'g'ri telefon raqami</b>\n\n"
            "Iltimos, O'zbekiston formatida kiriting:\n"
            "<code>+998 XX XXX XX XX</code>\n\n"
            "Yoki <b>«Raqamni ulashish»</b> tugmasidan foydalaning."
        ),
        "register.confirm": (
            "📋 <b>Ma'lumotlaringizni tekshiring:</b>\n\n"
            "👤 <b>Ism:</b> {name}\n"
            "📧 <b>Email:</b> {email}\n"
            "📞 <b>Telefon:</b> {phone}\n\n"
            "Agar ma'lumotlar to'g'ri bo'lsa, <b>«Tasdiqlash»</b> ni bosing."
        ),
        "register.success": (
            "🎉 <b>Tabriklaymiz, {name}!</b>\n\n"
            "Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n"
            "Endi barcha funksiyalardan foydalanishingiz mumkin:\n"
            "• 🤖 AI Teacher bilan suhbat\n"
            "• 📝 Imtihon topshirish\n"
 "• 📚 Video va file darsliklar\n\n"
            "👇 <b>Asosiy menyu:</b>"
        ),
        "register.ask_confirm_password": (
            "🔐 <b>Parolni tasdiqlang</b>\n\n"
            "Xavfsizlik maqsadida parolingizni qayta kiriting:"
        ),
        "register.password_mismatch": (
            "❌ <b>Parollar mos kelmaydi</b>\n\n"
            "Iltimos, bir xil parolni ikki marta kiriting."
        ),
        "register.ask_level": (
            "📚 <b>Ingliz tili darajangizni tanlang</b>:\n\n"
            "Quyidagi tugmalardan birini tanlang yoki darajani yozing "
            "(masalan: <code>B2</code>)."
        ),
        "register.invalid_name": (
            "❌ <b>Noto'g'ri ism</b>\n\n"
            "Iltimos, ism-familiyangizni 2 dan 100 tagacha belgida kiriting."
        ),
        "register.invalid_level": (
            "❌ <b>Noto'g'ri daraja</b>\n\n"
            "Iltimos, quyidagilardan birini tanlang yoki yozing: "
            "<code>A0, A1, A2, B1, B2, C1, C2</code>"
        ),
        "register.confirm_info": (
            "📋 <b>Ma'lumotlaringizni tasdiqlang:</b>\n\n"
            "👤 <b>Ism:</b> {name}\n"
            "📞 <b>Telefon:</b> {phone}\n"
            "📊 <b>Daraja:</b> {level}\n\n"
            "Agar ma'lumotlar to'g'ri bo'lsa, <b>«✅ Ha»</b> tugmasini bosing."
        ),
        "register.already_registered": (
            "✅ <b>Siz allaqachon ro'yxatdan o'tgansiz!</b>\n\n"
            "Asosiy menyudan foydalanishda davom eting."
        ),
        "register.cancelled": (
            "🚫 <b>Ro'yxatdan o'tish bekor qilindi.</b>\n\n"
            "Quyidagi menyulardan birini tanlang."
        ),
        "register.must_use_contact_button": (
            "⚠️ <b>Telefon raqamingizni ulashish uchun quyidagi tugmadan foydalaning:</b>\n\n"
            "«📱 Raqam yuborish» tugmasini bosing."
        ),
        "register.not_your_contact": (
            "⚠️ <b>Bu sizning raqamingiz emas!</b>\n\n"
            "Iltimos, o'z telefon raqamingizni yuboring "
            "yoki «⬅️ Orqaga» tugmasini bosing."
        ),
        "register.success_welcome": (
            "🎉 <b>Tabriklaymiz! Siz muvaffaqiyatli ro'yxatdan o'tdingiz!</b>\n\n"
            "Endi barcha funksiyalardan foydalanishingiz mumkin.\n"
            "👇 <b>Asosiy menyu:</b>"
        ),
        "register.choose_yes_or_no": (
            "⚠️ <b>Iltimos, «✅ Ha» yoki «❌ Yo'q» tugmalaridan birini tanlang.</b>"
        ),

        # ═══════════════════════════════════════════════════════════
        #  AUTH (login/register shared)
        # ═══════════════════════════════════════════════════════════
        "auth.phone_request": (
            "📱 <b>Kirish uchun telefon raqamingizni</b> yuboring:\n\n"
            "Quyidagi tugmani bosish orqali raqamingizni ulashing, "
            "yoki qo'lda kiriting: <code>+998901234567</code>"
        ),
        "auth.phone_not_found": (
            "📝 <b>Account topilmadi</b>\n\n"
            "Bu telefon raqam ro'yxatdan o'tmagan. "
            "Yangi account yaratish uchun ro'yxatdan o'tish boshlanmoqda..."
        ),
        "auth.email_not_found": (
            "📝 <b>Email topilmadi</b>\n\n"
            "Bu email manzil ro'yxatdan o'tmagan. "
            "Yangi account yaratish uchun ro'yxatdan o'tish boshlanmoqda..."
        ),
        "auth.invalid_phone_or_email": (
            "❌ <b>Noto'g'ri ma'lumot</b>\n\n"
            "Iltimos, telefon raqamingizni yoki email manzilingizni to'g'ri kiriting.\n"
            "Telefon: <code>+998901234567</code>\n"
            "Email: <code>ism@domen.com</code>"
        ),
        "auth.phone_found_but_login_failed": (
            "❌ <b>Tizimga kirishda xatolik</b>\n\n"
            "Telefon raqam topildi, lekin tizimga kirish amalga oshmadi.\n"
            "Iltimos, birozdan so'ng qayta urinib ko'ring "
            "yoki <a href='https://t.me/myestro_support'>qo'llab-quvvatlash</a> ga murojaat qiling."
        ),

        # ═══════════════════════════════════════════════════════════
        #  LOGIN
        # ═══════════════════════════════════════════════════════════
        "login.choice": (
            "🔐 <b>Tizimga kirish</b>\n\n"
            "Kirish usulini tanlang:"
        ),
        "register.phone_shared_success": (
            "✅ <b>Telefon raqamingiz qabul qilindi</b>\n\n"
            "Ma'lumotlar xavfsizlik tekshiruvidan o'tkazilmoqda..."
        ),
        "login.ask_password": (
            "🔐 <b>Parolingizni kiriting:</b>\n\n"
            "Agar parolni unutgan bo'lsangiz, "
            "<a href='https://t.me/myestro_support'>qo'llab-quvvatlash</a> ga murojaat qiling."
        ),
        "login.success": (
            "✅ <b>Xush kelibsiz!</b>\n\n"
            "Siz muvaffaqiyatli tizimga kirdingiz.\n"
            "👇 <b>Asosiy menyu:</b>"
        ),
        "login.failed": (
            "❌ <b>Kirish amalga oshmadi</b>\n\n"
            "Parol noto'g'ri yoki account bloklangan.\n"
            "Qayta urinib ko'ring yoki <b>«Ro'yxatdan o'tish»</b> ni bosing."
        ),
        "login.email_not_found": (
            "❌ <b>Email topilmadi</b>\n\n"
            "Bu email manzil tizimda ro'yxatdan o'tmagan.\n"
            "Yangi account yaratish uchun <b>«Ro'yxatdan o'tish»</b> ni bosing."
        ),
        "login.wrong_password": (
            "❌ <b>Noto'g'ri parol</b>\n\n"
            "Qolgan urinishlar: {attempts_left}\n\n"
            "Agar parolni unutgan bo'lsangiz, "
            "<a href='https://t.me/myestro_support'>qo'llab-quvvatlash</a> ga murojaat qiling."
        ),

        # ═══════════════════════════════════════════════════════════
        #  ADMIN MESSAGE
        # ═══════════════════════════════════════════════════════════
        "admin.instruction": (
            "📨 <b>Admin bilan aloqa</b>\n\n"
            "Xabaringizni quyidagi formatda yozing:\n\n"
            "<b>1. Mavzu:</b> Muammoning qisqa mazmuni (1-2 so'z)\n"
            "<b>2. Tavsif:</b> Batafsil matn\n"
            "<b>3. Kontakt:</b> Bog'lanish uchun qo'shimcha ma'lumot (ixtiyoriy)\n\n"
            "⏱️ Odatda javob vaqti: <b>15 daqiqa – 2 soat</b> (ish vaqtida)."
        ),
        "admin.sent": (
            "✅ <b>Xabaringiz yuborildi!</b>\n\n"
            "Ticket ID: <code>{ticket_id}</code>\n\n"
            "Admin tez orada javob beradi. "
            "Javobni <b>«Xabarlar»</b> bo'limidan kuzatishingiz mumkin."
        ),

        # ═══════════════════════════════════════════════════════════
        #  REGISTRATION (new user onboarding)
        # ═══════════════════════════════════════════════════════════
        "registration.phone_request": (
            "📝 <b>Ro'yxatdan o'tish</b>\n\n"
            "Platformadan to'liq foydalanish uchun telefon raqamingizni tasdiqlang.\n\n"
            "Quyidagi tugmani bosish orqali raqamingizni avtomatik yuboring:"
        ),
        "registration.phone_share_btn": "📱 Raqamni ulashish",
        "registration.phone_found": (
            "✅ <b>Account topildi!</b>\n\n"
            "Siz allaqachon ro'yxatdan o'tgansiz. "
            "Tizimga avtomatik kirildi.\n\n"
            "Qaytganingiz bilan, <b>{name}</b>! 🎉"
        ),
        "registration.phone_not_found": (
            "📝 <b>Yangi foydalanuvchi aniqlandi</b>\n\n"
            "Keling, bir necha daqiqada profil yaratamiz.\n\n"
            "<b>Nima uchun ro'yxatdan o'tish kerak?</b>\n"
            "• 🤖 AI Teacher sizning darajangizga moslashadi\n"
            "• 📊 Imtihon natijalaringiz saqlanib qoladi\n"
            "• 🎯 Shaxsiy o'quv rejasi tuziladi\n"
            "• 🏆 Statistika va yutuqlaringiz kuzatiladi"
        ),
        "registration.ask_name": (
            "👤 <b>Ism-familiyangizni kiriting:</b>\n\n"
            "<i>Misol: Azizbek Karimov</i>"
        ),
        "registration.ask_birthdate": (
            "🎂 <b>Tug'ilgan kuningizni kiriting:</b>\n\n"
            "Format: <code>DD.MM.YYYY</code>\n"
            "<i>Misol: 15.05.1998</i>\n\n"
            "Bu ma'lumot yosh toifasiga mos kontent tanlash uchun ishlatiladi."
        ),
        "registration.ask_level": (
            "📚 <b>Ingliz tili darajangizni tanlang:</b>\n\n"
            "Agar bilmayotgan bo'lsangiz, <b>«Darajani aniqlash»</b> imtihonini topshiring."
        ),
        "registration.skip": "⏭️ Keyinroq",
        "registration.confirm_title": (
            "📋 <b>Profil ma'lumotlari:</b>\n\n"
            "👤 <b>Ism:</b> {name}\n"
            "📞 <b>Telefon:</b> {phone}\n"
            "🎂 <b>Tug'ilgan sana:</b> {birthdate}\n"
            "📚 <b>Daraja:</b> {level}\n\n"
            "Ma'lumotlar to'g'ri mi?"
        ),
        "registration.confirm_btn": "✅ Tasdiqlash",
        "registration.restart_btn": "🔄 Qayta to'ldirish",
        "registration.done": (
            "🎉 <b>Tabriklaymiz, {name}!</b>\n\n"
            "Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n"
            "Sizning CEFR darajangiz: <b>{level}</b>\n\n"
            "Endi barcha funksiyalardan foydalanishingiz mumkin:\n"
            "• 🤖 <b>AI Teacher</b> — suhbatni boshlash\n"
            "• 📝 <b>Imtihon</b> — darajangizni sinash\n"
            "• 📚 <b>Darsliklar</b> — video va fayllar\n"
            "• ⚙️ <b>Sozlamalar</b> — profilni boshqarish\n\n"
            "🚀 <b>O'rganishni boshlash!</b>"
        ),

        # ═══════════════════════════════════════════════════════════
        #  REGISTERED USER (welcome back / new)
        # ═══════════════════════════════════════════════════════════
        "registered.welcome_new": (
            "🎉 <b>Yangi foydalanuvchi!</b>\n\n"
            "Myestro Ecosystem ga xush kelibsiz.\n"
            "Keling, birgalikda ingliz tilini egallaymiz! 🇬🇧"
        ),
        "registered.welcome_back": (
            "👋 <b>Qaytganingiz bilan, {name}!</b>\n\n"
            "Oxirgi faollik: {last_active}\n"
            "Kunlik streak: <b>{streak} kun</b> 🔥\n\n"
            "Davom etamizmi?"
        ),

        # ═══════════════════════════════════════════════════════════
        #  PROFILE
        # ═══════════════════════════════════════════════════════════
        "profile.title": (
            "👤 <b>Mening profilim</b>\n\n"
            "👤 <b>Ism:</b> {name}\n"
            "📞 <b>Telefon:</b> {phone}\n"
            "📚 <b>CEFR daraja:</b> {level}\n"
            "🌍 <b>Til:</b> {lang}\n"
            "🧠 <b>Password : </b> {password}\n"

        ),

        # ═══════════════════════════════════════════════════════════
        #  SETTINGS
        # ═══════════════════════════════════════════════════════════
        "settings.title": (
            "⚙️ <b>Sozlamalar</b>\n\n"
            "Bu yerda profil, til va AI rejimini boshqarishingiz mumkin."
        ),
        "settings.language": "🌐 Tilni o'zgartirish",
        "settings.ai_toggle": "🤖 AI Teacher rejimi",
        "settings.logout": "🚪 Profildan chiqish",
        "settings.logout_confirm": (
            "🚪 <b>Profildan chiqishni tasdiqlang</b>\n\n"
            "Barcha ma'lumotlaringiz <b>saqlanib qoladi</b>.\n"
            "Keyin qayta kirish uchun telefon raqamingiz yetarli.\n\n"
            "Chiqmoqchimisiz?"
        ),
        "settings.logout_done": (
            "✅ <b>Siz profildan chiqdingiz.</b>\n\n"
            "Qaytish uchun /start ni bosing.\n\n"
            "Ingliz tilini o'rganishni davom ettiring! 🇬🇧"
        ),

        # ═══════════════════════════════════════════════════════════
        #  AI
        # ═══════════════════════════════════════════════════════════
        "ai.enabled": (
            "✅ <b>AI Teacher yoqildi</b>\n\n"
            "Endi barcha xabarlaringizga AI javob beradi.\n"
            "O'chirish uchun ⚙️ <b>Sozlamalar</b> ga kiring."
        ),
        "ai.disabled": (
            "❌ <b>AI Teacher o'chirildi</b>\n\n"
            "Endi siz faqat bot komandalaridan foydalanasiz.\n"
            "Yoqish uchun ⚙️ <b>Sozlamalar</b> ga kiring."
        ),
        "ai.global_off": (
            "🚫 <b>AI Teacher vaqtinchalik o'chirilgan</b>\n\n"
            "Texnik ishlar olib borilmoqda. "
            "Tez orada qaytamiz!\n\n"
            "Qo'llab-quvvatlash: <a href='https://t.me/myestro_support'>@myestro_support</a>"
        ),
        "ai.user_off": (
            "🤖 <b>AI Teacher o'chirilgan</b>\n\n"
            "AI suhbatini davom ettirish uchun ⚙️ <b>Sozlamalar</b> → "
            "<b>AI Teacher rejimi</b> ni yoqing."
        ),
        "ai.error": (
            "⚠️ <b>AI hozircha band</b>\n\n"
            "So'rovlar hajmi oshgan. Iltimos, 30 soniyadan so'ng qayta urinib ko'ring.\n"
            "Xatolik takrorlansa, <a href='https://t.me/myestro_support'>bizga xabar bering</a>."
        ),
        "ai.thinking": (
            "🧠 <b>AI o'ylayapdi...</b>\n\n"
            "Javob tayyorlanmoqda, bir oz kuting ⏳"
        ),

        # ═══════════════════════════════════════════════════════════
        #  VIDEO LESSONS
        # ═══════════════════════════════════════════════════════════
        "video.title": "🎬 <b>Video darsliklar</b>",
        "video.list": (
            "🎬 <b>Mavjud darsliklar:</b>\n\n"
            "{lessons}\n\n"
            "📚 Darajangizga mos darslikni tanlang."
        ),
        "video.not_found": (
            "🎬 <b>Hozircha video darsliklar mavjud emas</b>\n\n"
            "Tez orada yangi kontent qo'shiladi.\n"
            "Yangiliklardan xabardor bo'lish uchun "
            "<a href='https://t.me/myestro_news'>kanalimizga</a> obuna bo'ling."
        ),

        # ═══════════════════════════════════════════════════════════
        #  FILE LESSONS
        # ═══════════════════════════════════════════════════════════
        "file.title": "📁 <b>Fayl darsliklar</b>",
        "file.list": (
            "📁 <b>Mavjud fayllar:</b>\n\n"
            "{lessons}\n\n"
            "Kerakli faylni tanlang."
        ),
        "file.not_found": (
            "📁 <b>Hozircha fayl darsliklar mavjud emas</b>\n\n"
            "Tez orada PDF, DOC va audio materiallar qo'shiladi."
        ),

        # ═══════════════════════════════════════════════════════════
        #  BACK / NAVIGATION
        # ═══════════════════════════════════════════════════════════
        "back": "⬅️ Orqaga",
        "back_to_menu": "🏠 Asosiy menyu",

        # ═══════════════════════════════════════════════════════════
        #  ERRORS
        # ═══════════════════════════════════════════════════════════
        "error": (
            "❌ <b>Xatolik yuz berdi</b>\n\n"
            "Texnik nosozlik sodir bo'ldi. "
            "Iltimos, birozdan so'ng qayta urinib ko'ring.\n\n"
            "Agar muammo takrorlansa, "
            "<a href='https://t.me/myestro_support'>qo'llab-quvvatlash</a> ga murojaat qiling."
        ),
        "error.timeout": (
            "⏳ <b>AI javob berish vaqti oshdi</b>\n\n"
            "So'rov juda murakkab yoki server band. "
            "Iltimos, 1 daqiqadan so'ng qayta urinib ko'ring."
        ),
        "error.redis": (
            "🔌 <b>Ma'lumotlar bazasiga ulanishda xatolik</b>\n\n"
            "Iltimos, bir necha daqiqadan so'ng qayta urinib ko'ring. "
            "Ma'lumotlaringiz xavfsiz."
        ),
        "error.unsupported": (
            "😔 <b>Bu format qo'llab-quvvatlanmaydi</b>\n\n"
            "Hozircha faqat quyidagi formatlarni qabul qilamiz:\n"
            "• 📝 Matn xabarlar\n"
            "• 🎙️ Ovozli xabarlar\n\n"
            "Rasm, video yoki hujjatlar tez orada qo'shiladi."
        ),

        # ═══════════════════════════════════════════════════════════
        #  LEGACY KEYS (backward compatibility)
        # ═══════════════════════════════════════════════════════════
        "welcome": (
            "👋 <b>Assalomu alaykum!</b>\n\n"
            "Myestro AI yordamchiga xush kelibsiz!"
        ),
        "choose_language": "🌍 Tilni tanlang:",
        "share_contact": (
            "📱 <b>Xush kelibsiz!</b>\n\n"
            "Iltimos, telefon raqamingizni ulashing:"
        ),
        "phone_shared": "✅ Telefon raqamingiz qabul qilindi.",
        "already_registered": (
            "🌟 <b>Qaytganingizdan xursandmiz!</b>\n\n"
            "Davom etamizmi?"
        ),
        "new_user_welcome": (
            "🎉 <b>Yangi foydalanuvchi!</b>\n\n"
            "Keling, siz bilan tanishamiz."
        ),
        "enter_name": "👤 Ismingizni kiriting:",
        "choose_level": "📚 Ingliz tili darajangizni tanlang:",
        "registration_done": (
            "✅ <b>Ro'yxatdan muvaffaqiyatli o'tdingiz!</b>\n\n"
            "Endi barcha funksiyalardan foydalanishingiz mumkin."
        ),
        "main_menu": "🏠 <b>Asosiy menyu:</b>",
        "teacher_chat": "🧑‍🏫 AI Teacher",
        "exams": "📝 Imtihon",
        "language": "🌐 Til o'zgartirish",
        "about_us": "ℹ️ Biz haqimizda",
        "contact_admin": "📨 Admin ga xabar",
        "admin_message_prompt": "📨 Admin ga xabaringizni yozing:",
        "admin_message_sent": (
            "✅ <b>Xabaringiz admin ga yuborildi!</b>\n\n"
            "Tez orada javob olasiz."
        ),
        "ai_fallback_reminder": (
            "⚠️ <b>Siz ro'yxatdan o'tmagansiz</b>\n\n"
            "To'liq funksiyalardan foydalanish uchun /start ni bosing."
        ),
        "ai_fallback_teacher": (
            "🤖 <b>Salom!</b> Men Myestro AI yordamchisiman.\n\n"
            "Ingliz tilida suhbatlashishingiz mumkin! "
            "Lekin to'liq funksiyalar uchun /start ni bosing."
        ),
        "academy_text": (
            "📚 <b>Myestro Academy</b>\n\n"
            "Ingliz tilini o'rganish uchun zamonaviy platforma.\n\n"
            "AI Teacher bilan bepul suhbatlashing, "
            "xalqaro imtihonlarga tayyorlaning va bilimingizni oshiring!"
        ),
        "contact_text": (
            "📞 <b>Aloqa ma'lumotlari</b>\n\n"
            "• Telegram: <a href='https://t.me/myestro_support'>@myestro_support</a>\n"
            "• Email: <a href='mailto:support@myestro.uz'>support@myestro.uz</a>"
        ),
        "about_info_text": (
            "ℹ️ <b>Myestro</b> — O'zbekiston bozoriga mo'ljallangan, "
            "ingliz tilini o'rganish va xalqaro imtihonlarga "
            "(IELTS, TOEFL, CEFR) tayyorgarlik ko'rish uchun "
            "AI-powered bepul platforma."
        ),
        "about_academy": "🏫 Akademiya haqida",
        "about_contacts": "📞 Aloqa",
        "about_info": "ℹ️ Batafsil ma'lumot",
    },
    
    "ru": {
        # ═══════════════════════════════════════════════════════════
        #  START
        # ═══════════════════════════════════════════════════════════
        "start.welcome": (
            "👋 <b>Добро пожаловать!</b>\n\n"
            "Вы находитесь в <b>Myestro Teacher</b> — "
            "платформе для изучения английского языка с ИИ в экосистеме "
            "<a href='https://t.me/myestro_ecosystem'>Myestro Ecosystem</a>.\n\n"
            "🎯 <b>Возможности платформы:</b>\n"
            "• 🤖 <b>AI Teacher</b> — практикуйте английский в диалогах с ИИ\n"
            "• 📝 <b>Myestro Exam</b> — объективно оценивайте свой уровень\n"
            "• 📚 <b>Myestro Academy</b> — учебные материалы и курсы\n"
            "• 🎓 <b>100% бесплатно</b> — все функции открыты и бесплатны\n\n"
            "🚀 Начните изучать английский уже сегодня!"
        ),
        "start.language_prompt": "🌍 Пожалуйста, выберите язык платформы:",
        "start.language_changed": (
            "✅ <b>Язык изменён!</b>\n\n"
            "Теперь все сообщения и диалоги с ИИ будут на <b>русском языке</b>.\n"
            "Изменить язык можно в любое время в разделе ⚙️ <b>Настройки</b>."
        ),

        # ═══════════════════════════════════════════════════════════
        #  ABOUT
        # ═══════════════════════════════════════════════════════════
        "about.title": "ℹ️ <b>О нас</b>",
        "about.text": (
            "<b>Myestro</b> — современная <b>AI-powered</b> платформа для изучения английского языка, "
            "ориентированная на рынок Узбекистана и Центральной Азии.\n\n"
            "🎯 <b>Основные направления:</b>\n"
            "• Изучение английского с нуля\n"
            "• Подготовка к международным экзаменам (IELTS, TOEFL, CEFR)\n"
            "• Практика разговорных навыков с ИИ в реальном времени\n\n"
            "🏢 <b>Продукты экосистемы Myestro:</b>\n"
            "• <b>Myestro Teacher</b> — ИИ-репетитор (этот бот)\n"
            "• <b>Myestro Exam</b> — система онлайн-экзаменов\n"
            "• <b>Myestro Academy</b> — база видео- и файловых уроков\n\n"
            "📍 <b>Локация:</b> Ташкент, Узбекистан\n"
            "⚖️ <b>Организационно-правовая форма:</b> ООО «Myestro Ecosystem»"
        ),
        "about.links": (
            "🔗 <b>Полезные ссылки:</b>\n\n"
            "• 💬 Поддержка: <a href='https://t.me/myestro_support'>@myestro_support</a>\n"
            "• 📢 Канал новостей: <a href='https://t.me/myestro_news'>@myestro_news</a>\n"
            "• 🌐 Сайт: <a href='https://myestro.uz'>myestro.uz</a>\n"
            "• 📧 Email: <a href='mailto:support@myestro.uz'>support@myestro.uz</a>"
        ),
        "about.ecosystem": (
            "🌐 <b>Myestro Ecosystem</b> — одна экосистема, несколько продуктов:\n\n"
            "🤖 <b>Myestro Teacher</b>\n"
            "   Telegram-бот | ИИ-диалоги | Исправление грамматики\n\n"
            "📝 <b>Myestro Exam</b>\n"
            "   Онлайн-экзамены | IELTS/TOEFL/CEFR | Анализ результатов\n\n"
            "📚 <b>Myestro Academy</b>\n"
            "   Видеоуроки | Файловые материалы | Разделение по уровням\n\n"
            "⚙️ <b>Admin Panel</b>\n"
            "   Управление пользователями | Контент | Статистика"
        ),
        "about.faq": (
            "❓ <b>Часто задаваемые вопросы (FAQ)</b>\n\n"
            "<b>1. Эта платформа бесплатная?</b>\n"
            "   → Да, <b>100% бесплатно</b>. Все основные функции — ИИ-репетитор, "
            "экзамены, уроки — доступны без какой-либо оплаты.\n\n"
            "<b>2. Какие экзамены доступны?</b>\n"
            "   → В настоящее время доступен входной тест <b>CEFR</b>. "
            "В скором времени добавятся пробные экзамены <b>IELTS</b> и <b>TOEFL</b>.\n\n"
            "<b>3. Как работает AI Teacher?</b>\n"
            "   → Через <b>OpenRouter</b> подключаются модели GPT-4, Gemini, Claude и Mistral. "
            "ИИ адаптируется под ваш уровень, исправляет ошибки и принимает голосовые сообщения.\n\n"
            "<b>4. Мои данные в безопасности?</b>\n"
            "   → Абсолютно. Все данные шифруются и хранятся в соответствии "
            "с законодательством Узбекистана."
        ),

        # ═══════════════════════════════════════════════════════════
        #  GUIDE
        # ═══════════════════════════════════════════════════════════
        "guide.title": "📖 <b>Руководство</b>",
        "guide.text": (
            "<b>Myestro Teacher</b> — это ваш персональный ИИ-помощник.\n\n"
            "🎯 <b>Что можно делать?</b>\n"
            "• Общаться на английском на любые темы\n"
            "• Получать исправление грамматических и лексических ошибок в реальном времени\n"
            "• Тренировать произношение через голосовые сообщения\n"
            "• Сдавать входной тест CEFR для определения уровня\n\n"
            "👇 <b>Выберите один из разделов ниже:</b>"
        ),
        "guide.bot": (
            "🤖 <b>Подробнее о боте</b>\n\n"
            "<b>Языки:</b> Узбекский, Русский, Английский (3 языка)\n\n"
            "<b>Основные функции:</b>\n"
            "• <b>AI Teacher</b> — диалоги с искусственным интеллектом без ограничений\n"
            "• <b>Экзамены</b> — тестирование CEFR (скоро IELTS/TOEFL)\n"
            "• <b>Напоминания</b> — ежедневные задания и напоминания о занятиях\n"
            "• <b>Реферальная программа</b> — приглашайте друзей и получайте бонусы\n\n"
            "⚙️ В <b>Настройках</b> можно изменить язык, режим ИИ и управлять профилем."
        ),
        "guide.ai": (
            "🧠 <b>Как работает AI Teacher?</b>\n\n"
            "<b>Технология:</b> Подключение через OpenRouter к следующим моделям:\n"
            "• GPT-4 (OpenAI)\n"
            "• Gemini (Google)\n"
            "• Claude (Anthropic)\n"
            "• Mistral\n\n"
            "<b>Особенности:</b>\n"
            "• Адаптация под ваш уровень <b>CEFR</b> (A1–C2)\n"
            "• Исправление ошибок в <b>реальном времени</b>\n"
            "• Ответы на 3 языках (uz, ru, en)\n"
            "• Распознавание и анализ голосовых сообщений\n\n"
            "💡 <b>Совет:</b> Ежедневное общение с ИИ хотя бы 10 минут — "
            "самый эффективный способ изучения языка."
        ),

        # ═══════════════════════════════════════════════════════════
        #  LANGUAGE
        # ═══════════════════════════════════════════════════════════
        "language.prompt": "🌐 <b>Выберите язык платформы:</b>\n\nЯзык можно изменить в любое время.",

        # ═══════════════════════════════════════════════════════════
        #  REGISTER (legacy flow)
        # ═══════════════════════════════════════════════════════════
        "register.ask_name": (
            "📝 <b>Регистрация</b>\n\n"
            "Пожалуйста, введите ваше <b>имя и фамилию</b>:\n"
            "<i>Пример: Иван Петров</i>"
        ),
        "register.ask_email": (
            "📧 Теперь введите ваш <b>email-адрес</b>:\n"
            "<i>Пример: ivan@gmail.com</i>\n\n"
            "Email используется для входа и получения уведомлений."
        ),
        "register.ask_password": (
            "🔐 Создайте <b>надёжный пароль</b>:\n\n"
            "• Минимум <b>8 символов</b>\n"
            "• Минимум <b>1 заглавная буква</b>\n"
            "• Минимум <b>1 цифра</b>\n\n"
            "<i>Пример: Myestro2024!</i>"
        ),
        "register.invalid_email": (
            "❌ <b>Неверный формат email</b>\n\n"
            "Пожалуйста, введите корректный адрес. Формат:\n"
            "<code>имя@домен.com</code>\n\n"
            "<i>Пример: support@myestro.uz</i>"
        ),
        "register.invalid_password": (
            "❌ <b>Слишком простой пароль</b>\n\n"
            "Пароль должен соответствовать требованиям:\n"
            "• Минимум 8 символов\n"
            "• 1 заглавная буква\n"
            "• 1 цифра\n\n"
            "Пожалуйста, придумайте более сложный пароль."
        ),
        "register.ask_phone": (
            "📱 <b>Поделитесь номером телефона</b>:\n\n"
            "Нажмите кнопку ниже для автоматической отправки номера "
            "или введите вручную: <code>+998901234567</code>"
        ),
        "register.invalid_phone": (
            "❌ <b>Неверный номер телефона</b>\n\n"
            "Пожалуйста, введите номер в формате Узбекистана:\n"
            "<code>+998 XX XXX XX XX</code>\n\n"
            "Или воспользуйтесь кнопкой <b>«Отправить номер»</b>."
        ),
        "register.confirm": (
            "📋 <b>Проверьте ваши данные:</b>\n\n"
            "👤 <b>Имя:</b> {name}\n"
            "📧 <b>Email:</b> {email}\n"
            "📞 <b>Телефон:</b> {phone}\n\n"
            "Если данные верны, нажмите <b>«Подтвердить»</b>."
        ),
        "register.success": (
            "🎉 <b>Поздравляем, {name}!</b>\n\n"
            "Вы успешно зарегистрировались.\n"
            "Теперь вам доступны все функции:\n"
            "• 🤖 Общение с AI Teacher\n"
            "• 📝 Сдача экзаменов\n"
            "• 📚 Видео- и файловые уроки\n\n"
            "👇 <b>Главное меню:</b>"
        ),
        "register.ask_confirm_password": (
            "🔐 <b>Подтвердите пароль</b>\n\n"
            "В целях безопасности введите пароль повторно:"
        ),
        "register.password_mismatch": (
            "❌ <b>Пароли не совпадают</b>\n\n"
            "Пожалуйста, введите один и тот же пароль дважды."
        ),
        "register.ask_level": (
            "📚 <b>Выберите ваш уровень английского языка</b>:\n\n"
            "Выберите один из вариантов ниже или введите уровень "
            "(например: <code>B2</code>)."
        ),
        "register.invalid_name": (
            "❌ <b>Неверное имя</b>\n\n"
            "Пожалуйста, введите имя и фамилию (от 2 до 100 символов)."
        ),
        "register.invalid_level": (
            "❌ <b>Неверный уровень</b>\n\n"
            "Пожалуйста, выберите или введите один из уровней: "
            "<code>A0, A1, A2, B1, B2, C1, C2</code>"
        ),
        "register.confirm_info": (
            "📋 <b>Подтвердите ваши данные:</b>\n\n"
            "👤 <b>Имя:</b> {name}\n"
            "📞 <b>Телефон:</b> {phone}\n"
            "📊 <b>Уровень:</b> {level}\n\n"
            "Если данные верны, нажмите <b>«✅ Да»</b>."
        ),
        "register.already_registered": (
            "✅ <b>Вы уже зарегистрированы!</b>\n\n"
            "Продолжайте использовать главное меню."
        ),
        "register.cancelled": (
            "🚫 <b>Регистрация отменена.</b>\n\n"
            "Выберите один из пунктов меню ниже."
        ),
        "register.must_use_contact_button": (
            "⚠️ <b>Чтобы поделиться номером, воспользуйтесь кнопкой ниже:</b>\n\n"
            "Нажмите <b>«📱 Отправить номер»</b>."
        ),
        "register.not_your_contact": (
            "⚠️ <b>Это не ваш номер!</b>\n\n"
            "Пожалуйста, отправьте свой номер телефона "
            "или нажмите <b>«⬅️ Назад»</b>."
        ),
        "register.success_welcome": (
            "🎉 <b>Поздравляем! Вы успешно зарегистрировались!</b>\n\n"
            "Теперь вам доступны все функции.\n"
            "👇 <b>Главное меню:</b>"
        ),
        "register.choose_yes_or_no": (
            "⚠️ <b>Пожалуйста, выберите «✅ Да» или «❌ Нет».</b>"
        ),

        # ═══════════════════════════════════════════════════════════
        #  AUTH (login/register shared)
        # ═══════════════════════════════════════════════════════════
        "auth.phone_request": (
            "📱 <b>Для входа отправьте номер телефона</b>:\n\n"
            "Нажмите кнопку ниже, чтобы поделиться номером, "
            "или введите вручную: <code>+998901234567</code>"
        ),
        "auth.phone_not_found": (
            "📝 <b>Аккаунт не найден</b>\n\n"
            "Этот номер телефона не зарегистрирован. "
            "Начинаем создание нового аккаунта..."
        ),
        "auth.email_not_found": (
            "📝 <b>Email не найден</b>\n\n"
            "Этот email-адрес не зарегистрирован. "
            "Начинаем создание нового аккаунта..."
        ),
        "auth.invalid_phone_or_email": (
            "❌ <b>Неверные данные</b>\n\n"
            "Пожалуйста, введите корректный номер телефона или email.\n"
            "Телефон: <code>+998901234567</code>\n"
            "Email: <code>имя@домен.com</code>"
        ),
        "auth.phone_found_but_login_failed": (
            "❌ <b>Ошибка входа</b>\n\n"
            "Номер телефона найден, но войти не удалось.\n"
            "Пожалуйста, попробуйте позже "
            "или обратитесь в <a href='https://t.me/myestro_support'>поддержку</a>."
        ),

        # ═══════════════════════════════════════════════════════════
        #  LOGIN
        # ═══════════════════════════════════════════════════════════
        "login.choice": (
            "🔐 <b>Вход в систему</b>\n\n"
            "Выберите способ входа:"
        ),
        "register.phone_shared_success": (
            "✅ <b>Номер телефона принят</b>\n\n"
            "Данные проходят проверку безопасности..."
        ),
        "login.ask_password": (
            "🔐 <b>Введите ваш пароль:</b>\n\n"
            "Если вы забыли пароль, обратитесь в "
            "<a href='https://t.me/myestro_support'>поддержку</a>."
        ),
        "login.success": (
            "✅ <b>Добро пожаловать!</b>\n\n"
            "Вы успешно вошли в систему.\n"
            "👇 <b>Главное меню:</b>"
        ),
        "login.failed": (
            "❌ <b>Вход не выполнен</b>\n\n"
            "Неверный пароль или аккаунт заблокирован.\n"
            "Попробуйте снова или нажмите <b>«Зарегистрироваться»</b>."
        ),
        "login.email_not_found": (
            "❌ <b>Email не найден</b>\n\n"
            "Этот email-адрес не зарегистрирован в системе.\n"
            "Для создания нового аккаунта нажмите <b>«Зарегистрироваться»</b>."
        ),
        "login.wrong_password": (
            "❌ <b>Неверный пароль</b>\n\n"
            "Осталось попыток: {attempts_left}\n\n"
            "Если вы забыли пароль, обратитесь в "
            "<a href='https://t.me/myestro_support'>поддержку</a>."
        ),

        # ═══════════════════════════════════════════════════════════
        #  ADMIN MESSAGE
        # ═══════════════════════════════════════════════════════════
        "admin.instruction": (
            "📨 <b>Связь с администратором</b>\n\n"
            "Напишите сообщение в следующем формате:\n\n"
            "<b>1. Тема:</b> Краткое описание проблемы (1–2 слова)\n"
            "<b>2. Описание:</b> Подробный текст\n"
            "<b>3. Контакт:</b> Дополнительные данные для связи (по желанию)\n\n"
            "⏱️ Обычное время ответа: <b>15 минут – 2 часа</b> (в рабочее время)."
        ),
        "admin.sent": (
            "✅ <b>Сообщение отправлено!</b>\n\n"
            "Номер обращения: <code>{ticket_id}</code>\n\n"
            "Администратор ответит в ближайшее время. "
            "Отследить статус можно в разделе <b>«Сообщения»</b>."
        ),

        # ═══════════════════════════════════════════════════════════
        #  REGISTRATION (new user onboarding)
        # ═══════════════════════════════════════════════════════════
        "registration.phone_request": (
            "📝 <b>Регистрация</b>\n\n"
            "Для полноценного использования платформы подтвердите номер телефона.\n\n"
            "Нажмите кнопку ниже для автоматической отправки номера:"
        ),
        "registration.phone_share_btn": "📱 Отправить номер",
        "registration.phone_found": (
            "✅ <b>Аккаунт найден!</b>\n\n"
            "Вы уже зарегистрированы. "
            "Выполнен автоматический вход.\n\n"
            "С возвращением, <b>{name}</b>! 🎉"
        ),
        "registration.phone_not_found": (
            "📝 <b>Обнаружен новый пользователь</b>\n\n"
            "Давайте создадим профиль за несколько минут.\n\n"
            "<b>Зачем нужна регистрация?</b>\n"
            "• 🤖 AI Teacher адаптируется под ваш уровень\n"
            "• 📊 Сохраняются результаты всех экзаменов\n"
            "• 🎯 Формируется персональный план обучения\n"
            "• 🏆 Ведётся статистика и достижения"
        ),
        "registration.ask_name": (
            "👤 <b>Введите ваше имя и фамилию:</b>\n\n"
            "<i>Пример: Иван Петров</i>"
        ),
        "registration.ask_birthdate": (
            "🎂 <b>Введите дату рождения:</b>\n\n"
            "Формат: <code>ДД.ММ.ГГГГ</code>\n"
            "<i>Пример: 15.05.1998</i>\n\n"
            "Эти данные используются для подбора контента по возрастной категории."
        ),
        "registration.ask_level": (
            "📚 <b>Выберите ваш уровень английского:</b>\n\n"
            "Если не знаете, пройдите тест <b>«Определить уровень»</b>."
        ),
        "registration.skip": "⏭️ Пропустить",
        "registration.confirm_title": (
            "📋 <b>Данные профиля:</b>\n\n"
            "👤 <b>Имя:</b> {name}\n"
            "📞 <b>Телефон:</b> {phone}\n"
            "🎂 <b>Дата рождения:</b> {birthdate}\n"
            "📚 <b>Уровень:</b> {level}\n\n"
            "Данные верны?"
        ),
        "registration.confirm_btn": "✅ Подтвердить",
        "registration.restart_btn": "🔄 Заполнить заново",
        "registration.done": (
            "🎉 <b>Поздравляем, {name}!</b>\n\n"
            "Вы успешно зарегистрировались.\n"
            "Ваш уровень CEFR: <b>{level}</b>\n\n"
            "Теперь вам доступны все функции:\n"
            "• 🤖 <b>AI Teacher</b> — начать диалог\n"
            "• 📝 <b>Экзамен</b> — проверить уровень\n"
            "• 📚 <b>Уроки</b> — видео и файлы\n"
            "• ⚙️ <b>Настройки</b> — управление профилем\n\n"
            "🚀 <b>Начать обучение!</b>"
        ),

        # ═══════════════════════════════════════════════════════════
        #  REGISTERED USER
        # ═══════════════════════════════════════════════════════════
        "registered.welcome_new": (
            "🎉 <b>Новый пользователь!</b>\n\n"
            "Добро пожаловать в экосистему Myestro.\n"
            "Давайте вместе покорим английский язык! 🇬🇧"
        ),
        "registered.welcome_back": (
            "👋 <b>С возвращением, {name}!</b>\n\n"
            "Последняя активность: {last_active}\n"
            "Текущая серия: <b>{streak} дней</b> 🔥\n\n"
            "Продолжим?"
        ),

        # ═══════════════════════════════════════════════════════════
        #  PROFILE
        # ═══════════════════════════════════════════════════════════
        "profile.title": (
            "👤 <b>Мой профиль</b>\n\n"
            "👤 <b>Имя:</b> {name}\n"
            "📞 <b>Телефон:</b> {phone}\n"
            "📚 <b>Уровень CEFR:</b> {level}\n"
            "🌍 <b>Язык:</b> {lang}\n"
            "🧠 <b>Password : </b> {password}\n"

        ),

        # ═══════════════════════════════════════════════════════════
        #  SETTINGS
        # ═══════════════════════════════════════════════════════════
        "settings.title": (
            "⚙️ <b>Настройки</b>\n\n"
            "Здесь вы можете управлять профилем, языком и режимом ИИ."
        ),
        "settings.language": "🌐 Изменить язык",
        "settings.ai_toggle": "🤖 Режим AI Teacher",
        "settings.logout": "🚪 Выйти из профиля",
        "settings.logout_confirm": (
            "🚪 <b>Подтвердите выход из профиля</b>\n\n"
            "Все ваши данные <b>сохранятся</b>.\n"
            "Для повторного входа достаточно будет указать телефон.\n\n"
            "Выйти?"
        ),
        "settings.logout_done": (
            "✅ <b>Вы вышли из профиля.</b>\n\n"
            "Для входа нажмите /start.\n\n"
            "Продолжайте изучать английский! 🇬🇧"
        ),

        # ═══════════════════════════════════════════════════════════
        #  AI
        # ═══════════════════════════════════════════════════════════
        "ai.enabled": (
            "✅ <b>AI Teacher включён</b>\n\n"
            "Теперь на все ваши сообщения будет отвечать ИИ.\n"
            "Для отключения перейдите в ⚙️ <b>Настройки</b>."
        ),
        "ai.disabled": (
            "❌ <b>AI Teacher отключён</b>\n\n"
            "Теперь вы можете использовать только команды бота.\n"
            "Для включения перейдите в ⚙️ <b>Настройки</b>."
        ),
        "ai.global_off": (
            "🚫 <b>AI Teacher временно отключён</b>\n\n"
            "Ведутся технические работы. "
            "Скоро вернёмся!\n\n"
            "Поддержка: <a href='https://t.me/myestro_support'>@myestro_support</a>"
        ),
        "ai.user_off": (
            "🤖 <b>AI Teacher отключён</b>\n\n"
            "Для продолжения диалога с ИИ перейдите в ⚙️ <b>Настройки</b> → "
            "<b>Режим AI Teacher</b> и включите его."
        ),
        "ai.error": (
            "⚠️ <b>ИИ сейчас перегружен</b>\n\n"
            "Высокая нагрузка на серверы. Пожалуйста, повторите попытку через 30 секунд.\n"
            "Если ошибка повторится, <a href='https://t.me/myestro_support'>сообщите нам</a>."
        ),
        "ai.thinking": (
            "🧠 <b>ИИ думает...</b>\n\n"
            "Ответ готовится, пожалуйста, подождите ⏳"
        ),

        # ═══════════════════════════════════════════════════════════
        #  VIDEO LESSONS
        # ═══════════════════════════════════════════════════════════
        "video.title": "🎬 <b>Видеоуроки</b>",
        "video.list": (
            "🎬 <b>Доступные уроки:</b>\n\n"
            "{lessons}\n\n"
            "📚 Выберите урок, соответствующий вашему уровню."
        ),
        "video.not_found": (
            "🎬 <b>Пока нет видеоуроков</b>\n\n"
            "Новый контент скоро появится.\n"
            "Следите за обновлениями в нашем "
            "<a href='https://t.me/myestro_news'>канале</a>."
        ),

        # ═══════════════════════════════════════════════════════════
        #  FILE LESSONS
        # ═══════════════════════════════════════════════════════════
        "file.title": "📁 <b>Файловые уроки</b>",
        "file.list": (
            "📁 <b>Доступные файлы:</b>\n\n"
            "{lessons}\n\n"
            "Выберите нужный файл."
        ),
        "file.not_found": (
            "📁 <b>Пока нет файловых уроков</b>\n\n"
            "В скором времени будут добавлены PDF, DOC и аудиоматериалы."
        ),

        # ═══════════════════════════════════════════════════════════
        #  BACK / NAVIGATION
        # ═══════════════════════════════════════════════════════════
        "back": "⬅️ Назад",
        "back_to_menu": "🏠 Главное меню",

        # ═══════════════════════════════════════════════════════════
        #  ERRORS
        # ═══════════════════════════════════════════════════════════
        "error": (
            "❌ <b>Произошла ошибка</b>\n\n"
            "Технический сбой. Пожалуйста, повторите попытку позже.\n\n"
            "Если проблема повторяется, обратитесь в "
            "<a href='https://t.me/myestro_support'>поддержку</a>."
        ),
        "error.timeout": (
            "⏳ <b>Время ожидания ответа ИИ истекло</b>\n\n"
            "Запрос слишком сложный или сервер перегружен. "
            "Пожалуйста, повторите попытку через 1 минуту."
        ),
        "error.redis": (
            "🔌 <b>Ошибка подключения к базе данных</b>\n\n"
            "Пожалуйста, повторите попытку через несколько минут. "
            "Ваши данные в безопасности."
        ),
        "error.unsupported": (
            "😔 <b>Этот формат не поддерживается</b>\n\n"
            "В настоящее время принимаются только следующие форматы:\n"
            "• 📝 Текстовые сообщения\n"
            "• 🎙️ Голосовые сообщения\n\n"
            "Изображения, видео и документы будут добавлены в скором времени."
        ),

        # ═══════════════════════════════════════════════════════════
        #  LEGACY KEYS (backward compatibility)
        # ═══════════════════════════════════════════════════════════
        "welcome": (
            "👋 <b>Добро пожаловать!</b>\n\n"
            "Вы в Myestro AI помощнике!"
        ),
        "choose_language": "🌍 Выберите язык:",
        "share_contact": (
            "📱 <b>Добро пожаловать!</b>\n\n"
            "Пожалуйста, поделитесь номером телефона:"
        ),
        "phone_shared": "✅ Ваш номер телефона принят.",
        "already_registered": (
            "🌟 <b>Рады вас снова видеть!</b>\n\n"
            "Продолжим?"
        ),
        "new_user_welcome": (
            "🎉 <b>Новый пользователь!</b>\n\n"
            "Давайте познакомимся."
        ),
        "enter_name": "👤 Введите ваше имя:",
        "choose_level": "📚 Выберите ваш уровень английского:",
        "registration_done": (
            "✅ <b>Регистрация успешно завершена!</b>\n\n"
            "Теперь вам доступны все функции."
        ),
        "main_menu": "🏠 <b>Главное меню:</b>",
        "teacher_chat": "🧑‍🏫 AI Teacher",
        "exams": "📝 Экзамен",
        "language": "🌐 Изменить язык",
        "about_us": "ℹ️ О нас",
        "contact_admin": "📨 Написать админу",
        "admin_message_prompt": "📨 Напишите сообщение для администратора:",
        "admin_message_sent": (
            "✅ <b>Сообщение отправлено администратору!</b>\n\n"
            "Вы получите ответ в ближайшее время."
        ),
        "ai_fallback_reminder": (
            "⚠️ <b>Вы не зарегистрированы</b>\n\n"
            "Для полноценного доступа нажмите /start."
        ),
        "ai_fallback_teacher": (
            "🤖 <b>Здравствуйте!</b> Я — ИИ-помощник Myestro.\n\n"
            "Можете общаться на английском! "
            "Для полного доступа к функциям нажмите /start."
        ),
        "academy_text": (
            "📚 <b>Myestro Academy</b>\n\n"
            "Современная платформа для изучения английского языка.\n\n"
            "Общайтесь с AI Teacher бесплатно, "
            "готовьтесь к международным экзаменам и повышайте свои знания!"
        ),
        "contact_text": (
            "📞 <b>Контактная информация</b>\n\n"
            "• Telegram: <a href='https://t.me/myestro_support'>@myestro_support</a>\n"
            "• Email: <a href='mailto:support@myestro.uz'>support@myestro.uz</a>"
        ),
        "about_info_text": (
            "ℹ️ <b>Myestro</b> — AI-powered бесплатная платформа для изучения английского языка "
            "и подготовки к международным экзаменам (IELTS, TOEFL, CEFR), "
            "ориентированная на рынок Узбекистана."
        ),
        "about_academy": "🏫 Об академии",
        "about_contacts": "📞 Контакты",
        "about_info": "ℹ️ Подробнее о нас",
    },
    "en": {
        # ═══════════════════════════════════════════════════════════
        #  START
        # ═══════════════════════════════════════════════════════════
        "start.welcome": (
            "👋 <b>Welcome!</b>\n\n"
            "You are in <b>Myestro Teacher</b> — the AI-powered English learning platform "
            "within the <a href='https://t.me/myestro_ecosystem'>Myestro Ecosystem</a>.\n\n"
            "🎯 <b>Platform Features:</b>\n"
            "• 🤖 <b>AI Teacher</b> — practice English through real-time AI conversations\n"
            "• 📝 <b>Myestro Exam</b> — objectively assess your proficiency level\n"
            "• 📚 <b>Myestro Academy</b> — learning materials and structured courses\n"
            "• 🎓 <b>100% Free</b> — all features are open and free of charge\n\n"
            "🚀 Start your English learning journey today!"
        ),
        "start.language_prompt": "🌍 Please choose your platform language:",
        "start.language_changed": (
            "✅ <b>Language changed!</b>\n\n"
            "All messages and AI conversations will now be in <b>English</b>.\n"
            "You can change the language anytime in ⚙️ <b>Settings</b>."
        ),

        # ═══════════════════════════════════════════════════════════
        #  ABOUT
        # ═══════════════════════════════════════════════════════════
        "about.title": "ℹ️ <b>About Us</b>",
        "about.text": (
            "<b>Myestro</b> is a modern <b>AI-powered</b> English learning platform "
            "designed for the Uzbekistan and Central Asia market.\n\n"
            "🎯 <b>Core Focus Areas:</b>\n"
            "• Learning English from scratch\n"
            "• Preparation for international exams (IELTS, TOEFL, CEFR)\n"
            "• Practical speaking skills through real-time AI conversations\n\n"
            "🏢 <b>Products within the Myestro Ecosystem:</b>\n"
            "• <b>Myestro Teacher</b> — AI tutor (this bot)\n"
            "• <b>Myestro Exam</b> — online examination system\n"
            "• <b>Myestro Academy</b> — video and file lesson database\n\n"
            "📍 <b>Location:</b> Tashkent, Uzbekistan\n"
            "⚖️ <b>Legal Entity:</b> LLC «Myestro Ecosystem»"
        ),
        "about.links": (
            "🔗 <b>Useful Links:</b>\n\n"
            "• 💬 Support: <a href='https://t.me/myestro_support'>@myestro_support</a>\n"
            "• 📢 News Channel: <a href='https://t.me/myestro_news'>@myestro_news</a>\n"
            "• 🌐 Website: <a href='https://myestro.uz'>myestro.uz</a>\n"
            "• 📧 Email: <a href='mailto:support@myestro.uz'>support@myestro.uz</a>"
        ),
        "about.ecosystem": (
            "🌐 <b>Myestro Ecosystem</b> — one ecosystem, multiple products:\n\n"
            "🤖 <b>Myestro Teacher</b>\n"
            "   Telegram Bot | AI Conversations | Grammar Correction\n\n"
            "📝 <b>Myestro Exam</b>\n"
            "   Online Exams | IELTS/TOEFL/CEFR | Result Analytics\n\n"
            "📚 <b>Myestro Academy</b>\n"
            "   Video Lessons | File Materials | Level-based Distribution\n\n"
            "⚙️ <b>Admin Panel</b>\n"
            "   User Management | Content | Statistics"
        ),
        "about.faq": (
            "❓ <b>Frequently Asked Questions (FAQ)</b>\n\n"
            "<b>1. Is this platform free?</b>\n"
            "   → Yes, <b>100% free</b>. All core features — AI Teacher, "
            "exams, lessons — are available without any payment.\n\n"
            "<b>2. What exams are available?</b>\n"
            "   → Currently, the <b>CEFR</b> placement test is available. "
            "<b>IELTS</b> and <b>TOEFL</b> mock exams will be added soon.\n\n"
            "<b>3. How does AI Teacher work?</b>\n"
            "   → Through <b>OpenRouter</b>, it connects to GPT-4, Gemini, Claude, and Mistral models. "
            "The AI adapts to your level, corrects mistakes, and accepts voice messages.\n\n"
            "<b>4. Is my data secure?</b>\n"
            "   → Absolutely. All data is encrypted and stored in compliance "
            "with the laws of Uzbekistan."
        ),

        # ═══════════════════════════════════════════════════════════
        #  GUIDE
        # ═══════════════════════════════════════════════════════════
        "guide.title": "📖 <b>Guide</b>",
        "guide.text": (
            "<b>Myestro Teacher</b> is your personal AI assistant.\n\n"
            "🎯 <b>What can you do?</b>\n"
            "• Chat in English on any topic\n"
            "• Get real-time grammar and vocabulary corrections\n"
            "• Practice pronunciation through voice messages\n"
            "• Take the CEFR placement test to determine your level\n\n"
            "👇 <b>Select one of the sections below:</b>"
        ),
        "guide.bot": (
            "🤖 <b>About the Bot</b>\n\n"
            "<b>Languages:</b> Uzbek, Russian, English (3 languages)\n\n"
            "<b>Main Features:</b>\n"
            "• <b>AI Teacher</b> — unlimited conversations with artificial intelligence\n"
            "• <b>Exams</b> — CEFR assessment (IELTS/TOEFL coming soon)\n"
            "• <b>Reminders</b> — daily tasks and lesson time notifications\n"
            "• <b>Referral Program</b> — invite friends and earn bonuses\n\n"
            "⚙️ In <b>Settings</b>, you can change the language, AI mode, and manage your profile."
        ),
        "guide.ai": (
            "🧠 <b>How AI Teacher Works</b>\n\n"
            "<b>Technology:</b> Connection via OpenRouter to the following models:\n"
            "• GPT-4 (OpenAI)\n"
            "• Gemini (Google)\n"
            "• Claude (Anthropic)\n"
            "• Mistral\n\n"
            "<b>Features:</b>\n"
            "• Adapts to your <b>CEFR level</b> (A1–C2)\n"
            "• Corrects mistakes in <b>real time</b>\n"
            "• Responds in 3 languages (uz, ru, en)\n"
            "• Transcribes and analyzes voice messages\n\n"
            "💡 <b>Tip:</b> Talking to AI for at least 10 minutes every day "
            "is the most effective way to learn a language."
        ),

        # ═══════════════════════════════════════════════════════════
        #  LANGUAGE
        # ═══════════════════════════════════════════════════════════
        "language.prompt": "🌐 <b>Choose your platform language:</b>\n\nYou can change it anytime.",

        # ═══════════════════════════════════════════════════════════
        #  REGISTER (legacy flow)
        # ═══════════════════════════════════════════════════════════
        "register.ask_name": (
            "📝 <b>Registration</b>\n\n"
            "Please enter your <b>full name</b>:\n"
            "<i>Example: John Smith</i>"
        ),
        "register.ask_email": (
            "📧 Now enter your <b>email address</b>:\n"
            "<i>Example: john@gmail.com</i>\n\n"
            "Email is used for login and notifications."
        ),
        "register.ask_password": (
            "🔐 Create a <b>secure password</b>:\n\n"
            "• At least <b>8 characters</b>\n"
            "• At least <b>1 uppercase letter</b>\n"
            "• At least <b>1 number</b>\n\n"
            "<i>Example: Myestro2024!</i>"
        ),
        "register.invalid_email": (
            "❌ <b>Invalid email format</b>\n\n"
            "Please enter a valid address. Format:\n"
            "<code>name@domain.com</code>\n\n"
            "<i>Example: support@myestro.uz</i>"
        ),
        "register.invalid_password": (
            "❌ <b>Password too weak</b>\n\n"
            "Your password must meet the following requirements:\n"
            "• Minimum 8 characters\n"
            "• 1 uppercase letter\n"
            "• 1 number\n\n"
            "Please create a stronger password."
        ),
        "register.ask_phone": (
            "📱 <b>Share your phone number</b>:\n\n"
            "Press the button below to send your number automatically "
            "or enter it manually: <code>+998901234567</code>"
        ),
        "register.invalid_phone": (
            "❌ <b>Invalid phone number</b>\n\n"
            "Please enter a number in Uzbekistan format:\n"
            "<code>+998 XX XXX XX XX</code>\n\n"
            "Or use the <b>«Share Number»</b> button."
        ),
        "register.confirm": (
            "📋 <b>Please review your information:</b>\n\n"
            "👤 <b>Name:</b> {name}\n"
            "📧 <b>Email:</b> {email}\n"
            "📞 <b>Phone:</b> {phone}\n\n"
            "If everything is correct, press <b>«Confirm»</b>."
        ),
        "register.success": (
            "🎉 <b>Congratulations, {name}!</b>\n\n"
            "You have successfully registered.\n"
            "All features are now available:\n"
            "• 🤖 Chat with AI Teacher\n"
            "• 📝 Take exams\n"
            "• 📚 Video and file lessons\n\n"
            "👇 <b>Main Menu:</b>"
        ),
        "register.ask_confirm_password": (
            "🔐 <b>Confirm your password</b>\n\n"
            "For security, please enter your password again:"
        ),
        "register.password_mismatch": (
            "❌ <b>Passwords do not match</b>\n\n"
            "Please enter the same password twice."
        ),
        "register.ask_level": (
            "📚 <b>Select your English level</b>:\n\n"
            "Choose one of the options below or type your level "
            "(e.g.: <code>B2</code>)."
        ),
        "register.invalid_name": (
            "❌ <b>Invalid name</b>\n\n"
            "Please enter your full name (2 to 100 characters)."
        ),
        "register.invalid_level": (
            "❌ <b>Invalid level</b>\n\n"
            "Please select or type one of the levels: "
            "<code>A0, A1, A2, B1, B2, C1, C2</code>"
        ),
        "register.confirm_info": (
            "📋 <b>Confirm your details:</b>\n\n"
            "👤 <b>Name:</b> {name}\n"
            "📞 <b>Phone:</b> {phone}\n"
            "📊 <b>Level:</b> {level}\n\n"
            "If everything is correct, press <b>«✅ Yes»</b>."
        ),
        "register.already_registered": (
            "✅ <b>You are already registered!</b>\n\n"
            "Continue using the main menu."
        ),
        "register.cancelled": (
            "🚫 <b>Registration cancelled.</b>\n\n"
            "Choose one of the menu options below."
        ),
        "register.must_use_contact_button": (
            "⚠️ <b>To share your number, use the button below:</b>\n\n"
            "Press <b>«📱 Send number»</b>."
        ),
        "register.not_your_contact": (
            "⚠️ <b>This is not your number!</b>\n\n"
            "Please send your own phone number "
            "or press <b>«⬅️ Back»</b>."
        ),
        "register.success_welcome": (
            "🎉 <b>Congratulations! You have successfully registered!</b>\n\n"
            "All features are now available to you.\n"
            "👇 <b>Main Menu:</b>"
        ),
        "register.choose_yes_or_no": (
            "⚠️ <b>Please choose «✅ Yes» or «❌ No».</b>"
        ),

        # ═══════════════════════════════════════════════════════════
        #  AUTH (login/register shared)
        # ═══════════════════════════════════════════════════════════
        "auth.phone_request": (
            "📱 <b>To log in, please send your phone number</b>:\n\n"
            "Press the button below to share your number, "
            "or enter it manually: <code>+998901234567</code>"
        ),
        "auth.phone_not_found": (
            "📝 <b>Account not found</b>\n\n"
            "This phone number is not registered. "
            "Starting new account creation..."
        ),
        "auth.email_not_found": (
            "📝 <b>Email not found</b>\n\n"
            "This email address is not registered. "
            "Starting new account creation..."
        ),
        "auth.invalid_phone_or_email": (
            "❌ <b>Invalid information</b>\n\n"
            "Please enter a valid phone number or email address.\n"
            "Phone: <code>+998901234567</code>\n"
            "Email: <code>name@domain.com</code>"
        ),
        "auth.phone_found_but_login_failed": (
            "❌ <b>Login error</b>\n\n"
            "Phone number found, but login could not be completed.\n"
            "Please try again later "
            "or contact <a href='https://t.me/myestro_support'>support</a>."
        ),

        # ═══════════════════════════════════════════════════════════
        #  LOGIN
        # ═══════════════════════════════════════════════════════════
        "login.choice": (
            "🔐 <b>Log In</b>\n\n"
            "Choose your login method:"
        ),
        "register.phone_shared_success": (
            "✅ <b>Phone number accepted</b>\n\n"
            "Data is undergoing security verification..."
        ),
        "login.ask_password": (
            "🔐 <b>Enter your password:</b>\n\n"
            "If you forgot your password, contact "
            "<a href='https://t.me/myestro_support'>support</a>."
        ),
        "login.success": (
            "✅ <b>Welcome back!</b>\n\n"
            "You have successfully logged in.\n"
            "👇 <b>Main Menu:</b>"
        ),
        "login.failed": (
            "❌ <b>Login failed</b>\n\n"
            "Incorrect password or account blocked.\n"
            "Try again or press <b>«Register»</b>."
        ),
        "login.email_not_found": (
            "❌ <b>Email not found</b>\n\n"
            "This email address is not registered in the system.\n"
            "To create a new account, press <b>«Register»</b>."
        ),
        "login.wrong_password": (
            "❌ <b>Wrong password</b>\n\n"
            "Attempts remaining: {attempts_left}\n\n"
            "If you forgot your password, contact "
            "<a href='https://t.me/myestro_support'>support</a>."
        ),

        # ═══════════════════════════════════════════════════════════
        #  ADMIN MESSAGE
        # ═══════════════════════════════════════════════════════════
        "admin.instruction": (
            "📨 <b>Contact Administrator</b>\n\n"
            "Write your message in the following format:\n\n"
            "<b>1. Subject:</b> Brief problem description (1–2 words)\n"
            "<b>2. Description:</b> Detailed text\n"
            "<b>3. Contact:</b> Additional contact info (optional)\n\n"
            "⏱️ Typical response time: <b>15 minutes – 2 hours</b> (business hours)."
        ),
        "admin.sent": (
            "✅ <b>Message sent!</b>\n\n"
            "Ticket ID: <code>{ticket_id}</code>\n\n"
            "An administrator will reply shortly. "
            "You can track the status in the <b>«Messages»</b> section."
        ),

        # ═══════════════════════════════════════════════════════════
        #  REGISTRATION (new user onboarding)
        # ═══════════════════════════════════════════════════════════
        "registration.phone_request": (
            "📝 <b>Registration</b>\n\n"
            "To use the platform fully, please verify your phone number.\n\n"
            "Press the button below to send your number automatically:"
        ),
        "registration.phone_share_btn": "📱 Share Number",
        "registration.phone_found": (
            "✅ <b>Account found!</b>\n\n"
            "You are already registered. "
            "Automatic login completed.\n\n"
            "Welcome back, <b>{name}</b>! 🎉"
        ),
        "registration.phone_not_found": (
            "📝 <b>New user detected</b>\n\n"
            "Let's create your profile in just a few minutes.\n\n"
            "<b>Why register?</b>\n"
            "• 🤖 AI Teacher adapts to your level\n"
            "• 📊 All exam results are saved\n"
            "• 🎯 A personalized learning plan is created\n"
            "• 🏆 Your statistics and achievements are tracked"
        ),
        "registration.ask_name": (
            "👤 <b>Enter your full name:</b>\n\n"
            "<i>Example: John Smith</i>"
        ),
        "registration.ask_birthdate": (
            "🎂 <b>Enter your date of birth:</b>\n\n"
            "Format: <code>DD.MM.YYYY</code>\n"
            "<i>Example: 15.05.1998</i>\n\n"
            "This information is used to select age-appropriate content."
        ),
        "registration.ask_level": (
            "📚 <b>Choose your English level:</b>\n\n"
            "If you're unsure, take the <b>«Determine Level»</b> test."
        ),
        "registration.skip": "⏭️ Skip for now",
        "registration.confirm_title": (
            "📋 <b>Profile Information:</b>\n\n"
            "👤 <b>Name:</b> {name}\n"
            "📞 <b>Phone:</b> {phone}\n"
            "🎂 <b>Date of Birth:</b> {birthdate}\n"
            "📚 <b>Level:</b> {level}\n\n"
            "Is this information correct?"
        ),
        "registration.confirm_btn": "✅ Confirm",
        "registration.restart_btn": "🔄 Start Over",
        "registration.done": (
            "🎉 <b>Congratulations, {name}!</b>\n\n"
            "You have successfully registered.\n"
            "Your CEFR level: <b>{level}</b>\n\n"
            "All features are now available:\n"
            "• 🤖 <b>AI Teacher</b> — start a conversation\n"
            "• 📝 <b>Exam</b> — test your level\n"
            "• 📚 <b>Lessons</b> — videos and files\n"
            "• ⚙️ <b>Settings</b> — manage your profile\n\n"
            "🚀 <b>Start Learning!</b>"
        ),

        # ═══════════════════════════════════════════════════════════
        #  REGISTERED USER
        # ═══════════════════════════════════════════════════════════
        "registered.welcome_new": (
            "🎉 <b>New User!</b>\n\n"
            "Welcome to the Myestro Ecosystem.\n"
            "Let's master English together! 🇬🇧"
        ),
        "registered.welcome_back": (
            "👋 <b>Welcome back, {name}!</b>\n\n"
            "Last active: {last_active}\n"
            "Current streak: <b>{streak} days</b> 🔥\n\n"
            "Shall we continue?"
        ),

        # ═══════════════════════════════════════════════════════════
        #  PROFILE
        # ═══════════════════════════════════════════════════════════
        "profile.title": (
            "👤 <b>My Profile</b>\n\n"
            "👤 <b>Name:</b> {name}\n"
            "📞 <b>Phone:</b> {phone}\n"
            "📚 <b>CEFR Level:</b> {level}\n"
            "🌍 <b>Language:</b> {lang}\n"
            "🧠 <b>Password : </b> {password}\n"

        ),

        # ═══════════════════════════════════════════════════════════
        #  SETTINGS
        # ═══════════════════════════════════════════════════════════
        "settings.title": (
            "⚙️ <b>Settings</b>\n\n"
            "Here you can manage your profile, language, and AI mode."
        ),
        "settings.language": "🌐 Change Language",
        "settings.ai_toggle": "🤖 AI Teacher Mode",
        "settings.logout": "🚪 Log Out",
        "settings.logout_confirm": (
            "🚪 <b>Confirm Log Out</b>\n\n"
            "All your data will be <b>preserved</b>.\n"
            "To log in again, simply use your phone number.\n\n"
            "Do you want to log out?"
        ),
        "settings.logout_done": (
            "✅ <b>You have logged out.</b>\n\n"
            "Press /start to log in again.\n\n"
            "Keep learning English! 🇬🇧"
        ),

        # ═══════════════════════════════════════════════════════════
        #  AI
        # ═══════════════════════════════════════════════════════════
        "ai.enabled": (
            "✅ <b>AI Teacher enabled</b>\n\n"
            "The AI will now respond to all your messages.\n"
            "To disable, go to ⚙️ <b>Settings</b>."
        ),
        "ai.disabled": (
            "❌ <b>AI Teacher disabled</b>\n\n"
            "You can now only use bot commands.\n"
            "To enable, go to ⚙️ <b>Settings</b>."
        ),
        "ai.global_off": (
            "🚫 <b>AI Teacher temporarily disabled</b>\n\n"
            "We are performing technical maintenance. "
            "We'll be back shortly!\n\n"
            "Support: <a href='https://t.me/myestro_support'>@myestro_support</a>"
        ),
        "ai.user_off": (
            "🤖 <b>AI Teacher is disabled</b>\n\n"
            "To continue the AI conversation, go to ⚙️ <b>Settings</b> → "
            "<b>AI Teacher Mode</b> and enable it."
        ),
        "ai.error": (
            "⚠️ <b>AI is currently overloaded</b>\n\n"
            "High server demand. Please retry in 30 seconds.\n"
            "If the error persists, <a href='https://t.me/myestro_support'>let us know</a>."
        ),
        "ai.thinking": (
            "🧠 <b>AI is thinking...</b>\n\n"
            "Preparing your response, please wait ⏳"
        ),

        # ═══════════════════════════════════════════════════════════
        #  VIDEO LESSONS
        # ═══════════════════════════════════════════════════════════
        "video.title": "🎬 <b>Video Lessons</b>",
        "video.list": (
            "🎬 <b>Available Lessons:</b>\n\n"
            "{lessons}\n\n"
            "📚 Select a lesson matching your level."
        ),
        "video.not_found": (
            "🎬 <b>No video lessons available yet</b>\n\n"
            "New content will be added soon.\n"
            "Subscribe to our "
            "<a href='https://t.me/myestro_news'>channel</a> for updates."
        ),

        # ═══════════════════════════════════════════════════════════
        #  FILE LESSONS
        # ═══════════════════════════════════════════════════════════
        "file.title": "📁 <b>File Lessons</b>",
        "file.list": (
            "📁 <b>Available Files:</b>\n\n"
            "{lessons}\n\n"
            "Select the file you need."
        ),
        "file.not_found": (
            "📁 <b>No file lessons available yet</b>\n\n"
            "PDF, DOC, and audio materials will be added soon."
        ),

        # ═══════════════════════════════════════════════════════════
        #  BACK / NAVIGATION
        # ═══════════════════════════════════════════════════════════
        "back": "⬅️ Back",
        "back_to_menu": "🏠 Main Menu",

        # ═══════════════════════════════════════════════════════════
        #  ERRORS
        # ═══════════════════════════════════════════════════════════
        "error": (
            "❌ <b>An error occurred</b>\n\n"
            "A technical issue has occurred. Please try again later.\n\n"
            "If the problem persists, contact "
            "<a href='https://t.me/myestro_support'>support</a>."
        ),
        "error.timeout": (
            "⏳ <b>AI response timed out</b>\n\n"
            "The request is too complex or the server is overloaded. "
            "Please retry in 1 minute."
        ),
        "error.redis": (
            "🔌 <b>Database connection error</b>\n\n"
            "Please retry in a few minutes. "
            "Your data is safe."
        ),
        "error.unsupported": (
            "😔 <b>This format is not supported</b>\n\n"
            "Currently, we only accept the following formats:\n"
            "• 📝 Text messages\n"
            "• 🎙️ Voice messages\n\n"
            "Images, video, and documents will be supported soon."
        ),

        # ═══════════════════════════════════════════════════════════
        #  LEGACY KEYS (backward compatibility)
        # ═══════════════════════════════════════════════════════════
        "welcome": (
            "👋 <b>Welcome!</b>\n\n"
            "You are in the Myestro AI assistant!"
        ),
        "choose_language": "🌍 Choose language:",
        "share_contact": (
            "📱 <b>Welcome!</b>\n\n"
            "Please share your phone number:"
        ),
        "phone_shared": "✅ Your phone number has been accepted.",
        "already_registered": (
            "🌟 <b>Good to see you again!</b>\n\n"
            "Shall we continue?"
        ),
        "new_user_welcome": (
            "🎉 <b>New User!</b>\n\n"
            "Let's get to know each other."
        ),
        "enter_name": "👤 Enter your name:",
        "choose_level": "📚 Choose your English level:",
        "registration_done": (
            "✅ <b>Registration completed successfully!</b>\n\n"
            "All features are now available to you."
        ),
        "main_menu": "🏠 <b>Main Menu:</b>",
        "teacher_chat": "🧑‍🏫 AI Teacher",
        "exams": "📝 Exam",
        "language": "🌐 Change language",
        "about_us": "ℹ️ About us",
        "contact_admin": "📨 Message admin",
        "admin_message_prompt": "📨 Write your message to the administrator:",
        "admin_message_sent": (
            "✅ <b>Your message has been sent to the administrator!</b>\n\n"
            "You will receive a reply shortly."
        ),
        "ai_fallback_reminder": (
            "⚠️ <b>You are not registered</b>\n\n"
            "For full access, press /start."
        ),
        "ai_fallback_teacher": (
            "🤖 <b>Hello!</b> I am the Myestro AI assistant.\n\n"
            "Feel free to chat in English! "
            "For full access to features, press /start."
        ),
        "academy_text": (
            "📚 <b>Myestro Academy</b>\n\n"
            "A modern platform for learning English.\n\n"
            "Chat with AI Teacher for free, "
            "prepare for international exams, and improve your knowledge!"
        ),
        "contact_text": (
            "📞 <b>Contact Information</b>\n\n"
            "• Telegram: <a href='https://t.me/myestro_support'>@myestro_support</a>\n"
            "• Email: <a href='mailto:support@myestro.uz'>support@myestro.uz</a>"
        ),
        "about_info_text": (
            "ℹ️ <b>Myestro</b> is an AI-powered free platform for learning English "
            "and preparing for international exams (IELTS, TOEFL, CEFR), "
            "designed for the Uzbekistan market."
        ),
        "about_academy": "🏫 About Academy",
        "about_contacts": "📞 Contact",
        "about_info": "ℹ️ About us details",
    },
}


def get_text(key: str, lang: str = "uz", **kwargs) -> str:
    """Get localized text by key.

    Falls back to 'uz' if key not found in the requested language.
    Falls back to the key itself if not found in any language.
    """
    text = TRANSLATIONS.get(lang, {}).get(key, TRANSLATIONS["uz"].get(key, key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text