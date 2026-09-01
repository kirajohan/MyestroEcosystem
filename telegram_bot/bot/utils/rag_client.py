"""
RAG (Retrieval-Augmented Generation) Client
Statik fayllar asosida AI uchun bilim bazasi

Ishlash tartibi:
1. Startup'da knowledge/ papkasidan barcha .md fayllarni yuklaydi
2. Har bir faylni chunk'larga bo'ladi
3. Har bir chunk uchun embedding hisoblaydi (OpenRouter)
4. Foydalanuvchi savoli kelganda:
   - Savol uchun embedding hisoblaydi
   - Barcha chunk'lar bilan cosine similarity solishtiradi
   - Eng o'xshash 3 ta chunk'ni oladi
   - AI promptiga context sifatida qo'shadi
"""

import os
import re
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Optional
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class RAGClient:
    """Statik fayllar asosidagi RAG tizimi"""
    
    def __init__(self):
        # Knowledge papkasi yo'li
        # __file__ = /app/bot/utils/rag_client.py
        # parent.parent.parent = /app  (telegram_bot root)
        # /app/knowledge = to'g'ri yo'l
        self.knowledge_dir = Path(__file__).resolve().parent.parent.parent / "knowledge"        # Barcha chunk'lar (yuklangandan keyin to'ldiriladi)
        self.chunks: List[Dict] = []
        
        # Embedding cache (bir xil matn uchun qayta hisoblamaslik uchun)
        self._embedding_cache: Dict[str, List[float]] = {}
        
        # Ishga tushirilganligini tekshirish
        self._initialized = False
        
        # OpenRouter embedding sozlamalari
        self.embedding_model = "openai/text-embedding-3-small"
        self.embedding_dimensions = 1536  # text-embedding-3-small uchun
        
        # Chunk sozlamalari
        self.chunk_size = 500        # bir chunk'da maksimal belgi
        self.chunk_overlap = 50      # qo'shni chunk'lar orasidagi overlap
        
        # Qidiruv sozlamalari
        self.top_k = 3               # qancha chunk qaytarish
        self.min_score = 0.1         # minimal similarity score
        
        logger.info(f"📚 RAG Client yaratildi. Knowledge dir: {self.knowledge_dir}")
    
    # ─────────────────────────────────────────────────────────
    # 1. FAYLLARNI YUKLASH
    # ─────────────────────────────────────────────────────────
    
    def load_knowledge(self) -> int:
        """
        Barcha .md fayllarni yuklaydi va chunk'larga bo'ladi.
        Startup'da chaqiriladi.
        
        Returns:
            int: Yuklangan chunk'lar soni
        """
        if not self.knowledge_dir.exists():
            logger.error(f"❌ Knowledge papkasi topilmadi: {self.knowledge_dir}")
            return 0
        
        self.chunks = []
        md_files = list(self.knowledge_dir.glob("*.md"))
        
        if not md_files:
            logger.warning(f"⚠️ Knowledge papkasida .md fayllar yo'q")
            return 0
        
        for md_file in md_files:
            try:
                file_chunks = self._process_file(md_file)
                self.chunks.extend(file_chunks)
                logger.info(f"  ✅ {md_file.name}: {len(file_chunks)} ta chunk")
            except Exception as e:
                logger.error(f"  ❌ {md_file.name} yuklashda xato: {e}")
        
        logger.info(f"📚 Jami {len(self.chunks)} ta chunk yuklandi")
        return len(self.chunks)
    
    def _process_file(self, file_path: Path) -> List[Dict]:
        """
        Bitta .md faylni o'qiydi va chunk'larga bo'ladi
        
        Args:
            file_path: .md fayl yo'li
            
        Returns:
            List[Dict]: Chunk'lar ro'yxati
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Frontmatter (--- ... ---) ajratish
        metadata, body = self._parse_frontmatter(content)
        
        # Body'ni chunk'larga bo'lish
        raw_chunks = self._split_into_chunks(body)
        
        # Har bir chunk uchun dict yaratish
        chunks = []
        for i, chunk_text in enumerate(raw_chunks):
            if len(chunk_text.strip()) < 50:  # Juda kichik chunk'larni tashlab yuboramiz
                continue
            
            chunks.append({
                "id": f"{file_path.stem}_{i}",
                "file": file_path.stem,
                "category": metadata.get("category", "general"),
                "tags": metadata.get("tags", []),
                "content": chunk_text.strip(),
                "embedding": None  # Keyin hisoblanadi
            })
        
        return chunks
    
    def _parse_frontmatter(self, content: str) -> tuple[Dict, str]:
        """
        YAML frontmatter ajratadi
        
        Misol:
        ---
        category: about
        tags: [myestro, platforma]
        ---
        # Asosiy kontent...
        
        Returns:
            tuple: (metadata_dict, body_text)
        """
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1]) or {}
                    body = parts[2].strip()
                    return metadata, body
                except yaml.YAMLError as e:
                    logger.warning(f"Frontmatter parse xatosi: {e}")
        
        return {}, content
    
    def _split_into_chunks(self, text: str) -> List[str]:
        """
        Matnni mantiqiy bo'laklarga bo'ladi (paragraf asosida)
        
        Strategiya:
        1. Avval paragraflarga bo'lamiz (\n\n)
        2. Har bir paragrafni chunk_size ichiga joylashtirishga harakat qilamiz
        3. Agar paragraf juda katta bo'lsa, gap'larga bo'lib qayta yig'amiz
        """
        # Paragraflarga bo'lish
        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Agar joriy chunk + yangi paragraf limitdan oshsa
            if len(current_chunk) + len(para) + 2 > self.chunk_size:
                # Joriy chunk'ni saqlash
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # Agar paragrafning o'zi limitdan katta bo'lsa
                if len(para) > self.chunk_size:
                    sub_chunks = self._split_paragraph(para)
                    chunks.extend(sub_chunks[:-1])  # Oxirgisidan tashqari barchasi
                    current_chunk = sub_chunks[-1] if sub_chunks else ""
                else:
                    current_chunk = para
            else:
                # Joriy chunk'ga qo'shish
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para
        
        # Oxirgi chunk'ni saqlash
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_paragraph(self, paragraph: str) -> List[str]:
        """
        Katta paragrafni gap'larga bo'lib qayta yig'adi
        """
        # Gap'larga bo'lish (. ! ?)
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        
        chunks = []
        current = ""
        
        for sentence in sentences:
            if len(current) + len(sentence) + 1 > self.chunk_size:
                if current:
                    chunks.append(current.strip())
                current = sentence
            else:
                current = current + " " + sentence if current else sentence
        
        if current:
            chunks.append(current.strip())
        
        return chunks
    
    # ─────────────────────────────────────────────────────────
    # 2. EMBEDDING HISOBLOV
    # ─────────────────────────────────────────────────────────
    
    async def _get_embedding(self, text: str) -> List[float]:
        """
        Matn uchun embedding oladi (OpenRouter orqali)
        
        Cache ishlatadi — bir xil matn uchun qayta API chaqirmaydi.
        
        Args:
            text: Embedding hisoblanadigan matn
            
        Returns:
            List[float]: 1536 o'lchamli embedding vektori
        """
        # Cache kaliti — birinchi 200 belgi (tezlik uchun)
        cache_key = text[:200].strip()
        
        if cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.embedding_model,
                        "input": text,
                        "encoding_format": "float"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Embedding API xatosi: {response.status_code} - {response.text}")
                    raise Exception(f"Embedding API error: {response.status_code}")
                
                data = response.json()
                embedding = data["data"][0]["embedding"]
                
                # Cache'ga saqlash
                self._embedding_cache[cache_key] = embedding
                
                return embedding
                
        except httpx.TimeoutException:
            logger.error("Embedding API timeout")
            raise
        except Exception as e:
            logger.error(f"Embedding xatosi: {e}")
            raise
    
    async def initialize_embeddings(self) -> int:
        """
        Barcha chunk'lar uchun embedding hisoblaydi.
        Startup'da chaqiriladi (bir marta).
        
        Returns:
            int: Hisoblangan embedding'lar soni
        """
        if self._initialized:
            logger.info("⚠️ RAG allaqachon ishga tushirilgan")
            return len(self.chunks)
        
        if not self.chunks:
            logger.warning("⚠️ Chunk'lar yo'q, avval load_knowledge() chaqiring")
            return 0
        
        logger.info(f"🔄 {len(self.chunks)} ta chunk uchun embedding hisoblanmoqda...")
        
        count = 0
        for chunk in self.chunks:
            if chunk["embedding"] is None:
                try:
                    chunk["embedding"] = await self._get_embedding(chunk["content"])
                    count += 1
                    
                    # Rate limit uchun kichik pauza (har 10 tadan keyin)
                    if count % 10 == 0:
                        import asyncio
                        await asyncio.sleep(0.5)
                        logger.info(f"  📊 {count}/{len(self.chunks)} embedding tayyor")
                        
                except Exception as e:
                    logger.error(f"  ❌ Chunk {chunk['id']} embedding xatosi: {e}")
        
        self._initialized = True
        logger.info(f"✅ {count} ta embedding hisoblandi. RAG tayyor!")
        return count
    
    # ─────────────────────────────────────────────────────────
    # 3. QIDIRUV (VECTOR SEARCH)
    # ─────────────────────────────────────────────────────────
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """
        Ikki vektor orasidagi cosine similarity
        
        Formula: cos(θ) = (A · B) / (||A|| × ||B||)
        
        Returns:
            float: 0 dan 1 gacha (1 = bir xil)
        """
        if len(a) != len(b):
            return 0.0
        
        # Dot product
        dot_product = sum(x * y for x, y in zip(a, b))
        
        # Normlar
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    async def search(self, query: str, top_k: Optional[int] = None) -> List[Dict]:
        """
        Savolga eng o'xshash chunk'larni qidiradi
        
        Args:
            query: Foydalanuvchi savoli
            top_k: Qancha chunk qaytarish (default: self.top_k)
            
        Returns:
            List[Dict]: Eng o'xshash chunk'lar (score bilan)
        """
        if not self._initialized:
            logger.warning("⚠️ RAG ishga tushirilmagan, bo'sh natija")
            return []
        
        if top_k is None:
            top_k = self.top_k
        
        # 1. Savol uchun embedding olish
        try:
            query_embedding = await self._get_embedding(query)
        except Exception as e:
            logger.error(f"Query embedding xatosi: {e}")
            return []
        
        # 2. Barcha chunk'lar bilan similarity hisoblash
        scored_chunks = []
        for chunk in self.chunks:
            if chunk["embedding"] is None:
                continue
            
            score = self._cosine_similarity(query_embedding, chunk["embedding"])
            
            # Minimal score'dan past bo'lsa tashlab yuboramiz
            if score >= self.min_score:
                scored_chunks.append({
                    "id": chunk["id"],
                    "file": chunk["file"],
                    "category": chunk["category"],
                    "tags": chunk["tags"],
                    "content": chunk["content"],
                    "score": score
                })
        
        # 3. Score bo'yicha tartiblash
        scored_chunks.sort(key=lambda x: x["score"], reverse=True)
        
        # 4. Top K qaytarish
        result = scored_chunks[:top_k]
        
        logger.debug(
            f"🔍 Qidiruv: '{query[:50]}...' → {len(result)} ta natija "
            f"(eng yaxshi: {result[0]['score']:.3f})" if result else "🔍 Natija yo'q"
        )
        
        return result
    
    # ─────────────────────────────────────────────────────────
    # 4. CONTEXT YARATISH (AI PROMPT UCHUN)
    # ─────────────────────────────────────────────────────────
    
    async def build_context(self, query: str, top_k: Optional[int] = None) -> str:
        """
        Savol uchun AI promptiga qo'shiladigan context yaratadi
        
        Args:
            query: Foydalanuvchi savoli
            top_k: Qancha chunk olish
            
        Returns:
            str: Formatlangan context matn (bo'sh bo'lishi ham mumkin)
        """
        chunks = await self.search(query, top_k)
        
        if not chunks:
            return ""
        
        # Context formatlash
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            score_percent = int(chunk["score"] * 100)
            context_parts.append(
                f"[Ma'lumot #{i} — {chunk['category']} | ishonch: {score_percent}%]\n"
                f"{chunk['content']}"
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    async def build_context_with_metadata(self, query: str, top_k: Optional[int] = None) -> Dict:
        """
        Context + qo'shimcha metadata qaytaradi (debug uchun)
        
        Returns:
            Dict: {
                "context": str,
                "chunks": List[Dict],
                "total_chunks": int,
                "query": str
            }
        """
        chunks = await self.search(query, top_k)
        context = self._format_chunks_to_context(chunks)
        
        return {
            "context": context,
            "chunks": chunks,
            "total_chunks": len(chunks),
            "query": query
        }
    
    def _format_chunks_to_context(self, chunks: List[Dict]) -> str:
        """Chunk'larni context matnga aylantiradi"""
        if not chunks:
            return ""
        
        parts = []
        for i, chunk in enumerate(chunks, 1):
            parts.append(
                f"[Ma'lumot #{i} — {chunk['category']}]\n{chunk['content']}"
            )
        
        return "\n\n---\n\n".join(parts)
    
    # ─────────────────────────────────────────────────────────
    # 5. YORDAMCHI METODLAR
    # ─────────────────────────────────────────────────────────
    
    def get_stats(self) -> Dict:
        """RAG holati haqida statistika"""
        return {
            "initialized": self._initialized,
            "total_chunks": len(self.chunks),
            "chunks_with_embeddings": sum(1 for c in self.chunks if c["embedding"]),
            "cache_size": len(self._embedding_cache),
            "categories": list(set(c["category"] for c in self.chunks)),
            "files": list(set(c["file"] for c in self.chunks))
        }
    
    def reload(self) -> int:
        """
        Knowledge base'ni qayta yuklaydi (embedding'lar saqlanib qoladi)
        
        Returns:
            int: Yangi chunk'lar soni
        """
        logger.info("🔄 RAG qayta yuklanmoqda...")
        old_count = len(self.chunks)
        
        # Eski chunk'larning embedding'larini saqlab qolish
        old_embeddings = {
            c["id"]: c["embedding"] 
            for c in self.chunks 
            if c["embedding"]
        }
        
        # Qayta yuklash
        self.load_knowledge()
        
        # Eski embedding'larni qaytarish (agar chunk o'zgarmagan bo'lsa)
        for chunk in self.chunks:
            if chunk["id"] in old_embeddings:
                chunk["embedding"] = old_embeddings[chunk["id"]]
        
        new_count = len(self.chunks)
        logger.info(f"✅ RAG qayta yuklandi: {old_count} → {new_count} chunk")
        
        return new_count
    
    async def reload_full(self) -> int:
        """
        To'liq qayta yuklash (embedding'lar bilan)
        """
        logger.info("🔄 RAG to'liq qayta yuklanmoqda...")
        self._embedding_cache.clear()
        self._initialized = False
        
        self.load_knowledge()
        count = await self.initialize_embeddings()
        
        logger.info(f"✅ RAG to'liq qayta yuklandi: {count} embedding")
        return count


# ─────────────────────────────────────────────────────────
# SINGLETON (butun bot uchun bitta instance)
# ─────────────────────────────────────────────────────────

rag_client = RAGClient()