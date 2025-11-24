from collections.abc import Generator
from typing import Any
import json
import base64
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool

class GetAgentCapabilitiesTool(Tool):
    def _build_agents_registry(self) -> dict[str, dict[str, Any]]:
        """
        Build agents registry from raw credential fields.
        This is called at runtime by the tool.
        """
        registry = {}

        for i in range(1, 6):
            agent_name = self.runtime.credentials.get(f"agent_{i}_name", "").strip()
            if not agent_name:
                continue

            agent_url = self.runtime.credentials.get(f"agent_{i}_url", "").strip()
            auth_type = self.runtime.credentials.get(f"agent_{i}_auth_type", "none")
            api_key = self.runtime.credentials.get(f"agent_{i}_api_key", "").strip()
            description = self.runtime.credentials.get(f"agent_{i}_description", "").strip()

            registry[agent_name] = {
                "base_url": agent_url,
                "auth_type": auth_type,
                "api_key": api_key,
                "description": description
            }

        return registry

    def _build_auth_header(self, auth_type: str, api_key: str) -> dict[str, str]:
        """
        Build the appropriate Authorization header based on auth type.
        """
        if auth_type == "none" or not api_key:
            return {}
        elif auth_type == "bearer":
            return {"Authorization": f"Bearer {api_key}"}
        elif auth_type == "api-key":
            return {"Authorization": f"Bearer {api_key}"}
        elif auth_type == "basic":
            encoded = base64.b64encode(api_key.encode()).decode()
            return {"Authorization": f"Basic {encoded}"}
        else:
            return {"Authorization": f"Bearer {api_key}"}

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the Get Agent Capabilities tool.
        Fetches the Agent Card from /.well-known/agent-card.json (with fallback to agent.json).
        Implements A2A Protocol agent discovery pattern.
        """
        agents_registry = self._build_agents_registry()
        if not agents_registry:
            yield self.create_text_message("Agents Registry is not configured.")
            return

        agent_name = tool_parameters.get("agent_name")
        if not agent_name or agent_name not in agents_registry:
            yield self.create_text_message(f"Agent '{agent_name}' not found in registry.")
            return

        agent_config = agents_registry[agent_name]
        agent_base_url = agent_config.get("base_url")
        auth_type = agent_config.get("auth_type", "none")
        api_key = agent_config.get("api_key", "")

        if not agent_base_url:
            yield self.create_text_message(f"Base URL missing for agent '{agent_name}'.")
            return

        # Build headers with appropriate authentication (some servers may require auth for agent card)
        headers = self._build_auth_header(auth_type, api_key)

        # Try both agent-card.json (preferred) and agent.json (fallback)
        agent_card = None
        last_error = None

        for filename in ["agent-card.json", "agent.json"]:
            agent_card_url = f"{agent_base_url.rstrip('/')}/.well-known/{filename}"

            try:
                response = requests.get(agent_card_url, headers=headers, timeout=10)
                response.raise_for_status()
                agent_card = response.json()
                break  # Successfully fetched, exit loop
            except requests.exceptions.RequestException as e:
                last_error = f"{filename}: {str(e)}"
                continue  # Try next filename
            except json.JSONDecodeError as e:
                last_error = f"{filename}: Invalid JSON - {str(e)}"
                continue

        # If neither path worked, return error
        if agent_card is None:
            yield self.create_text_message(
                f"Failed to fetch Agent Card from both paths. Last error: {last_error}"
            )
            return

        try:
            # Return more complete agent card per A2A spec
            filtered_card = {
                "name": agent_card.get("name", "Unknown Agent"),
                "description": agent_card.get("description", "No description provided."),
                "protocolVersion": agent_card.get("protocolVersion", "unknown"),
                "capabilities": agent_card.get("capabilities", {}),
                "skills": agent_card.get("skills", []),
                "securitySchemes": agent_card.get("securitySchemes", {}),
                "url": agent_card.get("url", agent_base_url)
            }

            yield self.create_text_message(json.dumps(filtered_card, indent=2))

        except Exception as e:
            yield self.create_text_message(f"Error processing Agent Card: {str(e)}")
