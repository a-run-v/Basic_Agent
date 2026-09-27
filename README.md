# aiagent-basic

A hands-on, minimal walkthrough of building an AI agent from scratch using a **local Ollama** model through the **OpenAI SDK**.

Each `stepN.py` file is a self-contained, runnable example that adds one concept on top of the previous one. Read them in order.

| File | What it teaches |
| --- | --- |
| `step1.py` | One-shot chat completion against a local model |
| `step2.py` | Multi-turn chat loop with conversation memory |
| `step3.py` | Tool / function calling — a real tool-calling agent loop |
| `main.py` | Package entrypoint stub |
| `notes.txt` | Sample document the agent in `step3.py` reads |

## Requirements

- Python 3.14+ (`uv` manages this via `.python-version`)
- [Ollama](https://ollama.com) installed and running (`ollama serve`)

## Setup

```bash
uv sync                      # or: pip install -r requirements.txt
```

Pull the models used by the examples (once):

```bash
ollama pull qwen2.5:3b
ollama pull qwen2.5-coder:3b-instruct-q4_K_M
ollama pull qwen2.5-coder:14b
```

Verify what's available with `ollama list` — the model string passed to the API must match exactly.

## Running the steps

```bash
uv run step1.py
uv run step2.py
uv run step3.py
```

## The walkthrough

### Step 1 — Single turn

`step1.py` initialises an `OpenAI` client pointed at Ollama's OpenAI-compatible endpoint
(`http://localhost:11434/v1`) and sends a single user message. Note that `api_key='ollama'` is
required by the SDK but ignored by Ollama.

### Step 2 — Conversation memory

`step2.py` adds a REPL loop. Every turn appends the user message and the assistant reply to a
`messages` list, so the model has context. The history is truncated to the last 10 messages to
keep the prompt bounded.

### Step 3 — Tool calling

`step3.py` is the actual agent. The pieces:

- **`TOOL_SCHEMAS`** — a JSON-Schema description of the `read_file` function, passed to the model
  as `tools=`. The schema is what tells the model *what* it can call and *when*.
- **`get_tool_call(reply)`** — a normalisation wrapper. Hosted models return a structured
  `reply.tool_calls` object; local models often ignore it and instead emit raw JSON text inside
  `reply.content`. `get_tool_call` handles both, returning `{"name": ..., "arguments": {...}}` or
  `None`.
- **The agent loop** — send messages → inspect the reply → if a tool was requested, run it and
  append the result → loop again. When no tool call comes back, the model's reply *is* the final
  answer.

The example asks the model to summarize `notes.txt`, which the model does by calling
`read_file(path="notes.txt")`.

## Why the `get_tool_call` wrapper exists

This trips up everyone building agents on local models:

1. The OpenAI tool-calling protocol puts the call in `reply.tool_calls`, and `reply.content` is
   typically `None` when a tool is invoked.
2. Ollama's support for that is inconsistent — many open-source models (Qwen, Llama 3, …) just
   print the JSON object as plain text: `{"name": "read_file", "arguments": {"path": "notes.txt"}}`.
3. So `get_tool_call` tries `tool_calls` first, then falls back to slicing the first `{` … last `}`
   out of the message text and validating that it has `name` and `arguments`.

Once parsed, arguments may arrive as a JSON *string* rather than a dict, so the loop re-parses
them before dispatching: `step3.py:90`.

## Requirements

`openai>=3.19.2` (see `pyproject.toml`).

## License

Personal learning project — use freely.
