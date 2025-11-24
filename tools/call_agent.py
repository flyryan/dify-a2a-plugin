from collections.abc import Generator
from typing import Any
import json
import uuid
import base64
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool

class CallAgentTool(Tool):
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
            # A2A spec allows custom headers, but Bearer is most common for API keys
            return {"Authorization": f"Bearer {api_key}"}
        elif auth_type == "basic":
            # For basic auth, api_key should be in format "username:password"
            encoded = base64.b64encode(api_key.encode()).decode()
            return {"Authorization": f"Basic {encoded}"}
        else:
            # Default to Bearer if unknown type
            return {"Authorization": f"Bearer {api_key}"}

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the Call Agent tool (Synchronous message/send).
        Implements A2A Protocol JSON-RPC 2.0 with proper Message object format.
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

        instruction = tool_parameters.get("instruction")

        # Construct JSON-RPC 2.0 Request with proper A2A Message object format
        rpc_request = {
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "kind": "message",
                    "role": "user",
                    "messageId": str(uuid.uuid4()),
                    "parts": [
                        {
                            "kind": "text",
                            "text": instruction
                        }
                    ]
                }
            },
            "id": str(uuid.uuid4())
        }

        # Build headers with appropriate authentication
        headers = {"Content-Type": "application/json"}
        headers.update(self._build_auth_header(auth_type, api_key))

        try:
            response = requests.post(
                agent_base_url,
                json=rpc_request,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()

            rpc_response = response.json()

            if "error" in rpc_response:
                yield self.create_text_message(f"A2A Error: {json.dumps(rpc_response['error'])}")
                return

            result = rpc_response.get("result")
            yield self.create_text_message(json.dumps(result) if result is not None else "Success")

        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Network Error: {str(e)}")
        except json.JSONDecodeError:
            yield self.create_text_message(f"Invalid JSON Response: {response.text}")
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
