# Code Assistant — Project Overview

A sandboxed coding agent built with the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/). Give it a task in plain English, and it reads, writes, edits, and runs code inside an isolated Docker container to get it done — planning its own steps, using tools as needed, and checking its own work before reporting back.

## How it works

A single agent runs the OpenAI Agents SDK's built-in agentic loop: you give it a task, it decides which tools to call, calls them, reads the results, and keeps going — writing files, running commands, iterating — until it has a complete answer. Model: `gpt-4.1`.

## Capabilities

- **Understands plain-English tasks** — no special syntax or command format required.
- **Reads and writes code autonomously** — creates new files or precisely edits existing ones (targeted text replacement, not blind overwrites, so unrelated content is preserved).
- **Runs and tests its own work** — executes scripts and test suites via shell commands and checks the output before finishing.
- **Multi-step reasoning** — handles tasks that require several sequential actions (generate data, process it, verify the result) in a single request.
- **Persistent conversation within a session** — follow-up instructions build on prior context, so you can iterate with it turn by turn.
- **Session logging** — every task's tool usage and token cost is recorded for later review.

## Architecture

| Component | Purpose |
|---|---|
| `agent.py` | Agent definition and behavioral instructions |
| `tools.py` | Five sandboxed tools: list, read, write, edit, run |
| `main.py` | Terminal entry point and conversation loop |
| `Dockerfile` | Builds the isolated runtime image |
| `workspace/` | The mounted sandbox — the only filesystem the agent can touch |

## Sandboxing

The entire agent runs inside a Docker container. Only a local `workspace/` folder is mounted in, and every tool call is scoped to that directory — the agent has no access to the host filesystem or the rest of the project. This means it can operate freely — generating files, running scripts, testing changes — without any risk to the surrounding system.

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

You'll get a `Task:` prompt — describe what you want built, fixed, or tested, and the agent takes it from there. Type `exit` to quit.
