# Code Assistant

A sandboxed coding agent built with the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/). Give it a task in plain English and it reads, writes, edits, and runs code to get it done — all inside an isolated Docker container so nothing it does can touch your real system.

## How it works

A single agent (`agent.py`) is given four tools (`tools.py`) and runs in a loop (`main.py`): you type a task, the agent decides which tools to call, calls them, sees the results, and keeps going until it has a final answer — all automatically via the Agents SDK's built-in agentic loop.

### Tools

- `list_directory(path)` — list files/folders in the workspace
- `read_file(path)` — read a file's contents
- `write_file(path, content)` — create a file, or fully overwrite one
- `edit_file(path, old_text, new_text)` — replace an exact, unique block of text in an existing file (safer than a full overwrite)
- `run_command(command)` — run a shell command and get back stdout/stderr/exit code

All tools are scoped to a `/workspace` directory — the agent can't read, write, or run anything outside it.

### Sandboxing

Everything runs inside a Docker container. Only the local `workspace/` folder is mounted in (as `/workspace`), so file edits and shell commands the agent runs are contained to that folder and the disposable container — your host machine and the rest of your files are never exposed to it.

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

You'll get a `Task:` prompt. Type what you want done; type `exit` to quit. Conversation history carries across turns within a session, so you can give follow-up instructions.

## Project structure

```
coding_agent/
  agent.py       # agent definition + instructions
  tools.py       # the 5 sandboxed tools
  main.py        # terminal entry point / conversation loop
  Dockerfile     # builds the sandboxed image
  workspace/     # mounted sandbox - the only filesystem the agent can touch
```
