"""Day 07: OpenStax Agentic RAG demo.

Place in starter/app.py and run from the repository root:
    python -m streamlit run starter/app.py

Uses the existing starter/agentic.py, baseline.py, dense.py and adapters.py.
No benchmark gold or expected answers are read or sent to the model.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from agentic import run_agent
from adapters import HybridRetriever, OpenAIController
from baseline import TfidfIndex, pack_context
from dense import DenseIndex, DIMENSIONS, MODEL

load_dotenv()
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHUNKS = str(ROOT / "data" / "day6_chunks.json")
DEFAULT_DB = os.getenv(
    "CHROMA_DB_PATH",
    r"C:\Ngay05\K5-L3A-DAY06-2A202603587-BuiNguyenDung-DataIngestionEngineering\starter\chroma_db",
)

st.set_page_config(page_title="Day 07 · Agentic RAG", page_icon="📚", layout="wide")


@st.cache_data(show_spinner=False)
def load_chunks(path: str, modified: float) -> list[dict]:
    del modified  # Included in cache key so edits invalidate the cache.
    chunks = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(chunks, list) or not chunks:
        raise ValueError("Chunk JSON phải là danh sách không rỗng")
    if len({c["id"] for c in chunks}) != len(chunks):
        raise ValueError("Có chunk ID bị trùng")
    return chunks


@st.cache_resource(show_spinner=False)
def make_tfidf(path: str, modified: float):
    return TfidfIndex(load_chunks(path, modified))


@st.cache_resource(show_spinner=False)
def openai_client():
    from openai import OpenAI
    return OpenAI()


@st.cache_resource(show_spinner=False)
def chroma_collection(db_path: str):
    import chromadb
    return chromadb.PersistentClient(path=db_path).get_collection("lab06_a")


class TfidfRetriever:
    """An adapter matching the agentic.Retriever interface, with optional metadata filters."""
    def __init__(self, index: TfidfIndex):
        self.index = index
        self.embedding_tokens = 0

    def search(self, query: str, *, filters=None, top_k=3):
        results = self.index.search(query, top_k=len(self.index.chunks))
        if filters:
            results = [c for c in results if all(c["metadata"].get(k) == v for k, v in filters.items())]
        return results[:top_k]


class DenseRetriever:
    """Reuses the existing Chroma vectors; only the query gets embedded."""
    def __init__(self, chunks, collection, client):
        self.index = DenseIndex(chunks, collection, client)
        self.embedding_tokens = 0

    def search(self, query: str, *, filters=None, top_k=3):
        if not filters:
            results = self.index.search(query, top_k=top_k)
            self.embedding_tokens = self.index.embedding_tokens
            return results

        # DenseIndex.search has no metadata-filter parameter; query Chroma directly.
        response = self.index.openai_client.embeddings.create(model=MODEL, input=query)
        vector = response.data[0].embedding
        if len(vector) != DIMENSIONS:
            raise ValueError("Query embedding không khớp 1536 chiều")
        self.embedding_tokens += getattr(getattr(response, "usage", None), "total_tokens", 0) or 0
        where = filters if len(filters) == 1 else {"$and": [{k: v} for k, v in filters.items()]}
        found = self.index.collection.query(
            query_embeddings=[vector], n_results=top_k, where=where, include=["distances"]
        )
        return [
            {**self.index.chunk_map[cid], "score": -float(dist), "strategy": "dense"}
            for cid, dist in zip(found["ids"][0], found["distances"][0])
        ]


def build_retriever(technique: str, chunks, chunk_path: str, modified: float, db_path: str, client):
    if technique == "TF-IDF":
        return TfidfRetriever(make_tfidf(chunk_path, modified))
    collection = chroma_collection(db_path)
    if technique == "Dense":
        return DenseRetriever(chunks, collection, client)
    if technique == "Hybrid RRF":
        return HybridRetriever(chunks, collection, client, candidates=10, rrf_k=60)
    raise ValueError(f"Unknown retrieval technique: {technique}")


def search_without_llm(query: str, retriever, *, top_k: int, budget: int):
    started = time.perf_counter()
    results = retriever.search(query, filters=None, top_k=top_k)
    context, context_ids = pack_context(results, budget=budget)
    elapsed = time.perf_counter() - started
    return {
        "status": "retrieval_only",
        "answer": "Chế độ chỉ retrieval: chưa gọi chat model. Xem các chunk bên dưới.",
        "citations": context_ids,
        "events": [{"event": "search", "query": query, "results": results,
                    "context": context, "context_ids": context_ids}],
        "elapsed_seconds": elapsed,
    }


def render_turn(turn: dict):
    with st.chat_message("user"):
        st.markdown(turn["question"])
    with st.chat_message("assistant"):
        st.markdown(turn["answer"])
        if turn["status"] == "abstain":
            event_types = [event.get("event") for event in turn["events"]]
            if "search_limit" in event_types:
                st.warning("Agent từ chối vì đã đạt giới hạn số lần tìm kiếm. Điều này KHÔNG có nghĩa tài liệu chắc chắn thiếu bằng chứng.")
            elif "invalid_or_missing_citations" in event_types:
                st.warning("Agent đã tạo kết quả nhưng không có citation hợp lệ. Cần kiểm tra định dạng citation trong Controller.")
            else:
                st.info("Agent từ chối; kiểm tra retrieval trace trước khi kết luận thiếu bằng chứng.")
        elif turn["status"] == "retrieval_only":
            st.caption("Chỉ tìm kiếm tài liệu, không gọi chat model.")

        a, b, c, d = st.columns(4)
        a.metric("Thời gian", f"{turn['elapsed_seconds']:.2f} giây")
        b.metric("Chat tokens", f"{turn['chat_in'] + turn['chat_out']:,}")
        c.metric("Embedding tokens", f"{turn['embed_tokens']:,}")
        d.metric("Search calls", str(turn["search_calls"]))
        st.caption(
            f"Technique: **{turn['technique']}** · Model: `{turn['model']}` · "
            f"Chat input/output: {turn['chat_in']} / {turn['chat_out']} tokens · "
            "API cost: chưa tính (token usage đo thực tế)"
        )

        with st.expander(f"Citations ({len(turn['citations'])})", expanded=True):
            if not turn["citations"]:
                st.write("Chưa có citation hợp lệ.")
            for cid in turn["citations"]:
                evidence = turn["evidence"].get(cid)
                st.code(f"[{cid}]", language=None)
                if evidence:
                    st.caption(f"Trang PDF: {evidence['page']} · Nguồn: {evidence['source']}")
                    st.write(evidence["text"])
                else:
                    st.warning("Không có chunk tương ứng trong context đã gửi cho model.")

        # Retrieved evidence is NOT automatically a valid answer citation.
        retrieved = {}
        for event in turn["events"]:
            if event.get("event") == "search":
                for chunk in event.get("results", []):
                    if chunk["id"] in event.get("context_ids", []):
                        retrieved[chunk["id"]] = chunk
        if turn["status"] == "abstain" and retrieved:
            with st.expander(f"Nguồn đã đưa vào context ({len(retrieved)}) — chưa phải citation hợp lệ", expanded=True):
                for cid, chunk in retrieved.items():
                    st.markdown(f"**{cid}** · trang {chunk['page']}")
                    st.caption(chunk["source"])
                    st.write(chunk["text"])

        with st.expander("Retrieval trace · chunks và thứ hạng", expanded=False):
            for index, event in enumerate(turn["events"], 1):
                if event.get("event") != "search":
                    st.write(f"Event {index}: `{event.get('event')}`")
                    continue
                st.markdown(f"**Search {index}:** `{event.get('query', '')}`")
                st.caption("IDs thực sự được đưa vào context: " + ", ".join(event.get("context_ids", [])))
                for rank, chunk in enumerate(event.get("results", []), 1):
                    st.markdown(
                        f"{rank}. **{chunk['id']}** · trang {chunk['page']} · "
                        f"score {chunk.get('score', 0):.5f}"
                    )
                    with st.expander(f"Nội dung chunk {rank}: {chunk['id']}"):
                        st.text(chunk["text"])


def main():
    st.title("📚 Day 07 · Agentic RAG")
    st.caption("OpenStax Python · ChromaDB Day 06 · TF-IDF / Dense / Hybrid RRF")

    with st.sidebar:
        st.header("Cấu hình")
        technique = st.selectbox("Retrieval technique", ["Hybrid RRF", "Dense", "TF-IDF"])
        mode = st.radio("Chế độ", ["Agent trả lời + citations", "Chỉ retrieval (không gọi chat model)"])
        model = st.text_input("Chat model", value=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"))
        chunks_path = st.text_input("Chunks JSON", value=DEFAULT_CHUNKS)
        db_path = st.text_input("ChromaDB Day 06", value=DEFAULT_DB)
        st.caption("Cấu hình Hybrid B: candidates=10 mỗi phương pháp, RRF k=60, top_k=3, budget=1600 ký tự")
        max_searches = st.slider("Số lượt search tối đa của Agent", min_value=1, max_value=4, value=2,
                                 help="Tăng lượt tìm kiếm có thể tăng chi phí và thời gian, không đảm bảo cải thiện kết quả.")
        st.caption("Không nhập API key vào giao diện. Đặt OPENAI_API_KEY trong .env tại thư mục gốc repo.")
        if st.button("Xóa lịch sử giao diện", use_container_width=True):
            st.session_state["turns"] = []
            st.rerun()

    st.session_state.setdefault("turns", [])
    st.info("Mỗi câu hỏi được xử lý độc lập; lịch sử hiển thị không được gửi vào model. Không gửi dữ liệu mật vào corpus hoặc câu hỏi.")
    for turn in st.session_state["turns"]:
        render_turn(turn)

    question = st.chat_input("Hỏi về nội dung chương 1–2 Python, ví dụ: What does input() do?")
    if not question:
        return

    try:
        path = Path(chunks_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Không tìm thấy chunks JSON: {path}")
        modified = path.stat().st_mtime
        chunks = load_chunks(str(path), modified)
        needs_api = technique != "TF-IDF" or mode.startswith("Agent")
        if needs_api and not os.getenv("OPENAI_API_KEY"):
            raise ValueError("Thiếu OPENAI_API_KEY trong .env")
        if technique != "TF-IDF" and not Path(db_path).is_dir():
            raise FileNotFoundError(f"Không tìm thấy ChromaDB: {db_path}")

        client = openai_client() if needs_api else None
        with st.spinner("Đang truy xuất và xử lý câu hỏi..."):
            retriever = build_retriever(technique, chunks, str(path), modified, db_path, client)
            controller = OpenAIController(client, model=model) if mode.startswith("Agent") else None
            start = time.perf_counter()
            if controller is not None:
                outcome = run_agent(
                    question, controller, retriever, filters=None,
                    max_searches=max_searches, top_k=3, budget=1600,
                )
                outcome["elapsed_seconds"] = time.perf_counter() - start
            else:
                outcome = search_without_llm(question, retriever, top_k=3, budget=1600)

        evidence = {}
        for event in outcome["events"]:
            if event.get("event") == "search":
                context_ids = set(event.get("context_ids", []))
                for chunk in event.get("results", []):
                    if chunk["id"] in context_ids:
                        evidence[chunk["id"]] = chunk
        record = {
            "question": question,
            "technique": technique,
            "model": model if controller is not None else "No chat model",
            "answer": outcome["answer"],
            "status": outcome["status"],
            "citations": outcome["citations"],
            "events": outcome["events"],
            "elapsed_seconds": outcome["elapsed_seconds"],
            "search_calls": sum(e.get("event") == "search" for e in outcome["events"]),
            "chat_in": controller.input_tokens if controller else 0,
            "chat_out": controller.output_tokens if controller else 0,
            "embed_tokens": retriever.embedding_tokens,
            "evidence": evidence,
        }
        st.session_state["turns"].append(record)
        st.rerun()
    except Exception as exc:
        st.error(f"Không thể xử lý câu hỏi: {type(exc).__name__}: {exc}")
        st.caption("Kiểm tra đường dẫn, API key trong .env, ChromaDB và model hỗ trợ tool calling.")


if __name__ == "__main__":
    main()
