"""Prompt template engine for converting natural speech to structured prompts."""

from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
import yaml


class PromptTemplate:
    """Template for structured prompts with XML tags and context blocks."""
    
    def __init__(self, template_str: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize prompt template.
        
        Args:
            template_str: Jinja2 template string
            metadata: Optional metadata about the template
        """
        self.template = Template(template_str)
        self.metadata = metadata or {}
    
    def render(self, **kwargs) -> str:
        """
        Render template with provided context.
        
        Args:
            **kwargs: Template variables
            
        Returns:
            Rendered prompt string
        """
        return self.template.render(**kwargs)


class PromptEngine:
    """Engine for managing and rendering prompt templates."""
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize prompt engine.
        
        Args:
            template_dir: Directory containing template files
        """
        self.template_dir = Path(template_dir) if template_dir else None
        self.templates: Dict[str, PromptTemplate] = {}
        
        if self.template_dir and self.template_dir.exists():
            self._load_templates()
    
    def _load_templates(self):
        """Load templates from template directory."""
        if not self.template_dir:
            return
        
        for template_file in self.template_dir.glob("*.yaml"):
            self._load_template_file(template_file)
    
    def _load_template_file(self, template_path: Path):
        """Load a single template file."""
        with open(template_path, 'r') as f:
            data = yaml.safe_load(f)
        
        template_name = data.get('name', template_path.stem)
        template_str = data.get('template', '')
        metadata = data.get('metadata', {})
        
        self.templates[template_name] = PromptTemplate(template_str, metadata)
    
    def register_template(
        self, 
        name: str, 
        template_str: str, 
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Register a new template.
        
        Args:
            name: Template name
            template_str: Template string
            metadata: Optional template metadata
        """
        self.templates[name] = PromptTemplate(template_str, metadata)
    
    def translate_to_structured_prompt(
        self,
        natural_text: str,
        task_type: str = "code_generation",
        include_cot: bool = True,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Translate natural speech to structured prompt.
        
        Args:
            natural_text: Natural language input from STT
            task_type: Type of task (code_generation, debug, refactor, etc.)
            include_cot: Whether to include Chain of Thought prompting
            context: Additional context information
            
        Returns:
            Structured prompt with XML tags and context blocks
        """
        context = context or {}
        
        # Extract intent and entities from natural text
        intent = self._extract_intent(natural_text, task_type)
        entities = self._extract_entities(natural_text)
        
        # Build structured prompt
        prompt_parts = []
        
        # Add XML task definition
        prompt_parts.append(f"<task type='{task_type}'>")
        prompt_parts.append(f"  <intent>{intent}</intent>")
        prompt_parts.append(f"  <natural_input>{natural_text}</natural_input>")
        
        # Add entities if present
        if entities:
            prompt_parts.append("  <entities>")
            for key, value in entities.items():
                prompt_parts.append(f"    <{key}>{value}</{key}>")
            prompt_parts.append("  </entities>")
        
        # Add context blocks
        if context:
            prompt_parts.append("  <context>")
            for key, value in context.items():
                prompt_parts.append(f"    <{key}>{value}</{key}>")
            prompt_parts.append("  </context>")
        
        prompt_parts.append("</task>")
        
        # Add Chain of Thought section if enabled
        if include_cot:
            prompt_parts.append("\n<reasoning>")
            prompt_parts.append("  Think step by step:")
            prompt_parts.append("  1. Understand the user's intent")
            prompt_parts.append("  2. Identify required components and structure")
            prompt_parts.append("  3. Plan the implementation approach")
            prompt_parts.append("  4. Generate clean, maintainable code")
            prompt_parts.append("</reasoning>")
        
        # Add output format specification
        prompt_parts.append("\n<output_format>")
        prompt_parts.append("  Provide the implementation with:")
        prompt_parts.append("  - Clear file structure")
        prompt_parts.append("  - Well-documented code")
        prompt_parts.append("  - Following best practices")
        prompt_parts.append("  - DDD principles where applicable")
        prompt_parts.append("</output_format>")
        
        return "\n".join(prompt_parts)
    
    def _extract_intent(self, text: str, default_task: str) -> str:
        """Extract user intent from natural text."""
        text_lower = text.lower()
        
        # Simple keyword-based intent extraction
        intents = {
            "create": ["create", "build", "make", "generate", "scaffold"],
            "modify": ["change", "update", "modify", "refactor", "improve"],
            "debug": ["fix", "debug", "resolve", "error", "bug"],
            "explain": ["explain", "describe", "what is", "how does"],
            "test": ["test", "testing", "unit test", "integration test"],
        }
        
        for intent, keywords in intents.items():
            if any(keyword in text_lower for keyword in keywords):
                return intent
        
        return default_task
    
    def _extract_entities(self, text: str) -> Dict[str, str]:
        """Extract entities from natural text."""
        entities = {}
        
        # Extract programming languages
        languages = ["python", "javascript", "typescript", "java", "go", "rust"]
        for lang in languages:
            if lang in text.lower():
                entities["language"] = lang
                break
        
        # Extract frameworks
        frameworks = ["fastapi", "django", "flask", "react", "vue", "express"]
        for framework in frameworks:
            if framework in text.lower():
                entities["framework"] = framework
                break
        
        # Extract patterns
        patterns = ["rest api", "microservice", "crud", "authentication"]
        for pattern in patterns:
            if pattern in text.lower():
                entities["pattern"] = pattern
                break
        
        return entities
    
    def render_template(
        self, 
        template_name: str, 
        **kwargs
    ) -> str:
        """
        Render a registered template.
        
        Args:
            template_name: Name of the template
            **kwargs: Template variables
            
        Returns:
            Rendered prompt
        """
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        return self.templates[template_name].render(**kwargs)
