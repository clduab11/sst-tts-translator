from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sst-tts-translator",
    version="0.1.0",
    author="SST-TTS Translator Team",
    description="SST/TTS middleman LLM for voice-driven code development",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clduab11/sst-tts-translator",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.109.1",
        "uvicorn[standard]>=0.27.0",
        "pydantic>=2.6.0",
        "pydantic-settings>=2.1.0",
        "openai-whisper>=20231117",
        "deepgram-sdk>=3.2.7",
        "sounddevice>=0.4.6",
        "numpy>=1.26.3",
        "aiofiles>=23.2.1",
        "httpx>=0.26.0",
        "jinja2>=3.1.6",
        "python-dotenv>=1.0.1",
        "pyyaml>=6.0.1",
        "python-multipart>=0.0.22",
        "click>=8.1.7",
        "soundfile",
        "anthropic>=0.30.0",
        "openai>=1.10.0",
    ],
)
