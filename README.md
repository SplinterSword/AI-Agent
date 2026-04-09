# Small Code

A small CLI-based AI coding agent built with the Google Gen AI Python SDK.

The project sends a user prompt to Gemini, allows the model to call a small set of local tools, executes those tools on disk, and feeds the results back to the model until it produces a final natural-language answer.

`calculator/` is not the main product. It is a dummy project included purely as a safe showcase workspace so the agent has something realistic to inspect, modify, and run.

### Video Demo
[Youtube Video](https://youtu.be/5adcj8urrgg)

## What This Project Does

At a high level, this repository demonstrates a simple "tool-using coding agent" pattern:

1. A user gives the CLI a prompt.
2. Gemini receives the prompt plus a system instruction and a list of available functions.
3. Gemini can choose to call one or more tools.
4. The Python app executes those tools locally.
5. Tool results are appended to the conversation.
6. Gemini continues reasoning with the new information.
7. When Gemini stops calling tools and returns plain text, the CLI prints the final answer.

This is intentionally small and easy to read. It is a good learning project for:

- understanding tool/function calling
- building a local coding assistant loop
- experimenting with safe filesystem boundaries
- seeing how an LLM can inspect and operate on a codebase

## Core Features

- CLI entrypoint that accepts a natural-language prompt
- Gemini integration using `google-genai`
- four local tools exposed to the model:
  - list files and directories
  - read file contents
  - write or overwrite files
  - run Python files with optional arguments
- path safety checks to prevent escaping the allowed workspace
- optional verbose mode for debugging tool usage and token counts
- a dummy sample project under `calculator/` for the agent to work on

## Important Design Choice

The agent does not operate on the entire repository by default.

In [`call_functions.py`](/home/splintersword/extraStorage/Projects/ai-agent/call_functions.py), every tool call is injected with:

```python
args["working_directory"] = "./calculator"
```

That means the LLM-facing tools are sandboxed to the `calculator/` folder, not the repo root.

So even though the main agent code lives at the top level:

- the user asks the agent for coding help
- the model sees relative paths only
- the tool implementations resolve those paths against `./calculator`

This is why the demo project matters: it is the controlled workspace the agent is allowed to manipulate.

## Repository Structure

```text
.
├── main.py                         # CLI entrypoint for the Gemini-powered agent
├── prompt.py                       # System instruction sent to the model
├── call_functions.py               # Tool registration and dispatcher
├── config.py                       # Shared constants (currently MAX_CHARS)
├── functions/
│   ├── get_files_info.py           # Directory listing tool
│   ├── get_file_content.py         # File reader tool
│   ├── write_file.py               # File writer tool
│   └── run_python_file.py          # Python execution tool
├── tests/
│   ├── test_get_files_info.py      # Smoke/demo script for get_files_info
│   ├── test_get_file_content.py    # Smoke/demo script for get_file_content
│   ├── test_write_file.py          # Smoke/demo script for write_file
│   └── test_run_python_file.py     # Smoke/demo script for run_python_file
├── calculator/                     # Dummy project used to showcase the agent
│   ├── main.py                     # Simple calculator CLI
│   ├── tests.py                    # unittest suite for the calculator demo
│   ├── lorem.txt                   # Sample file for file-reading/writing demos
│   ├── README.md                   # Minimal placeholder README
│   └── pkg/
│       ├── calculator.py           # Expression evaluator
│       ├── render.py               # JSON output formatter
│       └── morelorem.txt           # Another sample text file
├── pyproject.toml                  # Project metadata and dependencies
└── uv.lock                         # Locked dependencies for uv
```

## Requirements

- Python 3.12+
- a Gemini API key exposed as `GEMINI_API_KEY`
- network access when running the actual agent, since it calls the Gemini API

The repo includes a [`.python-version`](/home/splintersword/extraStorage/Projects/ai-agent/.python-version) file pinned to `3.12`.

## Dependencies

Defined in [`pyproject.toml`](/home/splintersword/extraStorage/Projects/ai-agent/pyproject.toml):

- `google-genai==1.12.1`
- `python-dotenv==1.1.0`

## Setup

### Using `uv` (recommended)

```bash
uv sync
```

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

### Using `pyenv` + pip

Because the repo is pinned to Python 3.12, a typical setup would look like:

```bash
pyenv install 3.12
pyenv local 3.12
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Then add:

```env
GEMINI_API_KEY=your_api_key_here
```

to a `.env` file in the project root.

## Running the Agent

Basic usage:

```bash
uv run python main.py "Summarize the calculator project"
```

Verbose mode:

```bash
uv run python main.py "List the files and explain what each one does" --verbose
```

The CLI defined in [`main.py`](/home/splintersword/extraStorage/Projects/ai-agent/main.py) accepts:

- `user_prompt`: required positional argument
- `--verbose`: optional flag that prints tool calls and token counts

## Example Prompts

Because the tools are sandboxed to `calculator/`, prompts should target files inside that demo project. For example:

- `Summarize this codebase`
- `Read main.py and explain how the calculator works`
- `List the files in pkg and describe them`
- `Run the calculator tests and tell me what failed`
- `Create a new notes.txt file describing the bug in test_complex_expression`

## How the Agent Loop Works

The main loop in [`main.py`](/home/splintersword/extraStorage/Projects/ai-agent/main.py) behaves like this:

- loads environment variables with `python-dotenv`
- creates a `genai.Client` using `GEMINI_API_KEY`
- sends the user's prompt as the first message
- calls `client.models.generate_content(...)` with:
  - model: `gemini-2.5-flash`
  - system instruction from [`prompt.py`](/home/splintersword/extraStorage/Projects/ai-agent/prompt.py)
  - tool declarations from [`call_functions.py`](/home/splintersword/extraStorage/Projects/ai-agent/call_functions.py)
- appends the model response to conversation history
- executes any returned function calls
- appends tool responses back into the conversation
- repeats for up to 20 iterations
- exits early once the model returns plain text instead of more function calls

If no final answer is produced after 20 iterations, the program exits with:

```text
Maximum iterations reached
```

## System Prompt

The system prompt in [`prompt.py`](/home/splintersword/extraStorage/Projects/ai-agent/prompt.py) is intentionally short. It tells the model:

- it is a helpful AI coding agent
- it should make a function call plan
- it can list files, read files, run Python files, and write files
- all paths must be relative to the working directory
- the working directory is injected automatically for safety

This keeps the example easy to understand while still being enough for basic tool use.

## Tooling Architecture

[`call_functions.py`](/home/splintersword/extraStorage/Projects/ai-agent/call_functions.py) is the bridge between Gemini function calls and local Python functions.

It does three main things:

1. Registers tool schemas with Gemini using `types.Tool(...)`.
2. Maps function names to local implementations.
3. Dispatches function calls, injects `working_directory="./calculator"`, and wraps results back into `types.Part.from_function_response(...)`.

It also handles two important error paths:

- unknown function names return an `"Unknown function"` error
- Python exceptions raised by tool implementations are caught and returned as tool errors instead of crashing the whole loop

## Available Tools

### `get_files_info`

Defined in [`functions/get_files_info.py`](/home/splintersword/extraStorage/Projects/ai-agent/functions/get_files_info.py).

Purpose:
- list files in a directory relative to the working directory
- return each entry's name, file size, and whether it is a directory

Parameters:
- `directory` (optional, defaults to `"."`)

Behavior:
- resolves the requested path against the sandbox root
- blocks path traversal outside the working directory
- errors if the target is not a directory
- returns newline-separated records such as:

```text
main.py: file_size=740, is_dir=False
pkg: file_size=4096, is_dir=True
```

Notes:
- output ordering depends on `os.listdir(...)` and is not explicitly sorted
- directory sizes come from filesystem metadata and are not recursive sizes

### `get_file_content`

Defined in [`functions/get_file_content.py`](/home/splintersword/extraStorage/Projects/ai-agent/functions/get_file_content.py).

Purpose:
- read a text file relative to the working directory

Parameters:
- `file_path` (required)

Behavior:
- blocks reads outside the sandbox root
- errors if the target does not exist or is not a regular file
- reads up to `MAX_CHARS` characters from [`config.py`](/home/splintersword/extraStorage/Projects/ai-agent/config.py)
- appends a truncation notice if the file is longer than the limit

Current config:

```python
MAX_CHARS = 10000
```

Notes:
- files are opened in text mode
- binary files or unusual encodings may fail

### `write_file`

Defined in [`functions/write_file.py`](/home/splintersword/extraStorage/Projects/ai-agent/functions/write_file.py).

Purpose:
- write or overwrite file content inside the sandboxed workspace

Parameters:
- `file_path` (required)
- `content` (required)

Behavior:
- blocks writes outside the working directory
- errors if the target path is a directory
- creates missing parent directories if needed
- overwrites the entire file content
- returns a success message with the number of characters written

Example success response:

```text
Successfully wrote to "notes.txt" (42 characters written)
```

### `run_python_file`

Defined in [`functions/run_python_file.py`](/home/splintersword/extraStorage/Projects/ai-agent/functions/run_python_file.py).

Purpose:
- execute a Python file inside the sandboxed workspace and capture output

Parameters:
- `file_path` (required)
- `args` (optional list of strings)

Behavior:
- blocks execution outside the working directory
- errors if the target is missing, is a directory, or does not end in `.py`
- runs:

```text
python <target_file> [args...]
```

- sets `cwd` to the working directory
- captures both stdout and stderr
- times out after 30 seconds
- returns output plus a success or non-zero exit message

Output format:

- `STDERR:` section if present
- `STDOUT:` section if present
- `No output produced` if neither stream contains output
- `Python file executed successfully` for exit code `0`
- `Process exited with code X` otherwise

## Security Model

Each tool uses the same pattern:

- convert the sandbox root to an absolute path
- join the user-provided relative path onto that root
- normalize the result
- compare with `os.path.commonpath(...)`

If the final path escapes the working directory, the tool rejects the operation.

Examples of blocked access:

- trying to read `/bin/cat`
- trying to list `../`
- trying to execute `../main.py`
- trying to write to `/tmp/temp.txt`

This is a simple but useful safeguard for a demo agent.

## The Dummy `calculator/` Project

`calculator/` exists to showcase the main project. It is intentionally small, easy to inspect, and safe for the agent to operate on.

It contains:

- a simple CLI calculator in [`calculator/main.py`](/home/splintersword/extraStorage/Projects/ai-agent/calculator/main.py)
- expression parsing/evaluation logic in [`calculator/pkg/calculator.py`](/home/splintersword/extraStorage/Projects/ai-agent/calculator/pkg/calculator.py)
- JSON formatting in [`calculator/pkg/render.py`](/home/splintersword/extraStorage/Projects/ai-agent/calculator/pkg/render.py)
- a `unittest` test suite in [`calculator/tests.py`](/home/splintersword/extraStorage/Projects/ai-agent/calculator/tests.py)
- sample text files for read/write demos

### Calculator CLI Behavior

With no arguments:

```bash
uv run python calculator/main.py
```

prints:

```text
Calculator App
Usage: python main.py "<expression>"
Example: python main.py "3 + 5"
```

With an expression:

```bash
uv run python calculator/main.py "3 + 5 * 2"
```

prints:

```json
{
  "expression": "3 + 5 * 2",
  "result": 13
}
```

### How the Calculator Works

The calculator:

- tokenizes expressions by splitting on whitespace
- supports `+`, `-`, `*`, and `/`
- parses infix expressions using two stacks:
  - a value stack
  - an operator stack
- applies operators based on a custom precedence table

The current precedence values in [`calculator/pkg/calculator.py`](/home/splintersword/extraStorage/Projects/ai-agent/calculator/pkg/calculator.py) are:

```python
{
    "+": 2,
    "-": 1,
    "*": 3,
    "/": 2,
}
```

This is non-standard because it effectively makes `*` highest, `+` and `/` tied, and `-` lowest.

Important limitation:

Expressions must already be space-separated. For example:

- works: `3 + 5`
- does not work: `3+5`

There is also no support for:

- parentheses
- unary operators
- variables
- functions
- robust syntax recovery

## Testing

There are two kinds of tests in this repository.

### 1. Root-level tool demo scripts

The files under [`tests/`](/home/splintersword/extraStorage/Projects/ai-agent/tests) are simple executable scripts that print tool results. They are closer to smoke tests or demonstrations than formal assertion-heavy tests.

Commands:

```bash
uv run python tests/test_get_files_info.py
uv run python tests/test_get_file_content.py
uv run python tests/test_write_file.py
uv run python tests/test_run_python_file.py
```

These scripts demonstrate:

- successful operations inside `calculator/`
- blocked operations outside `calculator/`
- file reads and writes
- Python execution and error handling

Note:

- `tests/test_write_file.py` is stateful and overwrites [`calculator/lorem.txt`](/home/splintersword/extraStorage/Projects/ai-agent/calculator/lorem.txt) and [`calculator/pkg/morelorem.txt`](/home/splintersword/extraStorage/Projects/ai-agent/calculator/pkg/morelorem.txt)

### 2. Calculator unit tests

The demo calculator includes a real `unittest` suite:

```bash
uv run python calculator/tests.py
```

It covers:

- addition
- subtraction
- multiplication
- division
- simple multi-operator expressions
- empty expressions
- invalid tokens
- insufficient operands

## Verified Behavior

The following commands were verified locally while writing this README:

- `uv run python calculator/main.py`
- `uv run python calculator/main.py "3 + 5 * 2"`
- `uv run python tests/test_get_files_info.py`
- `uv run python tests/test_get_file_content.py`
- `uv run python tests/test_write_file.py`
- `uv run python tests/test_run_python_file.py`

A direct `python ...` invocation did not work in this environment because Python 3.12 was not installed through `pyenv`, while `uv run ...` worked correctly.

## Known Issues and Limitations

### Main agent limitations

- the working directory is hardcoded to `./calculator`
- only four tools are exposed
- there is no delete, rename, move, or shell command tool
- `write_file` always overwrites rather than patching or appending
- `get_file_content` reads text only and truncates after 10,000 characters
- `run_python_file` only runs `.py` files
- the CLI is single-prompt and not an interactive REPL
- the agent depends on a valid `GEMINI_API_KEY` and working network access

### Calculator demo limitations

- expressions must be whitespace-separated
- there is no parentheses support
- precedence handling is inconsistent

One concrete consequence of the precedence bug:

```bash
uv run python calculator/tests.py
```

currently fails `test_complex_expression`:

```text
AssertionError: -3.0 != 7
```

That happens because the calculator is effectively evaluating operators with the precedence order `* > + = / > -`, which is not standard arithmetic behavior.

This bug is in the demo calculator, not in the agent framework itself.

## Potential Improvements

If you want to grow this project beyond a learning demo, likely next steps would be:

- make the working directory configurable instead of hardcoded
- add proper unit tests with assertions for the tool layer
- add richer file operations such as patching, append, rename, and delete
- switch `run_python_file` to use `sys.executable` for more predictable interpreter selection
- add structured logging around tool calls and model responses
- support an interactive chat session instead of a single prompt
- improve the calculator demo or replace it with a larger sample repo
- expand the system prompt with planning and editing conventions

## File-by-File Notes

### [`main.py`](/home/splintersword/extraStorage/Projects/ai-agent/main.py)

- parses CLI arguments
- initializes the Gemini client
- maintains the message history
- loops over tool-calling and final response generation
- prints token counts in verbose mode

### [`prompt.py`](/home/splintersword/extraStorage/Projects/ai-agent/prompt.py)

- stores the system prompt as a plain multi-line string

### [`call_functions.py`](/home/splintersword/extraStorage/Projects/ai-agent/call_functions.py)

- imports tool schemas and implementations
- registers function declarations with Gemini
- maps Gemini tool names to Python callables
- injects the `./calculator` working directory

### [`config.py`](/home/splintersword/extraStorage/Projects/ai-agent/config.py)

- currently defines `MAX_CHARS = 10000`

### [`functions/get_files_info.py`](/home/splintersword/extraStorage/Projects/ai-agent/functions/get_files_info.py)

- lists directory entries with size and `is_dir`

### [`functions/get_file_content.py`](/home/splintersword/extraStorage/Projects/ai-agent/functions/get_file_content.py)

- reads file contents with a character cap

### [`functions/write_file.py`](/home/splintersword/extraStorage/Projects/ai-agent/functions/write_file.py)

- writes file content and creates missing parent directories

### [`functions/run_python_file.py`](/home/splintersword/extraStorage/Projects/ai-agent/functions/run_python_file.py)

- executes Python files in the sandbox and captures their output

## Summary

This repo is a compact example of a tool-using coding agent:

- Gemini chooses when to call tools
- Python executes those tools locally
- the tool sandbox is intentionally restricted to `calculator/`
- the calculator project is just a dummy target for showcasing the agent

If you want to understand function calling, controlled file access, and a minimal agent loop without a lot of framework code, this repository is a strong starting point.
