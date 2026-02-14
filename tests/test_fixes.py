"""Tests for bug fixes: generator dead code, value object field ordering,
STT exception chaining, and WebSocket defensive handling."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sst_tts_translator.scaffold import (
    DDDGenerator,
    EntityField,
    ValueObject,
    Entity,
)


class TestValueObjectFieldOrdering:
    """Test that value object fields are reordered so dataclass is valid."""

    def test_required_fields_before_optional(self):
        """Required fields without defaults must come before optional fields."""
        generator = DDDGenerator(language="python")
        vo = ValueObject(
            name="Address",
            fields=[
                EntityField(name="zip_code", type="str", required=False),
                EntityField(name="street", type="str", required=True),
                EntityField(name="city", type="str", required=True),
            ],
        )
        code = generator._generate_python_value_object(vo)
        lines = code.split("\n")
        field_lines = [l.strip() for l in lines if ": " in l and "class " not in l and '"""' not in l and "import" not in l]
        # street and city (required, no default) must come before zip_code (optional, default=None)
        street_idx = next(i for i, l in enumerate(field_lines) if "street" in l)
        city_idx = next(i for i, l in enumerate(field_lines) if "city" in l)
        zip_idx = next(i for i, l in enumerate(field_lines) if "zip_code" in l)
        assert street_idx < zip_idx
        assert city_idx < zip_idx

    def test_required_with_default_before_optional(self):
        """Required fields with defaults come before optional fields."""
        generator = DDDGenerator(language="python")
        vo = ValueObject(
            name="Money",
            fields=[
                EntityField(name="note", type="str", required=False),
                EntityField(name="currency", type="str", required=True, default='"USD"'),
                EntityField(name="amount", type="float", required=True),
            ],
        )
        code = generator._generate_python_value_object(vo)
        lines = code.split("\n")
        field_lines = [l.strip() for l in lines if ": " in l and "class " not in l and '"""' not in l and "import" not in l]
        amount_idx = next(i for i, l in enumerate(field_lines) if "amount" in l)
        currency_idx = next(i for i, l in enumerate(field_lines) if "currency" in l)
        note_idx = next(i for i, l in enumerate(field_lines) if "note" in l)
        # amount (required, no default) < currency (required, with default) < note (optional)
        assert amount_idx < currency_idx
        assert currency_idx < note_idx

    def test_all_required_no_reordering_needed(self):
        """All required fields: no reordering needed, output should be valid."""
        generator = DDDGenerator(language="python")
        vo = ValueObject(
            name="Point",
            fields=[
                EntityField(name="x", type="float", required=True),
                EntityField(name="y", type="float", required=True),
            ],
        )
        code = generator._generate_python_value_object(vo)
        assert "x: float" in code
        assert "y: float" in code


class TestEntityDeadCodeRemoved:
    """Test that the duplicate return in _generate_python_entity is removed."""

    def test_entity_returns_valid_code(self):
        """Entity generation should return valid code with single return."""
        generator = DDDGenerator(language="python")
        entity = Entity(
            name="Order",
            fields=[
                EntityField(name="total", type="float"),
            ],
            methods=["calculate_total"],
        )
        code = generator._generate_python_entity(entity)
        assert "class Order:" in code
        assert "total: float" in code
        assert "def calculate_total(self):" in code
        # The code should be valid Python (no syntax error from orphan lines)
        compile(code, "<test>", "exec")


class TestDeepgramExceptionChaining:
    """Test that Deepgram transcription errors chain the original exception."""

    @pytest.mark.asyncio
    async def test_transcribe_stream_chains_exception(self):
        """RuntimeError raised during streaming should chain the original exception."""
        from sst_tts_translator.stt.provider import DeepgramSTT

        stt = DeepgramSTT(api_key="fake_key")

        async def failing_stream():
            yield b"audio_data"

        with patch("deepgram.DeepgramClient") as mock_cls:
            mock_client = MagicMock()
            mock_cls.return_value = mock_client
            mock_conn = MagicMock()
            mock_client.listen.websocket.v.return_value = mock_conn
            mock_conn.start = AsyncMock(side_effect=ValueError("connection failed"))

            with pytest.raises(RuntimeError) as exc_info:
                async for _ in stt.transcribe_stream(failing_stream()):
                    pass

            assert exc_info.value.__cause__ is not None
            assert isinstance(exc_info.value.__cause__, ValueError)
            assert "connection failed" in str(exc_info.value.__cause__)
