import unittest
import json
from unittest.mock import MagicMock, patch, Mock
import sys
import os
import base64

# Mock dify_plugin before importing tools
mock_dify_plugin = MagicMock()
sys.modules["dify_plugin"] = mock_dify_plugin
sys.modules["dify_plugin.entities.tool"] = MagicMock()

# Mock ToolInvokeMessage
class MockToolInvokeMessage:
    def __init__(self, text):
        self.text = text

# Mock Tool class
class MockTool:
    def __init__(self, runtime):
        self.runtime = runtime

    def create_text_message(self, text):
        return MockToolInvokeMessage(text)

mock_dify_plugin.Tool = MockTool
mock_dify_plugin.entities.tool.ToolInvokeMessage = MockToolInvokeMessage

# Add project root to path to import tools
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from tools.list_agents import ListAgentsTool
from tools.get_agent_capabilities import GetAgentCapabilitiesTool
from tools.call_agent import CallAgentTool
from tools.submit_task import SubmitTaskTool
from tools.get_task_status import GetTaskStatusTool


class TestListAgents(unittest.TestCase):
    """Test cases for list_agents tool"""

    def setUp(self):
        """Setup mock runtime with agent credentials"""
        self.mock_runtime = MagicMock()
        self.mock_runtime.credentials = {
            "agent_1_name": "sales_agent",
            "agent_1_url": "https://sales.example.com",
            "agent_1_auth_type": "bearer",
            "agent_1_api_key": "sales-key-123",
            "agent_1_description": "Sales expert",
            "agent_2_name": "support_agent",
            "agent_2_url": "https://support.example.com",
            "agent_2_auth_type": "none",
            "agent_2_api_key": "",
            "agent_2_description": "Customer support",
            "agent_3_name": "",  # Empty - should be skipped
            "agent_3_url": "",
            "agent_3_auth_type": "none",
            "agent_3_api_key": "",
            "agent_3_description": ""
        }

    def test_list_agents_success(self):
        """Test listing configured agents"""
        tool = ListAgentsTool(self.mock_runtime)
        result_generator = tool._invoke({})
        result = next(result_generator)

        # Parse the JSON response
        agents = json.loads(result.text)

        # Should have 2 agents (agent_3 is empty)
        self.assertEqual(len(agents), 2)

        # Check sales_agent
        sales = next(a for a in agents if a["name"] == "sales_agent")
        self.assertEqual(sales["base_url"], "https://sales.example.com")
        self.assertEqual(sales["auth_type"], "bearer")
        self.assertEqual(sales["description"], "Sales expert")
        self.assertTrue(sales["has_credentials"])

        # Check support_agent
        support = next(a for a in agents if a["name"] == "support_agent")
        self.assertEqual(support["base_url"], "https://support.example.com")
        self.assertEqual(support["auth_type"], "none")
        self.assertFalse(support["has_credentials"])

    def test_list_agents_empty_registry(self):
        """Test listing with no agents configured"""
        self.mock_runtime.credentials = {}
        tool = ListAgentsTool(self.mock_runtime)
        result_generator = tool._invoke({})
        result = next(result_generator)

        self.assertEqual(result.text, "No agents configured in registry.")


class TestGetAgentCapabilities(unittest.TestCase):
    """Test cases for get_agent_capabilities tool"""

    def setUp(self):
        """Setup mock runtime"""
        self.mock_runtime = MagicMock()
        self.mock_runtime.credentials = {
            "agent_1_name": "test_agent",
            "agent_1_url": "https://test.example.com",
            "agent_1_auth_type": "bearer",
            "agent_1_api_key": "test-key",
            "agent_1_description": "Test agent"
        }

    @patch('requests.get')
    def test_get_capabilities_success(self, mock_get):
        """Test successful capability fetch from agent-card.json"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "name": "Test Agent",
            "description": "A test agent",
            "protocolVersion": "1.0",
            "capabilities": {"streaming": True},
            "skills": ["chat", "analysis"],
            "url": "https://test.example.com"
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        tool = GetAgentCapabilitiesTool(self.mock_runtime)
        result_generator = tool._invoke({"agent_name": "test_agent"})
        result = next(result_generator)

        # Parse response
        card = json.loads(result.text)
        self.assertEqual(card["name"], "Test Agent")
        self.assertEqual(card["protocolVersion"], "1.0")
        self.assertTrue(card["capabilities"]["streaming"])

        # Verify correct URL was called
        mock_get.assert_called()
        call_args = mock_get.call_args[0][0]
        self.assertIn("/.well-known/agent-card.json", call_args)

    @patch('requests.get')
    def test_get_capabilities_fallback_to_agent_json(self, mock_get):
        """Test fallback to agent.json when agent-card.json fails"""
        import requests

        def side_effect(url, **kwargs):
            if "agent-card.json" in url:
                raise requests.exceptions.RequestException("Not found")
            else:  # agent.json
                mock_response = MagicMock()
                mock_response.json.return_value = {"name": "Test Agent"}
                mock_response.raise_for_status.return_value = None
                return mock_response

        mock_get.side_effect = side_effect

        tool = GetAgentCapabilitiesTool(self.mock_runtime)
        result_generator = tool._invoke({"agent_name": "test_agent"})
        result = next(result_generator)

        # Should still get result from fallback
        card = json.loads(result.text)
        self.assertEqual(card["name"], "Test Agent")

    def test_get_capabilities_agent_not_found(self):
        """Test error when agent doesn't exist"""
        tool = GetAgentCapabilitiesTool(self.mock_runtime)
        result_generator = tool._invoke({"agent_name": "unknown_agent"})
        result = next(result_generator)

        self.assertIn("not found in registry", result.text)

    def test_get_capabilities_empty_registry(self):
        """Test error when registry is empty"""
        self.mock_runtime.credentials = {}
        tool = GetAgentCapabilitiesTool(self.mock_runtime)
        result_generator = tool._invoke({"agent_name": "test_agent"})
        result = next(result_generator)

        self.assertEqual(result.text, "Agents Registry is not configured.")


class TestCallAgent(unittest.TestCase):
    """Test cases for call_agent tool (sync)"""

    def setUp(self):
        """Setup mock runtime with different auth types"""
        self.mock_runtime = MagicMock()
        self.mock_runtime.credentials = {
            "agent_1_name": "bearer_agent",
            "agent_1_url": "https://bearer.example.com",
            "agent_1_auth_type": "bearer",
            "agent_1_api_key": "bearer-key-123",
            "agent_1_description": "Bearer auth agent",
            "agent_2_name": "apikey_agent",
            "agent_2_url": "https://apikey.example.com",
            "agent_2_auth_type": "api-key",
            "agent_2_api_key": "apikey-456",
            "agent_2_description": "API key agent",
            "agent_3_name": "basic_agent",
            "agent_3_url": "https://basic.example.com",
            "agent_3_auth_type": "basic",
            "agent_3_api_key": "user:pass",
            "agent_3_description": "Basic auth agent",
            "agent_4_name": "none_agent",
            "agent_4_url": "https://none.example.com",
            "agent_4_auth_type": "none",
            "agent_4_api_key": "",
            "agent_4_description": "No auth agent"
        }

    @patch('requests.post')
    def test_call_agent_bearer_auth(self, mock_post):
        """Test call with bearer token authentication"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": "Operation successful",
            "id": "test-id"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        tool = CallAgentTool(self.mock_runtime)
        result_generator = tool._invoke({
            "agent_name": "bearer_agent",
            "instruction": "Test instruction"
        })
        result = next(result_generator)

        # Verify request
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['headers']['Authorization'], "Bearer bearer-key-123")
        self.assertEqual(kwargs['json']['method'], "message/send")
        self.assertEqual(kwargs['json']['params']['message']['kind'], "message")
        self.assertEqual(kwargs['json']['params']['message']['role'], "user")
        self.assertEqual(kwargs['json']['params']['message']['parts'][0]['text'], "Test instruction")

        # Verify result
        self.assertIn("Operation successful", result.text)

    @patch('requests.post')
    def test_call_agent_api_key_auth(self, mock_post):
        """Test call with API key authentication"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"jsonrpc": "2.0", "result": "Success", "id": "1"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        tool = CallAgentTool(self.mock_runtime)
        result_generator = tool._invoke({
            "agent_name": "apikey_agent",
            "instruction": "Test"
        })
        next(result_generator)

        # Verify API key auth (uses Bearer format)
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['headers']['Authorization'], "Bearer apikey-456")

    @patch('requests.post')
    def test_call_agent_basic_auth(self, mock_post):
        """Test call with basic authentication"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"jsonrpc": "2.0", "result": "Success", "id": "1"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        tool = CallAgentTool(self.mock_runtime)
        result_generator = tool._invoke({
            "agent_name": "basic_agent",
            "instruction": "Test"
        })
        next(result_generator)

        # Verify basic auth
        _, kwargs = mock_post.call_args
        expected_auth = "Basic " + base64.b64encode(b"user:pass").decode()
        self.assertEqual(kwargs['headers']['Authorization'], expected_auth)

    @patch('requests.post')
    def test_call_agent_no_auth(self, mock_post):
        """Test call with no authentication"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"jsonrpc": "2.0", "result": "Success", "id": "1"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        tool = CallAgentTool(self.mock_runtime)
        result_generator = tool._invoke({
            "agent_name": "none_agent",
            "instruction": "Test"
        })
        next(result_generator)

        # Verify no auth header
        _, kwargs = mock_post.call_args
        self.assertNotIn('Authorization', kwargs['headers'])

    @patch('requests.post')
    def test_call_agent_a2a_error_response(self, mock_post):
        """Test handling of A2A error response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "error": {"code": -32602, "message": "Invalid params"},
            "id": "1"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        tool = CallAgentTool(self.mock_runtime)
        result_generator = tool._invoke({
            "agent_name": "bearer_agent",
            "instruction": "Test"
        })
        result = next(result_generator)

        self.assertIn("A2A Error", result.text)
        self.assertIn("Invalid params", result.text)

    @patch('requests.post')
    def test_call_agent_network_error(self, mock_post):
        """Test handling of network errors"""
        mock_post.side_effect = Exception("Connection failed")

        tool = CallAgentTool(self.mock_runtime)
        result_generator = tool._invoke({
            "agent_name": "bearer_agent",
            "instruction": "Test"
        })
        result = next(result_generator)

        self.assertIn("Error", result.text)

    def test_call_agent_missing_agent(self):
        """Test error when agent not found"""
        tool = CallAgentTool(self.mock_runtime)
        result_generator = tool._invoke({
            "agent_name": "unknown",
            "instruction": "Test"
        })
        result = next(result_generator)

        self.assertIn("not found in registry", result.text)

    def test_call_agent_empty_registry(self):
        """Test error when registry is empty"""
        self.mock_runtime.credentials = {}
        tool = CallAgentTool(self.mock_runtime)
        result_generator = tool._invoke({
            "agent_name": "test",
            "instruction": "Test"
        })
        result = next(result_generator)

        self.assertEqual(result.text, "Agents Registry is not configured.")


class TestSubmitTask(unittest.TestCase):
    """Test cases for submit_task tool (async)"""

    def setUp(self):
        """Setup mock runtime"""
        self.mock_runtime = MagicMock()
        self.mock_runtime.credentials = {
            "agent_1_name": "async_agent",
            "agent_1_url": "https://async.example.com",
            "agent_1_auth_type": "bearer",
            "agent_1_api_key": "async-key-123",
            "agent_1_description": "Async agent"
        }

    @patch('requests.post')
    def test_submit_task_success(self, mock_post):
        """Test successful task submission with SSE stream"""
        # Mock SSE response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None

        # Mock SSEClient to return taskId
        with patch('tools.submit_task.SSEClient') as mock_sse_client:
            mock_event = MagicMock()
            mock_event.data = json.dumps({
                "jsonrpc": "2.0",
                "result": {"taskId": "task-abc-123", "state": "submitted"},
                "id": "1"
            })
            mock_sse_client.return_value.events.return_value = [mock_event]
            mock_post.return_value = mock_response

            tool = SubmitTaskTool(self.mock_runtime)
            result_generator = tool._invoke({
                "agent_name": "async_agent",
                "instruction": "Long running task"
            })
            result = next(result_generator)

            # Verify taskId was extracted
            self.assertEqual(result.text, "task-abc-123")

            # Verify request
            mock_post.assert_called_once()
            _, kwargs = mock_post.call_args
            self.assertEqual(kwargs['json']['method'], "message/stream")
            self.assertTrue(kwargs['stream'])

    @patch('requests.post')
    def test_submit_task_network_error(self, mock_post):
        """Test handling of network errors"""
        mock_post.side_effect = Exception("Connection timeout")

        tool = SubmitTaskTool(self.mock_runtime)
        result_generator = tool._invoke({
            "agent_name": "async_agent",
            "instruction": "Test"
        })
        result = next(result_generator)

        self.assertIn("Error", result.text)

    def test_submit_task_missing_agent(self):
        """Test error when agent not found"""
        tool = SubmitTaskTool(self.mock_runtime)
        result_generator = tool._invoke({
            "agent_name": "unknown",
            "instruction": "Test"
        })
        result = next(result_generator)

        self.assertIn("not found in registry", result.text)


class TestGetTaskStatus(unittest.TestCase):
    """Test cases for get_task_status tool"""

    def setUp(self):
        """Setup mock runtime"""
        self.mock_runtime = MagicMock()
        self.mock_runtime.credentials = {
            "agent_1_name": "status_agent",
            "agent_1_url": "https://status.example.com",
            "agent_1_auth_type": "bearer",
            "agent_1_api_key": "status-key-123",
            "agent_1_description": "Status agent"
        }

    @patch('requests.post')
    def test_get_task_status_success(self, mock_post):
        """Test successful task status retrieval"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": {
                "taskId": "task-123",
                "state": "completed",
                "result": "Task completed successfully"
            },
            "id": "1"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        tool = GetTaskStatusTool(self.mock_runtime)
        result_generator = tool._invoke({
            "agent_name": "status_agent",
            "task_id": "task-123"
        })
        result = next(result_generator)

        # Verify result contains task info
        task_info = json.loads(result.text)
        self.assertEqual(task_info["state"], "completed")

        # Verify correct JSON-RPC method
        mock_post.assert_called_once()
        _, kwargs = mock_post.call_args
        self.assertEqual(kwargs['json']['method'], "tasks/get")
        self.assertEqual(kwargs['json']['params']['id'], "task-123")

    def test_get_task_status_missing_agent(self):
        """Test error when agent not found"""
        tool = GetTaskStatusTool(self.mock_runtime)
        result_generator = tool._invoke({
            "agent_name": "unknown",
            "task_id": "task-123"
        })
        result = next(result_generator)

        self.assertIn("not found in registry", result.text)

    @patch('requests.post')
    def test_get_task_status_network_error(self, mock_post):
        """Test handling of network errors"""
        mock_post.side_effect = Exception("Connection failed")

        tool = GetTaskStatusTool(self.mock_runtime)
        result_generator = tool._invoke({
            "agent_name": "status_agent",
            "task_id": "task-123"
        })
        result = next(result_generator)

        self.assertIn("Error", result.text)


if __name__ == '__main__':
    unittest.main()
