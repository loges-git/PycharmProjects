# services/agent_service.py
"""
Agent Service
=============
Processes natural language prompts for release operations.
Uses the AI provider configured in config/ai_config.yaml.
"""

import json
from typing import Dict, Any, Tuple

from models.release_context import ReleaseContext, Intent, Environment, ReleaseType
from services.ai_provider import get_ai_provider


class AgentService:
    def __init__(self):
        self.provider = get_ai_provider()

    def process_prompt(self, prompt: str, context: ReleaseContext) -> Tuple[str, Dict[str, Any], bool]:
        """
        Process a user prompt and update the context.
        
        Returns:
            - A response message to show the user.
            - A dictionary of updated fields.
            - A boolean indicating if the action should be EXECUTED immediately.
        """
        
        # Build context-aware system prompt
        current_state = []
        if context.release_jira:
            current_state.append(f"release_jira: {context.release_jira}")
        if context.environment:
            current_state.append(f"environment: {context.environment.value}")
        if context.cluster:
            current_state.append(f"cluster: {context.cluster.upper()}")
        if context.release_type:
            current_state.append(f"release_type: {context.release_type.value}")
        
        state_summary = ", ".join(current_state) if current_state else "Nothing configured yet."
        
        system_prompt = f"""You are a Release Operations Assistant for a banking software team.
Help users execute releases by understanding their natural language requests.

Current Context: {state_summary}

Available Options:
- Environments: CIT, BFX
- Clusters: SSA, LDN, WEU, CEE, CIST, MENA, POL
- Release Types: FULL, FIX, ROLLBACK

ALWAYS respond with valid JSON only:
{{
    "intent": "RELEASE" | "REPO_MANAGER" | "CHAT",
    "entities": {{
        "release_jira": "BANKING-123" | null,
        "environment": "CIT" | "BFX" | null,
        "cluster": "SSA" | "LDN" | ... | null,
        "release_type": "FULL" | "FIX" | "ROLLBACK" | null
    }},
    "confirm": true | false,
    "needs_clarification": true | false,
    "message": "Optional message"
}}

Rules:
1. Extract parameters from user input
2. If something is unclear, set needs_clarification=true and ask in message
3. If user says "yes/confirm/do it/execute/now", set confirm=true
4. For casual chat, use intent="CHAT" with a helpful message
"""
        
        try:
            raw_response = self.provider.query(prompt, system_prompt)
            
            # Handle markdown code blocks
            json_str = raw_response.strip()
            if json_str.startswith("```"):
                lines = json_str.split("\n")
                json_str = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
            
            data = json.loads(json_str)
            
        except json.JSONDecodeError:
            # Non-JSON response - treat as conversational
            return raw_response if raw_response else "I'm here to help! Tell me about your release.", {}, False
        except Exception:
            return "I'm having trouble right now. Please try again.", {}, False

        # Handle clarification or chat
        if data.get("needs_clarification") or data.get("intent") == "CHAT":
            return data.get("message", "What would you like to do?"), {}, False

        # Update intent
        intent_str = data.get("intent")
        if intent_str == "RELEASE":
            context.intent = Intent.RELEASE
        elif intent_str == "REPO_MANAGER":
            context.intent = Intent.REPO_MANAGER
        else:
            return data.get("message", "How can I help with your release?"), {}, False

        # Update context from entities
        entities = data.get("entities", {})
        updates = {}

        if jira := entities.get("release_jira"):
            context.release_jira = jira
            updates["Release Jira"] = jira

        if env_str := entities.get("environment"):
            try:
                context.environment = Environment(env_str)
                updates["Environment"] = env_str
            except ValueError:
                pass

        if cluster := entities.get("cluster"):
            context.cluster = cluster.lower()
            updates["Cluster"] = cluster.upper()

        if r_type := entities.get("release_type"):
            try:
                context.release_type = ReleaseType(r_type)
                updates["Release Type"] = r_type
            except ValueError:
                pass

        # Build response
        if data.get("message"):
            response_text = data.get("message")
        elif updates:
            response_text = "✅ Got it! I've updated the configuration."
            
            missing = []
            if not context.release_jira:
                missing.append("Jira ticket")
            if not context.environment:
                missing.append("environment")
            if not context.cluster:
                missing.append("cluster")
            
            if missing:
                response_text += f"\n\nStill need: **{', '.join(missing)}**"
            else:
                response_text += "\n\n🎯 Ready! Say **'confirm'** to execute."
        else:
            response_text = "✅ Ready when you are!"

        return response_text, updates, data.get("confirm", False)
