
import json
import sys
from pathlib import Path

import chromadb

# Nhận đường dẫn thư mục chroma_db của Day 06
db_path = Path(sys.argv[1])

client = chromadb.PersistentClient(path=str(db_path))
collection = client.get_collection("lab06_a")

# Lấy toàn bộ chunks đã lưu
data = collection.get(include=["documents", "metadatas"])

chunks = []

for chunk_id, text, meta in zip(
    data["ids"], data["documents"], data["metadatas"]
):
    chunks.append({
        "id": chunk_id,
        "source_id": meta["document_id"],
        "source": meta["source"],
        "page": meta["page"],
        "text": text,
        "metadata": meta
    })

# Lưu theo định dạng Day 07
output = Path("data/day6_chunks.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(
    json.dumps(chunks, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print(f"Exported {len(chunks)} chunks to {output}")
