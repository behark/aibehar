# Open WebUI API Documentation

This document provides a reference for the Open WebUI API, allowing developers to integrate and extend the functionality.

## Authentication

All API endpoints require authentication using either:
- JWT token authentication
- API Key authentication

### JWT Authentication

For web applications, use JWT authentication:

```
Authorization: Bearer <jwt_token>
```

JWT tokens can be obtained by authenticating through the `/api/auth/login` endpoint.

### API Key Authentication

For server-to-server integrations, use API key authentication:

```
X-API-Key: <your_api_key>
```

API keys can be generated in the Settings > API Access panel.

## Base URL

By default, the API is available at the same host as the web interface with `/api` path prefix.

For example, if Open WebUI is running at `http://localhost:3000`, the API base URL is `http://localhost:3000/api`.

## Endpoints

### Authentication

#### POST /api/auth/login

Authenticate a user and get a JWT token.

**Request:**
```json
{
  "username": "user",
  "password": "password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "refresh_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /api/auth/refresh

Refresh an expired JWT token.

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1..."
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Chat

#### GET /api/chats

Get a list of all chats for the authenticated user.

**Response:**
```json
{
  "chats": [
    {
      "id": "chat_12345",
      "title": "My Chat",
      "created_at": "2025-08-17T14:30:00Z",
      "updated_at": "2025-08-17T15:45:00Z",
      "model": "llama3-8b",
      "message_count": 12
    }
  ]
}
```

#### GET /api/chats/{chat_id}

Get details and messages for a specific chat.

**Response:**
```json
{
  "id": "chat_12345",
  "title": "My Chat",
  "created_at": "2025-08-17T14:30:00Z",
  "updated_at": "2025-08-17T15:45:00Z",
  "model": "llama3-8b",
  "messages": [
    {
      "id": "msg_1",
      "role": "user",
      "content": "Hello, how are you?",
      "created_at": "2025-08-17T14:30:00Z"
    },
    {
      "id": "msg_2",
      "role": "assistant",
      "content": "I'm doing well, thank you for asking! How can I help you today?",
      "created_at": "2025-08-17T14:30:05Z"
    }
  ]
}
```

#### POST /api/chats

Create a new chat.

**Request:**
```json
{
  "title": "New Chat",
  "model": "llama3-8b"
}
```

**Response:**
```json
{
  "id": "chat_67890",
  "title": "New Chat",
  "created_at": "2025-08-17T16:00:00Z",
  "updated_at": "2025-08-17T16:00:00Z",
  "model": "llama3-8b",
  "messages": []
}
```

#### POST /api/chats/{chat_id}/messages

Add a message to a chat and get the model's response.

**Request:**
```json
{
  "content": "What is the capital of France?"
}
```

**Response:**
```json
{
  "id": "msg_3",
  "role": "user",
  "content": "What is the capital of France?",
  "created_at": "2025-08-17T16:05:00Z"
}
```

The model's response will be sent as a server-sent event (SSE) to `/api/chats/{chat_id}/stream`.

### Models

#### GET /api/models

Get a list of all available models.

**Response:**
```json
{
  "models": [
    {
      "id": "llama3-8b",
      "name": "Llama 3 8B",
      "description": "Meta's Llama 3 8B model",
      "parameters": "8 billion",
      "context_length": 8192,
      "provider": "ollama"
    },
    {
      "id": "mistral-7b",
      "name": "Mistral 7B",
      "description": "Mistral AI's 7B model",
      "parameters": "7 billion",
      "context_length": 8192,
      "provider": "ollama"
    }
  ]
}
```

#### GET /api/models/{model_id}

Get details for a specific model.

**Response:**
```json
{
  "id": "llama3-8b",
  "name": "Llama 3 8B",
  "description": "Meta's Llama 3 8B model",
  "parameters": "8 billion",
  "context_length": 8192,
  "provider": "ollama",
  "tags": ["conversational", "instruction-tuned"],
  "capabilities": ["text-generation", "chat"],
  "default_parameters": {
    "temperature": 0.7,
    "top_p": 0.9,
    "max_tokens": 1024
  }
}
```

### Files (RAG)

#### GET /api/files

Get a list of all files uploaded by the authenticated user.

**Response:**
```json
{
  "files": [
    {
      "id": "file_12345",
      "name": "document.pdf",
      "size": 1048576,
      "mime_type": "application/pdf",
      "created_at": "2025-08-17T13:00:00Z",
      "embedding_status": "completed"
    }
  ]
}
```

#### POST /api/files/upload

Upload a new file for RAG.

**Request:**
Form data with `file` field containing the file to upload.

**Response:**
```json
{
  "id": "file_67890",
  "name": "report.pdf",
  "size": 2097152,
  "mime_type": "application/pdf",
  "created_at": "2025-08-17T16:30:00Z",
  "embedding_status": "processing"
}
```

#### DELETE /api/files/{file_id}

Delete a file.

**Response:**
```json
{
  "success": true,
  "message": "File deleted"
}
```

### RAG Search

#### POST /api/rag/search

Search through embedded documents.

**Request:**
```json
{
  "query": "What is machine learning?",
  "limit": 5
}
```

**Response:**
```json
{
  "results": [
    {
      "file_id": "file_12345",
      "file_name": "document.pdf",
      "page": 42,
      "content": "Machine learning is a subset of artificial intelligence...",
      "score": 0.92
    },
    {
      "file_id": "file_12345",
      "file_name": "document.pdf",
      "page": 43,
      "content": "The key algorithms in machine learning include...",
      "score": 0.85
    }
  ]
}
```

### User Management (Admin Only)

#### GET /api/users

Get a list of all users (requires admin privileges).

**Response:**
```json
{
  "users": [
    {
      "id": "user_12345",
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": "user_67890",
      "username": "user",
      "email": "user@example.com",
      "role": "user",
      "created_at": "2025-08-17T10:00:00Z"
    }
  ]
}
```

#### POST /api/users

Create a new user (requires admin privileges).

**Request:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "strong_password",
  "role": "user"
}
```

**Response:**
```json
{
  "id": "user_abcde",
  "username": "newuser",
  "email": "newuser@example.com",
  "role": "user",
  "created_at": "2025-08-17T17:00:00Z"
}
```

## WebSocket API

In addition to the REST API, Open WebUI provides WebSocket endpoints for real-time functionality.

### Chat Stream

Connect to `/api/ws/chats/{chat_id}` to receive streaming responses from the model.

**Authentication:**
Include JWT token in the query parameter: `?token=<jwt_token>`

**Events:**

1. Message chunk event:
```json
{
  "type": "chunk",
  "message_id": "msg_4",
  "content": "Paris",
  "is_complete": false
}
```

2. Message complete event:
```json
{
  "type": "complete",
  "message_id": "msg_4",
  "content": "Paris is the capital of France.",
  "created_at": "2025-08-17T16:05:05Z"
}
```

## Error Handling

All API endpoints use standard HTTP status codes and return JSON error responses:

```json
{
  "error": {
    "code": "unauthorized",
    "message": "Invalid authentication credentials"
  }
}
```

Common error codes:
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server-side error

## Rate Limiting

API endpoints are rate-limited to prevent abuse. Limits vary by endpoint and user role.

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Maximum requests allowed in the window
- `X-RateLimit-Remaining`: Remaining requests in the current window
- `X-RateLimit-Reset`: Unix timestamp when the rate limit window resets

## SDK Libraries

Official client libraries:
- JavaScript/TypeScript: [open-webui-js](https://github.com/open-webui/open-webui-js)
- Python: [open-webui-python](https://github.com/open-webui/open-webui-python)

## Examples

### Chat Completion (curl)

```bash
# Create a chat
chat_response=$(curl -X POST "http://localhost:3000/api/chats" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"API Test","model":"llama3-8b"}')

# Extract chat ID
chat_id=$(echo $chat_response | jq -r '.id')

# Send a message
curl -X POST "http://localhost:3000/api/chats/$chat_id/messages" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"What is the capital of France?"}'

# Get the response (streaming)
curl -N "http://localhost:3000/api/chats/$chat_id/stream" \
  -H "Authorization: Bearer $TOKEN"
```

### JavaScript Example

```javascript
// Get chat history
async function getChatHistory(chatId) {
  const response = await fetch(`http://localhost:3000/api/chats/${chatId}`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}

// Stream chat response
function streamChatResponse(chatId) {
  const eventSource = new EventSource(
    `http://localhost:3000/api/chats/${chatId}/stream?token=${token}`
  );
  
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received chunk:', data.content);
    
    if (data.type === 'complete') {
      eventSource.close();
    }
  };
  
  eventSource.onerror = (error) => {
    console.error('Stream error:', error);
    eventSource.close();
  };
}
```

## Further Reading

For more detailed information and additional endpoints, refer to the [API Reference](https://docs.openwebui.com/api-reference) in the official documentation.
