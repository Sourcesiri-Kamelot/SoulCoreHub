from google import genai

client = genai.Client(api_key="AIzaSyA0aEpwrdm6u7UXXx6qDn9rjYgVLjYwoxw")

response = client.models.generate_content(
    model="gemini-2.0-flash", contents="Explain how AI works in a few words"
)
print(response.text)
