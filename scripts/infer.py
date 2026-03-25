from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from common import load_config_with_extends
from generalist_vla_agent import GeneralistVLAAgent
from generalist_vla_agent.utils.types import Observation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MVP VLA inference flow.")
    parser.add_argument("--config", type=str, default="configs/infer.yaml")
    parser.add_argument("--instruction", type=str, default=None)
    parser.add_argument("--prev-action", type=str, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config_with_extends(args.config)

    observation = Observation(
        rgb=config["observation_defaults"]["rgb"],
        depth=config["observation_defaults"]["depth"],
        text=config["observation_defaults"].get("text", ""),
    )
    instruction = args.instruction or config["inference"]["instruction"]
    prev_action = args.prev_action or config.get("inference", {}).get("prev_action")

    agent = GeneralistVLAAgent.from_config(config)
    context = {"prev_action": prev_action} if prev_action else {}
    result = agent.step(instruction_text=instruction, observation=observation, context=context)

    print(
        f"action_name={result['action_name']} "
        f"confidence={result['confidence']:.2f} "
        f"metadata={result['params']}"
    )


if __name__ == "__main__":
    main()
