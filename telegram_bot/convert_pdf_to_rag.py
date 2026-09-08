import os
from pathlib import Path
from markitdown import MarkItDown

# Loyiha yo'llarini sozlash
BASE_DIR = Path(__file__).resolve().parent
PDF_INPUT_DIR = BASE_DIR / "knowledge" / "pdfs"  # PDF lar shu papkada turadi
MD_OUTPUT_DIR = BASE_DIR / "knowledge"           # Tayyor .md fayllar shu yerga tushadi

def convert_all_pdfs_to_rag_markdown(default_category: str = "book", default_tags: list = None):
    """
    Papkadagi BARCHA PDF fayllarni topadi va ularni RAG uchun tayyor Markdown formatiga o'giradi.
    """
    if default_tags is None:
        default_tags = ["kitob", "general"]
        
    # Papkalarni tekshirish va kerak bo'lsa yaratish
    PDF_INPUT_DIR.mkdir(parents=True, exist_ok=True)
    MD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Papkadagi barcha .pdf fayllarni topish
    pdf_files = list(PDF_INPUT_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"⚠️ '{PDF_INPUT_DIR}' papkasida hech qanday PDF fayl topilmadi.")
        print("PDF fayllarni shu papkaga joylashtirib, qaytadan urinib ko'ring.")
        return
        
    print(f"📂 Jami {len(pdf_files)} ta PDF fayl topildi. Konvertatsiya boshlanmoqda...\n")
    
    md_converter = MarkItDown()
    success_count = 0
    error_count = 0
    
    for index, pdf_path in enumerate(pdf_files, 1):
        print(f"[{index}/{len(pdf_files)}] 🔄 '{pdf_path.name}' o'girilmoqda...")
        
        try:
            # 1. MarkItDown orqali o'girish
            result = md_converter.convert(str(pdf_path))
            markdown_text = result.text_content
            
            # 2. YAML Frontmatter tayyorlash (rag_client.py aynan shu formatni kutadi)
            tags_yaml = ", ".join([f'"{tag}"' for tag in default_tags])
            frontmatter = f"""---
category: {default_category}
tags: [{tags_yaml}]
source_file: {pdf_path.name}
---

"""
            
            # 3. Yakuniy matnni shakllantirish
            final_content = frontmatter + markdown_text.strip()
            
            # 4. .md fayl sifatida saqlash (xuddi shu nom bilan, lekin .md kengaytmasida)
            output_filename = pdf_path.stem + ".md"
            output_path = MD_OUTPUT_DIR / output_filename
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_content)
                
            print(f"  ✅ Muvaffaqiyatli: {output_path.name} ({len(markdown_text)} ta belgi)")
            success_count += 1
            
        except Exception as e:
            print(f"  ❌ Xato: '{pdf_path.name}' faylini o'girishda muammo yuz berdi: {e}")
            error_count += 1
            
    print(f"\n🎉 Jarayon yakunlandi!")
    print(f"📊 Natija: {success_count} ta muvaffaqiyatli, {error_count} ta xato.")
    print(f"📁 Tayyor fayllar: {MD_OUTPUT_DIR}")

if __name__ == "__main__":
    # BU YERNI O'ZINGIZGA MOSLASHINGIZ MUMKIN:
    # Barcha fayllar uchun umumiy category va tags shu yerda belgilanadi.
    convert_all_pdfs_to_rag_markdown(
        default_category="general", 
        default_tags=["kitob", "myestro", "knowledge"]
    )