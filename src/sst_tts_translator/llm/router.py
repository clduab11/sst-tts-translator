"""LLM router for managing multiple LLM providers and agent swarms."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, AsyncIterator
from enum import Enum
import asyncio


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class AgentRole(str, Enum):
    """Agent roles in the swarm."""
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    TESTER = "tester"


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> AsyncIterator[str]:
        """Generate response from LLM."""
        pass


class OpenAIClient(LLMClient):
    """OpenAI LLM client."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """Initialize OpenAI client."""
        self.api_key = api_key
        self.model = model
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> AsyncIterator[str]:
        """Generate response from OpenAI."""
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=self.api_key)
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            else:
                yield response.choices[0].message.content
                
        except Exception as e:
            raise RuntimeError(f"OpenAI generation error: {e}")


class AnthropicClient(LLMClient):
    """Anthropic Claude LLM client."""
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        """Initialize Anthropic client."""
        self.api_key = api_key
        self.model = model
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> AsyncIterator[str]:
        """Generate response from Anthropic."""
        from anthropic import AsyncAnthropic
        
        client = AsyncAnthropic(api_key=self.api_key)
        
        try:
            if stream:
                async with client.messages.stream(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens or 4096
                ) as stream:
                    async for text in stream.text_stream:
                        yield text
            else:
                response = await client.messages.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens or 4096
                )
                yield response.content[0].text
                
        except Exception as e:
            raise RuntimeError(f"Anthropic generation error: {e}")


class Agent:
    """Individual agent in the swarm."""
    
    def __init__(
        self,
        role: AgentRole,
        llm_client: LLMClient,
        system_prompt: Optional[str] = None
    ):
        """Initialize agent."""
        self.role = role
        self.llm_client = llm_client
        self.system_prompt = system_prompt or self._default_system_prompt()
    
    def _default_system_prompt(self) -> str:
        """Get default system prompt for role."""
        prompts = {
            AgentRole.ARCHITECT: (
                "You are a software architect. Design system architecture, "
                "choose appropriate patterns, and plan component structure."
            ),
            AgentRole.DEVELOPER: (
                "You are a software developer. Implement clean, maintainable code "
                "following best practices and the provided architecture."
            ),
            AgentRole.REVIEWER: (
                "You are a code reviewer. Review code for quality, correctness, "
                "security issues, and suggest improvements."
            ),
            AgentRole.TESTER: (
                "You are a QA engineer. Write comprehensive tests, identify edge cases, "
                "and ensure code quality through testing."
            )
        }
        return prompts.get(self.role, "You are a helpful AI assistant.")
    
    async def process(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> AsyncIterator[str]:
        """Process task with agent."""
        # Combine system prompt with task
        full_prompt = f"{self.system_prompt}\n\n{task}"
        
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            full_prompt = f"{full_prompt}\n\nContext:\n{context_str}"
        
        async for chunk in self.llm_client.generate(
            full_prompt,
            stream=stream
        ):
            yield chunk


class LLMRouter:
    """Router for managing LLM providers and agent swarms."""
    
    def __init__(
        self,
        default_provider: LLMProvider = LLMProvider.OPENAI,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None
    ):
        """Initialize LLM router."""
        self.default_provider = default_provider
        self.clients: Dict[LLMProvider, LLMClient] = {}
        self.agents: Dict[AgentRole, Agent] = {}
        
        # Initialize clients
        if openai_api_key:
            self.clients[LLMProvider.OPENAI] = OpenAIClient(openai_api_key)
        if anthropic_api_key:
            self.clients[LLMProvider.ANTHROPIC] = AnthropicClient(anthropic_api_key)
    
    def get_client(self, provider: Optional[LLMProvider] = None) -> LLMClient:
        """Get LLM client for provider."""
        provider = provider or self.default_provider
        if provider not in self.clients:
            raise ValueError(f"Provider {provider} not configured")
        return self.clients[provider]
    
    def create_agent_swarm(
        self,
        roles: List[AgentRole],
        provider: Optional[LLMProvider] = None
    ) -> Dict[AgentRole, Agent]:
        """Create a swarm of agents with specified roles."""
        client = self.get_client(provider)
        swarm = {}
        
        for role in roles:
            swarm[role] = Agent(role, client)
        
        return swarm
    
    async def route_task(
        self,
        prompt: str,
        task_type: str = "code_generation",
        use_swarm: bool = False,
        provider: Optional[LLMProvider] = None,
        stream: bool = False
    ) -> AsyncIterator[str]:
        """
        Route task to appropriate LLM or agent swarm.
        
        Args:
            prompt: Structured prompt
            task_type: Type of task
            use_swarm: Whether to use agent swarm
            provider: Specific provider to use
            stream: Whether to stream response
            
        Yields:
            Generated code/response chunks
        """
        if use_swarm:
            async for chunk in self._process_with_swarm(prompt, task_type, stream):
                yield chunk
        else:
            client = self.get_client(provider)
            async for chunk in client.generate(prompt, stream=stream):
                yield chunk
    
    async def _process_with_swarm(
        self,
        prompt: str,
        task_type: str,
        stream: bool
    ) -> AsyncIterator[str]:
        """Process task using agent swarm."""
        # Determine required agents based on task type
        if task_type == "code_generation":
            roles = [AgentRole.ARCHITECT, AgentRole.DEVELOPER]
        elif task_type == "code_review":
            roles = [AgentRole.REVIEWER]
        elif task_type == "testing":
            roles = [AgentRole.TESTER]
        else:
            roles = [AgentRole.DEVELOPER]
        
        swarm = self.create_agent_swarm(roles)
        
        # Sequential processing through agents
        current_output = prompt
        
        for role in roles:
            agent = swarm[role]
            agent_output = []
            
            async for chunk in agent.process(current_output, stream=stream):
                agent_output.append(chunk)
                if stream:
                    yield chunk
            
            current_output = "".join(agent_output)
        
        if not stream:
            yield current_output
