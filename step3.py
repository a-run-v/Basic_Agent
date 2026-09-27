import json
import os

from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize the client pointing to your local Ollama server
client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
    timeout=60.0
)


def read_file(path):
    """Read a text file and return its contents"""
    try:
        with open(os.path.join(BASE_DIR, path), "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        return f"Error: cannot read {path} ({e})"


def get_tool_call(reply):
    """Return the tool the model wants to run as {"name": ..., "arguments": {...}}.

    Ollama sends the tool call as plain JSON text instead of a tool_call,
    so if there is no tool_call we read it out of the message text.
    """
    if reply.tool_calls:
        call = reply.tool_calls[0]
        return {"name": call.function.name, "arguments": call.function.arguments}

    text = reply.content or ""
    if "{" not in text or "}" not in text:
        return None

    try:
        call = json.loads(text[text.index("{"):text.rindex("}") + 1])
    except ValueError:
        return None

    if "name" in call and "arguments" in call:
        return call
    return None



TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a text file and return its contents",   
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Name of the file to read"}
                },
                "required": ["path"],
            },
        },
    },
]

messages = [
    {"role": "user", "content": "What is inside notes.txt? Summarize in one line"},
]

while True:
    chat_completion = client.chat.completions.create(
        model='qwen2.5-coder:14b',  # use a model that is good at tool calling
        messages=messages,
        tools=TOOL_SCHEMAS,
        temperature=0,
    )

    reply = chat_completion.choices[0].message
    tool_call = get_tool_call(reply)

    # No tool call means the model is done and has given the final answer
    if tool_call is None:
        print("Summary:", reply.content)
        break

    # Run the tool the model asked for
    name = tool_call["name"]
    args = tool_call["arguments"]
    if isinstance(args, str):
        args = json.loads(args)

    print(f"Running tool: {name}({args})")
    if name == "read_file":
        result = read_file(**args)
    else:
        result = f"Error: unknown tool {name}"

    # Send the tool request and its result back, then loop for the final answer
    messages.append({"role": "assistant", "content": reply.content})
    messages.append({"role": "user", "content": f"Tool result: {result}"})
