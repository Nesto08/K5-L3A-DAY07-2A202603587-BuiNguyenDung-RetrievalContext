"""Day 07 Dense Retrieval: reuse Day 06 Chroma vectors and embed queries only.

Run from the repository root with ``python starter/dense.py ...``.
Gold labels are used only after retrieval, for evaluation.
"""
import argparse
import json
import os
import statistics
import time
from pathlib import Path

from baseline import hit, pack_context, validate

MODEL = "text-embedding-3-small"
DIMENSIONS = 1536
COLLECTION = "lab06_a"
TOP_K = 3
CONTEXT_BUDGET = 800


class DenseIndex:
    """Adapter over an existing Day 06 Chroma collection."""

    def __init__(self, chunks, collection, openai_client):
        self.chunk_map = {c["id"]: c for c in chunks}
        self.collection = collection
        self.openai_client = openai_client
        self.embedding_tokens = 0

        if collection.count() != len(chunks):
            raise ValueError("Số chunk của ChromaDB và JSON không khớp")
        stored_ids = set(collection.get(include=[])["ids"])
        if stored_ids != set(self.chunk_map):
            raise ValueError("Chunk ID của ChromaDB và JSON không khớp")

    def search(self, question, top_k=TOP_K):
        # NEVER include benchmark gold/expected_answer in this request.
        response = self.openai_client.embeddings.create(model=MODEL, input=question)
        vector = response.data[0].embedding
        if len(vector) != DIMENSIONS:
            raise ValueError(f"Query embedding phải có {DIMENSIONS} chiều")
        if response.usage:
            self.embedding_tokens += response.usage.total_tokens

        matches = self.collection.query(
            query_embeddings=[vector],
            n_results=top_k,
            include=["distances"],
        )
        ids = matches["ids"][0]
        distances = matches["distances"][0]
        # A smaller Chroma distance is better. Negative distance preserves ranking
        # without assuming the collection uses cosine rather than L2/IP.
        return [
            {**self.chunk_map[cid], "score": -float(dist), "strategy": "dense"}
            for cid, dist in zip(ids, distances)
        ]


def evaluate_dense(index, questions):
    traces = []
    for q in questions:
        start = time.perf_counter()
        results = index.search(q["question"], top_k=TOP_K)
        context, context_ids = pack_context(results, budget=CONTEXT_BUDGET)
        elapsed_ms = (time.perf_counter() - start) * 1000
        marked = [{**c, "hit": hit(c, q["gold"])} for c in results]
        traces.append({
            "query_id": q["id"],
            "split": q["split"],
            "question": q["question"],
            "strategy": "dense",
            "top_k": TOP_K,
            "budget_chars": CONTEXT_BUDGET,
            "gold": q["gold"],
            "results": marked,
            "context": context,
            "context_ids": context_ids,
            "context_chars": len(context),
            "elapsed_ms": elapsed_ms,
            "hit1": bool(marked and marked[0]["hit"]),
            "hit3": any(c["hit"] for c in marked),
            "context_hit": any(c["hit"] and c["id"] in context_ids for c in marked),
        })
    return traces


def main():
    parser = argparse.ArgumentParser(description="Dense retrieval sử dụng ChromaDB Day 06")
    parser.add_argument("--chunks", required=True, type=Path)
    parser.add_argument("--questions", required=True, type=Path)
    parser.add_argument("--split", choices=("dev", "test"), required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--db", required=True, type=Path, help="Đường dẫn chroma_db của Day 06")
    args = parser.parse_args()

    from dotenv import load_dotenv
    import chromadb
    from openai import OpenAI

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Thiếu OPENAI_API_KEY trong .env")
    if not args.db.is_dir():
        raise FileNotFoundError(f"Không tìm thấy ChromaDB: {args.db}")

    chunks = json.loads(args.chunks.read_text(encoding="utf-8"))
    all_questions = json.loads(args.questions.read_text(encoding="utf-8"))
    questions = [q for q in all_questions if q.get("split") == args.split]
    validate(chunks, questions)

    collection = chromadb.PersistentClient(path=str(args.db)).get_collection(COLLECTION)
    index = DenseIndex(chunks, collection, OpenAI())
    traces = evaluate_dense(index, questions)

    summary = {
        "strategy": "dense",
        "split": args.split,
        "n": len(traces),
        "hit1": sum(t["hit1"] for t in traces),
        "hit3": sum(t["hit3"] for t in traces),
        "context_hit": sum(t["context_hit"] for t in traces),
        "avg_context_chars": statistics.mean(t["context_chars"] for t in traces),
        "median_ms": statistics.median(t["elapsed_ms"] for t in traces),
        "embedding_model": MODEL,
        "embedding_dimensions": DIMENSIONS,
        "query_embedding_tokens": index.embedding_tokens,
        "service_cost_usd": None,  # Fill in using documented API rates for the run date.
    }
    args.output.mkdir(parents=True, exist_ok=True)
    for name, data in (("summary.json", summary), ("traces.json", traces)):
        (args.output / name).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
