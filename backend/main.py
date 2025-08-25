from nt import error

from requests import status_codes
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from ai_handler import generate_sql_from_prompt
from db_handler import execute_query,parameterize_query,is_safe_query,extract_db_metadata
import os
from fastapi.responses import JSONResponse
from embedder import embed_texts
from pinecone_utils import  query_similar_metadata
from oracle_metadata import full_metadata_embedding_pipeline
from dotenv import load_dotenv
import oracledb

load_dotenv()   

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
        print(f"generated_sql: {generated_sql}\n\n")
        # Optional: If AI fails to generate proper SQL
        if not generated_sql.strip().lower().startswith(("select", "insert", "update" "create")):
           raise HTTPException(status_code=400, detail="AI did not generate a valid SQL query.")
        if not is_safe_query(generated_sql):
            return JSONResponse(
            status_code=500,
            content={"success": False, "data": None, "error": f"Database Error: {str(e)}"}
        )
        parameterized_sql, params = parameterize_query(generated_sql)
        print(f"Parameteized Query: {parameterized_sql}\n\nParameters: {params}\n\n")

        db_result = execute_query(query=parameterized_sql,params=params)
        print(f"db_result: {db_result}\n\n")
        
        if isinstance(db_result,dict) and "error" in db_result:
            return f"{db_result['error']}: {db_result['message']}"
        else:
        # 3. Return both the generated SQL and database result
            return QueryResponse(generated_sql=generated_sql, results=db_result)

    except oracledb.DatabaseError as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "data": None, "error": f"Database Error: {str(e)}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/refresh-metadata")
def refresh_metadata():
    """
    API endpoint to refresh cached DB metadata.
    """
    metadata = extract_db_metadata(force_refresh=True)
    return {"message": "Metadata refreshed", "metadata": metadata}



@app.get("/db-direct")
def db_direct(query:str):
    """
    API endpoint to execute a raw SQL query directly on the database.
    """
    print(query)
    query,params = parameterize_query(query)
    if(is_safe_query(query)):
        try:
            db_result = execute_query(query=query, params=params)
            return {"success": True, 'results': query,  "results": db_result}
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"success": False, "results": None, "error": str(e)})
    else:
        return JSONResponse(
            status_code=500,
            content={"success": False, "results": None, "error": "The following action is restricted and cannot be performed, inform the user accordingly"})


class SimilarRequest(BaseModel):
    query: str

@app.post("/similar-metadata")
def semantic_metadata_search(req: SimilarRequest):
    if not req.query:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "failed", "error": "Missing Query"}
        )
    
    try:
        user_embedding = embed_texts([req.query], task_type="RETRIEVAL_QUERY")[0]
        similar_metadata = query_similar_metadata(user_embedding)
        
        # Format the response
        formatted_results = []
        for item in similar_metadata:
            # Table-level result
            if "column_count" in item:
                formatted_results.append({
                    "type": "table",
                    "table": item.get("table", ""),
                    "score": item.get("score", 0),
                    "description": item.get("table_comment", ""),
                    "column_count": item.get("column_count", 0),
                    "primary_keys": item.get("primary_keys", []),
                    "foreign_keys": item.get("foreign_keys", []),
                    "columns": item.get("columns", [])
                })
            # Column-level result
            elif "column" in item:
                formatted_results.append({
                    "type": "column",
                    "table": item.get("table", ""),
                    "column": item.get("column", ""),
                    "score": item.get("score", 0),
                    "data_type": item.get("type", ""),
                    "is_primary_key": item.get("is_primary_key", False),
                    "is_foreign_key": item.get("is_foreign_key", False),
                    "foreign_key_ref": item.get("foreign_key_ref", "")
                })
            # Raw metadata (fallback)
            else:
                formatted_results.append(item)
        
        return {"context": formatted_results}
    
    except Exception as e:
        print(f"Error in semantic search: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "failed", "error": str(e)}
        )
 

@app.on_event("startup")
def preload_embeddings():
    metadata = extract_db_metadata(force_refresh=False)
    print(f"✅ DB connection & metadata cache initialized. Found {len(metadata)} tables. No embeddings done.")


@app.post("/embed-metadata")
def embed_metadata(owner: str = Query(os.getenv('DB_USER'), description="owner/name for pipeline")):
    """
    Trigger the full metadata -> embeddings -> upsert pipeline on demand.
    """
    try:
        # Force refresh the cache to get fresh metadata
        metadata = extract_db_metadata(owner=owner, force_refresh=True)
        
        if not metadata:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False, 
                    "message": "No metadata extracted from database",
                    "details": f"Owner '{owner}' has tables but metadata extraction failed. Check server logs."
                }
            )
        
        print(f"📊 Starting embedding pipeline for {len(metadata)} tables")
        # Log the tables we found
        for table_name in metadata.keys():
            print(f"   - {table_name}")
            
        full_metadata_embedding_pipeline(owner=owner)
        return {
            "success": True, 
            "message": f"Embedding pipeline completed for {len(metadata)} tables",
            "tables_processed": len(metadata),
            "table_names": list(metadata.keys())
        }
    except Exception as e:
        print(f"❌ Error in embed-metadata endpoint: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "failed", "error": str(e)})