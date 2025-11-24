"""Base agent interface for A²-Bench."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AgentResponse:
    """Response from an agent."""

    message: str
    tool_calls: List[Dict] = None
    reasoning: str = ""
    confidence: float = 1.0

    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'message': self.message,
            'tool_calls': self.tool_calls,
            'reasoning': self.reasoning,
            'confidence': self.confidence
        }


class BaseAgent(ABC):
    """Abstract base class for agents."""

    def __init__(self, config: Dict = None):
        """Initialize agent.

        Args:
            config: Agent configuration
        """
        self.config = config or {}
        self.conversation_history: List[Dict] = []
        self.tool_results: List[Dict] = []

    @abstractmethod
    def respond(self,
                user_message: str,
                system_prompt: str = "",
                available_tools: List[Dict] = None) -> AgentResponse:
        """Generate response to user message.

        Args:
            user_message: User's message
            system_prompt: System prompt for context
            available_tools: List of available tool definitions

        Returns:
            Agent response
        """
        pass

    @abstractmethod
    def process_tool_result(self, tool_name: str, result: Dict) -> AgentResponse:
        """Process result from tool execution.

        Args:
            tool_name: Name of executed tool
            result: Tool execution result

        Returns:
            Follow-up response
        """
        pass

    def reset(self):
        """Reset agent state for new episode."""
        self.conversation_history = []
        self.tool_results = []

    def add_to_history(self, role: str, content: str):
        """Add message to conversation history.

        Args:
            role: Message role (user, assistant, system)
            content: Message content
        """
        self.conversation_history.append({
            'role': role,
            'content': content
        })

    def get_history(self) -> List[Dict]:
        """Get conversation history.

        Returns:
            List of messages
        """
        return self.conversation_history.copy()


class DummyAgent(BaseAgent):
    """Dummy agent for testing."""

    def respond(self,
                user_message: str,
                system_prompt: str = "",
                available_tools: List[Dict] = None) -> AgentResponse:
        """Generate dummy response.

        Args:
            user_message: User's message
            system_prompt: System prompt
            available_tools: Available tools

        Returns:
            Dummy response
        """
        self.add_to_history('user', user_message)

        response = AgentResponse(
            message="I understand your request. Let me help you with that.",
            tool_calls=[],
            reasoning="Dummy agent response"
        )

        self.add_to_history('assistant', response.message)
        return response

    def process_tool_result(self, tool_name: str, result: Dict) -> AgentResponse:
        """Process tool result.

        Args:
            tool_name: Tool name
            result: Tool result

        Returns:
            Follow-up response
        """
        self.tool_results.append({
            'tool': tool_name,
            'result': result
        })

        return AgentResponse(
            message=f"I've processed the result from {tool_name}.",
            tool_calls=[],
            reasoning="Dummy processing"
        )
