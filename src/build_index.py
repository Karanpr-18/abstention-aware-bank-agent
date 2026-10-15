"""
Build ChromaDB index from kb_raw/*.md
Chunk 200-400 tokens (~1200 chars), MiniLM-L6-v2 embeddings.
Run: .venv/bin/python src/build_index.py
"""
import os
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

KB_RAW = Path("./kb_raw")
CHROMA_DIR = os.environ.get("CHROMA_DIR", "./chroma_db")
CHUNK = 1000
OVERLAP = 200

def chunks(text: str):
    for i in range(0, len(text), CHUNK - OVERLAP):
        c = text[i:i+CHUNK].strip()
        if len(c) > 200:
            yield c

def main():
    files = sorted(KB_RAW.glob("*.md"))
    assert files, "kb_raw empty — run scrape_kb.py first (plus manual downloads)"
    print(f"Embedding {len(files)} files with all-MiniLM-L6-v2 ...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    col = client.get_or_create_collection("bank_kb", metadata={"hnsw:space": "cosine"})
    # fresh rebuild
    try:
        client.delete_collection("bank_kb")
        col = client.create_collection("bank_kb", metadata={"hnsw:space": "cosine"})
    except Exception:
        pass
    n = 0
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        # country_bank prefix from filename
        parts = f.stem.split("_")
        meta_base = {"source_file": f.name}
        for i, ch in enumerate(chunks(text)):
            emb = model.encode(ch).tolist()
            col.add(ids=[f"{f.stem}__{i}"], documents=[ch], embeddings=[emb],
                    metadatas=[{**meta_base, "chunk": i}])
            n += 1
    print(f"Indexed {n} chunks from {len(files)} files -> {CHROMA_DIR}")

if __name__ == "__main__":
    main()
