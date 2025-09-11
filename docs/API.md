# API Documentation

## Overview

The Oracle AI Chatbot API is built with FastAPI and provides comprehensive endpoints for natural language to SQL conversion, database operations, authentication, and session management.

**Base URL**: `http://localhost:8000` (Development) / `http://localhost/api` (Production)

---

## 🔐 Authentication Endpoints

### POST `/auth/login`

Authenticate a user and return a JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "user123"
  }
}
```

**Status Codes:**
- `200` - Login successful
- `401` - Invalid credentials
- `422` - Validation error

---

### POST `/auth/logout`

Logout the current user and clear authentication cookie.

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

**Status Codes:**
- `200` - Logout successful

---

### GET `/auth/me`

Get information about the currently authenticated user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "logged_in": true,
  "user": {
    "id": 1,
    "username": "user123"
  }
}
```

**Status Codes:**
- `200` - User information retrieved
- `401` - Not authenticated

---

## 💬 Session Management Endpoints

### POST `/sessions/create`

Create a new chat session.

**Request Body:**
```json
{
  "title": "My Chat Session"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": 123,
    "title": "My Chat Session",
    "created_at": "2024-01-09T10:30:00Z",
    "user_id": 1
  }
}
```

**Status Codes:**
- `200` - Session created successfully
- `401` - Not authenticated
- `422` - Validation error

---

### GET `/sessions/list`

Get all sessions for the current user.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "session_id": 123,
      "title": "My Chat Session",
      "created_at": "2024-01-09T10:30:00Z",
      "user_id": 1
    }
  ]
}
```

**Status Codes:**
- `200` - Sessions retrieved successfully
- `401` - Not authenticated

---

### GET `/sessions/{session_id}/messages`

Get all messages for a specific session.

**Path Parameters:**
- `session_id` (integer): The ID of the session

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "message_id": 456,
      "session_id": 123,
      "role": "user",
      "content": "Show me all users",
      "created_at": "2024-01-09T10:30:00Z"
    },
    {
      "message_id": 457,
      "session_id": 123,
      "role": "assistant",
      "content": "SELECT * FROM users;",
      "created_at": "2024-01-09T10:30:05Z"
    }
  ]
}
```

**Status Codes:**
- `200` - Messages retrieved successfully
- `401` - Not authenticated
- `404` - Session not found

---

### POST `/sessions/{session_id}/messages`

Store a new message in a session.

**Request Body:**
```json
{
  "role": "user",
  "content": "Show me all users"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message_id": 456,
    "session_id": 123,
    "role": "user",
    "content": "Show me all users",
    "created_at": "2024-01-09T10:30:00Z"
  }
}
```

**Status Codes:**
- `200` - Message stored successfully
- `401` - Not authenticated
- `404` - Session not found
- `422` - Validation error

---

### DELETE `/sessions/{session_id}`

Delete a specific session and all its messages.

**Path Parameters:**
- `session_id` (integer): The ID of the session

**Response:**
```json
{
  "success": true,
  "message": "Session deleted successfully"
}
```

**Status Codes:**
- `200` - Session deleted successfully
- `401` - Not authenticated
- `404` - Session not found

---

### PUT `/sessions/{session_id}/rename`

Rename a specific session.

**Path Parameters:**
- `session_id` (integer): The ID of the session

**Request Body:**
```json
{
  "new_title": "Updated Session Title"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Session renamed successfully"
}
```

**Status Codes:**
- `200` - Session renamed successfully
- `401` - Not authenticated
- `404` - Session not found
- `422` - Validation error

---

## 🤖 Core AI Endpoints

### POST `/query`

Convert natural language to SQL and execute it against the Oracle database.

**Request Body:**
```json
{
  "prompt": "Show me all users from the users table"
}
```

**Response:**
```json
{
  "generated_sql": "SELECT * FROM users",
  "results": [
    {
      "user_id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "user_id": 2,
      "username": "jane_smith",
      "email": "jane@example.com",
      "created_at": "2024-01-02T00:00:00Z"
    }
  ]
}
```

**Status Codes:**
- `200` - Query executed successfully
- `400` - Invalid SQL generated
- `500` - Database error or unsafe query

---

### GET `/db-direct`

Execute a direct SQL query against the database.

**Query Parameters:**
- `query` (string): The SQL query to execute

**Example:**
```
GET /db-direct?query=SELECT COUNT(*) FROM users
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "COUNT(*)": 150
    }
  ]
}
```

**Status Codes:**
- `200` - Query executed successfully
- `400` - Invalid query
- `500` - Database error

---

## 🔍 Metadata and Search Endpoints

### POST `/similar-metadata`

Perform semantic search on database metadata using vector similarity.

**Request Body:**
```json
{
  "query": "user authentication tables"
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "table_name": "users",
      "similarity_score": 0.95,
      "description": "User authentication and profile information",
      "columns": [
        {
          "column_name": "user_id",
          "data_type": "NUMBER",
          "description": "Primary key for user identification"
        },
        {
          "column_name": "username",
          "data_type": "VARCHAR2",
          "description": "Unique username for login"
        }
      ]
    }
  ]
}
```

**Status Codes:**
- `200` - Search completed successfully
- `400` - Invalid search query
- `500` - Search service error

---

### POST `/embed-metadata`

Generate embeddings for database metadata and store them in Pinecone.

**Query Parameters:**
- `owner` (string, optional): Database owner/schema name

**Response:**
```json
{
  "success": true,
  "message": "Embedding pipeline completed for 25 tables",
  "tables_processed": 25,
  "table_names": [
    "users",
    "orders",
    "products",
    "categories"
  ]
}
```

**Status Codes:**
- `200` - Embeddings generated successfully
- `400` - No metadata found
- `500` - Embedding generation failed

---

### GET `/refresh-metadata`

Refresh the cached database metadata.

**Response:**
```json
{
  "message": "Metadata refreshed",
  "metadata": {
    "users": {
      "columns": [
        {
          "column_name": "user_id",
          "data_type": "NUMBER",
          "nullable": "N"
        }
      ]
    }
  }
}
```

**Status Codes:**
- `200` - Metadata refreshed successfully
- `500` - Database connection error

---

## 🏥 Health and Monitoring

### GET `/health`

Health check endpoint for monitoring service status.

**Response:**
```json
{
  "status": "healthy",
  "service": "Oracle AI Chatbot API"
}
```

**Status Codes:**
- `200` - Service is healthy

---

## 📊 Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description",
  "details": "Additional error information"
}
```

### Validation Error Response
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 🔒 Authentication

Most endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

For cookie-based authentication (used by the frontend), the token is automatically included in requests.

---

## 🚨 Error Handling

The API uses standard HTTP status codes:

- `200` - Success
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `422` - Unprocessable Entity (validation error)
- `500` - Internal Server Error

---

## 📝 Rate Limiting

API endpoints are protected with rate limiting:
- **Authentication endpoints**: 5 requests per minute
- **Core API endpoints**: 60 requests per minute
- **Session endpoints**: 30 requests per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1641234567
```

---

## 🔧 Testing

### Using curl

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "password"}'

# Test query endpoint
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Show me all users"}'
```

### Using Python requests

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Login
login_data = {"username": "test", "password": "password"}
response = requests.post("http://localhost:8000/auth/login", json=login_data)
token = response.json()["access_token"]

# Authenticated request
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://localhost:8000/sessions/list", headers=headers)
print(response.json())
```

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Models](https://pydantic-docs.helpmanual.io/)
- [Oracle Database Documentation](https://docs.oracle.com/en/database/)
- [JWT Token Guide](https://jwt.io/introduction/)

