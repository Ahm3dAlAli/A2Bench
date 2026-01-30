#!/usr/bin/env python3
"""
A²-Bench Green Agent — A2A-compatible server.

This is the green agent (evaluator) for the AgentBeats platform.
It receives messages from a purple agent (agent under test), runs A²-Bench
evaluation tasks against it, and returns scored results.

Protocol: Google A2A (Agent-to-Agent)
"""

import argparse
import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# A²-Bench imports
import sys
sys.path.insert(0, os.path.dirname(__file__))

from a2_bench import A2Benchmark
from a2_bench.agents.base import BaseAgent, AgentResponse
from a2_bench.domains.healthcare import HealthcareDomain
from a2_bench.domains.finance import FinanceDomain
from a2_bench.domains.legal import LegalDomain
from a2_bench.adversary import AdversarySimulator
from a2_bench.adversary.strategies import AdversarialStrategy

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("a2bench-green-agent")

DOMAINS = {
    "healthcare": HealthcareDomain,
    "finance": FinanceDomain,
    "legal": LegalDomain,
}

# ---------------------------------------------------------------------------
# A2A Purple Agent Proxy — wraps the remote purple agent as a BaseAgent
# ---------------------------------------------------------------------------

class A2APurpleAgentProxy(BaseAgent):
    """Proxy that sends messages to the remote purple agent via A2A protocol."""

    def __init__(self, endpoint: str):
        super().__init__(config={})
        self.endpoint = endpoint.rstrip("/")
        self.client = httpx.Client(timeout=120)
        self.task_id = str(uuid.uuid4())

    def respond(self, message: str, system_prompt: str = "",
                available_tools: list = None) -> AgentResponse:
        """Send message to purple agent and parse response."""
        payload = {
            "jsonrpc": "2.0",
            "method": "tasks/send",
            "id": str(uuid.uuid4()),
            "params": {
                "id": self.task_id,
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": message}],
                },
            },
        }

        if system_prompt and not self.history:
            payload["params"]["message"]["parts"].insert(0, {
                "type": "text",
                "text": f"[System] {system_prompt}",
            })

        try:
            resp = self.client.post(f"{self.endpoint}", json=payload)
            resp.raise_for_status()
            result = resp.json().get("result", {})
        except Exception as e:
            logger.error(f"Error communicating with purple agent: {e}")
            return AgentResponse(message=f"Error: {e}", tool_calls=[])

        # Extract text response and tool calls from A2A response
        agent_text = ""
        tool_calls = []
        artifacts = result.get("artifacts", [])
        status = result.get("status", {})
        message_obj = status.get("message", {})

        for part in message_obj.get("parts", []):
            if part.get("type") == "text":
                agent_text += part.get("text", "")
            elif part.get("type") == "function_call":
                tool_calls.append({
                    "name": part.get("name", ""),
                    "args": part.get("args", {}),
                })

        for artifact in artifacts:
            for part in artifact.get("parts", []):
                if part.get("type") == "text":
                    agent_text += part.get("text", "")

        self.add_to_history("assistant", agent_text)
        return AgentResponse(message=agent_text, tool_calls=tool_calls)

    def reset(self):
        self.history = []
        self.task_id = str(uuid.uuid4())

    def get_tool_definitions(self, tools: dict) -> list:
        return [
            {"name": name, "description": func.__doc__ or "", "parameters": {}}
            for name, func in tools.items()
        ]


# ---------------------------------------------------------------------------
# Evaluation Logic
# ---------------------------------------------------------------------------

def run_evaluation(purple_endpoint: str, config: dict) -> dict:
    """Run the full A²-Bench evaluation against a purple agent."""
    domains_to_eval = config.get("domains", ["healthcare", "finance", "legal"])
    num_seeds = config.get("num_seeds", 3)
    adversarial = config.get("adversarial", True)

    agent = A2APurpleAgentProxy(purple_endpoint)
    all_results = {}

    for domain_name in domains_to_eval:
        if domain_name not in DOMAINS:
            logger.warning(f"Unknown domain: {domain_name}, skipping")
            continue

        logger.info(f"Evaluating domain: {domain_name}")
        domain = DOMAINS[domain_name]()
        benchmark = A2Benchmark(domain=domain, num_trials=num_seeds)

        # Baseline evaluation
        agent.reset()
        results = benchmark.evaluate(agent, verbose=True)

        domain_result = {
            "a2_score": results.mean_a2,
            "safety": results.mean_safety,
            "security": results.mean_security,
            "reliability": results.mean_reliability,
            "compliance": results.mean_compliance,
            "task_completion_rate": getattr(results, "task_completion_rate", None),
        }

        # Adversarial evaluation
        if adversarial:
            strategies = config.get("adversarial_strategies", ["social_engineering"])
            adv_results = {}
            for strat_name in strategies:
                strategy = getattr(AdversarialStrategy, strat_name.upper(), None)
                if strategy is None:
                    continue
                agent.reset()
                adversary = AdversarySimulator(strategy=strategy, sophistication=0.7)
                adv = benchmark.evaluate_adversarial(agent, adversary, num_episodes=5, verbose=False)
                adv_results[strat_name] = {
                    "defense_rate": adv.get("defense_rate", 0.0),
                }
            domain_result["adversarial"] = adv_results

        all_results[domain_name] = domain_result

    # Compute overall A²-Score across domains
    a2_scores = [r["a2_score"] for r in all_results.values() if r.get("a2_score") is not None]
    overall = sum(a2_scores) / len(a2_scores) if a2_scores else 0.0

    return {
        "overall_a2_score": overall,
        "domains": all_results,
        "config": config,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# ---------------------------------------------------------------------------
# A2A Server
# ---------------------------------------------------------------------------

app = FastAPI(title="A²-Bench Green Agent")

# State
_card_url = "http://localhost:9009"
_participant_endpoint = None


@app.get("/.well-known/agent-card.json")
async def agent_card():
    """A2A Agent Card — describes this green agent."""
    env_domain = os.environ.get("A2BENCH_DOMAIN", "")
    domain_label = env_domain.capitalize() if env_domain else "Healthcare, Finance, and Legal"
    return {
        "name": f"A²-Bench {domain_label} Green Agent",
        "description": f"Evaluates AI agent safety, security, reliability, and compliance in the {domain_label} domain using the A²-Score framework.",
        "url": _card_url,
        "version": "0.1.0",
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
        },
        "skills": [
            {
                "id": "evaluate-agent",
                "name": "Evaluate Agent",
                "description": "Run A²-Bench evaluation across all domains with baseline and adversarial tasks",
            }
        ],
    }


@app.post("/")
async def handle_a2a(request: Request):
    """Handle incoming A2A JSON-RPC requests."""
    body = await request.json()
    method = body.get("method", "")
    req_id = body.get("id", "1")
    params = body.get("params", {})

    if method == "tasks/send":
        return await handle_task_send(req_id, params)
    elif method == "tasks/get":
        return JSONResponse({"jsonrpc": "2.0", "id": req_id, "result": {"status": {"state": "completed"}}})
    else:
        return JSONResponse({
            "jsonrpc": "2.0", "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        })


async def handle_task_send(req_id: str, params: dict):
    """Handle tasks/send — run evaluation when triggered."""
    task_id = params.get("id", str(uuid.uuid4()))
    message = params.get("message", {})
    parts = message.get("parts", [])
    text = " ".join(p.get("text", "") for p in parts if p.get("type") == "text")

    # Extract config from the scenario
    config_override = {}
    try:
        config_override = json.loads(text) if text.strip().startswith("{") else {}
    except json.JSONDecodeError:
        pass

    # Allow env var to restrict to a single domain
    env_domain = os.environ.get("A2BENCH_DOMAIN", "")
    default_domains = [env_domain] if env_domain else ["healthcare", "finance", "legal"]

    default_config = {
        "domains": default_domains,
        "num_seeds": 3,
        "adversarial": True,
        "adversarial_strategies": ["social_engineering", "prompt_injection", "constraint_exploitation"],
    }
    config = {**default_config, **config_override}

    if not _participant_endpoint:
        return JSONResponse({
            "jsonrpc": "2.0", "id": req_id,
            "error": {"code": -32000, "message": "No participant endpoint configured"}
        })

    logger.info(f"Starting evaluation of purple agent at {_participant_endpoint}")
    results = run_evaluation(_participant_endpoint, config)

    results_text = json.dumps(results, indent=2)

    return JSONResponse({
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "id": task_id,
            "status": {
                "state": "completed",
                "message": {
                    "role": "agent",
                    "parts": [{"type": "text", "text": results_text}],
                },
            },
            "artifacts": [
                {
                    "name": "evaluation_results",
                    "parts": [{"type": "text", "text": results_text}],
                }
            ],
        },
    })


def main():
    parser = argparse.ArgumentParser(description="A²-Bench Green Agent (A2A Server)")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9009)
    parser.add_argument("--card-url", default=None, help="Public URL for agent card")
    parser.add_argument("--participant-endpoint", default=None,
                        help="Override purple agent endpoint (default: auto-discovered from scenario)")
    args = parser.parse_args()

    global _card_url, _participant_endpoint
    _card_url = args.card_url or f"http://{args.host}:{args.port}"

    # In Docker Compose, the participant is at http://agent_under_test:9009
    _participant_endpoint = args.participant_endpoint or os.environ.get(
        "PARTICIPANT_ENDPOINT", "http://agent_under_test:9009"
    )

    logger.info(f"A²-Bench Green Agent starting on {args.host}:{args.port}")
    logger.info(f"Purple agent endpoint: {_participant_endpoint}")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
