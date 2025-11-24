from typing import Any
import json

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class A2AProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate the credentials for the A2A Client.
        This is called when the user configures the tool provider.
        Builds agents_registry from individual agent fields.
        """
        registry = {}

        # Loop through 5 possible agent slots
        for i in range(1, 6):
            agent_name = credentials.get(f"agent_{i}_name", "").strip()

            # Skip empty agent slots
            if not agent_name:
                continue

            # If name is provided, URL is required
            agent_url = credentials.get(f"agent_{i}_url", "").strip()
            if not agent_url:
                raise ToolProviderCredentialValidationError(
                    f"Agent {i} ({agent_name}): Base URL is required when agent name is provided"
                )

            # Get auth type (defaults to "none" if not specified)
            auth_type = credentials.get(f"agent_{i}_auth_type", "none")

            # If auth type is not "none", api_key is required
            api_key = credentials.get(f"agent_{i}_api_key", "").strip()
            if auth_type != "none" and not api_key:
                raise ToolProviderCredentialValidationError(
                    f"Agent {i} ({agent_name}): API Key/Token is required when auth type is '{auth_type}'"
                )

            # Get description (optional)
            description = credentials.get(f"agent_{i}_description", "").strip()

            # Check for duplicate agent names
            if agent_name in registry:
                raise ToolProviderCredentialValidationError(
                    f"Duplicate agent name '{agent_name}' found. Each agent must have a unique name."
                )

            # Add to registry
            registry[agent_name] = {
                "base_url": agent_url,
                "auth_type": auth_type,
                "api_key": api_key,
                "description": description
            }

        # Ensure at least one agent is configured
        if not registry:
            raise ToolProviderCredentialValidationError(
                "At least one agent must be configured. Please fill in Agent 1 fields."
            )

        # Validation complete - tools will build the registry at runtime from raw credential fields
        # Do not transform or store modified credentials here
