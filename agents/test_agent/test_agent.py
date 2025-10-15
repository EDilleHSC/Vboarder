import os
import unittest

from agents.agent_runtime.utils import load_agent, load_memory

AGENT_NAME = "test_agent"
AGENT_DIR = os.path.join("agents", AGENT_NAME)


class AgentSystemTest(unittest.TestCase):

    def test_agent_loading(self):
        agent_data = load_agent(AGENT_DIR)
        self.assertIn("system_prompt", agent_data)
        self.assertIsInstance(agent_data["system_prompt"], str)

    def test_memory_json_fallback(self):
        # Assumes no vector RAG for test agent — using JSON fallback
        memory = load_memory(AGENT_DIR)
        self.assertIsInstance(memory, list)
        for item in memory:
            self.assertIn("q", item)
            self.assertIn("a", item)

    def test_prompt_composition(self):
        # Simulate prompt generation using memory
        agent_data = load_agent(AGENT_DIR)
        memory = load_memory(AGENT_DIR)

        messages = [
            {
                "role": "system",
                "content": agent_data.get(
                    "system_prompt", "You are a helpful assistant."
                ),
            }
        ]
        for entry in memory:
            messages.append({"role": "user", "content": entry["q"]})
            messages.append({"role": "assistant", "content": entry["a"]})

        messages.append({"role": "user", "content": "What is this system?"})

        self.assertGreaterEqual(len(messages), 3)
        self.assertEqual(messages[-1]["role"], "user")
        self.assertIn("content", messages[-1])


if __name__ == "__main__":
    unittest.main()
