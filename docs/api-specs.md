# API Specification

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required. Future versions will support API key authentication.

## Endpoints

### 1. Health Check

**GET** `/health`

Check if the service is running.

**Response**
```json
{
  "status": "healthy"
}
```

---

### 2. Transcribe Audio File

**POST** `/api/transcribe`

Transcribe an audio file to text.

**Request**
- Content-Type: `multipart/form-data`
- Body: Audio file (wav, mp3, flac)

**Response**
```json
{
  "success": true,
  "text": "create a FastAPI endpoint for user authentication"
}
```

**Curl Example**
```bash
curl -X POST http://localhost:8000/api/transcribe \
  -F "file=@audio.wav"
```

---

### 3. Stream Audio Transcription

**WebSocket** `/ws/transcribe`

Real-time audio transcription via WebSocket.

**Message Format (Client → Server)**
```
Binary audio chunks
```

**Message Format (Server → Client)**
```json
{
  "type": "transcription",
  "text": "partial transcription"
}
```

**End Message**
```json
{
  "type": "end"
}
```

**Error Message**
```json
{
  "type": "error",
  "message": "error description"
}
```

---

### 4. Translate to Structured Prompt

**POST** `/api/translate-prompt`

Convert natural language to structured prompt.

**Request Body**
```json
{
  "text": "create a user authentication service",
  "task_type": "code_generation",
  "include_cot": true,
  "context": {
    "language": "python",
    "framework": "fastapi"
  }
}
```

**Response**
```json
{
  "success": true,
  "structured_prompt": "<task type='code_generation'>...</task>"
}
```

---

### 5. Generate Code

**POST** `/api/generate-code`

Generate code from structured prompt.

**Request Body**
```json
{
  "prompt": "<task>...</task>",
  "task_type": "code_generation",
  "use_swarm": false,
  "provider": "openai",
  "stream": true
}
```

**Response (Non-streaming)**
```json
{
  "success": true,
  "code": "def authenticate_user():\n    pass"
}
```

**Response (Streaming)**
```
text/plain stream of code chunks
```

---

### 6. Voice to Code (Complete Pipeline)

**POST** `/api/voice-to-code`

Complete pipeline from voice input to code generation.

**Request**
- Content-Type: `multipart/form-data`
- Body: 
  - `file`: Audio file
  - `task_type`: Task type (default: "code_generation")
  - `use_swarm`: Boolean (default: false)
  - `include_cot`: Boolean (default: true)

**Response**
```json
{
  "success": true,
  "transcription": "create a REST API endpoint",
  "structured_prompt": "<task>...</task>",
  "code": "from fastapi import FastAPI\n..."
}
```

**Curl Example**
```bash
curl -X POST http://localhost:8000/api/voice-to-code \
  -F "file=@voice.wav" \
  -F "task_type=code_generation" \
  -F "use_swarm=false"
```

---

### 7. Generate DDD Scaffold

**POST** `/api/generate-scaffold`

Generate Domain-Driven Design scaffold.

**Request Body**
```json
{
  "domain_name": "user_management",
  "description": "User authentication and authorization domain",
  "language": "python"
}
```

**Response**
```json
{
  "success": true,
  "domain_name": "user_management",
  "files": {
    "user_management/entities/user.py": "class User:...",
    "user_management/repositories/user_repository.py": "class UserRepository:..."
  }
}
```

---

## Error Responses

All endpoints return errors in the following format:

```json
{
  "detail": "Error description"
}
```

**HTTP Status Codes**
- `200`: Success
- `400`: Bad Request
- `500`: Internal Server Error

---

## Data Models

### TranscriptionRequest
```python
{
  "audio_url": Optional[str]
}
```

### PromptRequest
```python
{
  "text": str,
  "task_type": str = "code_generation",
  "include_cot": bool = True,
  "context": Optional[Dict[str, Any]] = None
}
```

### CodeGenerationRequest
```python
{
  "prompt": str,
  "task_type": str = "code_generation",
  "use_swarm": bool = False,
  "provider": Optional[str] = None,
  "stream": bool = True
}
```

---

## Rate Limits

Currently no rate limits enforced. Planned for future releases:
- 100 requests per minute per IP
- 1000 requests per hour per IP

---

## WebSocket Connection

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/transcribe');

ws.onopen = () => {
  // Send audio chunks
  const audioChunk = getAudioChunk(); // Your audio data
  ws.send(audioChunk);
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'transcription') {
    console.log('Text:', data.text);
  } else if (data.type === 'end') {
    console.log('Transcription complete');
  }
};
```

---

## OpenAPI/Swagger Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
