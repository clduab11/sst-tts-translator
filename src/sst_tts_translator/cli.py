"""Command-line interface for SST/TTS Translator."""

import click
import asyncio
from pathlib import Path

from .config import settings


@click.group()
@click.version_option(version="0.2.0")
def cli():
    """SST/TTS Translator - Voice-driven development with LLM integration."""
    pass


@cli.command()
@click.option("--host", default=settings.api_host, help="Host to bind to")
@click.option("--port", default=settings.api_port, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def serve(host: str, port: int, reload: bool):
    """Start the API server."""
    import uvicorn
    
    click.echo(f"Starting SST/TTS Translator API server on {host}:{port}")
    
    uvicorn.run(
        "sst_tts_translator.api.server:app",
        host=host,
        port=port,
        reload=reload
    )


@cli.command()
@click.argument("audio_file", type=click.Path(exists=True))
def transcribe(audio_file: str):
    """Transcribe an audio file."""
    from .stt import create_stt_provider
    
    click.echo(f"Transcribing {audio_file}...")
    
    async def run_transcription():
        stt = create_stt_provider(
            settings.stt_provider,
            settings.deepgram_api_key
        )
        
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        
        text = await stt.transcribe_file(audio_data)
        return text
    
    text = asyncio.run(run_transcription())
    click.echo("\nTranscription:")
    click.echo(text)


@cli.command()
@click.argument("text")
@click.option("--task-type", default="code_generation", help="Task type")
@click.option("--cot/--no-cot", default=True, help="Include Chain of Thought")
def translate(text: str, task_type: str, cot: bool):
    """Translate natural language to structured prompt."""
    from .prompt import PromptEngine
    
    engine = PromptEngine()
    prompt = engine.translate_to_structured_prompt(
        natural_text=text,
        task_type=task_type,
        include_cot=cot
    )
    
    click.echo("Structured Prompt:")
    click.echo(prompt)


@cli.command()
@click.argument("audio_file", type=click.Path(exists=True))
@click.option("--task-type", default="code_generation", help="Task type")
@click.option("--swarm/--no-swarm", default=False, help="Use agent swarm")
@click.option("--output", "-o", type=click.Path(), help="Output file")
def voice_to_code(audio_file: str, task_type: str, swarm: bool, output: str):
    """Convert voice input to code (full pipeline)."""
    from .stt import create_stt_provider
    from .prompt import PromptEngine
    from .llm import LLMRouter, LLMProvider
    
    click.echo(f"Processing {audio_file}...")
    
    async def run_pipeline():
        # Initialize components
        stt = create_stt_provider(
            settings.stt_provider,
            settings.deepgram_api_key
        )
        prompt_engine = PromptEngine()
        llm_router = LLMRouter(
            default_provider=LLMProvider(settings.default_llm_provider),
            openai_api_key=settings.openai_api_key,
            anthropic_api_key=settings.anthropic_api_key
        )
        
        # Step 1: Transcribe
        click.echo("Transcribing audio...")
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        text = await stt.transcribe_file(audio_data)
        click.echo(f"Transcription: {text}")
        
        # Step 2: Translate to structured prompt
        click.echo("\nGenerating structured prompt...")
        structured_prompt = prompt_engine.translate_to_structured_prompt(
            natural_text=text,
            task_type=task_type,
            include_cot=True
        )
        
        # Step 3: Generate code
        click.echo("\nGenerating code...")
        code_chunks = []
        async for chunk in llm_router.route_task(
            prompt=structured_prompt,
            task_type=task_type,
            use_swarm=swarm,
            stream=False
        ):
            code_chunks.append(chunk)
        
        return "".join(code_chunks)
    
    code = asyncio.run(run_pipeline())
    
    if output:
        with open(output, "w") as f:
            f.write(code)
        click.echo(f"\nCode written to {output}")
    else:
        click.echo("\nGenerated Code:")
        click.echo(code)


@cli.command()
@click.argument("text")
@click.option("--voice", default="default", help="Voice identifier")
@click.option("--output", "-o", type=click.Path(), help="Output audio file")
def speak(text: str, voice: str, output: str):
    """Synthesize text to speech audio."""
    from .tts import create_tts_provider
    
    click.echo(f"Synthesizing speech...")
    
    async def run_synthesis():
        tts = create_tts_provider(
            settings.tts_provider,
            settings.elevenlabs_api_key
        )
        return await tts.synthesize(text=text, voice=voice)
    
    audio_data = asyncio.run(run_synthesis())
    
    if output:
        with open(output, "wb") as f:
            f.write(audio_data)
        click.echo(f"Audio written to {output}")
    else:
        click.echo(f"Generated {len(audio_data)} bytes of audio data")


@cli.command()
def git_status():
    """Show git repository status."""
    from .git import GitManager
    
    async def run_status():
        gm = GitManager()
        return await gm.status()
    
    result = asyncio.run(run_status())
    click.echo(f"Branch: {result.get('branch', 'unknown')}")
    click.echo(f"Clean: {result.get('clean', False)}")
    if result.get('output'):
        click.echo(f"\n{result['output']}")


if __name__ == "__main__":
    cli()
