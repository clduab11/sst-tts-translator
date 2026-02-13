# Usage Guide

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip package manager
- (Optional) FFmpeg for audio processing
- API keys for STT/LLM providers

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/clduab11/sst-tts-translator.git
   cd sst-tts-translator
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Basic Usage

### Starting the Server

```bash
# Using CLI
python -m sst_tts_translator serve

# With custom host and port
python -m sst_tts_translator serve --host 0.0.0.0 --port 8080

# With auto-reload for development
python -m sst_tts_translator serve --reload
```

### Using the CLI

#### 1. Transcribe Audio
```bash
python -m sst_tts_translator transcribe path/to/audio.wav
```

#### 2. Translate Text to Prompt
```bash
python -m sst_tts_translator translate "create a REST API for users"
```

#### 3. Voice to Code Pipeline
```bash
python -m sst_tts_translator voice-to-code audio.wav -o output.py
```

### Using the API

#### 1. Simple Transcription
```bash
curl -X POST http://localhost:8000/api/transcribe \
  -F "file=@recording.wav"
```

#### 2. Voice to Code
```bash
curl -X POST http://localhost:8000/api/voice-to-code \
  -F "file=@voice.wav" \
  -F "task_type=code_generation" \
  -F "use_swarm=false"
```

#### 3. Generate DDD Scaffold
```bash
curl -X POST http://localhost:8000/api/generate-scaffold \
  -H "Content-Type: application/json" \
  -d '{
    "domain_name": "order_management",
    "description": "E-commerce order processing system",
    "language": "python"
  }'
```

## Advanced Usage

### Using Agent Swarms

Enable agent swarm for complex tasks:

```bash
curl -X POST http://localhost:8000/api/voice-to-code \
  -F "file=@complex_task.wav" \
  -F "use_swarm=true"
```

This uses multiple specialized agents:
- **Architect**: System design
- **Developer**: Code implementation
- **Reviewer**: Code quality
- **Tester**: Test generation

### Custom Templates

Create custom prompt templates in `templates/` directory:

```yaml
# templates/my_template.yaml
name: my_custom_template
metadata:
  description: My custom template
  task_type: code_generation

template: |
  <task type="custom">
    <input>{{ user_input }}</input>
    <requirements>
      <requirement>Custom requirement 1</requirement>
    </requirements>
  </task>
```

### WebSocket Streaming

Stream audio in real-time:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/transcribe');

// Send audio chunks
const mediaRecorder = new MediaRecorder(stream);
mediaRecorder.ondataavailable = (event) => {
  ws.send(event.data);
};

// Receive transcriptions
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'transcription') {
    console.log('Text:', data.text);
  }
};
```

### Python SDK Usage

```python
import asyncio
from sst_tts_translator.stt import create_stt_provider
from sst_tts_translator.prompt import PromptEngine
from sst_tts_translator.llm import LLMRouter, LLMProvider

async def generate_code_from_voice(audio_path):
    # Initialize components
    stt = create_stt_provider("whisper")
    prompt_engine = PromptEngine()
    llm_router = LLMRouter(
        default_provider=LLMProvider.OPENAI,
        openai_api_key="your-key"
    )
    
    # Read audio
    with open(audio_path, "rb") as f:
        audio_data = f.read()
    
    # Transcribe
    text = await stt.transcribe_file(audio_data)
    
    # Create structured prompt
    prompt = prompt_engine.translate_to_structured_prompt(
        natural_text=text,
        task_type="code_generation"
    )
    
    # Generate code
    code_chunks = []
    async for chunk in llm_router.route_task(
        prompt=prompt,
        stream=False
    ):
        code_chunks.append(chunk)
    
    return "".join(code_chunks)

# Run
code = asyncio.run(generate_code_from_voice("audio.wav"))
print(code)
```

## Docker Usage

### Build and Run

```bash
# Build image
docker build -t sst-tts-translator .

# Run container
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e STT_PROVIDER=whisper \
  sst-tts-translator
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_HOST` | API server host | `0.0.0.0` |
| `API_PORT` | API server port | `8000` |
| `STT_PROVIDER` | STT provider (whisper/deepgram) | `whisper` |
| `DEEPGRAM_API_KEY` | Deepgram API key | None |
| `OPENAI_API_KEY` | OpenAI API key | None |
| `ANTHROPIC_API_KEY` | Anthropic API key | None |
| `DEFAULT_LLM_PROVIDER` | Default LLM provider | `openai` |
| `DEFAULT_LLM_MODEL` | Default LLM model | `gpt-4` |
| `LOG_LEVEL` | Logging level | `INFO` |

### STT Providers

#### Whisper (Local)
- No API key required
- Runs locally
- Models: tiny, base, small, medium, large

#### Deepgram (Cloud)
- API key required
- Real-time streaming
- Lower latency

### LLM Providers

#### OpenAI
- Models: gpt-4, gpt-3.5-turbo
- Excellent code generation
- Requires API key

#### Anthropic
- Models: claude-3-opus, claude-3-sonnet
- Strong reasoning
- Requires API key

## Troubleshooting

### Common Issues

#### 1. Audio File Not Recognized
```bash
# Install FFmpeg
sudo apt-get install ffmpeg  # Linux
brew install ffmpeg  # macOS
```

#### 2. Whisper Model Download Fails
```bash
# Manually download model
python -c "import whisper; whisper.load_model('base')"
```

#### 3. Port Already in Use
```bash
# Use different port
python -m sst_tts_translator serve --port 8080
```

#### 4. API Key Not Found
```bash
# Check .env file exists and is loaded
cat .env
# Verify environment variables
python -c "from sst_tts_translator.config import settings; print(settings.openai_api_key)"
```

## Performance Tips

1. **Use smaller Whisper models** for faster transcription (tiny, base)
2. **Enable streaming** for real-time responses
3. **Cache models** to avoid reload delays
4. **Use agent swarms** only for complex tasks
5. **Adjust audio quality** based on needs (16kHz sufficient)

## Examples

See `examples/` directory for:
- Client implementations
- Integration examples
- Use case demonstrations
- Sample audio files

## Next Steps

- Read [Architecture Documentation](architecture.md)
- Review [API Specifications](api-specs.md)
- Explore template customization
- Integrate with your workflow
