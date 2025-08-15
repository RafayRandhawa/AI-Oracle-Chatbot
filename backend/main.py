from nt import error
from auth.auth_routes import auth_router
from requests import status_codes
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_handler import generate_sql_from_prompt
from db_handler import execute_query,parameterize_query,is_safe_query,extract_db_metadata
import os
from fastapi.responses import JSONResponse
from embedder import embed_texts
from pinecone_utils import  query_similar_metadata
from oracle_metadata import full_metadata_embedding_pipeline
from dotenv import load_dotenv
from auth.auth_service import get_current_user_from_cookie
load_dotenv()   

# Initialize the FastAPI application
app = FastAPI(
    title="AI-Powered Oracle Chatbot API",
    description="Converts user prompts into SQL queries, executes them on Oracle DB, and returns the results.",
    version="1.0.0"
)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

origins = [
    "http://localhost:5173",   # Front
    "http://localhost:5678",  # N8N
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)
# Define a Pydantic model for the expected input structure from the frontend
class QueryRequest(BaseModel):
    prompt: str  # This is the user prompt 

# Define a Pydantic model for the response 
class QueryResponse(BaseModel):
    generated_sql: str
    results: list | dict  
    
class SimilarRequest(BaseModel):
    query: str
    
    
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
def db_direct(query:str, user=Depends(get_current_user_from_cookie)):
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


@app.post("/similar-metadata")
def semantic_metadata_search(req: SimilarRequest):
    if not req.query:
        
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "failed", "error": "Missing Query"}
         )
    
    user_embedding = embed_texts([req.query], task_type="RETRIEVAL_QUERY")[0]
    similar_metadata = query_similar_metadata(user_embedding)
    return {"context": similar_metadata}


@app.on_event("startup")
def preload_embeddings():
    extract_db_metadata(force_refresh=False)
    print("✅ DB connection & metadata cache initialized. No embeddings done.")


@app.post("/embed-metadata")
def embed_metadata(owner: str = Query(os.getenv('DB_USER'), description="owner/name for pipeline")):
    """
    Trigger the full metadata -> embeddings -> upsert pipeline on demand.
    """
    try:
        full_metadata_embedding_pipeline(owner=owner)
        return {"success": True, "message": "Embedding pipeline completed"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "failed", "error": "Vector Embeddings cannot be completed at the moment"})

