import os
from google import genai

# Initialize Gemini client
client = genai.Client(api_key=os.environ["GOOGLE_GENAI_API_KEY"])

def get_gemini_client():
    return client
