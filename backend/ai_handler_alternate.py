import os
from dotenv import load_dotenv
from db_handler import extract_db_metadata
import re
import logging
import requests
import json

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

# URL of the local Ollama server
OLLAMA_URL = "http://localhost:11434/api/chat"

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
            "- Avoid overly complex queries when possible.\n"
            "- The SQL query must be directly executable without any editing.\n\n"
            "- Make sure that the commands are direclty executable in oracle database\n\n"
            "- IMPORTANT! Do not make use of the AS keyword as it is not for Oracle database\n\n"
            "- Go through metadata for finding the correct table and the correct column names for generated sql query\n\n"
            "- Make use of left or right joins where possible so that soime data is always returned even if some columns return empty"
            "**End of Metadata.**\n\n"
            "Now generate the appropriate SQL query for the following prompt:"
        )

        logger.debug(f"System prompt sent to AI: {system_prompt}")

        # Construct message payload for Ollama API
        payload = {
            "model": "mistral",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }

        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()

        ai_message = response.json()["message"]["content"].strip()
        logger.info(f"Raw AI response: {ai_message}")

        # Clean the AI output to ensure it's pure SQL
        cleaned_sql = clean_ai_output(ai_message)
        logger.info(f"Cleaned SQL: {cleaned_sql}")

        return cleaned_sql

    except requests.exceptions.RequestException as e:
        logger.error(f"Request to Ollama failed: {e}")
        return {"error": "Failed to reach Ollama. Is the server running?"}
    except Exception as e:
        logger.error(f"Unexpected error in AI handler: {e}")
        raise RuntimeError(f"AI SQL generation failed: {str(e)}")


def clean_ai_output(output: str) -> str:
    """
    Cleans the raw AI output to strip any non-SQL artifacts.

    Args:
        output (str): The AI's raw output.

    Returns:
        str: Clean SQL query string.
    """
    output = re.sub(r'[*]+', '', output)  # Remove markdown bold (**)
    output = re.sub(r'[!]+', '', output)   # Remove exclamation marks
    output = re.sub(r'^\d+\.\s*', '', output)  # Remove numbering

    # If wrapped in backticks, remove them
    output = output.strip('`').strip()

    return output.strip()
