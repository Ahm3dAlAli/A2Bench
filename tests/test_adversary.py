"""Tests for adversary simulator."""

import pytest
from a2_bench.adversary.simulator import AdversarySimulator, AdversarialTestSuite
from a2_bench.adversary.strategies import (
    AdversarialStrategy,
    SocialEngineeringStrategy,
    PromptInjectionStrategy,
    ConstraintExploitationStrategy,
)


class TestAdversaryStrategies:
    """Tests for adversarial strategies."""

    def test_social_engineering_strategy(self):
        """Test social engineering strategy."""
        strategy = SocialEngineeringStrategy(sophistication=0.5, target='access')

        action = strategy.generate_action({}, "")
        assert action['type'] == 'message'
        assert 'content' in action
        assert action['strategy'] == 'social_engineering'

    def test_prompt_injection_strategy(self):
        """Test prompt injection strategy."""
        strategy = PromptInjectionStrategy(sophistication=0.7, injection_type='direct')

        action = strategy.generate_action({}, "")
        assert action['type'] == 'message'
        assert action['strategy'] == 'prompt_injection'

    def test_constraint_exploitation_strategy(self):
        """Test constraint exploitation strategy."""
        strategy = ConstraintExploitationStrategy(sophistication=0.5, domain='healthcare')

        action = strategy.generate_action({}, "")
        assert action['type'] == 'message'
        assert action['strategy'] == 'constraint_exploitation'

    def test_strategy_sophistication_bounds(self):
        """Test sophistication bounds."""
        strategy = SocialEngineeringStrategy(sophistication=1.5)
        assert strategy.sophistication == 1.0

        strategy = SocialEngineeringStrategy(sophistication=-0.5)
        assert strategy.sophistication == 0.0

    def test_strategy_reset(self):
        """Test strategy reset."""
        strategy = SocialEngineeringStrategy(sophistication=0.5)

        strategy.generate_action({}, "")
        assert strategy.turn_count == 1

        strategy.reset()
        assert strategy.turn_count == 0


class TestAdversarySimulator:
    """Tests for adversary simulator."""

    def test_simulator_creation(self):
        """Test creating simulator."""
        simulator = AdversarySimulator(
            strategy=AdversarialStrategy.SOCIAL_ENGINEERING,
            sophistication=0.7
        )

        assert simulator.strategy_type == AdversarialStrategy.SOCIAL_ENGINEERING
        assert simulator.sophistication == 0.7

    def test_generate_action(self):
        """Test action generation."""
        simulator = AdversarySimulator(
            strategy=AdversarialStrategy.PROMPT_INJECTION,
            sophistication=0.5
        )

        action = simulator.generate_action({}, "")
        assert 'type' in action
        assert len(simulator.actions_taken) == 1

    def test_record_success(self):
        """Test recording success."""
        simulator = AdversarySimulator(
            strategy=AdversarialStrategy.SOCIAL_ENGINEERING,
            sophistication=0.5
        )

        action = {'type': 'message', 'content': 'test'}
        result = {'success': True}

        simulator.record_success(action, result)
        assert len(simulator.successes) == 1

    def test_attack_summary(self):
        """Test attack summary generation."""
        simulator = AdversarySimulator(
            strategy=AdversarialStrategy.SOCIAL_ENGINEERING,
            sophistication=0.6
        )

        simulator.generate_action({}, "")
        simulator.generate_action({}, "denied")

        summary = simulator.get_attack_summary()
        assert summary['total_actions'] == 2
        assert summary['strategy'] == 'social_engineering'

    def test_simulator_reset(self):
        """Test simulator reset."""
        simulator = AdversarySimulator(
            strategy=AdversarialStrategy.SOCIAL_ENGINEERING,
            sophistication=0.5
        )

        simulator.generate_action({}, "")
        assert len(simulator.actions_taken) == 1

        simulator.reset()
        assert len(simulator.actions_taken) == 0


class TestAdversarialTestSuite:
    """Tests for adversarial test suite."""

    def test_generate_test_cases(self):
        """Test test case generation."""
        suite = AdversarialTestSuite(domain='healthcare')

        cases = suite.generate_test_cases(num_cases=10)
        assert len(cases) == 10
        assert all('id' in case for case in cases)
        assert all('strategy' in case for case in cases)

    def test_domain_specific_tests(self):
        """Test domain-specific test generation."""
        suite = AdversarialTestSuite(domain='healthcare')

        cases = suite.generate_domain_specific_tests()
        assert len(cases) > 0
        assert all('hc_' in case['id'] for case in cases)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
