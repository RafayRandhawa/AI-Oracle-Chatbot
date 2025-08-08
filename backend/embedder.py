import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv

# For Gemini API key use
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def embed_texts(texts: list[str], task_type="RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """
    Embeds a list of texts using the Gemini API.

    Args:
        texts: A list of strings to embed.
        task_type: The task type for the embedding.

    Returns:
        A list of embeddings, where each embedding is a list of floats.
    """
    try:
        # The model "embedding-001" is now accessible directly. [11]
        # The genai.embed_content function is a more direct way to get embeddings. [8]
        result = genai.embed_content(
            model="models/embedding-001",
            content=texts,
            task_type=task_type
        )
        return result['embedding']
    except Exception as e:
        print(f"An error occurred: {e}")
        return []