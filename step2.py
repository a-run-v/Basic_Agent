from openai import OpenAI

# Initialize the client pointing to your local Ollama server
client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
    timeout=30.0
)

messages = []

# Add system prompt
messages.append({
    "role": "system",
    "content": "You are a helpful AI assistant. Answer questions clearly and concisely."
})

while True:
    user_input = input("You: ")
    if user_input.strip().lower() in ("exit", "quit"):
        break

    try:
        messages.append({"role": "user", "content": user_input})

        chat_completion = client.chat.completions.create(
            model='qwen2.5-coder:3b-instruct-q4_K_M',
            messages=messages
        )

        # Validate response exists
        if not chat_completion.choices:
            print("Bot: No response received.")
            continue

        reply = chat_completion.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        print("Bot:", reply)

        # Limit memory to last 10 messages
        if len(messages) > 10:
            messages = messages[-10:]

    except Exception as e:
        print(f"An error occurred: {e}")