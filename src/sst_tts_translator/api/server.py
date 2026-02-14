"""Main FastAPI application for SST/TTS Translator."""

from fastapi import FastAPI, UploadFile, File, WebSocket, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, AsyncIterator
from starlette.websockets import WebSocketDisconnect
import asyncio
import logging

from ..config import settings
from ..stt import create_stt_provider
from ..prompt import PromptEngine
from ..llm import LLMRouter, LLMProvider
from ..scaffold import DDDGenerator

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SST/TTS Translator",
    description="Voice-driven development with LLM integration",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
stt_provider = None
prompt_engine = None
llm_router = None
ddd_generator = None


class TranscriptionRequest(BaseModel):
    """Request model for transcription."""
    audio_url: Optional[str] = None


class PromptRequest(BaseModel):
    """Request model for prompt translation."""
    text: str
    task_type: str = "code_generation"
    include_cot: bool = True
    context: Optional[Dict[str, Any]] = None


class CodeGenerationRequest(BaseModel):
    """Request model for code generation."""
    prompt: str
    task_type: str = "code_generation"
    use_swarm: bool = False
    provider: Optional[str] = None
    stream: bool = True


class VoiceToCodeRequest(BaseModel):
    """Request model for complete voice-to-code pipeline."""
    task_type: str = "code_generation"
    use_swarm: bool = False
    include_cot: bool = True
    context: Optional[Dict[str, Any]] = None


class ScaffoldRequest(BaseModel):
    """Request model for DDD scaffold generation."""
    domain_name: str
    description: str
    language: str = "python"


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global stt_provider, prompt_engine, llm_router, ddd_generator
    
    logger.info("Starting SST/TTS Translator...")
    
    # Initialize STT provider
    stt_provider = create_stt_provider(
        settings.stt_provider,
        settings.deepgram_api_key
    )
    logger.info(f"Initialized STT provider: {settings.stt_provider}")
    
    # Initialize prompt engine
    prompt_engine = PromptEngine(settings.prompt_template_dir)
    logger.info("Initialized prompt engine")
    
    # Initialize LLM router
    llm_router = LLMRouter(
        default_provider=LLMProvider(settings.default_llm_provider),
        openai_api_key=settings.openai_api_key,
        anthropic_api_key=settings.anthropic_api_key
    )
    logger.info("Initialized LLM router")
    
    # Initialize DDD generator
    ddd_generator = DDDGenerator()
    logger.info("Initialized DDD generator")
    
    logger.info("SST/TTS Translator started successfully")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "SST/TTS Translator",
        "version": "0.1.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribe audio file to text.
    
    Args:
        file: Audio file upload
        
    Returns:
        Transcription result
    """
    try:
        # Read audio data
        audio_data = await file.read()
        
        # Transcribe
        text = await stt_provider.transcribe_file(audio_data)
        
        return {
            "success": True,
            "text": text
        }
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/transcribe")
async def websocket_transcribe(websocket: WebSocket):
    """
    WebSocket endpoint for streaming audio transcription.
    
    This endpoint receives audio chunks via WebSocket and streams back
    transcribed text in real-time.
    """
    await websocket.accept()
    
    try:
        async def audio_stream():
            while True:
                try:
                    data = await websocket.receive_bytes()
                    if data:
                        yield data
                    else:
                        break
                except WebSocketDisconnect:
                    break
        
        # Stream transcription
        async for text_chunk in stt_provider.transcribe_stream(audio_stream()):
            await websocket.send_json({
                "type": "transcription",
                "text": text_chunk
            })
        
        await websocket.send_json({"type": "end"})
        
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected during transcription")
    except Exception as e:
        logger.error(f"WebSocket transcription error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except (WebSocketDisconnect, Exception) as send_err:
            logger.debug(f"Could not send error to websocket: {send_err}")
    finally:
        try:
            await websocket.close()
        except (WebSocketDisconnect, Exception) as close_err:
            logger.debug(f"WebSocket already closed: {close_err}")


@app.post("/api/translate-prompt")
async def translate_prompt(request: PromptRequest):
    """
    Translate natural language to structured prompt.
    
    Args:
        request: Prompt translation request
        
    Returns:
        Structured prompt
    """
    try:
        structured_prompt = prompt_engine.translate_to_structured_prompt(
            natural_text=request.text,
            task_type=request.task_type,
            include_cot=request.include_cot,
            context=request.context
        )
        
        return {
            "success": True,
            "structured_prompt": structured_prompt
        }
    except Exception as e:
        logger.error(f"Prompt translation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-code")
async def generate_code(request: CodeGenerationRequest):
    """
    Generate code from structured prompt.
    
    Args:
        request: Code generation request
        
    Returns:
        Generated code (streaming if requested)
    """
    try:
        provider = LLMProvider(request.provider) if request.provider else None
        
        if request.stream:
            async def stream_generator():
                async for chunk in llm_router.route_task(
                    prompt=request.prompt,
                    task_type=request.task_type,
                    use_swarm=request.use_swarm,
                    provider=provider,
                    stream=True
                ):
                    yield chunk
            
            return StreamingResponse(
                stream_generator(),
                media_type="text/plain"
            )
        else:
            code_chunks = []
            async for chunk in llm_router.route_task(
                prompt=request.prompt,
                task_type=request.task_type,
                use_swarm=request.use_swarm,
                provider=provider,
                stream=False
            ):
                code_chunks.append(chunk)
            
            return {
                "success": True,
                "code": "".join(code_chunks)
            }
    except Exception as e:
        logger.error(f"Code generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/voice-to-code")
async def voice_to_code(
    file: UploadFile = File(...),
    task_type: str = "code_generation",
    use_swarm: bool = False,
    include_cot: bool = True
):
    """
    Complete pipeline: voice input to code generation.
    
    Args:
        file: Audio file upload
        task_type: Type of code generation task
        use_swarm: Whether to use agent swarm
        include_cot: Include Chain of Thought
        
    Returns:
        Generated code
    """
    try:
        # Step 1: Transcribe audio
        audio_data = await file.read()
        transcribed_text = await stt_provider.transcribe_file(audio_data)
        logger.debug(f"Transcribed: {transcribed_text[:100]}...")  # Only log first 100 chars at debug level
        
        # Step 2: Translate to structured prompt
        structured_prompt = prompt_engine.translate_to_structured_prompt(
            natural_text=transcribed_text,
            task_type=task_type,
            include_cot=include_cot
        )
        logger.info("Generated structured prompt")
        
        # Step 3: Generate code
        code_chunks = []
        async for chunk in llm_router.route_task(
            prompt=structured_prompt,
            task_type=task_type,
            use_swarm=use_swarm,
            stream=False
        ):
            code_chunks.append(chunk)
        
        generated_code = "".join(code_chunks)
        
        return {
            "success": True,
            "transcription": transcribed_text,
            "structured_prompt": structured_prompt,
            "code": generated_code
        }
    except Exception as e:
        logger.error(f"Voice-to-code pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-scaffold")
async def generate_scaffold(request: ScaffoldRequest):
    """
    Generate DDD scaffold from description.
    
    Args:
        request: Scaffold generation request with domain_name, description, and language
        
    Returns:
        Generated scaffold files
    """
    try:
        # Create prompt for scaffold generation
        scaffold_prompt = f"""
Generate a DDD scaffold for a {request.domain_name} domain with the following description:

{request.description}

Provide the output as JSON with entities, value objects, repositories, and services.
"""
        
        # Generate scaffold definition using LLM
        llm_output_chunks = []
        async for chunk in llm_router.route_task(
            prompt=scaffold_prompt,
            task_type="code_generation",
            stream=False
        ):
            llm_output_chunks.append(chunk)
        
        llm_output = "".join(llm_output_chunks)
        
        # Parse and generate scaffold
        generator = DDDGenerator(language=request.language)
        scaffold = generator.parse_from_llm_output(llm_output)
        scaffold.domain_name = request.domain_name
        
        files = generator.generate_scaffold(scaffold)
        
        return {
            "success": True,
            "domain_name": request.domain_name,
            "files": files
        }
    except Exception as e:
        logger.error(f"Scaffold generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "sst_tts_translator.api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )
