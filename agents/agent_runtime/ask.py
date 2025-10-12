import os
import json
import argparse
import logging
from dotenv import load_dotenv
from agents.agent_runtime.model_router import smart_hybrid_inference
from agents.agent_runtime.utils import (
    load_agent,
    load_memory,
    # REMOVED: compose_prompt, 
    print_verbose_block,
)

# Optional RAG
try:
    from agents.rag_memory import get_top_k_memories, store_interaction
    RAG_ENABLED = True
except ImportError:
    RAG_ENABLED = False

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description="Ask your local agent something.")
    parser.add_argument("--agent", type=str, required=True, help="Name of the agent")
    parser.add_argument("--query", type=str, required=True, help="Question to ask")
    parser.add_argument("--max_memory", type=int, default=5, help="Max memory entries to inject")
    parser.add_argument("--model", type=str, default=None, help="Override model")
    parser.add_argument("--info", action="store_true", help="Print raw prompt (messages array) and exit")
    parser.add_argument("--verbose", action="store_true", help="Print all debug blocks")
    args = parser.parse_args()

    # === Load agent data ===
    agent_path = os.path.join("agents", args.agent)
    agent_data = load_agent(agent_path)

    # === Load memory ===
    memory_entries = []
    if RAG_ENABLED:
        try:
            rag_memories = get_top_k_memories(agent_name=args.agent, query=args.query, k=args.max_memory)
            # Memory entries must be structured as [{"q": ..., "a": ...}, ...]
            memory_entries = [{"q": m["query"], "a": m["answer"]} for m in rag_memories]

            if args.verbose:
                print_verbose_block("🧠 Retrieved RAG Memory Entries", json.dumps(memory_entries, indent=2))

        except Exception as e:
            logger.warning(f"[RAG ERROR] Falling back to JSON memory: {e}")
            memory_entries = load_memory(agent_path)
    else:
        memory_entries = load_memory(agent_path)

    # =======================================================
    # === NEW: Build structured messages array (messages[]) ===
    # =======================================================
    messages = []
    
    # 1. System prompt
    system_prompt = agent_data.get("system_prompt", "You are a helpful assistant.")
    messages.append({"role": "system", "content": system_prompt})

    # 2. Add prior memory (user + assistant)
    for entry in memory_entries:
        # User message (q) from prior turn
        messages.append({"role": "user", "content": entry["q"]})
        # Assistant message (a) from prior turn
        messages.append({"role": "assistant", "content": entry["a"]})

    # 3. Add the current query
    current_query = args.query
    messages.append({"role": "user", "content": current_query})


    if args.info or args.verbose:
        # Print the structured array instead of the old string prompt
        print_verbose_block("📝 Final Messages Array Sent to Model", json.dumps(messages, indent=2))
        if args.info:
            return

    # ===================================================
    # === NEW INFERENCE CALL: Pass 'messages' as context ===
    # ===================================================
    # Note: We pass the full messages list as 'context'.
    # We pass 'prompt=current_query' for backward compatibility 
    # but the router should primarily use 'context'.
    response = smart_hybrid_inference(prompt=current_query, model_override=args.model, context=messages)
    print(f"\n🤖 {response}\n")

    # === Store new memory (optional) ===
    if RAG_ENABLED:
        try:
            store_interaction(agent=args.agent, query=args.query, answer=response)
            if args.verbose:
                logger.info("🧠 Stored new interaction in vector memory.")
        except Exception as e:
            logger.warning(f"[RAG STORE FAILED] {e}")

if __name__ == "__main__":
    main()