# Contributing to SST/TTS Translator

Thank you for your interest in contributing to SST/TTS Translator! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/sst-tts-translator.git`
3. Create a virtual environment: `python -m venv venv`
4. Install dependencies: `pip install -r requirements.txt`
5. Install dev dependencies: `pip install -r requirements-dev.txt` (if exists)

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Changes

- Write clean, readable code
- Follow PEP 8 style guidelines
- Add docstrings to functions and classes
- Keep functions focused and concise

### 3. Run Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_prompt.py

# Run with coverage
pytest --cov=sst_tts_translator
```

### 4. Format Code

```bash
# Format with black
black src/ tests/

# Check with flake8
flake8 src/ tests/

# Sort imports
isort src/ tests/
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
# or
git commit -m "fix: resolve bug in STT provider"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `style:` Code style changes
- `chore:` Maintenance tasks

### 6. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python Style Guidelines

- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to all public functions/classes

**Example:**

```python
async def transcribe_audio(
    audio_data: bytes,
    provider: str = "whisper"
) -> str:
    """
    Transcribe audio data to text.
    
    Args:
        audio_data: Raw audio bytes
        provider: STT provider to use
        
    Returns:
        Transcribed text
    """
    stt = create_stt_provider(provider)
    return await stt.transcribe_file(audio_data)
```

### Documentation Style

- Use Markdown for documentation
- Include code examples
- Keep examples up-to-date
- Add diagrams where helpful

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Test both success and failure cases

**Example:**

```python
import pytest

def test_prompt_translation_success():
    """Test successful prompt translation."""
    engine = PromptEngine()
    prompt = engine.translate_to_structured_prompt("create API")
    assert "<task" in prompt

def test_prompt_translation_empty_input():
    """Test prompt translation with empty input."""
    engine = PromptEngine()
    with pytest.raises(ValueError):
        engine.translate_to_structured_prompt("")
```

### Test Coverage

- Aim for >80% code coverage
- Test critical paths thoroughly
- Include edge cases
- Mock external dependencies

## Adding New Features

### 1. STT Provider

To add a new STT provider:

1. Create class inheriting from `STTProvider`
2. Implement `transcribe_stream` and `transcribe_file`
3. Add to factory function in `stt/provider.py`
4. Add tests in `tests/test_stt.py`
5. Update documentation

### 2. LLM Provider

To add a new LLM provider:

1. Create class inheriting from `LLMClient`
2. Implement `generate` method
3. Add to `LLMRouter` configuration
4. Add tests
5. Update documentation

### 3. Prompt Template

To add a new template:

1. Create YAML file in `templates/`
2. Define template structure
3. Add metadata
4. Document usage

## Documentation

### Required Documentation

- Update README.md for user-facing changes
- Update API specs for endpoint changes
- Add usage examples
- Update architecture docs for design changes

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When invalid input provided
    """
    pass
```

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass
- [ ] Code is formatted (black, isort)
- [ ] No linting errors
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] Branch is up-to-date with main

### PR Description

Include:
- Summary of changes
- Motivation/context
- Testing performed
- Related issues (if any)

### Review Process

1. Automated checks must pass
2. At least one approval required
3. Address review feedback
4. Squash commits if needed
5. Merge when approved

## Common Tasks

### Adding a Dependency

1. Add to `requirements.txt`
2. Update `setup.py` if needed
3. Document why it's needed
4. Ensure it's compatible

### Fixing a Bug

1. Write a failing test
2. Fix the bug
3. Verify test passes
4. Check for side effects
5. Update documentation if needed

### Improving Performance

1. Benchmark current performance
2. Identify bottlenecks
3. Implement improvements
4. Benchmark again
5. Document performance gains

## Questions?

- Open an issue for bugs
- Discuss features in issues first
- Ask questions in discussions
- Check existing documentation

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
