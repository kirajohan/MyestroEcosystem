import re
from pathlib import Path

# Fayl yo'llari
INPUT_FILE = Path("Your paragraph text-compressed.md")
OUTPUT_DIR = Path("knowledge/grammar_chunks")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Eskisi frontmatter bo'lsa, olib tashlaymiz
content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL).strip()

# UNIT va Appendix bo'yicha bo'lish (Lookahead ishlatamiz)
sections = re.split(r'(?=UNIT\s*\n\d+|Appendix\s*\d+)', content)

created_count = 0
for section in sections:
    section = section.strip()
    if not section:
        continue
    
    # Sarlavhani aniqlash (masalan: unit_88 yoki appendix_1)
    match = re.search(r'(UNIT\s*\n\d+|Appendix\s*\d+)', section)
    if match:
        title = match.group(1).replace('\n', '_').lower().replace(' ', '_')
    else:
        title = "intro_muqaddima"
        
    # RAG uchun frontmatter
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
    print(f"✅ Yaratildi: {output_file.name}")

print(f"\n🎉 Jami {created_count} ta chunk muvaffaqiyatli yaratildi: {OUTPUT_DIR}")