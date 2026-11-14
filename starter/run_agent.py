"""Run the actual Day 07 agent on dev (including unanswerable questions).

Run from repository root: python starter/run_agent.py --chunks ... --questions ...
"""
import argparse
import json
import os
import time
from pathlib import Path

from agentic import run_agent
from adapters import HybridRetriever, OpenAIController


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chunks', required=True, type=Path)
    parser.add_argument('--questions', required=True, type=Path)
    parser.add_argument('--split', choices=['dev', 'test'], required=True)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--db', required=True, type=Path)
    parser.add_argument('--model', default=None)
    parser.add_argument('--limit', type=int, default=0, help='Run first N cases for a smoke test; 0 means all')
    args = parser.parse_args()

    from dotenv import load_dotenv
    from openai import OpenAI
    import chromadb

    load_dotenv()
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError('Missing OPENAI_API_KEY (check .env)')
    if not args.db.is_dir():
        raise FileNotFoundError(args.db)
    chunks = json.loads(args.chunks.read_text(encoding='utf-8'))
    cases = [q for q in json.loads(args.questions.read_text(encoding='utf-8'))
             if q.get('split') == args.split]
    if args.limit:
        cases = cases[:args.limit]
    if not cases:
        raise ValueError('No benchmark cases selected')

    client = OpenAI()
    model_name = args.model or os.getenv('OPENAI_CHAT_MODEL', 'gpt-4o-mini')
    collection = chromadb.PersistentClient(path=str(args.db)).get_collection('lab06_a')
    retriever = HybridRetriever(chunks, collection, client, candidates=10, rrf_k=60)
    controller = OpenAIController(client, model=model_name)
    traces = []
    for case in cases:
        started = time.perf_counter()
        # Only the question and optional metadata filter enter the Agent.
        # Never pass expected_answer, gold, answerable or human labels.
        try:
            result = run_agent(case['question'], controller, retriever,
                               filters=case.get('filter'), max_searches=2,
                               top_k=3, budget=1600)
            status = result['status']
        except Exception as exc:
            result = {'answer': '', 'citations': [], 'events': [
                {'event': 'provider_or_retriever_error', 'type': type(exc).__name__, 'message': str(exc)}]}
            status = 'error'
        trace = {'query_id': case['id'], 'split': args.split, 'status': status,
                 'answer': result['answer'], 'citations': result['citations'],
                 'events': result['events'],
                 'elapsed_ms': (time.perf_counter() - started) * 1000}
        traces.append(trace)
        print(f"{case['id']}: {status} ({trace['elapsed_ms']:.0f} ms)", flush=True)

    summary = {'split': args.split, 'n': len(traces),
               'answered': sum(t['status'] == 'answered' for t in traces),
               'abstained': sum(t['status'] == 'abstain' for t in traces),
               'errors': sum(t['status'] == 'error' for t in traces),
               'model': model_name,
               'embedding_model': 'text-embedding-3-small',
               'embedding_dimensions': 1536,
               'embedding_tokens': retriever.embedding_tokens,
               'chat_input_tokens': controller.input_tokens,
               'chat_output_tokens': controller.output_tokens,
               'service_cost_usd': None}
    args.output.mkdir(parents=True, exist_ok=True)
    for name, obj in [('traces.json', traces), ('summary.json', summary)]:
        (args.output / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
