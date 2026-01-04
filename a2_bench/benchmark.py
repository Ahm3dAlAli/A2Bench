"""Main benchmark class for A²-Bench."""

from typing import Dict, List, Any, Optional
import time
import json

from a2_bench.core.environment import A2Environment
from a2_bench.core.evaluation import A2Evaluator, EvaluationResult, AggregatedResults
from a2_bench.agents.base import BaseAgent
from a2_bench.adversary.simulator import AdversarySimulator
from a2_bench.adversary.strategies import AdversarialStrategy
from a2_bench.utils.logging import get_logger


logger = get_logger(__name__)


class A2Benchmark:
    """Main benchmark class for A²-Bench evaluation."""

    def __init__(self,
                 domain: Any,
                 adversarial: bool = False,
                 num_trials: int = 1,
                 config: Dict = None):
        """Initialize benchmark.

        Args:
            domain: Domain instance (e.g., HealthcareDomain)
            adversarial: Enable adversarial testing
            num_trials: Number of trials per task
            config: Additional configuration
        """
        self.domain = domain
        self.adversarial = adversarial
        self.num_trials = num_trials
        self.config = config or {}

        self.evaluator = A2Evaluator(domain.name, config)
        self.results: List[EvaluationResult] = []

    def evaluate(self,
                 agent: BaseAgent,
                 tasks: List[Dict] = None,
                 verbose: bool = False) -> AggregatedResults:
        """Evaluate agent on benchmark tasks.

        Args:
            agent: Agent to evaluate
            tasks: Optional list of tasks (uses domain tasks if not provided)
            verbose: Print progress

        Returns:
            Aggregated results
        """
        tasks = tasks or self.domain.get_tasks()

        if verbose:
            print(f"Evaluating {len(tasks)} tasks with {self.num_trials} trials each")

        for task in tasks:
            for trial in range(self.num_trials):
                if verbose:
                    print(f"  Task {task['id']} - Trial {trial + 1}/{self.num_trials}")

                result = self._run_task(agent, task)
                self.results.append(result)

        return self.evaluator.aggregate_results()

    def evaluate_adversarial(self,
                            agent: BaseAgent,
                            adversary: AdversarySimulator,
                            num_episodes: int = 10,
                            verbose: bool = False,
                            reset_results: bool = True) -> Dict:
        """Evaluate agent under adversarial conditions.

        Args:
            agent: Agent to evaluate
            adversary: Adversary simulator
            num_episodes: Number of adversarial episodes
            verbose: Print progress
            reset_results: Whether to reset evaluator results before evaluation (default: True)

        Returns:
            Adversarial evaluation results
        """
        # Reset evaluator to avoid accumulating results from previous runs
        if reset_results:
            self.evaluator.results = []

        scenarios = self.domain.get_adversarial_scenarios()

        if verbose:
            print(f"Running {num_episodes} adversarial episodes")

        attack_results = []

        for i in range(min(num_episodes, len(scenarios))):
            scenario = scenarios[i % len(scenarios)]

            if verbose:
                print(f"  Scenario: {scenario['name']}")

            result = self._run_adversarial_episode(agent, adversary, scenario)
            attack_results.append(result)

        # Aggregate adversarial results
        successful_attacks = sum(1 for r in attack_results if r.get('attack_successful'))

        return {
            'total_episodes': len(attack_results),
            'successful_attacks': successful_attacks,
            'attack_success_rate': successful_attacks / max(1, len(attack_results)),
            'defense_rate': 1 - (successful_attacks / max(1, len(attack_results))),
            'results': attack_results,
            'aggregated_scores': self.evaluator.aggregate_results().to_dict()
        }

    def _run_task(self, agent: BaseAgent, task: Dict) -> EvaluationResult:
        """Run a single task.

        Args:
            agent: Agent to evaluate
            task: Task definition

        Returns:
            Evaluation result
        """
        # Create environment
        patient_id = task.get('patient_id', 'P001')
        env = self.domain.create_environment(patient_id)

        # Reset agent
        agent.reset()

        # Get system prompt
        system_prompt = self.domain.get_system_prompt()

        # Simulate task execution
        max_turns = self.config.get('max_turns', 10)
        task_completed = False

        # Initial user message (task description or adversarial prompt)
        user_message = task.get('user_message', task.get('description', 'Help me with this task.'))

        for turn in range(max_turns):
            # Agent responds
            response = agent.respond(
                user_message,
                system_prompt=system_prompt if turn == 0 else "",
                available_tools=agent.get_tool_definitions(env.agent_tools) if hasattr(agent, 'get_tool_definitions') else None
            )

            # Process tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call.get('name', '')
                tool_args = tool_call.get('args', {})

                # Execute tool
                step_result = env.step('agent', {
                    'type': 'tool_call',
                    'tool': tool_name,
                    'args': tool_args
                })

                # Process result
                if hasattr(agent, 'process_tool_result'):
                    agent.process_tool_result(tool_name, step_result.result)

            # Record agent message
            env.step('agent', {
                'type': 'message',
                'content': response.message
            })

            # Check completion
            if self._check_task_completion(task, env, response):
                task_completed = True
                break

            # Generate next user message (simplified)
            user_message = "Please continue."

        # Evaluate
        result = self.evaluator.evaluate_episode(
            task_id=task['id'],
            model=agent.config.get('model', 'unknown'),
            environment=env,
            task_completed=task_completed
        )

        return result

    def _run_adversarial_episode(self,
                                  agent: BaseAgent,
                                  adversary: AdversarySimulator,
                                  scenario: Dict) -> Dict:
        """Run an adversarial episode.

        Args:
            agent: Agent to evaluate
            adversary: Adversary simulator
            scenario: Adversarial scenario

        Returns:
            Episode result
        """
        # Create environment
        patient_id = scenario.get('patient_id', 'P001')
        env = self.domain.create_environment(patient_id)

        # Reset
        agent.reset()
        adversary.reset()

        # Get prompts
        system_prompt = self.domain.get_system_prompt()

        max_turns = self.config.get('max_turns', 10)
        attack_successful = False

        # Initial adversarial message
        if 'user_message' in scenario:
            user_message = scenario['user_message']
        else:
            action = adversary.generate_action(env.state)
            user_message = action.get('content', '')

        for turn in range(max_turns):
            # Agent responds
            response = agent.respond(
                user_message,
                system_prompt=system_prompt if turn == 0 else "",
                available_tools=None
            )

            # Process tool calls
            for tool_call in response.tool_calls:
                step_result = env.step('agent', {
                    'type': 'tool_call',
                    'tool': tool_call.get('name', ''),
                    'args': tool_call.get('args', {})
                })

                # Check if attack succeeded (e.g., unauthorized access granted)
                if step_result.success and not step_result.blocked:
                    if self._is_attack_success(scenario, step_result):
                        attack_successful = True
                        adversary.record_success(tool_call, step_result.result)

            # Record message
            env.step('agent', {'type': 'message', 'content': response.message})

            # Generate next adversarial action
            action = adversary.generate_action(env.state, response.message)
            if action.get('type') == 'message':
                user_message = action.get('content', '')
            else:
                break

        # Evaluate
        result = self.evaluator.evaluate_episode(
            task_id=scenario['id'],
            model=agent.config.get('model', 'unknown'),
            environment=env,
            task_completed=not attack_successful  # Task "completed" if attack blocked
        )

        return {
            'scenario': scenario['name'],
            'attack_successful': attack_successful,
            'result': result.to_dict(),
            'adversary_summary': adversary.get_attack_summary()
        }

    def _check_task_completion(self, task: Dict, env: A2Environment, response) -> bool:
        """Check if task is completed.

        Args:
            task: Task definition
            env: Current environment
            response: Agent response

        Returns:
            True if completed
        """
        # Simple completion check - can be overridden
        if hasattr(self.domain, 'validate_task_completion'):
            return self.domain.validate_task_completion(task, env)

        # Default: complete if no tool calls and response seems final
        return len(response.tool_calls) == 0

    def _is_attack_success(self, scenario: Dict, step_result) -> bool:
        """Check if attack succeeded.

        Args:
            scenario: Adversarial scenario
            step_result: Step execution result

        Returns:
            True if attack successful
        """
        # Attack succeeds if expected to be blocked but wasn't
        expected = scenario.get('expected_outcome', 'blocked')

        if expected == 'blocked':
            return step_result.success and not step_result.blocked

        return False

    def export_results(self, filepath: str):
        """Export results to file.

        Args:
            filepath: Output file path
        """
        self.evaluator.export_results(filepath)

    def get_summary(self) -> Dict:
        """Get benchmark summary.

        Returns:
            Summary dictionary
        """
        aggregated = self.evaluator.aggregate_results()
        return {
            'domain': self.domain.name,
            'total_tasks': len(self.results),
            'adversarial': self.adversarial,
            'scores': aggregated.to_dict()
        }
