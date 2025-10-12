import json
import argparse
import os
from pathlib import Path

from llama_cpp import Llama

def load_prompt(prompt_path):
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()

def load_agent_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    system_prompt_path = os.path.join(Path(config_path).parent, config["prompts"]["system"])
    persona_prompt_path = os.path.join(Path(config_path).parent, config["prompts"]["persona"])
    
    system_prompt = load_prompt(system_prompt_path)
    persona_prompt = load_prompt(persona_prompt_path)
    
    full_prompt = persona_prompt.strip() + "\n\n" + system_prompt.strip()
    
    return full_prompt, config

def run_local_llama_chat_loop(prompt, config):
    model_path = config["model"].get("local_model_path", "models/llama3-8b.Q4_K_M.gguf")
    temperature = config["model"].get("temperature", 0.3)
    max_tokens = config["model"].get("max_tokens", 1500)

    llm = Llama(
        model_path=model_path,
        n_ctx=4096,
        n_threads=8,  # adjust to your CPU
        verbose=False
    )

    history = f"<|system|>\n{prompt.strip()}</s>\n"

    print("\n💬 Type a message to your agent. Type `exit` to quit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            break

        history += f"<|user|>\n{user_input.strip()}</s>\n<|assistant|>\n"
        output = llm(history, max_tokens=max_tokens, temperature=temperature, stop=["</s>"])
        reply = output["choices"][0]["text"].strip()

        print(f"\nCTO Agent: {reply}\n")
        history += reply + "</s>\n"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quick Local LLaMA Runner")
    parser.add_argument("config_path", help="Path to agent_config.json")
    args = parser.parse_args()

    full_prompt, config = load_agent_config(args.config_path)
    run_local_llama_chat_loop(full_prompt, config)
