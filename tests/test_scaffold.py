"""Tests for DDD scaffold generator."""

import pytest
from sst_tts_translator.scaffold import (
    DDDGenerator,
    DDDScaffold,
    Entity,
    EntityField,
    Repository
)


def test_ddd_generator_initialization():
    """Test DDD generator initialization."""
    generator = DDDGenerator(language="python")
    assert generator.language == "python"


def test_generate_python_entity():
    """Test generating Python entity."""
    generator = DDDGenerator(language="python")
    
    entity = Entity(
        name="User",
        fields=[
            EntityField(name="username", type="str"),
            EntityField(name="email", type="str"),
        ]
    )
    
    code = generator._generate_python_entity(entity)
    
    assert "class User:" in code
    assert "username: str" in code
    assert "email: str" in code
    assert "from dataclasses import dataclass" in code


def test_generate_python_repository():
    """Test generating Python repository."""
    generator = DDDGenerator(language="python")
    
    repo = Repository(
        name="UserRepository",
        entity="User"
    )
    
    code = generator._generate_python_repository(repo)
    
    assert "class UserRepository(ABC):" in code
    assert "get_by_id" in code
    assert "get_all" in code
    assert "save" in code
    assert "delete" in code


def test_generate_scaffold():
    """Test generating complete scaffold."""
    generator = DDDGenerator(language="python")
    
    scaffold = DDDScaffold(
        domain_name="user_management",
        entities=[
            Entity(
                name="User",
                fields=[EntityField(name="name", type="str")]
            )
        ]
    )
    
    files = generator.generate_scaffold(scaffold)
    
    assert "user_management/__init__.py" in files
    assert "user_management/entities/__init__.py" in files
    assert "user_management/entities/user.py" in files
