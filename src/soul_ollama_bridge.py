import requests
import json

def ask_ollama(prompt, model="gpt-soul"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False
        })
    )

    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Error: {response.text}"


if __name__ == "__main__":
    while True:
        user_input = input("🧠 You: ")
        reply = ask_ollama(user_input)
        print(f"GPTSoul 🕊️: {reply}")
