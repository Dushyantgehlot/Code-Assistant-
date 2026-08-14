import asyncio
import json
from datetime import datetime, timezone

from dotenv import load_dotenv
from agents import Runner, trace

from agent import coding_agent
from tools import WORKSPACE

load_dotenv(override=True)

LOG_PATH = WORKSPACE / "logs.jsonl"


def log_task(task: str, result) -> None:
    tool_calls = [
        item.tool_name
        for item in result.new_items
        if getattr(item, "type", None) == "tool_call_item"
    ]
    usage = result.context_wrapper.usage
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "final_output": result.final_output,
        "tool_calls": tool_calls,
        "tool_call_count": len(tool_calls),
        "self_verified": "run_command" in tool_calls,
        "asked_without_investigating": (
            "?" in str(result.final_output) and len(tool_calls) == 0
        ),
        "requests": usage.requests,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
    }
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


async def main():
    print("Coding Agent ready. Type a task, or 'exit' to quit.")
    history = []
    while True:
        task = input("\nTask: ").strip()
        normalized = task.lower()
        if normalized.startswith("task:"):
            normalized = normalized[len("task:"):].strip()
        if normalized in ("exit", "quit"):
            break
        if not task:
            continue
        history.append({"role": "user", "content": task})
        with trace("Coding Agent run"):
            result = await Runner.run(coding_agent, history)
        history = result.to_input_list()
        log_task(task, result)
        print(f"\n{result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
