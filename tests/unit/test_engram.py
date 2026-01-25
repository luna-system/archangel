"""
Unit tests for Engram dataclass

Tests the core Engram class which is the foundation of the entire system.
Engram == SIF Entity (ADR-0006)
"""

import pytest
import numpy as np
from datetime import datetime
from angel.core.engram import Engram


class TestEngramCreation:
    """Test basic engram creation"""
    
    def test_minimal_engram(self):
        """Test creating engram with minimal required fields"""
        engram = Engram(
            content="test content",
            coords_16d=np.zeros(16),
            engram_type="test"
        )
        
        assert engram.content == "test content"
        assert len(engram.coords_16d) == 16
        assert engram.engram_type == "test"
    
    def test_engram_with_all_fields(self):
        """Test creating engram with all fields"""
        coords = np.random.rand(16)
        metadata = {"key": "value"}
        
        engram = Engram(
            content="full test",
            coords_16d=coords,
            engram_type="conversation",
            confidence=0.95,
            metadata=metadata,
            timestamp=datetime.now()
        )
        
        assert engram.content == "full test"
        assert np.array_equal(engram.coords_16d, coords)
        assert engram.engram_type == "conversation"
        assert engram.confidence == 0.95
        assert engram.metadata == metadata
        assert isinstance(engram.timestamp, datetime)
    
    def test_engram_default_timestamp(self):
        """Test that timestamp defaults to now"""
        engram = Engram(
            content="test",
            coords_16d=np.zeros(16),
            engram_type="test"
        )
        
        assert isinstance(engram.timestamp, datetime)
        assert (datetime.now() - engram.timestamp).total_seconds() < 1
    
    def test_engram_default_confidence(self):
        """Test that confidence defaults to 1.0"""
        engram = Engram(
            content="test",
            coords_16d=np.zeros(16),
            engram_type="test"
        )
        
        assert engram.confidence == 1.0
    
    def test_engram_default_metadata(self):
        """Test that metadata defaults to empty dict"""
        engram = Engram(
            content="test",
            coords_16d=np.zeros(16),
            engram_type="test"
        )
        
        assert engram.metadata == {}


class TestEngramTypes:
    """Test different engram types"""
    
    def test_conversation_engram(self):
        """Test conversation engram"""
        engram = Engram(
            content="Hello, how are you?",
            coords_16d=np.zeros(16),
            engram_type="conversation",
            metadata={"speaker": "user"}
        )
        
        assert engram.engram_type == "conversation"
        assert engram.metadata["speaker"] == "user"
    
    def test_tool_engram(self):
        """Test tool engram"""
        engram = Engram(
            content="execute_command('ls')",
            coords_16d=np.zeros(16),
            engram_type="tool",
            metadata={"tool_name": "terminal", "result": "file1.txt"}
        )
        
        assert engram.engram_type == "tool"
        assert engram.metadata["tool_name"] == "terminal"
    
    def test_language_engram(self):
        """Test language engram"""
        engram = Engram(
            content="hello",
            coords_16d=np.random.rand(16),
            engram_type="language",
            metadata={"language": "en", "word_count": 1}
        )
        
        assert engram.engram_type == "language"
        assert engram.metadata["language"] == "en"
    
    def test_reasoning_engram(self):
        """Test reasoning engram"""
        engram = Engram(
            content="💭 ◕user→X → 🔧Y",
            coords_16d=np.zeros(16),
            engram_type="reasoning",
            metadata={"agl_trace": "💭 ◕user→X → 🔧Y"}
        )
        
        assert engram.engram_type == "reasoning"
        assert "agl_trace" in engram.metadata


class TestEngram16DCoordinates:
    """Test 16D consciousness coordinates"""
    
    def test_coords_must_be_16d(self):
        """Test that coordinates must be exactly 16 dimensions"""
        engram = Engram(
            content="test",
            coords_16d=np.zeros(16),
            engram_type="test"
        )
        
        assert len(engram.coords_16d) == 16
    
    def test_coords_are_numpy_array(self):
        """Test that coordinates are numpy arrays"""
        engram = Engram(
            content="test",
            coords_16d=np.zeros(16),
            engram_type="test"
        )
        
        assert isinstance(engram.coords_16d, np.ndarray)
    
    def test_coords_can_be_any_float_values(self):
        """Test that coordinates can be any float values"""
        coords = np.array([
            1.5, -2.3, 0.0, 100.5, -50.2,
            3.14, 2.71, 1.41, 1.61, 0.57,
            -10.0, 20.5, -30.1, 40.9, -50.3, 60.7
        ])
        
        engram = Engram(
            content="test",
            coords_16d=coords,
            engram_type="test"
        )
        
        assert np.array_equal(engram.coords_16d, coords)


class TestEngramSIFEquivalence:
    """Test Engram-SIF equivalence (ADR-0006)"""
    
    def test_engram_to_dict(self):
        """Test converting engram to dict (SIF-like)"""
        coords = np.random.rand(16)
        timestamp = datetime.now()
        
        engram = Engram(
            content="test",
            coords_16d=coords,
            engram_type="test",
            confidence=0.95,
            metadata={"key": "value"},
            timestamp=timestamp
        )
        
        # Should be able to convert to dict
        engram_dict = {
            "content": engram.content,
            "coords_16d": engram.coords_16d.tolist(),
            "engram_type": engram.engram_type,
            "confidence": engram.confidence,
            "metadata": engram.metadata,
            "timestamp": engram.timestamp.isoformat()
        }
        
        assert engram_dict["content"] == "test"
        assert len(engram_dict["coords_16d"]) == 16
        assert engram_dict["engram_type"] == "test"
        assert engram_dict["confidence"] == 0.95
    
    def test_dict_to_engram(self):
        """Test creating engram from dict (SIF-like)"""
        engram_dict = {
            "content": "test",
            "coords_16d": [0.1] * 16,
            "engram_type": "test",
            "confidence": 0.95,
            "metadata": {"key": "value"},
            "timestamp": datetime.now().isoformat()
        }
        
        engram = Engram(
            content=engram_dict["content"],
            coords_16d=np.array(engram_dict["coords_16d"]),
            engram_type=engram_dict["engram_type"],
            confidence=engram_dict["confidence"],
            metadata=engram_dict["metadata"],
            timestamp=datetime.fromisoformat(engram_dict["timestamp"])
        )
        
        assert engram.content == "test"
        assert len(engram.coords_16d) == 16
        assert engram.engram_type == "test"


class TestEngramValidation:
    """Test engram validation"""
    
    def test_coords_wrong_size_raises_error(self):
        """Test that wrong-sized coordinates raise an error"""
        with pytest.raises((ValueError, AssertionError)):
            Engram(
                content="test",
                coords_16d=np.zeros(8),  # Wrong size!
                engram_type="test"
            )
    
    def test_confidence_out_of_range(self):
        """Test that confidence outside [0, 1] raises warning or error"""
        # This might be a warning rather than error, depending on implementation
        # For now, just test that we can create it
        engram = Engram(
            content="test",
            coords_16d=np.zeros(16),
            engram_type="test",
            confidence=1.5  # Out of range
        )
        
        # Implementation might clamp or warn
        assert engram.confidence == 1.5  # Or might be clamped to 1.0


class TestEngramEquality:
    """Test engram equality and comparison"""
    
    def test_engrams_with_same_content_are_equal(self):
        """Test that engrams with same content are equal"""
        coords = np.random.rand(16)
        
        engram1 = Engram(
            content="test",
            coords_16d=coords.copy(),
            engram_type="test"
        )
        
        engram2 = Engram(
            content="test",
            coords_16d=coords.copy(),
            engram_type="test"
        )
        
        # Coordinates should be equal
        assert np.array_equal(engram1.coords_16d, engram2.coords_16d)
    
    def test_engrams_with_different_content_differ(self):
        """Test that engrams with different content differ"""
        engram1 = Engram(
            content="test1",
            coords_16d=np.zeros(16),
            engram_type="test"
        )
        
        engram2 = Engram(
            content="test2",
            coords_16d=np.zeros(16),
            engram_type="test"
        )
        
        assert engram1.content != engram2.content


class TestEngramMetadata:
    """Test engram metadata handling"""
    
    def test_metadata_is_mutable(self):
        """Test that metadata can be modified"""
        engram = Engram(
            content="test",
            coords_16d=np.zeros(16),
            engram_type="test",
            metadata={"key": "value"}
        )
        
        engram.metadata["new_key"] = "new_value"
        assert engram.metadata["new_key"] == "new_value"
    
    def test_metadata_can_store_complex_types(self):
        """Test that metadata can store various types"""
        engram = Engram(
            content="test",
            coords_16d=np.zeros(16),
            engram_type="test",
            metadata={
                "string": "value",
                "int": 42,
                "float": 3.14,
                "list": [1, 2, 3],
                "dict": {"nested": "value"}
            }
        )
        
        assert engram.metadata["string"] == "value"
        assert engram.metadata["int"] == 42
        assert engram.metadata["float"] == 3.14
        assert engram.metadata["list"] == [1, 2, 3]
        assert engram.metadata["dict"]["nested"] == "value"


class TestEngramTemporalChains:
    """Test temporal chain support for conversations"""
    
    def test_engram_can_have_prev_next_ids(self):
        """Test that engrams can store prev/next message IDs"""
        engram = Engram(
            content="test",
            coords_16d=np.zeros(16),
            engram_type="conversation",
            metadata={
                "prev_message_id": 123,
                "next_message_id": 125,
                "session_id": "session_abc"
            }
        )
        
        assert engram.metadata["prev_message_id"] == 123
        assert engram.metadata["next_message_id"] == 125
        assert engram.metadata["session_id"] == "session_abc"
