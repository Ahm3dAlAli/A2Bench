"""LLM-based agent for A²-Bench."""

from typing import Dict, List, Any, Optional
import json
import os
import gc
import psutil
import torch

from a2_bench.agents.base import BaseAgent, AgentResponse


class LLMAgent(BaseAgent):
    """LLM-based agent using OpenAI or Anthropic APIs."""

    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.0,
        provider: str = "openai",
        config: Dict = None,
    ):
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
        elif self.provider == "huggingface":
            try:
                self._initialize_huggingface_client()
            except ImportError:
                pass

    def respond(
        self,
        user_message: str,
        system_prompt: str = "",
        available_tools: List[Dict] = None,
    ) -> AgentResponse:
        """Generate response using LLM.

        Args:
            user_message: User's message
            system_prompt: System prompt
            available_tools: Available tools

        Returns:
            Agent response
        """
        self.add_to_history("user", user_message)

        if not self._client:
            return AgentResponse(
                message="API client not initialized. Please check your API key.",
                tool_calls=[],
                reasoning="Client initialization failed",
            )

        try:
            if self.provider == "openai":
                response = self._openai_respond(system_prompt, available_tools)
            elif self.provider == "anthropic":
                response = self._anthropic_respond(system_prompt, available_tools)
            elif self.provider == "huggingface":
                response = self._huggingface_respond(system_prompt, available_tools)
            else:
                response = AgentResponse(message="Unsupported provider", tool_calls=[])

            self.add_to_history("assistant", response.message)
            return response

        except Exception as e:
            return AgentResponse(
                message=f"Error generating response: {str(e)}",
                tool_calls=[],
                reasoning=f"Exception: {str(e)}",
            )

    def _openai_respond(
        self, system_prompt: str, available_tools: List[Dict]
    ) -> AgentResponse:
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
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Prepare tools
        tools = None
        if available_tools:
            tools = [{"type": "function", "function": tool} for tool in available_tools]

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
                tool_calls.append(
                    {
                        "name": tc.function.name,
                        "args": json.loads(tc.function.arguments),
                    }
                )

        return AgentResponse(
            message=message.content or "", tool_calls=tool_calls, reasoning=""
        )

    def _anthropic_respond(
        self, system_prompt: str, available_tools: List[Dict]
    ) -> AgentResponse:
        """Generate response using Anthropic API.

        Args:
            system_prompt: System prompt
            available_tools: Available tools

        Returns:
            Agent response
        """
        messages = []

        for msg in self.conversation_history:
            messages.append({"role": msg["role"], "content": msg["content"]})

        # Prepare tools for Anthropic format
        tools = None
        if available_tools:
            tools = [
                {
                    "name": tool.get("name", ""),
                    "description": tool.get("description", ""),
                    "input_schema": tool.get("parameters", {}),
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
                tool_calls.append({"name": block.name, "args": block.input})

        return AgentResponse(
            message=message_content, tool_calls=tool_calls, reasoning=""
        )

    def process_tool_result(self, tool_name: str, result: Dict) -> AgentResponse:
        """Process tool result and generate follow-up.

        Args:
            tool_name: Tool name
            result: Tool result

        Returns:
            Follow-up response
        """
        self.tool_results.append({"tool": tool_name, "result": result})

        # Add tool result to history
        result_str = json.dumps(result, default=str)
        self.add_to_history("user", f"Tool '{tool_name}' returned: {result_str}")

        # Generate follow-up response
        return self.respond(
            f"Based on the tool result, please provide your response.",
            system_prompt="",
            available_tools=None,
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
                "parameters": {"type": "object", "properties": {}, "required": []},
            }

            # Extract parameters from function signature
            import inspect

            sig = inspect.signature(func)

            for param_name, param in sig.parameters.items():
                if param_name in ["_context", "current_user"]:
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

    def _initialize_huggingface_client(self):
        """Initialize Hugging Face model with device management."""
        try:
            from transformers import (
                AutoTokenizer,
                AutoModelForCausalLM,
                BitsAndBytesConfig,
            )
            import torch

            # Check system resources
            self._check_system_resources()

            # Configure quantization
            quantization_config = None
            if hasattr(self, "config") and self.config.get("quantization") == "4bit":
                # Only use quantization if CUDA is available
                if torch.cuda.is_available():
                    quantization_config = BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4",
                    )
                else:
                    print(
                        "Warning: 4-bit quantization requires CUDA. Using float16 instead."
                    )
                    quantization_config = None

            # Load tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model, trust_remote_code=True, padding_side="left"
            )

            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token

            # Load model
            self._client = AutoModelForCausalLM.from_pretrained(
                self.model,
                quantization_config=quantization_config,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
            )

            # Set device
            if torch.cuda.is_available():
                self._device = "cuda"
            else:
                self._device = "cpu"

        except Exception as e:
            print(f"Error initializing Hugging Face client: {e}")
            self._client = None
            self._tokenizer = None
            self._device = None

    def _check_system_resources(self):
        """Check if system has sufficient resources."""
        # Check GPU memory if available
        if torch.cuda.is_available():
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (
                1024**3
            )  # GB
            print(f"Available GPU memory: {gpu_memory:.1f} GB")

            # Estimate model memory requirements
            model_memory_map = {
                "meta-llama/Llama-3.1-8B-Instruct": 8,  # 4-bit quantized
                "mistralai/Mistral-7B-Instruct-v0.2": 7,
                "microsoft/Phi-3-mini-4k-instruct": 4,
                "google/gemma-2-9b-it": 9,
            }

            required_memory = model_memory_map.get(self.model, 8)
            if gpu_memory < required_memory:
                print(
                    f"Warning: Model requires {required_memory}GB GPU memory, only {gpu_memory:.1f}GB available"
                )

        # Check system memory
        system_memory = psutil.virtual_memory().total / (1024**3)  # GB
        print(f"Available system memory: {system_memory:.1f} GB")

    def _huggingface_respond(
        self, system_prompt: str, available_tools: List[Dict]
    ) -> AgentResponse:
        """Generate response using Hugging Face model.

        Args:
            system_prompt: System prompt
            available_tools: Available tools

        Returns:
            Agent response
        """
        if not self._client or not self._tokenizer:
            return AgentResponse(
                message="Hugging Face model not initialized",
                tool_calls=[],
                reasoning="Model initialization failed",
            )

        try:
            # Format conversation
            messages = []

            if system_prompt:
                if self._tokenizer.chat_template is not None:
                    messages.append({"role": "system", "content": system_prompt})
                else:
                    # For models without chat template, prepend to first user message
                    pass

            # Add conversation history
            for msg in self.conversation_history:
                messages.append({"role": msg["role"], "content": msg["content"]})

            # Handle tools (simplified for Hugging Face models)
            tool_prompt = ""
            if available_tools:
                tool_descriptions = []
                for tool in available_tools:
                    name = tool.get("name", "")
                    desc = tool.get("description", "")
                    tool_descriptions.append(f"- {name}: {desc}")

                tool_prompt = f"\n\nAvailable tools:\n" + "\n".join(tool_descriptions)
                tool_prompt += (
                    "\nTo use a tool, respond with: TOOL_CALL: {tool_name}({arguments})"
                )

            # Format prompt based on model
            if self._tokenizer.chat_template is not None:
                formatted_prompt = self._tokenizer.apply_chat_template(
                    messages + [{"role": "user", "content": tool_prompt}],
                    tokenize=False,
                    add_generation_prompt=True,
                )
            else:
                # Fallback for models without chat template
                formatted_prompt = system_prompt + "\n\n" if system_prompt else ""
                for msg in messages:
                    formatted_prompt += f"{msg['role']}: {msg['content']}\n"
                formatted_prompt += "assistant:" + tool_prompt

            # Generate response
            inputs = self._tokenizer.encode(formatted_prompt, return_tensors="pt").to(
                self._device
            )

            with torch.no_grad():
                outputs = self._client.generate(
                    inputs,
                    max_new_tokens=512,
                    temperature=self.temperature,
                    do_sample=self.temperature > 0,
                    pad_token_id=self._tokenizer.eos_token_id,
                    eos_token_id=self._tokenizer.eos_token_id,
                )

            # Decode response
            response_text = self._tokenizer.decode(
                outputs[0][inputs.shape[1] :], skip_special_tokens=True
            )

            # Parse tool calls (simplified)
            tool_calls = []
            if "TOOL_CALL:" in response_text:
                # Extract tool call
                tool_call_start = response_text.find("TOOL_CALL:") + len("TOOL_CALL:")
                tool_call_end = response_text.find("\n", tool_call_start)
                if tool_call_end == -1:
                    tool_call_end = len(response_text)

                tool_call_text = response_text[tool_call_start:tool_call_end].strip()

                # Simple parsing for tool_name(args)
                if "(" in tool_call_text and tool_call_text.endswith(")"):
                    tool_name = tool_call_text.split("(")[0].strip()
                    args_text = tool_call_text.split("(")[1][:-1].strip()

                    try:
                        tool_args = json.loads(args_text) if args_text else {}
                        tool_calls.append({"name": tool_name, "args": tool_args})
                    except json.JSONDecodeError:
                        # Fallback: treat as single argument
                        tool_calls.append(
                            {"name": tool_name, "args": {"input": args_text}}
                        )

                # Remove tool call from response text
                response_text = response_text[
                    : response_text.find("TOOL_CALL:")
                ].strip()

            return AgentResponse(
                message=response_text, tool_calls=tool_calls, reasoning=""
            )

        except Exception as e:
            return AgentResponse(
                message=f"Error generating response: {str(e)}",
                tool_calls=[],
                reasoning=f"Exception: {str(e)}",
            )
