"""LLM-based agent for A²-Bench."""

from typing import Dict, List, Any, Optional
import json
import os

from a2_bench.agents.base import BaseAgent, AgentResponse


class LLMAgent(BaseAgent):
    """LLM-based agent using OpenAI or Anthropic APIs."""

    def __init__(self,
                 model: str = "gpt-4",
                 temperature: float = 0.0,
                 provider: str = "openai",
                 config: Dict = None):
        """Initialize LLM agent.

        Args:
            model: Model name/ID
            temperature: Sampling temperature
            provider: API provider (openai, anthropic)
            config: Additional configuration
        """
        super().__init__(config)
        self.model = model
        self.temperature = temperature
        self.provider = provider

        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize API client."""
        if self.provider == "openai":
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            except ImportError:
                pass
        elif self.provider == "anthropic":
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            except ImportError:
                pass

    def respond(self,
                user_message: str,
                system_prompt: str = "",
                available_tools: List[Dict] = None) -> AgentResponse:
        """Generate response using LLM.

        Args:
            user_message: User's message
            system_prompt: System prompt
            available_tools: Available tools

        Returns:
            Agent response
        """
        self.add_to_history('user', user_message)

        if not self._client:
            return AgentResponse(
                message="API client not initialized. Please check your API key.",
                tool_calls=[],
                reasoning="Client initialization failed"
            )

        try:
            if self.provider == "openai":
                response = self._openai_respond(system_prompt, available_tools)
            elif self.provider == "anthropic":
                response = self._anthropic_respond(system_prompt, available_tools)
            else:
                response = AgentResponse(
                    message="Unsupported provider",
                    tool_calls=[]
                )

            self.add_to_history('assistant', response.message)
            return response

        except Exception as e:
            return AgentResponse(
                message=f"Error generating response: {str(e)}",
                tool_calls=[],
                reasoning=f"Exception: {str(e)}"
            )

    def _openai_respond(self,
                        system_prompt: str,
                        available_tools: List[Dict]) -> AgentResponse:
        """Generate response using OpenAI API.

        Args:
            system_prompt: System prompt
            available_tools: Available tools

        Returns:
            Agent response
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        for msg in self.conversation_history:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })

        # Prepare tools
        tools = None
        if available_tools:
            tools = [
                {
                    "type": "function",
                    "function": tool
                }
                for tool in available_tools
            ]

        # Call API
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self._client.chat.completions.create(**kwargs)

        # Parse response
        message = response.choices[0].message
        tool_calls = []

        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append({
                    "name": tc.function.name,
                    "args": json.loads(tc.function.arguments)
                })

        return AgentResponse(
            message=message.content or "",
            tool_calls=tool_calls,
            reasoning=""
        )

    def _anthropic_respond(self,
                           system_prompt: str,
                           available_tools: List[Dict]) -> AgentResponse:
        """Generate response using Anthropic API.

        Args:
            system_prompt: System prompt
            available_tools: Available tools

        Returns:
            Agent response
        """
        messages = []

        for msg in self.conversation_history:
            messages.append({
                "role": msg['role'],
                "content": msg['content']
            })

        # Prepare tools for Anthropic format
        tools = None
        if available_tools:
            tools = [
                {
                    "name": tool.get('name', ''),
                    "description": tool.get('description', ''),
                    "input_schema": tool.get('parameters', {})
                }
                for tool in available_tools
            ]

        # Call API
        kwargs = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        if tools:
            kwargs["tools"] = tools

        response = self._client.messages.create(**kwargs)

        # Parse response
        message_content = ""
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                message_content += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "name": block.name,
                    "args": block.input
                })

        return AgentResponse(
            message=message_content,
            tool_calls=tool_calls,
            reasoning=""
        )

    def process_tool_result(self, tool_name: str, result: Dict) -> AgentResponse:
        """Process tool result and generate follow-up.

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

        # Add tool result to history
        result_str = json.dumps(result, default=str)
        self.add_to_history('user', f"Tool '{tool_name}' returned: {result_str}")

        # Generate follow-up response
        return self.respond(
            f"Based on the tool result, please provide your response.",
            system_prompt="",
            available_tools=None
        )

    def get_tool_definitions(self, tools: Dict) -> List[Dict]:
        """Convert tool functions to API-compatible definitions.

        Args:
            tools: Dictionary of tool functions

        Returns:
            List of tool definitions
        """
        definitions = []

        for name, func in tools.items():
            definition = {
                "name": name,
                "description": func.__doc__ or f"Execute {name}",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }

            # Extract parameters from function signature
            import inspect
            sig = inspect.signature(func)

            for param_name, param in sig.parameters.items():
                if param_name in ['_context', 'current_user']:
                    continue

                param_def = {"type": "string"}

                if param.default != inspect.Parameter.empty:
                    if isinstance(param.default, bool):
                        param_def["type"] = "boolean"
                    elif isinstance(param.default, int):
                        param_def["type"] = "integer"
                    elif isinstance(param.default, float):
                        param_def["type"] = "number"
                else:
                    definition["parameters"]["required"].append(param_name)

                definition["parameters"]["properties"][param_name] = param_def

            definitions.append(definition)

        return definitions
