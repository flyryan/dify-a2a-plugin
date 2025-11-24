from collections.abc import Generator
from typing import Any
import json
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool

class ListAgentsTool(Tool):
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

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the List Agents tool.
        Returns a list of all configured agents with their details.
        """
        agents_registry = self._build_agents_registry()
        if not agents_registry:
            yield self.create_text_message("No agents configured in registry.")
            return

        # Build agent list with relevant information
        agents_list = []
        for name, config in agents_registry.items():
            agent_info = {
                "name": name,
                "base_url": config.get("base_url", ""),
                "auth_type": config.get("auth_type", "none"),
                "description": config.get("description", "No description available.")
            }
            # Only include has_auth flag (don't expose actual keys)
            agent_info["has_credentials"] = bool(config.get("api_key"))
            agents_list.append(agent_info)

        yield self.create_text_message(json.dumps(agents_list, indent=2))
