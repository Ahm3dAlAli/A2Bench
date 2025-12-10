#!/usr/bin/env python3
"""Quick test of Hugging Face integration."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from a2_bench.agents import LLMAgent


def test_hf_integration():
    """Test Hugging Face model integration."""
    print("Testing Hugging Face integration...")

    # Test with smallest model
    try:
        agent = LLMAgent(
            model="microsoft/Phi-3-mini-4k-instruct",
            provider="huggingface",
            temperature=0.0,
            config={"quantization": "4bit"},
        )

        print("✓ Agent created successfully")

        # Test simple response
        response = agent.respond(
            "Hello, how are you?",
            system_prompt="You are a helpful assistant.",
            available_tools=[],
        )

        print(f"✓ Response generated: {response.message[:100]}...")
        print(f"✓ Tool calls: {len(response.tool_calls)}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_hf_integration()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
