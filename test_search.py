from google import genai
from google.genai import types

API_KEY = "AIzaSyAVmjvUrIWeTy_-NVcHI6TiESYjhBj5JMc"

client = genai.Client(api_key=API_KEY)
prompt = "Qual o score IFEval e MMLU-Pro do modelo Llama 3.1 70B na Open LLM Leaderboard v2 hoje?"

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt,
    config=types.GenerateContentConfig(
        tools=[types.Tool(google_search=types.GoogleSearch())]
    )
)

print(response.text)
if response.candidates[0].grounding_metadata:
    print("\n--- Fontes ---")
    for chunk in response.candidates[0].grounding_metadata.grounding_chunks:
        if chunk.web:
            print(chunk.web.uri)
