import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv

# For Gemini API key use
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def embed_texts(texts: list[str], task_type="RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """
    Embeds each text individually using Gemini API (no batching).
    Returns a list of embedding vectors (list of floats).
    """
    vectors = []

    for i, text in enumerate(texts):
        try:
            result = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type=task_type
            )
            if isinstance(result, dict) and "embedding" in result:
                vectors.append(result["embedding"])
            else:
                print(f"[⚠️] Unexpected response at index {i}: {result}")
        except Exception as e:
            print(f"[❌] Error embedding text at index {i}: {e}")
            vectors.append([])

    return vectors
