/**
 * Thin API client for the FastAPI backend.
 *
 * Centralizes endpoint URLs and request/response shapes so UI components
 * don't need to know backend routing details.
 * 
 * All functions handle basic error cases and throw descriptive errors
 * that can be displayed directly to users in the UI.
 */
export type QueryResponse = {
  generated_sql: string;
  results: unknown;
};

/**
 * Base URL for the backend, configured via Vite env.
 * Example: VITE_API_URL=http://localhost:8000
 * Falls back to relative paths when empty (useful behind a reverse proxy).
 * 
 * In development: typically http://localhost:8000 (FastAPI default)
 * In production: could be https://api.yourdomain.com or relative path
 */
const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || "";

/**
 * Normalizes URL joining so we can accept values with/without trailing slashes.
 * 
 * Examples:
 * - joinUrl("http://localhost:8000", "/query") -> "http://localhost:8000/query"
 * - joinUrl("http://localhost:8000/", "query") -> "http://localhost:8000/query"
 * - joinUrl("", "/query") -> "/query" (relative path)
 */
function joinUrl(base: string, path: string): string {
  if (!base) return path;
  if (base.endsWith("/")) base = base.slice(0, -1);
  if (!path.startsWith("/")) path = `/${path}`;
  return `${base}${path}`;
}

/**
 * Send a natural-language prompt to be translated to SQL and executed.
 * 
 * This is the main chat endpoint that:
 * 1. Takes user's natural language question
 * 2. Backend generates SQL using AI
 * 3. Executes the SQL against Oracle database
 * 4. Returns both the generated SQL and query results
 * 
 * @param prompt - Natural language question about the database
 * @returns Promise with generated SQL and query results
 * @throws Error if request fails (network, server error, etc.)
 */
export async function sendQuery(prompt: string): Promise<QueryResponse> {
  const response = await fetch(joinUrl(API_BASE_URL, "/query"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    const text = await response.text().catch(() => "");
    throw new Error(text || `Request failed with status ${response.status}`);
  }

  return (await response.json()) as QueryResponse;
}

/**
 * Refresh cached database metadata on the server.
 * 
 * This forces the backend to re-scan the Oracle database schema
 * and update its cached metadata. Useful when database structure
 * has changed and you want the AI to be aware of new tables/columns.
 * 
 * @returns Promise with success message and updated metadata
 * @throws Error if refresh fails
 */
export async function refreshMetadata(): Promise<{ message: string; metadata: unknown }> {
  const response = await fetch(joinUrl(API_BASE_URL, "/refresh-metadata"));
  if (!response.ok) throw new Error("Failed to refresh metadata");
  return response.json();
}

/**
 * Execute a raw SQL query directly (guarded server-side by is_safe_query).
 * 
 * This bypasses the AI SQL generation and executes the provided SQL directly.
 * The backend validates the query for safety (no DROP, DELETE, etc.) before execution.
 * 
 * @param query - Raw SQL query to execute
 * @returns Promise with query results
 * @throws Error if query is unsafe or execution fails
 */
export async function dbDirect(query: string): Promise<unknown> {
  const url = new URL(joinUrl(API_BASE_URL, "/db-direct"), window.location.origin);
  url.searchParams.set("query", query);
  const response = await fetch(url.toString());
  if (!response.ok) throw new Error("Failed to execute direct DB query");
  return response.json();
}

/**
 * Retrieve semantically similar metadata for a natural-language query.
 * 
 * Uses vector embeddings to find database objects (tables, columns, etc.)
 * that are semantically similar to the user's query. This helps the AI
 * understand context when generating SQL.
 * 
 * @param query - Natural language query to find similar metadata for
 * @returns Promise with context information
 * @throws Error if search fails
 */
export async function similarMetadata(query: string): Promise<{ context: unknown }> {
  const response = await fetch(joinUrl(API_BASE_URL, "/similar-metadata"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!response.ok) throw new Error("Failed to search similar metadata");
  return response.json();
}

/**
 * Trigger the full metadata embedding pipeline (parameterized by owner).
 * 
 * This runs the complete pipeline to:
 * 1. Extract database metadata
 * 2. Generate vector embeddings for semantic search
 * 3. Store embeddings in vector database
 * 
 * This is typically a long-running operation and should be called
 * when you want to update the AI's knowledge of the database schema.
 * 
 * @param owner - Database owner/schema to process (default: "TIF")
 * @returns Promise with success status and message
 * @throws Error if pipeline fails
 */
export async function embedMetadata(owner = "TIF"): Promise<{ success: boolean; message: string }> {
  const url = new URL(joinUrl(API_BASE_URL, "/embed-metadata"), window.location.origin);
  url.searchParams.set("owner", owner);
  const response = await fetch(url.toString(), { method: "POST" });
  if (!response.ok) throw new Error("Failed to run embedding pipeline");
  return response.json();
}


