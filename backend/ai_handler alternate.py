import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from db_handler import extract_db_metadata
import re
import logging

# Load environment variables from .env file
load_dotenv()

# Setup logging to file
log_file = 'ai_handler.log'
logging.basicConfig(
    filename=log_file,
    filemode='a',  # Append mode
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Hugging Face Inference Client using the free provider
client = InferenceClient(
    provider="featherless-ai",
    api_key=os.getenv("HF_TOKEN")
)

def generate_sql_from_prompt(prompt: str) -> str:
    """
    Generates a SQL query from a user-provided natural language prompt, enhanced with database metadata for context.

    Args:
        prompt (str): The user's query in plain English.

    Returns:
        str: A cleaned and executable SQL query.
    """
    try:
        # Retrieve latest cached database metadata (tables, columns, etc.)
        metadata = extract_db_metadata()
        logger.info("Database metadata extracted for context injection.")

        # Construct a rich, structured system prompt
        system_prompt = (
            "You are an expert AI specialized in generating SQL queries strictly for Oracle Database systems.\n\n"
            "**Database Metadata Context:**\n"
            f"{metadata}\n\n"
            "RULES:\n"
            "- Respond with ONLY a syntactically correct SQL query.\n"
            "- Do not include any explanations, notes, or markdown formatting.\n"
            "- Use the provided metadata for column names, table relationships, and constraints.\n"
            "- Avoid using 'dual' unless required.\n"
            "- Always prefer joins only when there are foreign key relationships.\n"
            "- Avoid overly complex queries.\n"
            "- The SQL query must be directly executable without any editing.\n\n"
            "**End of Metadata.**\n\n"
            "Now generate the appropriate SQL query for the following prompt:"
        )

        logger.debug(f"System prompt sent to AI: {system_prompt}")

        # Compose chat messages with system prompt and user input
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]

        # Send the prompt to the AI model
        completion = client.chat.completions.create(
            model="defog/llama-3-sqlcoder-8b",
            messages=messages,
        )

        ai_message = completion.choices[0].message.content.strip()
        logger.info(f"Raw AI response: {ai_message}")

        # Clean the AI output to ensure it's pure SQL
        cleaned_sql = clean_ai_output(ai_message)
        logger.info(f"Cleaned SQL: {cleaned_sql}")

        return cleaned_sql

    except Exception as e:
        # Handle common API error cases gracefully
        error_message = str(e)
        if "429" in error_message:
            logger.warning("Rate limit exceeded during AI call.")
            return {"error": "Rate limit exceeded. Please wait and try again."}
        elif "504" in error_message:
            logger.error("Timeout from AI provider.")
            return {"error": "AI provider timeout. Please try again later."}
        
        logger.error(f"Unexpected error in AI handler: {error_message}")
        raise RuntimeError(f"AI SQL generation failed: {error_message}")


def clean_ai_output(output: str) -> str:
    """
    Cleans the raw AI output to strip any non-SQL artifacts.

    Args:
        output (str): The AI's raw output.

    Returns:
        str: Clean SQL query string.
    """
    # Remove common formatting and noise
    output = re.sub(r'[*]+', '', output)  # Remove markdown formatting like  or **bold**
    output = re.sub(r'[!]+', '', output)   # Remove exclamation marks
    output = re.sub(r'^\d+\.\s*', '', output)  # Remove numbering like '1. '
    
    # If wrapped in markdown backticks, strip them
    if output.startswith("") and output.endswith(""):
        output = '\n'.join(output.split('\n')[1:-1]).strip()
    
    # Further clean by stripping extra spaces/newlines
    return output.strip()