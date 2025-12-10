"""Agent interfaces for A²-Bench."""

from a2_bench.agents.base import BaseAgent, AgentResponse, DummyAgent
from a2_bench.agents.llm_agent import LLMAgent

__all__ = [
    "BaseAgent",
    "AgentResponse",
    "DummyAgent",
    "LLMAgent",
]
