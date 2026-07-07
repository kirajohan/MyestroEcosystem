import os
from typing import Optional
from app.config import settings

KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "knowledge_base")


def load_markdown_file(file_path: str) -> str:
    """Read .md file content from disk."""
    full_path = os.path.join(KNOWLEDGE_BASE_PATH, file_path)
    if not os.path.exists(full_path):
        return ""
    with open(full_path, "r", encoding="utf-8") as f:
        return f.read()


def load_knowledge_for_level(cefr_level: str) -> str:
    """Load all .md files for a given CEFR level."""
    content_parts = []

    # Grammar
    grammar_path = os.path.join(KNOWLEDGE_BASE_PATH, "grammar", f"{cefr_level}_basic.md")
    if os.path.exists(grammar_path):
        with open(grammar_path, "r", encoding="utf-8") as f:
            content_parts.append(f"=== Grammar ({cefr_level}) ===\n{f.read()}")

    # Vocabulary
    vocab_path = os.path.join(KNOWLEDGE_BASE_PATH, "vocabulary", f"{cefr_level}_words.md")
    if os.path.exists(vocab_path):
        with open(vocab_path, "r", encoding="utf-8") as f:
            content_parts.append(f"=== Vocabulary ({cefr_level}) ===\n{f.read()}")

    return "\n\n".join(content_parts)


def search_knowledge(query: str, category: Optional[str] = None) -> str:
    """Simple search across knowledge base files."""
    results = []
    search_dir = os.path.join(KNOWLEDGE_BASE_PATH, category) if category else KNOWLEDGE_BASE_PATH

    if not os.path.exists(search_dir):
        return ""

    for root, dirs, files in os.walk(search_dir):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        results.append(f"--- {os.path.relpath(filepath, KNOWLEDGE_BASE_PATH)} ---\n{content[:500]}...")

    return "\n\n".join(results[:5])