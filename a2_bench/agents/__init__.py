"""Agent interfaces for A²-Bench."""

from a2_bench.agents.base import BaseAgent, AgentResponse
from a2_bench.agents.llm_agent import LLMAgent
from a2_bench.agents.dummy import DummyAgent

__all__ = [
    'BaseAgent',
    'AgentResponse',
    'LLMAgent',
    'DummyAgent',
]
