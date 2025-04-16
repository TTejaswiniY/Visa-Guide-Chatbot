import os
from google.generativeai import configure, embed_content
from dotenv import load_dotenv

load_dotenv()

# Configure with your Gemini API key
configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_embedding(text: str):
    try:
        response = embed_content(
            model="models/embedding-001",
            content=text,
            task_type="retrieval_document"
        )
        return response['embedding']
    except Exception as e:
        print("Error generating embedding:", e)
        return None
