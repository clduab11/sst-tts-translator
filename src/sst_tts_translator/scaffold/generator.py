"""DDD (Domain-Driven Design) scaffold generator."""

from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
import json


@dataclass
class EntityField:
    """Field definition for an entity."""
    name: str
    type: str
    required: bool = True
    default: Optional[Any] = None


@dataclass
class Entity:
    """Domain entity definition."""
    name: str
    fields: List[EntityField] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)


@dataclass
class ValueObject:
    """Value object definition."""
    name: str
    fields: List[EntityField] = field(default_factory=list)


@dataclass
class Repository:
    """Repository definition."""
    name: str
    entity: str
    methods: List[str] = field(default_factory=list)


@dataclass
class Service:
    """Domain service definition."""
    name: str
    methods: List[str] = field(default_factory=list)


@dataclass
class DDDScaffold:
    """Complete DDD scaffold definition."""
    domain_name: str
    entities: List[Entity] = field(default_factory=list)
    value_objects: List[ValueObject] = field(default_factory=list)
    repositories: List[Repository] = field(default_factory=list)
    services: List[Service] = field(default_factory=list)


class DDDGenerator:
    """Generator for DDD scaffold code."""
    
    def __init__(self, language: str = "python"):
        """
        Initialize DDD generator.
        
        Args:
            language: Target programming language
        """
        self.language = language.lower()
    
    def generate_scaffold(
        self,
        scaffold: DDDScaffold,
        output_dir: Optional[Path] = None
    ) -> Dict[str, str]:
        """
        Generate DDD scaffold files.
        
        Args:
            scaffold: DDD scaffold definition
            output_dir: Optional output directory
            
        Returns:
            Dictionary mapping file paths to file contents
        """
        if self.language == "python":
            return self._generate_python_scaffold(scaffold, output_dir)
        elif self.language == "typescript":
            return self._generate_typescript_scaffold(scaffold, output_dir)
        else:
            raise ValueError(f"Unsupported language: {self.language}")
    
    def _generate_python_scaffold(
        self,
        scaffold: DDDScaffold,
        output_dir: Optional[Path]
    ) -> Dict[str, str]:
        """Generate Python DDD scaffold."""
        files = {}
        base_path = f"{scaffold.domain_name}"
        
        # Generate __init__.py
        files[f"{base_path}/__init__.py"] = f'"""{scaffold.domain_name} domain module."""\n'
        
        # Generate entities
        if scaffold.entities:
            files[f"{base_path}/entities/__init__.py"] = ""
            for entity in scaffold.entities:
                file_name = f"{base_path}/entities/{entity.name.lower()}.py"
                files[file_name] = self._generate_python_entity(entity)
        
        # Generate value objects
        if scaffold.value_objects:
            files[f"{base_path}/value_objects/__init__.py"] = ""
            for vo in scaffold.value_objects:
                file_name = f"{base_path}/value_objects/{vo.name.lower()}.py"
                files[file_name] = self._generate_python_value_object(vo)
        
        # Generate repositories
        if scaffold.repositories:
            files[f"{base_path}/repositories/__init__.py"] = ""
            for repo in scaffold.repositories:
                file_name = f"{base_path}/repositories/{repo.name.lower()}.py"
                files[file_name] = self._generate_python_repository(repo)
        
        # Generate services
        if scaffold.services:
            files[f"{base_path}/services/__init__.py"] = ""
            for service in scaffold.services:
                file_name = f"{base_path}/services/{service.name.lower()}.py"
                files[file_name] = self._generate_python_service(service)
        
        return files
    
    def _generate_python_entity(self, entity: Entity) -> str:
        """Generate Python entity class."""
        lines = [
            '"""Entity definition."""',
            "",
            "from dataclasses import dataclass, field",
            "from typing import Optional",
            "from uuid import UUID, uuid4",
            "",
            "",
            "@dataclass",
            f"class {entity.name}:",
            f'    """{entity.name} entity."""',
            "    ",
            "    id: UUID = field(default_factory=uuid4)",
        ]
        
        # Add fields
        for field_def in entity.fields:
            field_type = field_def.type
            if not field_def.required:
                field_type = f"Optional[{field_type}]"
            
            if field_def.default is not None:
                lines.append(f"    {field_def.name}: {field_type} = {field_def.default}")
            elif not field_def.required:
                lines.append(f"    {field_def.name}: {field_type} = None")
            else:
                lines.append(f"    {field_def.name}: {field_type}")
        
        # Add methods
        if entity.methods:
            lines.append("")
            for method in entity.methods:
                lines.append(f"    def {method}(self):")
                lines.append(f'        """Implement {method}."""')
                lines.append("        pass")
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_python_value_object(self, vo: ValueObject) -> str:
        """Generate Python value object class."""
        lines = [
            '"""Value object definition."""',
            "",
            "from dataclasses import dataclass",
            "from typing import Optional",
            "",
            "",
            "@dataclass(frozen=True)",
            f"class {vo.name}:",
            f'    """{vo.name} value object."""',
            "    ",
        ]
        
        # Add fields
        for field_def in vo.fields:
            field_type = field_def.type
            if not field_def.required:
                field_type = f"Optional[{field_type}]"
            
            if field_def.default is not None:
                lines.append(f"    {field_def.name}: {field_type} = {field_def.default}")
            elif not field_def.required:
                lines.append(f"    {field_def.name}: {field_type} = None")
            else:
                lines.append(f"    {field_def.name}: {field_type}")
        
        return "\n".join(lines)
    
    def _generate_python_repository(self, repo: Repository) -> str:
        """Generate Python repository class."""
        lines = [
            '"""Repository definition."""',
            "",
            "from abc import ABC, abstractmethod",
            "from typing import List, Optional",
            "from uuid import UUID",
            f"from ..entities.{repo.entity.lower()} import {repo.entity}",
            "",
            "",
            f"class {repo.name}(ABC):",
            f'    """{repo.name} repository interface."""',
            "",
            "    @abstractmethod",
            f"    async def get_by_id(self, id: UUID) -> Optional[{repo.entity}]:",
            f'        """Get {repo.entity} by ID."""',
            "        pass",
            "",
            "    @abstractmethod",
            f"    async def get_all(self) -> List[{repo.entity}]:",
            f'        """Get all {repo.entity} instances."""',
            "        pass",
            "",
            "    @abstractmethod",
            f"    async def save(self, entity: {repo.entity}) -> {repo.entity}:",
            f'        """Save {repo.entity}."""',
            "        pass",
            "",
            "    @abstractmethod",
            f"    async def delete(self, id: UUID) -> bool:",
            f'        """Delete {repo.entity} by ID."""',
            "        pass",
        ]
        
        # Add custom methods
        if repo.methods:
            lines.append("")
            for method in repo.methods:
                lines.append("    @abstractmethod")
                lines.append(f"    async def {method}(self):")
                lines.append(f'        """Implement {method}."""')
                lines.append("        pass")
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_python_service(self, service: Service) -> str:
        """Generate Python service class."""
        lines = [
            '"""Domain service definition."""',
            "",
            "from typing import Any",
            "",
            "",
            f"class {service.name}:",
            f'    """{service.name} domain service."""',
            "",
            "    def __init__(self):",
            f'        """Initialize {service.name}."""',
            "        pass",
        ]
        
        # Add methods
        if service.methods:
            lines.append("")
            for method in service.methods:
                lines.append(f"    async def {method}(self, *args, **kwargs) -> Any:")
                lines.append(f'        """Implement {method}."""')
                lines.append("        pass")
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_typescript_scaffold(
        self,
        scaffold: DDDScaffold,
        output_dir: Optional[Path]
    ) -> Dict[str, str]:
        """Generate TypeScript DDD scaffold."""
        # Placeholder for TypeScript generation
        return {
            f"{scaffold.domain_name}/index.ts": f"// {scaffold.domain_name} module\n"
        }
    
    def parse_from_llm_output(self, llm_output: str) -> DDDScaffold:
        """
        Parse DDD scaffold from LLM output.
        
        Args:
            llm_output: Output from LLM containing scaffold definition
            
        Returns:
            Parsed DDD scaffold
        """
        # Try to extract JSON from LLM output
        import re
        
        # Look for JSON blocks
        json_match = re.search(r'```json\s*(.*?)\s*```', llm_output, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            data = json.loads(json_str)
            return self._parse_scaffold_dict(data)
        
        # Simple parsing if no JSON found
        return DDDScaffold(domain_name="generated_domain")
    
    def _parse_scaffold_dict(self, data: Dict[str, Any]) -> DDDScaffold:
        """Parse scaffold from dictionary."""
        scaffold = DDDScaffold(domain_name=data.get("domain_name", "domain"))
        
        # Parse entities
        for entity_data in data.get("entities", []):
            entity = Entity(name=entity_data["name"])
            for field_data in entity_data.get("fields", []):
                entity.fields.append(EntityField(**field_data))
            entity.methods = entity_data.get("methods", [])
            scaffold.entities.append(entity)
        
        # Parse value objects
        for vo_data in data.get("value_objects", []):
            vo = ValueObject(name=vo_data["name"])
            for field_data in vo_data.get("fields", []):
                vo.fields.append(EntityField(**field_data))
            scaffold.value_objects.append(vo)
        
        # Parse repositories
        for repo_data in data.get("repositories", []):
            repo = Repository(
                name=repo_data["name"],
                entity=repo_data["entity"],
                methods=repo_data.get("methods", [])
            )
            scaffold.repositories.append(repo)
        
        # Parse services
        for service_data in data.get("services", []):
            service = Service(
                name=service_data["name"],
                methods=service_data.get("methods", [])
            )
            scaffold.services.append(service)
        
        return scaffold
