"""AI Provider abstraction for RevScan AI (Spec 3, Spec 12 - Member 2).
Decouples LLM/VLM vendor specifics from exploration business logic.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import json
import logging
import httpx
from src.core.config import settings

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract interface for AI Providers."""

    @abstractmethod
    def generate_action(self, prompt: str, screen_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a next-action JSON from screen context."""
        pass


class MockAIProvider(AIProvider):
    """Deterministic Mock AI Provider for testing and local development."""

    def generate_action(self, prompt: str, screen_context: Dict[str, Any]) -> Dict[str, Any]:
        elements = screen_context.get("elements", [])
        prev_actions = screen_context.get("previous_actions", [])

        # Find clickable elements not yet tapped or typed
        tapped_targets = {
            a.get("target_id") for a in prev_actions if isinstance(a, dict) and a.get("type") == "tap"
        }
        typed_targets = {
            a.get("target_id") for a in prev_actions if isinstance(a, dict) and a.get("type") == "type"
        }
        visited_targets = tapped_targets | typed_targets

        # 1. Fill un-typed inputs
        for elem in elements:
            elem_id = elem.get("id")
            elem_type = elem.get("type")
            if elem_type == "input" and elem_id not in typed_targets:
                return {
                    "type": "type",
                    "target_id": elem_id,
                    "text": "test@example.com"
                }

        # 2. Click un-tapped / unvisited buttons & elements
        for elem in elements:
            elem_id = elem.get("id")
            if elem_id not in visited_targets and elem.get("clickable", True):
                return {
                    "type": "tap",
                    "target_id": elem_id
                }

        # 3. Fallback: scroll or finish if history is long
        if len(prev_actions) > 5:
            return {"type": "finish"}
        return {"type": "scroll", "direction": "down"}



class GeminiAIProvider(AIProvider):
    """Google Gemini AI Provider using REST API."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.AI_API_KEY
        self.model_name = model_name or settings.AI_MODEL_NAME or "gemini-1.5-flash"

    def generate_action(self, prompt: str, screen_context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("[GeminiAIProvider] No API key provided, falling back to Mock provider logic.")
            return MockAIProvider().generate_action(prompt, screen_context)

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
        user_content = json.dumps(screen_context, indent=2)

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{prompt}\n\nScreen Context:\n{user_content}"}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json"
            }
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()

                text = data["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except Exception as e:
            logger.error(f"[GeminiAIProvider] Request failed: {e}")
            return MockAIProvider().generate_action(prompt, screen_context)


class OpenAIAIProvider(AIProvider):
    """OpenAI API Provider."""

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.AI_API_KEY
        self.model_name = model_name or settings.AI_MODEL_NAME or "gpt-4o-mini"

    def generate_action(self, prompt: str, screen_context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            logger.warning("[OpenAIAIProvider] No API key provided, falling back to Mock provider logic.")
            return MockAIProvider().generate_action(prompt, screen_context)

        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(screen_context, indent=2)}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return json.loads(content)
        except Exception as e:
            logger.error(f"[OpenAIAIProvider] Request failed: {e}")
            return MockAIProvider().generate_action(prompt, screen_context)


class OllamaAIProvider(AIProvider):
    """Ollama Local LLM Provider."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.AI_MODEL_NAME or "llama3"

    def generate_action(self, prompt: str, screen_context: Dict[str, Any]) -> Dict[str, Any]:
        url = "http://localhost:11434/api/generate"
        full_prompt = f"{prompt}\n\nScreen Context:\n{json.dumps(screen_context, indent=2)}\n\nRespond ONLY with JSON."
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "format": "json"
        }

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return json.loads(data["response"])
        except Exception as e:
            logger.error(f"[OllamaAIProvider] Request failed: {e}")
            return MockAIProvider().generate_action(prompt, screen_context)


def get_ai_provider() -> AIProvider:
    """Factory to retrieve configured AI Provider."""
    provider_name = settings.AI_PROVIDER.lower()
    if provider_name == "mock":
        return MockAIProvider()
    elif provider_name == "gemini":
        return GeminiAIProvider()
    elif provider_name == "openai":
        return OpenAIAIProvider()
    elif provider_name == "ollama":
        return OllamaAIProvider()

    logger.warning(f"Unknown provider '{provider_name}', defaulting to MockAIProvider")
    return MockAIProvider()

