"""Day 07 Hybrid Retrieval: TF-IDF + Day 06 Chroma Dense via RRF.

Run from repo root: python starter/hybrid.py --chunks ... --questions ...
Gold labels are used only for evaluation after the search.
"""
import argparse
import json
import os
import statistics
import time
from pathlib import Path

from baseline import TfidfIndex, hit, pack_context, validate
from dense import COLLECTION, DIMENSIONS, MODEL, DenseIndex

TOP_K = 3
CANDIDATES = 10
RRF_K = 60
CONTEXT_BUDGET = 1600


def fuse_rrf(tfidf_results, dense_results, top_k=TOP_K, k=RRF_K):
    """Combine two ranked chunk lists. Each method has equal RRF weight."""
    scores = {}
    chunks_by_id = {}
    for ranked in (tfidf_results, dense_results):
        seen = set()
        for rank, chunk in enumerate(ranked, start=1):
            cid = chunk["id"]
            if cid in seen:
                continue
            seen.add(cid)
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
            chunks_by_id.setdefault(cid, chunk)
    ordered_ids = sorted(scores, key=lambda cid: (-scores[cid], cid))[:top_k]
    return [
        {**chunks_by_id[cid], "score": scores[cid], "strategy": "hybrid"}
        for cid in ordered_ids
    ]


def evaluate_hybrid(tfidf_index, dense_index, questions):
    traces = []
    for q in questions:
        start = time.perf_counter()
        # Only the question enters retrieval. Gold is not sent to either retriever.
        tfidf_results = tfidf_index.search(q["question"], top_k=CANDIDATES)
        dense_results = dense_index.search(q["question"], top_k=CANDIDATES)
        results = fuse_rrf(tfidf_results, dense_results)
        context, ids = pack_context(results, budget=CONTEXT_BUDGET)
        elapsed_ms = (time.perf_counter() - start) * 1000
        marked = [{**c, "hit": hit(c, q["gold"])} for c in results]
        traces.append({
            "query_id": q["id"],
            "split": q["split"],
            "question": q["question"],
            "strategy": "hybrid_rrf",
            "top_k": TOP_K,
            "candidate_k_per_method": CANDIDATES,
            "rrf_k": RRF_K,
            "budget_chars": CONTEXT_BUDGET,
            "gold": q["gold"],
            "results": marked,
            "context": context,
            "context_ids": ids,
            "context_chars": len(context),
            "elapsed_ms": elapsed_ms,
            "hit1": bool(marked and marked[0]["hit"]),
            "hit3": any(c["hit"] for c in marked),
            "context_hit": any(c["hit"] and c["id"] in ids for c in marked),
        })
    return traces


def main():
    parser = argparse.ArgumentParser(description="Hybrid retrieval TF-IDF + Dense ChromaDB with RRF")
    parser.add_argument("--chunks", required=True, type=Path)
    parser.add_argument("--questions", required=True, type=Path)
    parser.add_argument("--split", required=True, choices=("dev", "test"))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--db", required=True, type=Path)
    args = parser.parse_args()

    from dotenv import load_dotenv
    from openai import OpenAI
    import chromadb

    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Thiếu OPENAI_API_KEY trong .env")
    if not args.db.is_dir():
        raise FileNotFoundError(f"Không tìm thấy ChromaDB: {args.db}")

    chunks = json.loads(args.chunks.read_text(encoding="utf-8"))
    all_questions = json.loads(args.questions.read_text(encoding="utf-8"))
    questions = [q for q in all_questions if q.get("split") == args.split]
    validate(chunks, questions)

    tfidf_start = time.perf_counter()
    tfidf_index = TfidfIndex(chunks)
    index_seconds = time.perf_counter() - tfidf_start
    collection = chromadb.PersistentClient(path=str(args.db)).get_collection(COLLECTION)
    dense_index = DenseIndex(chunks, collection, OpenAI())
    traces = evaluate_hybrid(tfidf_index, dense_index, questions)

    summary = {
        "strategy": "hybrid_rrf",
        "split": args.split,
        "n": len(traces),
        "hit1": sum(t["hit1"] for t in traces),
        "hit3": sum(t["hit3"] for t in traces),
        "context_hit": sum(t["context_hit"] for t in traces),
        "avg_context_chars": statistics.mean(t["context_chars"] for t in traces),
        "median_ms": statistics.median(t["elapsed_ms"] for t in traces),
        "index_seconds": index_seconds,
        "top_k": TOP_K,
        "candidate_k_per_method": CANDIDATES,
        "rrf_k": RRF_K,
        "embedding_model": MODEL,
        "embedding_dimensions": DIMENSIONS,
        "query_embedding_tokens": dense_index.embedding_tokens,
        "service_cost_usd": None,
    }
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, data in (("summary.json", summary), ("traces.json", traces)):
        (args.output / filename).write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
