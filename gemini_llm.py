from google import genai
import os
from dotenv import load_dotenv
from google.genai import types

load_dotenv()

client = genai.Client(api_key=os.getenv("gemini-api-key"))

response = client.models.generate_content(
    model="gemini-3-flash-preview", contents="Explain how AI works in a few words",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0),
        temperature=0.1
        # Turn off thinking:
        # thinking_config=types.ThinkingConfig(thinking_budget=0)
        # Turn on dynamic thinking:
        # thinking_config=types.ThinkingConfig(thinking_budget=-1)
    ),
)
print(response.text)