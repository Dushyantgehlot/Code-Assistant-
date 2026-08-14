import subprocess
from pathlib import Path

from agents import function_tool

WORKSPACE = Path("/workspace").resolve()


def _resolve(path: str) -> Path:
    candidate = (WORKSPACE / path).resolve()
    if candidate != WORKSPACE and WORKSPACE not in candidate.parents:
        raise ValueError(f"Path '{path}' escapes the workspace sandbox")
    return candidate


@function_tool
def list_directory(path: str = ".") -> str:
    """List files and folders under the given path, relative to the workspace root."""
    target = _resolve(path)
    if not target.exists():
        return f"Path not found: {path}"
    entries = sorted(p.name + ("/" if p.is_dir() else "") for p in target.iterdir())
    return "\n".join(entries) if entries else "(empty)"


@function_tool
def read_file(path: str) -> str:
    """Read and return the text contents of a file, relative to the workspace root."""
    target = _resolve(path)
    if not target.is_file():
        return f"File not found: {path}"
    return target.read_text(encoding="utf-8", errors="replace")


@function_tool
def write_file(path: str, content: str) -> str:
    """Create or overwrite a file with the given content, relative to the workspace root."""
    target = _resolve(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} chars to {path}"


@function_tool
def edit_file(path: str, old_text: str, new_text: str) -> str:
    """Replace an exact block of text in an existing file with new text, leaving the rest
    of the file untouched. old_text must match exactly once in the file - include enough
    surrounding context to make it unique. Use this for modifying existing files instead
    of write_file, so unrelated content is never accidentally dropped."""
    target = _resolve(path)
    if not target.is_file():
        return f"File not found: {path}"
    content = target.read_text(encoding="utf-8", errors="replace")
    count = content.count(old_text)
    if count == 0:
        return f"old_text not found in {path} - no changes made"
    if count > 1:
        return (
            f"old_text matches {count} places in {path} - it must be unique. "
            "Include more surrounding context and try again. No changes made."
        )
    target.write_text(content.replace(old_text, new_text), encoding="utf-8")
    return f"Edited {path}"


@function_tool
def run_command(command: str) -> str:
    """Run a shell command inside the workspace sandbox and return its stdout/stderr/exit code."""
    result = subprocess.run(
        command,
        shell=True,
        cwd=WORKSPACE,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return (
        f"exit_code: {result.returncode}\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
