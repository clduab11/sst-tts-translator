"""Main FastAPI application for SST/TTS Translator."""

from fastapi import FastAPI, UploadFile, File, WebSocket, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List, AsyncIterator
from starlette.websockets import WebSocketDisconnect
import asyncio
import logging

from ..config import settings
from ..stt import create_stt_provider
from ..tts import create_tts_provider
from ..prompt import PromptEngine
from ..llm import LLMRouter, LLMProvider
from ..scaffold import DDDGenerator
from ..session import SessionManager
from ..git import GitManager

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
    version="0.2.0"
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
tts_provider = None
prompt_engine = None
llm_router = None
ddd_generator = None
session_manager = None
git_manager = None


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


class TTSRequest(BaseModel):
    """Request model for text-to-speech synthesis."""
    text: str
    voice: str = "default"
    stream: bool = False


class SessionCreateRequest(BaseModel):
    """Request model for creating a session."""
    context: Optional[Dict[str, Any]] = None


class SessionEntryRequest(BaseModel):
    """Request model for adding an entry to a session."""
    role: str
    content: str


class GitCommitRequest(BaseModel):
    """Request model for git commit."""
    message: str


class GitBranchRequest(BaseModel):
    """Request model for creating a git branch."""
    branch_name: str


@app.on_event("startup")
async def startup_event():
    """Initialize components on startup."""
    global stt_provider, tts_provider, prompt_engine, llm_router, ddd_generator
    global session_manager, git_manager
    
    logger.info("Starting SST/TTS Translator...")
    
    # Initialize STT provider
    stt_provider = create_stt_provider(
        settings.stt_provider,
        settings.deepgram_api_key
    )
    logger.info(f"Initialized STT provider: {settings.stt_provider}")
    
    # Initialize TTS provider
    try:
        tts_provider = create_tts_provider(
            settings.tts_provider,
            settings.elevenlabs_api_key
        )
        logger.info(f"Initialized TTS provider: {settings.tts_provider}")
    except Exception as e:
        logger.warning(f"TTS provider not available: {e}")
    
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
    
    # Initialize session manager
    session_manager = SessionManager(max_sessions=settings.max_sessions)
    logger.info("Initialized session manager")
    
    # Initialize git manager
    git_manager = GitManager()
    logger.info("Initialized git manager")
    
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


# --- TTS Endpoints ---

@app.post("/api/synthesize")
async def synthesize_speech(request: TTSRequest):
    """
    Synthesize text to speech audio.
    
    Args:
        request: TTS request with text, voice, and stream options
        
    Returns:
        Audio data or streaming audio response
    """
    if tts_provider is None:
        raise HTTPException(
            status_code=503,
            detail="TTS provider not configured. Check TTS_PROVIDER and "
                   "related API keys in environment variables."
        )
    
    try:
        if request.stream:
            async def audio_stream():
                async for chunk in tts_provider.synthesize_stream(
                    text=request.text,
                    voice=request.voice
                ):
                    yield chunk
            
            return StreamingResponse(
                audio_stream(),
                media_type="audio/wav"
            )
        else:
            audio_data = await tts_provider.synthesize(
                text=request.text,
                voice=request.voice
            )
            return StreamingResponse(
                iter([audio_data]),
                media_type="audio/wav",
                headers={"Content-Length": str(len(audio_data))}
            )
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Session Endpoints ---

@app.post("/api/sessions")
async def create_session(request: SessionCreateRequest):
    """Create a new voice development session."""
    session = session_manager.create_session(context=request.context)
    return {"success": True, "session": session.get_summary()}


@app.get("/api/sessions")
async def list_sessions():
    """List all active sessions."""
    return {"success": True, "sessions": session_manager.list_sessions()}


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session details by ID."""
    session = session_manager.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "success": True,
        "session": session.get_summary(),
        "history": session.history
    }


@app.post("/api/sessions/{session_id}/entries")
async def add_session_entry(session_id: str, request: SessionEntryRequest):
    """Add an entry to a session."""
    if not session_manager.add_to_session(session_id, request.role, request.content):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    if not session_manager.delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True}


# --- Git Endpoints ---

@app.get("/api/git/status")
async def git_status():
    """Get git repository status."""
    result = await git_manager.status()
    return {"success": True, **result}


@app.get("/api/git/diff")
async def git_diff(staged: bool = False):
    """Get git diff output."""
    result = await git_manager.diff(staged=staged)
    return {"success": True, "diff": result}


@app.get("/api/git/log")
async def git_log(count: int = 10):
    """Get recent git commit log."""
    commits = await git_manager.log(count=count)
    return {"success": True, "commits": commits}


@app.get("/api/git/branches")
async def git_branches():
    """List git branches."""
    branches = await git_manager.branch_list()
    current = await git_manager.current_branch()
    return {"success": True, "branches": branches, "current": current}


@app.post("/api/git/commit")
async def git_commit(request: GitCommitRequest):
    """Stage all changes and commit."""
    result = await git_manager.commit(message=request.message)
    return result


@app.post("/api/git/branch")
async def git_create_branch(request: GitBranchRequest):
    """Create and switch to a new branch."""
    result = await git_manager.create_branch(branch_name=request.branch_name)
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "sst_tts_translator.api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    )
