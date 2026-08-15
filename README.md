# Code Assistant

A sandboxed coding agent built with the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/). Give it a task in plain English and it reads, writes, edits, and runs code to get it done — all inside an isolated Docker container so nothing it does can touch your real system.

## How it works

A single agent (`agent.py`) is given five tools (`tools.py`) and runs in a loop (`main.py`): you type a task, the agent decides which tools to call, calls them, sees the results, and keeps going until it has a final answer — all automatically via the Agents SDK's built-in agentic loop (capped at 30 turns per task).

### Tools

- `list_directory(path)` — list files/folders in the workspace
- `read_file(path)` — read a file's contents
- `write_file(path, content)` — create a file, or fully overwrite one
- `edit_file(path, old_text, new_text)` — replace an exact, unique block of text in an existing file (safer than a full overwrite)
- `run_command(command)` — run a shell command and get back stdout/stderr/exit code

All tools are scoped to a `/workspace` directory — the agent can't read, write, or run anything outside it.

### Sandboxing

Everything runs inside a Docker container. Only the local `workspace/` folder is mounted in (as `/workspace`), so file edits and shell commands the agent runs are contained to that folder and the disposable container — your host machine and the rest of your files are never exposed to it. There is currently no guard against destructive commands *within* the workspace itself (e.g. `rm -rf .`) — the sandbox limits the blast radius to disposable files, but doesn't prevent them from being wiped.

### Reliability features

- **Retry on rate limits** — transient API rate-limit errors are retried with backoff instead of crashing the session.
- **Safe history trimming** — conversation history is capped to bound token usage per request, but only ever cut at whole-turn boundaries so a tool call is never separated from its result.
- **Session logging** — every task is appended to `workspace/logs.jsonl` (timestamp, tool calls made, whether it self-verified, token usage), so agent behavior can be audited after the fact rather than just trusted.

## Setup

1. Add your OpenAI API key to `.env`:
   ```
   OPENAI_API_KEY=sk-...
   ```
2. Build the image:
   ```
   docker build -t coding-agent .
   ```

## Usage

```
docker run -it --rm -v "<path-to>/coding_agent/workspace:/workspace" --env-file .env coding-agent
```

You'll get a `Task:` prompt. Type what you want done; type `exit` to quit. Conversation history carries across turns within a session, so you can give follow-up instructions. Give the whole task on one line — pasting multi-line text can get split into separate, fragmented tasks by the terminal.

## Known limitations

- It will sometimes guess at an unclear/incomplete instruction and act confidently on the guess instead of asking for clarification.
- Its self-written tests can occasionally encode a bug's actual (wrong) behavior as the expected/correct value, rather than the intended behavior — meaning "tests pass" doesn't always mean "the code is right."
- Always review what it did rather than trusting its summary at face value, especially for anything beyond a routine, well-specified task.

## Project structure

```
coding_agent/
  agent.py                     # agent definition + instructions
  tools.py                     # the 5 sandboxed tools
  main.py                      # terminal entry point / conversation loop
  Dockerfile                   # builds the sandboxed image
  workspace/                   # mounted sandbox - the only filesystem the agent can touch
```
