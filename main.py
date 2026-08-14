import asyncio

from dotenv import load_dotenv
from agents import Runner, trace

from agent import coding_agent

load_dotenv(override=True)


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
        print(f"\n{result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
