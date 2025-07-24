# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ai_handler import generate_sql_from_prompt
from db_handler import execute_query


# Initialize the FastAPI application
app = FastAPI(
    title="AI-Powered Oracle Chatbot API",
    description="Converts user prompts into SQL queries, executes them on Oracle DB, and returns the results.",
    version="1.0.0"
)

# Define a Pydantic model for the expected input structure from the frontend
class QueryRequest(BaseModel):
    prompt: str  # This is the user prompt (natural language question)

# Define a Pydantic model for the response (optional but good practice)
class QueryResponse(BaseModel):
    generated_sql: str
    results: list | dict  # Could be a list of dicts for SELECT, or a dict for DML/DDL


@app.post("/query", response_model=QueryResponse)
def query_database(request: QueryRequest):
    """
    API endpoint to handle incoming prompts, generate SQL, execute it, and return the result.

    Args:
        request (QueryRequest): JSON body with a 'prompt' field.

    Returns:
        QueryResponse: The generated SQL and its execution result.
    """
    try:
        # 1. Generate SQL from the AI model
        generated_sql = generate_sql_from_prompt(request.prompt)
        print(f"generated_sql: {generated_sql}")
        # Optional: If AI fails to generate proper SQL
        if not generated_sql.strip().lower().startswith(("select", "insert", "update", "delete", "create", "alter", "drop","(")):
            raise HTTPException(status_code=400, detail="AI did not generate a valid SQL query.")

        # 2. Execute the SQL on Oracle DB
        db_result = execute_query(generated_sql)
        print(f"db_result: {db_result}")
        if isinstance(db_result,dict) and "error" in db_result:
            return f"{db_result['error']}: {db_result['message']}"
        else:
        # 3. Return both the generated SQL and database result
            return QueryResponse(generated_sql=generated_sql, results=db_result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/refresh-metadata")
def refresh_metadata():
    """
    API endpoint to refresh cached DB metadata.
    """
    metadata = get_db_metadata(force_refresh=True)
    return {"message": "Metadata refreshed", "metadata": metadata}