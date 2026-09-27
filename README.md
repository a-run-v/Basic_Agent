

# Define a list of schemas that declare the tools (functions) available to the AI model.
# This structure follows the standard format required for LLM tool-calling APIs (like OpenAI).
TOOL_SCHEMAS = [
    {
        # Specify that this tool is a executable function
        "type": "function",
        "function": {
            # The exact name of the Python function the model will look for
            "name": "read_file",
            # A natural language description that helps the model understand *when* to use this tool
            "description": "Read a text file and return its contents",
            # Define the arguments (inputs) that the model needs to provide to run this function
            "parameters": {
                "type": "object",
                "properties": {
                    # Define the 'path' parameter, its expected data type, and what it represents
                    "path": {"type": "string", "description": "Name of the file to read"}
                },
                # Explicitly state that the 'path' argument must be provided by the model
                "required": ["path"],
            },
        },
    },
]

=====

Why is get_tool_call Required?
When using standard OpenAI models (like gpt-4o), tool calling is handled at the API protocol level:

The API response returns a structured field: reply.tool_calls.
reply.content is usually None when a tool call occurs.
However, when using Ollama as a local OpenAI-compatible endpoint:

Inconsistent Function Calling Support: Not all open-source local models (or Ollama API versions) populate the native reply.tool_calls object reliably.
Raw Text JSON Responses: Many open-source models (e.g., Qwen, Llama 3) respond to tool prompts by outputting raw JSON text directly inside reply.content (e.g. {"name": "read_file", "arguments": {"path": "notes.txt"}}), while reply.tool_calls remains None.
get_tool_call acts as a normalization wrapper. It ensures your code gets a clean Python dictionary ({"name": "...", "arguments": {...}}) regardless of whether the model used official OpenAI schema structured objects or output raw JSON text inside content.

Detailed Line-by-Line Breakdown of get_tool_call

Apply
def get_tool_call(reply):
Step 1: Check for Native Structured Tool Calls

Apply
    if reply.tool_calls:
        call = reply.tool_calls[0]
        return {"name": call.function.name, "arguments": call.function.arguments}
How it works: Checks if the SDK/Ollama successfully populated the native OpenAI tool_calls array.
Result: If present, extracts the function name and arguments directly from the first tool call object and returns a normalized dictionary.
Step 2: Handle Raw Text Fallback (When tool_calls is empty)

Apply
    text = reply.content or ""
    if "{" not in text or "}" not in text:
        return None
How it works: If reply.tool_calls was empty, it inspects the plain text output in reply.content.
Guard clause: If the text doesn't contain curly braces {} at all, it means the model output plain text (a final answer, not JSON). It returns None immediately.
Step 3: Extract & Parse JSON Substring

Apply
    try:
        call = json.loads(text[text.index("{"):text.rindex("}") + 1])
    except ValueError:
        return None
text.index("{"): Finds the index of the first { in the string.
text.rindex("}"): Finds the index of the last } in the string.
text[text.index("{"):text.rindex("}") + 1]: Slices the exact JSON substring out of the response. This is crucial because local models sometimes output extra conversational text around the JSON block (e.g., "Sure, let me call the tool: {"name": ...}").
json.loads(...): Parses the sliced JSON string into a Python dictionary.
except ValueError: If the text inside {} isn't valid JSON, it catches the error and safely returns None.
Step 4: Validate Tool Schema Structure

Apply
    if "name" in call and "arguments" in call:
        return call
    return None
How it works: Checks if the parsed JSON object contains both required keys (name and arguments).
Result: Returns the dictionary if it represents a valid tool call, or None if it was just a random JSON object.

=====