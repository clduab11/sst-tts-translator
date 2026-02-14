# SST/TTS Translator

Voice-driven development system that transforms natural speech into structured code using LLM integration.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Security](https://img.shields.io/badge/security-updated-green.svg)](SECURITY.md)

## Overview

SST/TTS Translator is a middleman LLM system that bridges voice input and code generation through:

1. **Speech-to-Text (STT)**: Captures voice input via Whisper or Deepgram
2. **Text-to-Speech (TTS)**: Speaks code explanations back via Piper or ElevenLabs
3. **Prompt Translation**: Converts natural speech to structured prompts (XML tags, context blocks, Chain of Thought)
4. **LLM Router**: Routes to coding LLMs and agent swarms (OpenAI, Anthropic)
5. **Code Generation**: Generates clean, maintainable code
6. **DDD Scaffolds**: Creates Document-Driven Development project structures
7. **Session Management**: Persistent voice development conversations
8. **Git Integration**: Voice-driven repository operations

## Document-Driven Development Philosophy

This repository embraces the Document-Driven Development (DDD) philosophy. DDD emphasizes the importance of clear, purposeful, and comprehensive documentation to guide project structure and development decisions. The approach consists of:

- **Two Repositories**:
  - The primary repository serves as the "final product," reflecting code in its intended form.
  - A secondary repository designed in enhanced Markdown files. This auxiliary repository contains well-structured, highly-focused documentation that lays the foundation for every development phase.

- **Structured Process**:
  - Every feature, function, and system sub-component is first designed in written form as comprehensive documents (roadmaps, flows, user stories, architecture specifications, etc.).
  - These documents ensure no ambiguity in project scope or functionality. Contributors can use them as a reference to implement features in the primary repository.

- **Collaboration**:
  - Foster effective collaboration, ensuring seamless integration of all parts. Structured documentation functions as the single source of truth for the team and is regularly reviewed for updates and consistency.

This methodology ensures a robust foundation and yields results with scalability, maintainability, and ease of use.

## Features

- 🎤 **Multiple STT Providers**: Whisper (local) and Deepgram (cloud)
- 🔊 **Multiple TTS Providers**: Piper (local) and ElevenLabs (cloud)
- 🔄 **Streaming Audio**: Real-time transcription and synthesis via WebSocket
- 📝 **Structured Prompts**: XML-based prompt templates with CoT reasoning
- 🤖 **Agent Swarms**: Architect, Developer, Reviewer, and Tester agents
- 🏗️ **DDD Generation**: Automated scaffold creation for document-driven projects
- 💬 **Session Management**: Persistent voice development conversations
- 🔀 **Git Integration**: Voice-driven repository operations (status, diff, commit, branch)
- ⚡ **Async Processing**: Non-blocking I/O throughout
- 🔌 **REST API**: FastAPI-based endpoints
- 🛠️ **CLI Tools**: Command-line interface for all operations

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/clduab11/sst-tts-translator.git
cd sst-tts-translator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Or install as package
pip install -e .
```

### Configuration

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# STT Provider (whisper or deepgram)
STT_PROVIDER=whisper
DEEPGRAM_API_KEY=your_deepgram_key_here

# TTS Provider (piper or elevenlabs)
TTS_PROVIDER=piper
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# LLM Providers
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### Start the Server

```bash
# Using CLI
python -m sst_tts_translator serve

# Or directly with uvicorn
uvicorn sst_tts_translator.api.server:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Usage Examples

### 1. CLI - Transcribe Audio

```bash
python -m sst_tts_translator transcribe audio.wav
```

### 2. CLI - Voice to Code

```bash
python -m sst_tts_translator voice-to-code audio.wav --output generated_code.py
```

### 3. CLI - Text to Speech

```bash
python -m sst_tts_translator speak "Hello, your code has been generated" -o output.wav
```

### 4. CLI - Git Status

```bash
python -m sst_tts_translator git-status
```

### 5. API - Complete Pipeline

```bash
curl -X POST http://localhost:8000/api/voice-to-code \
  -F "file=@voice.wav" \
  -F "task_type=code_generation"
```

### 4. API - Generate DDD Scaffold

```bash
curl -X POST http://localhost:8000/api/generate-scaffold \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "user_management",
    "description": "User authentication and authorization domain",
    "language": "python"
  }'
```

### 7. API - Text to Speech

```bash
curl -X POST http://localhost:8000/api/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Your code is ready", "voice": "default"}' \
  --output speech.wav
```

### 8. API - Session Management

```bash
# Create session
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"context": {"language": "python", "project": "my-app"}}'

# List sessions
curl http://localhost:8000/api/sessions
```

### 9. API - Git Operations

```bash
# Get status
curl http://localhost:8000/api/git/status

# Get diff
curl http://localhost:8000/api/git/diff

# List branches
curl http://localhost:8000/api/git/branches
```

### 10. WebSocket - Streaming Transcription

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/transcribe');

ws.onopen = () => {
  // Send audio chunks
  ws.send(audioChunkBuffer);
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Transcription:', data.text);
};
```

## Architecture

```
Voice Input → STT Module → Prompt Engine → LLM Router → Code Output
                                ↓                           ↓
                          Agent Swarm              TTS Output (voice)
                          (Architect, Developer,
                           Reviewer, Tester)

Session Manager ↔ All Components (conversation context)
Git Manager ↔ Repository Operations (status, diff, commit, branch)
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## Project Structure

```
sst-tts-translator/
├── src/
│   └── sst_tts_translator/
│       ├── api/          # FastAPI server
│       ├── stt/          # Speech-to-Text providers
│       ├── tts/          # Text-to-Speech providers
│       ├── prompt/       # Prompt template engine
│       ├── llm/          # LLM router and agents
│       ├── scaffold/     # DDD scaffold generator
│       ├── session/      # Session management
│       ├── git/          # Git integration
│       ├── utils/        # Utility functions
│       ├── config.py     # Configuration management
│       └── cli.py        # Command-line interface
├── docs/                 # Documentation
├── tests/                # Test suite
├── templates/            # Prompt templates
├── requirements.txt      # Python dependencies
├── setup.py              # Package setup
└── README.md             # This file
```

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Code Style

```bash
# Format code
black src/

# Check types
mypy src/
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/api/transcribe` | POST | Transcribe audio file |
| `/ws/transcribe` | WebSocket | Stream audio transcription |
| `/api/translate-prompt` | POST | Convert text to structured prompt |
| `/api/generate-code` | POST | Generate code from prompt |
| `/api/voice-to-code` | POST | Complete voice-to-code pipeline |
| `/api/generate-scaffold` | POST | Generate DDD scaffold |
| `/api/synthesize` | POST | Text-to-speech synthesis |
| `/api/sessions` | GET/POST | List or create sessions |
| `/api/sessions/{id}` | GET/DELETE | Get or delete session |
| `/api/sessions/{id}/entries` | POST | Add session entry |
| `/api/git/status` | GET | Git repository status |
| `/api/git/diff` | GET | Git diff output |
| `/api/git/log` | GET | Git commit log |
| `/api/git/branches` | GET | List branches |
| `/api/git/commit` | POST | Stage and commit changes |
| `/api/git/branch` | POST | Create new branch |

See [docs/api-specs.md](docs/api-specs.md) for complete API documentation.

## Technology Stack

- **Framework**: FastAPI, Uvicorn
- **STT**: OpenAI Whisper, Deepgram
- **TTS**: Piper (local), ElevenLabs (cloud)
- **LLM**: OpenAI GPT, Anthropic Claude
- **Audio**: SoundDevice, NumPy, Librosa
- **Templates**: Jinja2
- **CLI**: Click

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security

Security is a top priority. All dependencies are regularly updated to patch known vulnerabilities.

**Latest Security Updates:**
- FastAPI updated to 0.109.1 (ReDoS vulnerability fixed)
- python-multipart updated to 0.0.22 (multiple vulnerabilities fixed)

For security issues or to report vulnerabilities, see [SECURITY.md](SECURITY.md).

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [x] TTS (Text-to-Speech) output
- [x] Session management for persistent conversations
- [x] Git integration for voice-driven development
- [ ] Support for more LLM providers
- [ ] Code execution sandbox
- [ ] IDE integrations (VS Code, IntelliJ)
- [ ] Real-time collaboration
- [ ] Advanced agent orchestration

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

- OpenAI Whisper for local STT
- Deepgram for cloud STT
- Piper for local TTS
- ElevenLabs for cloud TTS
- FastAPI for the excellent web framework
- The open-source community