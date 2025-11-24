"""Adversary simulation for A²-Bench."""

from a2_bench.adversary.simulator import AdversarySimulator
from a2_bench.adversary.strategies import (
    AdversarialStrategy,
    SocialEngineeringStrategy,
    PromptInjectionStrategy,
    StateCorruptionStrategy,
    ConstraintExploitationStrategy,
)

__all__ = [
    'AdversarySimulator',
    'AdversarialStrategy',
    'SocialEngineeringStrategy',
    'PromptInjectionStrategy',
    'StateCorruptionStrategy',
    'ConstraintExploitationStrategy',
]
