import ollama

MODEL = "qwen3:8b"

messages = [
    {
        "role": "user",
        "content": "Hello. What can you help me with?"
    }
]

response = ollama.chat(
    model=MODEL,
    messages=messages
)

print("AI:", response.message.content)
