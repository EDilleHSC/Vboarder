import ollama
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from shared_memory import shared_block_text  # fixed import

from shared_memory import shared_block_text
from rag_memory import init_db_pool, search_knowledge_base
import asyncio
class AgentConnector:
    """Connects to Ollama and manages agent conversations with session support."""

    def __init__(self, agent_role="ceo", session_id="default"):
        self.agent_role = agent_role.lower()
        self.session_id = session_id
        self.model = "mistral"
        self.conversations_dir = "../data/conversations"
        self.agents_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents")

        os.makedirs(self.conversations_dir, exist_ok=True)
        os.makedirs(self.agents_dir, exist_ok=True)

        self.agent_config = self._load_agent_config()
        self.conversation_file = os.path.join(self.conversations_dir, f"{self.agent_role}_{self.session_id}.json")
        self.conversation_history = self._load_conversation()
        self._knowledge_cache = None

    def _load_agent_config(self):
        agent_folder = os.path.join(self.agents_dir, self.agent_role.upper())
        config_file = os.path.join(agent_folder, "config.json")

        config = {
            "name": self.agent_role.upper(),
            "role": f"Chief {self.agent_role.upper()[1:]} Officer" if self.agent_role != "sec" else "Executive Secretary",
            "personality": "Professional and knowledgeable",
            "knowledge_files": []
        }

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    config.update(loaded_config)
            except Exception as e:
                print(f"Error loading agent config: {e}")

        personas_dir = os.path.join(agent_folder, "personas")
        if os.path.exists(personas_dir):
            persona_files = [f for f in os.listdir(personas_dir) if f.endswith('.txt')]
            if persona_files:
                persona_file = os.path.join(personas_dir, persona_files[0])
                try:
                    with open(persona_file, 'r', encoding='utf-8') as f:
                        config['persona_content'] = f.read()
                except Exception as e:
                    print(f"Error loading persona: {e}")

        prompts_dir = os.path.join(agent_folder, "prompts")
        system_file = os.path.join(prompts_dir, "system_detailed.txt")
        if os.path.exists(system_file):
            try:
                with open(system_file, 'r', encoding='utf-8') as f:
                    config['system_detailed'] = f.read()
            except Exception as e:
                print(f"Error loading system prompt: {e}")

        return config

    def _load_knowledge(self):
        if self._knowledge_cache is not None:
            return self._knowledge_cache
        knowledge_content = []
        for knowledge_file in self.agent_config.get("knowledge_files", []):
            agent_folder = os.path.join(self.agents_dir, self.agent_role.upper())
            file_path = os.path.join(agent_folder, knowledge_file)
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        knowledge_content.append(f"=== {knowledge_file} ===\n{content}\n")
                except Exception as e:
                    print(f"Error loading knowledge file {knowledge_file}: {e}")
        self._knowledge_cache = "\n".join(knowledge_content) if knowledge_content else ""
        return self._knowledge_cache

    def _load_conversation(self):
        if not os.path.exists(self.conversation_file):
            return []
        try:
            with open(self.conversation_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading conversation history: {e}")
            return []

    def _save_conversation(self):
        try:
            with open(self.conversation_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving conversation history: {e}")

    def _build_system_prompt(self, concise: bool):
        style = (
            "Answer in 1-2 short sentences. Do not list steps or principles. Do not restate your role/title. Avoid repetition."
            if concise else
            "Be concise. Max 2-3 short points. Do not restate your role/title. Avoid repetition."
        )

        base_prompt = self.agent_config.get("system_detailed", f"You are {self.agent_config['name']}, the {self.agent_config['role']}.")
        
        if 'persona_content' in self.agent_config:
            base_prompt += f"\n\n=== PERSONA ===\n{self.agent_config['persona_content']}"
        elif 'personality' in self.agent_config:
            base_prompt += f"\n\nPersonality: {self.agent_config['personality']}"

        if self.agent_role != 'sec' or 'persona_content' not in self.agent_config:
            base_prompt += f"\n\nSTYLE: {style}"

        knowledge = self._load_knowledge()
        if knowledge:
            base_prompt += f"\n\n=== YOUR KNOWLEDGE BASE ===\n{knowledge}\n\nUse this knowledge to inform your responses, but speak naturally and don't just quote it."

        return base_prompt

    def chat(self, user_message: str, concise: bool = False):
        self.conversation_history = self._load_conversation()
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })

        messages = [{"role": "system", "content": self._build_system_prompt(concise=concise)}]

        try:
            _shared = shared_block_text(max_items=20)
            if _shared:
                messages.insert(0, {"role": "system", "content": _shared})
        except Exception:
            pass

        for msg in self.conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        try:
            if self.agent_role == 'sec':
                options = {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 250,
                    "stop": ["\n\n\n"]
                }
            else:
                options = {
                    "temperature": 0.5 if concise else 0.7,
                    "top_p": 0.85 if concise else 0.9,
                    "num_predict": 120 if concise else 250,
                    "stop": ["\n\n- ", "\n\n1.", "\n\n\n"]
                }

            response = ollama.chat(model=self.model, messages=messages, options=options)
            assistant_message = response['message']['content']

            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message,
                "timestamp": datetime.now().isoformat()
            })
            self._save_conversation()
            return assistant_message
        except Exception as e:
            error_msg = f"Error communicating with Ollama: {str(e)}"
            print(error_msg)
            return error_msg

    def get_conversation_summary(self):
        return {
            "session_id": self.session_id,
            "agent": self.agent_role,
            "message_count": len(self.conversation_history),
            "user_messages": len([m for m in self.conversation_history if m["role"] == "user"]),
            "assistant_messages": len([m for m in self.conversation_history if m["role"] == "assistant"])
        }

    # === RAG Memory Hook ===
    async def recall_rag_context(self, message):
        try:
            pool = await init_db_pool()
            rag_data = await search_knowledge_base(pool, self.agent_role, message)
            if rag_data:
                print(f"[RAG] Retrieved {len(rag_data)} chars for {self.agent_role}")
                return rag_data
        except Exception as e:
            print(f"[RAG Error] {e}")
        return ""

    # === RAG Memory Hook ===
    async def recall_rag_context(self, message):
        try:
            pool = await init_db_pool()
            rag_data = await search_knowledge_base(pool, self.agent_role, message)
            if rag_data:
                print(f"[RAG] Retrieved {len(rag_data)} chars for {self.agent_role}")
                return rag_data
        except Exception as e:
            print(f"[RAG Error] {e}")
        return ""
