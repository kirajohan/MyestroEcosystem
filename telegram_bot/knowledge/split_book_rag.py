# -*- coding: utf-8 -*-
import re
import sys
import os
from pathlib import Path

# UTF-8 encoding uchun Windows da
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

# Fayl yo'llari (o'zingiznikiga moslab o'zgartiring)
script_dir = Path(__file__).parent
INPUT_FILE = script_dir / "Your paragraph text-compressed.md"
OUTPUT_DIR = script_dir / "grammar_chunks"

# Papkani yaratish
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not INPUT_FILE.exists():
    print(f"XATO: {INPUT_FILE} fayli topilmadi! Fayl shu papkada turganiga ishonch hosil qiling.")
    print(f"Hozirgi papka: {Path.cwd()}")
    exit(1)

print(f"Fayl o'qilmoqda: {INPUT_FILE.name}...")
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Eski frontmatter bo'lsa, olib tashlaymiz
content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL).strip()

# UNIT va Appendix bo'yicha bo'lish (Lookahead ishlatamiz)
# Bu UNIT 88, UNIT 91, Appendix 1 kabi sarlavhalarni aniqlaydi
sections = re.split(r'(?=UNIT\s*\n\d+|Appendix\s*\d+)', content)

created_count = 0
for section in sections:
    section = section.strip()
    if not section or len(section) < 50:  # Juda kichik bo'sh bo'laklarni o'tkazib yuboramiz
        continue
    
    # Sarlavhani aniqlash (masalan: unit_88 yoki appendix_1)
    match = re.search(r'(UNIT\s*\n\d+|Appendix\s*\n*\d+)', section)
    if match:
        title = match.group(1).replace('\n', '_').lower().replace(' ', '_')
    else:
        title = "intro_muqaddima"
        
    # RAG uchun frontmatter (sizning rag_client.py talablariga mos)
    frontmatter = f"""---
category: grammar
tags: ["myestro", "grammar_book", "{title}"]
source_file: myestro_grammar_{title}
---

"""
    
    # Faylga yozish
    output_file = OUTPUT_DIR / f"myestro_grammar_{title}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(frontmatter + section)
    
    created_count += 1

print(f"MUVAFFAQIYATLI! Jami {created_count} ta chunk yaratildi.")
print(f"Barcha fayllar shu papkada: {OUTPUT_DIR.resolve()}")
print("Endi bu fayllarni asosiy 'knowledge/' papkasiga ko'chirib, botni qayta ishga tushirishingiz mumkin.")
