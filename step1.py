from openai import OpenAI


def main():
    # Initialize the client pointing to your local Ollama server
    client = OpenAI(
        base_url='http://localhost:11434/v1',
        api_key='ollama',  # Required by the SDK, but ignored by Ollama
        timeout=120.0
    )

    messages = [
        {
            'role': 'user',
            'content': 'Explain the difference between a list and a tuple in Python.',
        }
    ]

    # Ensure this matches exactly what is shown in 'ollama list'
    try:
        chat_completion = client.chat.completions.create(
            model='qwen2.5:3b',
            messages=messages,
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Print the response content
    if not chat_completion.choices:
        print("No response received.")
        return

    reply = chat_completion.choices[0].message.content
    print(reply)


if __name__ == "__main__":
    main()


