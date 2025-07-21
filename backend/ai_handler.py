import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables from .env file (especially HF_TOKEN)
load_dotenv()

# Initialize Hugging Face Inference Client using a provider
client = InferenceClient(
    provider="featherless-ai",  # This is a free inference provider
    api_key=os.getenv("HF_TOKEN")  # The token is securely loaded from the .env
)


def generate_sql_from_prompt(prompt: str) -> str:
    """
    Sends a user prompt to the AI model and returns the model's raw SQL output.

    Args:
        prompt (str): A natural language prompt from the user (e.g. "Show me all employees")

    Returns:
        str: The AI model's response containing an SQL query or explanation.
    """
    try:
        # Send the prompt to the model and get a completion
        completion = client.chat.completions.create(
            model="defog/llama-3-sqlcoder-8b",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates SQL queries from natural language prompts." "You are an AI SQL expert. Convert user prompts into **ONLY** SQL queries "
                    "compatible with Oracle databases. Do not add any explanation or extra text." },
                {"role": "user", "content": prompt}
            ],
        )

        # Extract the text content from the model's response
        ai_message = completion.choices[0].message.content.strip()

        return ai_message

    except Exception as e:
        # If any error occurs during API call, return the error message
        return f"Error generating SQL: {str(e)}"
