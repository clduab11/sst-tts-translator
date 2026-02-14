# SST/TTS Translator

Voice-driven development system that transforms natural speech into structured code using LLM integration.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Security](https://img.shields.io/badge/security-updated-green.svg)](SECURITY.md)

## Overview

SST/TTS Translator is a middleman LLM system that bridges voice input and code generation through:

1. **Speech-to-Text (STT)**: Captures voice input via Whisper or Deepgram
2. **Prompt Translation**: Converts natural speech to structured prompts (XML tags, context blocks, Chain of Thought)
3. **LLM Router**: Routes to coding LLMs and agent swarms (OpenAI, Anthropic)
4. **Code Generation**: Generates clean, maintainable code
5. **DDD Scaffolds**: Creates Domain-Driven Design project structures

## Features

- 🎤 **Multiple STT Providers**: Whisper (local) and Deepgram (cloud)
- 🔄 **Streaming Audio**: Real-time transcription via WebSocket
- 📝 **Structured Prompts**: XML-based prompt templates with CoT reasoning
- 🤖 **Agent Swarms**: Architect, Developer, Reviewer, and Tester agents
- 🏗️ **DDD Generation**: Automated scaffold creation for domain-driven projects
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

### 3. API - Complete Pipeline

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

### 5. WebSocket - Streaming Transcription

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
                                ↓
                          Agent Swarm
                          (Architect, Developer, Reviewer, Tester)
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## Project Structure

```
sst-tts-translator/
├── src/
│   └── sst_tts_translator/
│       ├── api/          # FastAPI server
│       ├── stt/          # Speech-to-Text providers
│       ├── prompt/       # Prompt template engine
│       ├── llm/          # LLM router and agents
│       ├── scaffold/     # DDD scaffold generator
│       ├── utils/        # Utility functions
│       ├── config.py     # Configuration management
│       └── cli.py        # Command-line interface
├── docs/                 # Documentation
├── tests/                # Test suite
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

See [docs/api-specs.md](docs/api-specs.md) for complete API documentation.

## Technology Stack

- **Framework**: FastAPI, Uvicorn
- **STT**: OpenAI Whisper, Deepgram
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

- [ ] TTS (Text-to-Speech) output
- [ ] Support for more LLM providers
- [ ] Code execution sandbox
- [ ] IDE integrations (VS Code, IntelliJ)
- [ ] Real-time collaboration
- [ ] Git integration
- [ ] Advanced agent orchestration

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

- OpenAI Whisper for local STT
- Deepgram for cloud STT
- FastAPI for the excellent web framework
- The open-source community
