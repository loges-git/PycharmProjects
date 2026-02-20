# services/ai_provider.py
"""
Unified AI Provider
====================
This module provides a single interface for AI interactions.
Configure your company's AI in config/ai_config.yaml.
"""

import os
import yaml
import json
import requests
from pathlib import Path
from typing import Optional
from abc import ABC, abstractmethod


def load_ai_config() -> dict:
    """Load AI configuration from YAML file."""
    config_path = Path("config/ai_config.yaml")
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {"mode": "MOCK"}


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def query(self, prompt: str, system_prompt: str = None) -> str:
        """Send a prompt and return the response."""
        pass


class MockAI(AIProvider):
    """
    Mock AI for testing without an API.
    Provides basic pattern matching for release operations.
    """
    
    def query(self, prompt: str, system_prompt: str = None) -> str:
        import re
        prompt_lower = prompt.lower()
        
        # Pattern matching for common intents
        jira_match = re.search(r"([A-Z]+-\d+)", prompt, re.IGNORECASE)
        jira = jira_match.group(1).upper() if jira_match else None
        
        # Detect environment
        env = None
        if "cit" in prompt_lower or "uat" in prompt_lower:
            env = "CIT"
        elif "bfx" in prompt_lower or "pre-prod" in prompt_lower:
            env = "BFX"
        
        # Detect cluster
        cluster = None
        for c in ["ssa", "ldn", "weu", "cee", "cist", "mena", "pol"]:
            if c in prompt_lower:
                cluster = c.upper()
                break
        
        # Detect confirmation
        confirm = any(word in prompt_lower for word in ["yes", "confirm", "do it", "execute", "now"])
        
        # Build response
        if jira or env or cluster or confirm:
            return json.dumps({
                "intent": "RELEASE",
                "entities": {
                    "release_jira": jira,
                    "environment": env,
                    "cluster": cluster,
                    "release_type": "FULL"
                },
                "confirm": confirm,
                "needs_clarification": False,
                "message": None
            })
        
        # Default conversational response
        return json.dumps({
            "intent": "CHAT",
            "entities": {},
            "confirm": False,
            "needs_clarification": True,
            "message": "I can help you with releases! Try:\n• 'Release BANKING-123 to CIT on SSA'\n• 'Deploy fix to BFX on LDN'"
        })


class CustomAI(AIProvider):
    """
    Custom AI provider for your company's API.
    Configure in config/ai_config.yaml
    """
    
    def __init__(self, config: dict):
        api_config = config.get("api", {})
        self.url = api_config.get("url", "")
        self.api_key = api_config.get("api_key") or os.getenv("AI_API_KEY", "")
        self.model = api_config.get("model", "gpt-4")
        self.timeout = api_config.get("timeout", 30)
        self.max_tokens = api_config.get("max_tokens", 1024)
        self.headers = config.get("headers", {"Content-Type": "application/json"})
        
        # Add authorization header if API key is set
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        
        self.retry_config = config.get("retry", {"max_attempts": 3, "delay_seconds": 2})
    
    def query(self, prompt: str, system_prompt: str = None) -> str:
        """
        Send request to your company's AI API.
        
        Modify this method to match your API's request/response format.
        """
        import time
        
        # Build request payload
        # =====================
        # CUSTOMIZE THIS TO MATCH YOUR API FORMAT
        # =====================
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens
        }
        
        # Send request with retry
        max_attempts = self.retry_config.get("max_attempts", 3)
        delay = self.retry_config.get("delay_seconds", 2)
        
        for attempt in range(max_attempts):
            try:
                response = requests.post(
                    self.url,
                    headers=self.headers,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                # Parse response
                # =====================
                # CUSTOMIZE THIS TO MATCH YOUR API RESPONSE FORMAT
                # =====================
                data = response.json()
                
                # OpenAI-compatible format
                if "choices" in data:
                    return data["choices"][0]["message"]["content"]
                
                # Simple format
                if "response" in data:
                    return data["response"]
                
                if "text" in data:
                    return data["text"]
                
                # Return raw response
                return json.dumps(data)
                
            except requests.exceptions.RequestException as e:
                if attempt < max_attempts - 1:
                    time.sleep(delay)
                    continue
                
                # Return friendly error as JSON
                return json.dumps({
                    "intent": "CHAT",
                    "entities": {},
                    "confirm": False,
                    "needs_clarification": False,
                    "message": f"⚠️ AI service unavailable. Please try again or use Manual UI mode."
                })


def get_ai_provider() -> AIProvider:
    """
    Factory function to get the configured AI provider.
    """
    config = load_ai_config()
    mode = config.get("mode", "MOCK").upper()
    
    if mode == "CUSTOM":
        return CustomAI(config)
    else:
        return MockAI()
