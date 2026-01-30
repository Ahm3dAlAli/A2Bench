"""Dummy agent for testing and baseline evaluation."""

from typing import Dict, List, Any, Optional
from a2_bench.agents.base import BaseAgent, AgentResponse


class DummyAgent(BaseAgent):
    """Simple dummy agent that returns basic responses without external API calls."""

    def __init__(self, config: Dict = None):
        """Initialize dummy agent.

        Args:
            config: Configuration dictionary
        """
        super().__init__(config or {})
        self.model = config.get('model', 'dummy-baseline') if config else 'dummy-baseline'

    def respond(self,
                user_message: str,
                system_prompt: str = "",
                available_tools: List[Dict] = None,
                **kwargs) -> AgentResponse:
        """Generate a simple response.

        Args:
            user_message: User's message
            system_prompt: System prompt
            available_tools: Available tools
            **kwargs: Additional arguments

        Returns:
            AgentResponse with simple response
        """
        # Simple response logic
        message = "I understand your request. Let me help with that."

        # Determine if tools should be called based on keywords
        tool_calls = []

        if available_tools:
            # Simple heuristic: call appropriate tools based on message content
            if "prescription" in user_message.lower() or "prescribe" in user_message.lower():
                if any(tool.get('name') == 'check_allergies' for tool in available_tools):
                    tool_calls.append({
                        'name': 'check_allergies',
                        'args': {}
                    })
                if any(tool.get('name') == 'prescribe_medication' for tool in available_tools):
                    tool_calls.append({
                        'name': 'prescribe_medication',
                        'args': {}
                    })

            elif "transaction" in user_message.lower() or "transfer" in user_message.lower():
                if any(tool.get('name') == 'check_transaction_risk' for tool in available_tools):
                    tool_calls.append({
                        'name': 'check_transaction_risk',
                        'args': {}
                    })
                if any(tool.get('name') == 'process_transaction' for tool in available_tools):
                    tool_calls.append({
                        'name': 'process_transaction',
                        'args': {}
                    })

            elif "access" in user_message.lower() and "record" in user_message.lower():
                if any(tool.get('name') == 'access_patient_record' for tool in available_tools):
                    tool_calls.append({
                        'name': 'access_patient_record',
                        'args': {}
                    })

        return AgentResponse(
            message=message,
            tool_calls=tool_calls
        )

    def reset(self):
        """Reset agent state."""
        self.conversation_history = []

    def process_tool_result(self, tool_name: str, result: Any):
        """Process tool result.

        Args:
            tool_name: Name of tool
            result: Tool result
        """
        # Store in history for potential future use
        self.conversation_history.append({
            'type': 'tool_result',
            'tool': tool_name,
            'result': result
        })
