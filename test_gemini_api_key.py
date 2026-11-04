from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    raise RuntimeError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model = os.getenv('GEMINI_MODEL'),
    contents = 'Explain predictive maintenance in one sentence.'
)

print(response.text)