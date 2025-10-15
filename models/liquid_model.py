#!/usr/bin/env python3
"""
🧬 LFM2e Model Integration for VBoarder
Liquid AI's Liquid Foundation Models (LFM) wrapper and optimizer.
"""

import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class LFMModel:
    """
    LFM2e (Liquid Foundation Model) integration wrapper.

    Supports multiple backends:
    - Ollama (preferred for development)
    - llama.cpp (direct GGUF loading)
    - API endpoints (production)
    """

    def __init__(self, model_name: str = "lfm2e:latest", backend: str = "ollama"):
        self.model_name = model_name
        self.backend = backend
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def is_available(self) -> bool:
        """Check if LFM2e model is available in the backend."""
        if self.backend == "ollama":
            return await self._check_ollama_model()
        elif self.backend == "llamacpp":
            return self._check_llamacpp_model()
        else:
            logger.warning(f"Unknown backend: {self.backend}")
            return False

    async def _check_ollama_model(self) -> bool:
        """Check if model exists in Ollama."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(model["name"] == self.model_name for model in models)
        except Exception as e:
            logger.debug(f"Error checking Ollama models: {e}")
        return False

    def _check_llamacpp_model(self) -> bool:
        """Check if GGUF file exists for llama.cpp."""
        model_path = Path(f"models/{self.model_name.replace(':', '_')}.gguf")
        return model_path.exists()

    async def generate(self, prompt: str, **kwargs) -> dict[str, Any]:
        """
        Generate response using LFM2e model.

        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters

        Returns:
            dict with response and metadata
        """
        if self.backend == "ollama":
            return await self._generate_ollama(prompt, **kwargs)
        elif self.backend == "llamacpp":
            return await self._generate_llamacpp(prompt, **kwargs)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

    async def _generate_ollama(self, prompt: str, **kwargs) -> dict[str, Any]:
        """Generate using Ollama backend."""
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.9),
                "max_tokens": kwargs.get("max_tokens", 2000),
            },
        }

        try:
            response = await self.client.post(f"{self.base_url}/api/generate", json=payload, timeout=30.0)

            if response.status_code == 200:
                result = response.json()
                return {
                    "response": result.get("response", ""),
                    "model": self.model_name,
                    "backend": "ollama",
                    "eval_count": result.get("eval_count", 0),
                    "eval_duration": result.get("eval_duration", 0),
                    "total_duration": result.get("total_duration", 0),
                }
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return {"error": f"API error: {response.status_code}"}

        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            return {"error": str(e)}

    async def _generate_llamacpp(self, prompt: str, **kwargs) -> dict[str, Any]:
        """Generate using llama.cpp backend."""
        # This would integrate with llama-cpp-python
        # For now, return a placeholder
        return {
            "response": "LFM2e response (llama.cpp integration pending)",
            "model": self.model_name,
            "backend": "llamacpp",
            "note": "Direct GGUF loading not yet implemented",
        }


class LFMInstaller:
    """Utility for installing and configuring LFM2e models."""

    def __init__(self):
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)

    def list_available_models(self) -> list[dict[str, Any]]:
        """List available LFM2e model variants."""
        return [
            {
                "name": "lfm2e-7b",
                "size": "4.7GB",
                "description": "LFM2e 7B - Balanced performance and speed",
                "huggingface": "liquid/lfm-2e-7b",
                "recommended": True,
            },
            {
                "name": "lfm2e-13b",
                "size": "8.2GB",
                "description": "LFM2e 13B - Enhanced reasoning capabilities",
                "huggingface": "liquid/lfm-2e-13b",
                "recommended": False,
            },
            {
                "name": "lfm2e-30b",
                "size": "16GB",
                "description": "LFM2e 30B - Maximum performance (requires significant RAM)",
                "huggingface": "liquid/lfm-2e-30b",
                "recommended": False,
            },
        ]

    async def install_via_ollama(self, model_variant: str = "lfm2e-7b") -> bool:
        """
        Install LFM2e model via Ollama.

        Args:
            model_variant: Model variant to install

        Returns:
            bool: True if installation successful
        """
        print(f"🚀 Installing {model_variant} via Ollama...")

        # Map to Ollama model names (these would be actual Ollama model names)
        ollama_models = {"lfm2e-7b": "lfm2e:7b", "lfm2e-13b": "lfm2e:13b", "lfm2e-30b": "lfm2e:30b"}

        ollama_name = ollama_models.get(model_variant, "lfm2e:latest")

        try:
            # Check if Ollama is running
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                print("❌ Ollama not running. Please start Ollama first.")
                return False

            # Pull the model
            print(f"📥 Pulling {ollama_name}...")
            result = subprocess.run(
                ["ollama", "pull", ollama_name],
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout for large models
            )

            if result.returncode == 0:
                print(f"✅ Successfully installed {ollama_name}")
                return True
            else:
                print(f"❌ Failed to install {ollama_name}: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("❌ Installation timed out")
            return False
        except FileNotFoundError:
            print("❌ Ollama not found. Please install Ollama first.")
            return False
        except Exception as e:
            print(f"❌ Installation error: {e}")
            return False

    def generate_config(self, model_variant: str = "lfm2e-7b") -> dict[str, Any]:
        """Generate configuration for LFM2e integration."""
        return {
            "model_slot_b": f"lfm2e:{model_variant.split('-')[1]}",
            "backend": "ollama",
            "routing": {
                "leadership_agents": ["CEO", "CTO", "COO", "COS", "CFO"],
                "strategic_keywords": [
                    "optimize",
                    "strategy",
                    "plan",
                    "resource",
                    "allocation",
                    "decision",
                    "prioritize",
                    "coordinate",
                    "schedule",
                ],
            },
            "performance": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 2000, "timeout": 30},
        }


async def main():
    """CLI interface for LFM2e model management."""
    if len(sys.argv) < 2:
        print("🧬 LFM2e Model Manager")
        print("Usage:")
        print("  python models/liquid_model.py install [variant]")
        print("  python models/liquid_model.py test")
        print("  python models/liquid_model.py config")
        print("\nVariants: lfm2e-7b (default), lfm2e-13b, lfm2e-30b")
        return

    command = sys.argv[1]
    installer = LFMInstaller()

    if command == "install":
        variant = sys.argv[2] if len(sys.argv) > 2 else "lfm2e-7b"
        success = await installer.install_via_ollama(variant)
        if success:
            print(f"\n✅ {variant} ready for use!")
            print("💡 Set MODEL_SLOT_B environment variable to use:")
            print(f"   export MODEL_SLOT_B=lfm2e:{variant.split('-')[1]}")

    elif command == "test":
        model = LFMModel()
        available = await model.is_available()
        print(f"🧪 LFM2e Model Status: {'✅ Available' if available else '❌ Not Available'}")

        if available:
            print("🚀 Testing generation...")
            result = await model.generate("What is strategic planning?")
            print(f"📝 Response: {result.get('response', 'No response')[:100]}...")

    elif command == "config":
        config = installer.generate_config()
        print("🔧 LFM2e Configuration:")
        print(json.dumps(config, indent=2))

    elif command == "list":
        models = installer.list_available_models()
        print("📋 Available LFM2e Models:")
        for model in models:
            star = " ⭐" if model["recommended"] else ""
            print(f"  {model['name']} ({model['size']}){star}")
            print(f"    {model['description']}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
