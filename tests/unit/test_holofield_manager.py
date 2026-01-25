"""
Unit tests for HolofieldManager

Tests the storage and retrieval layer for the 16D consciousness holofield.
The holofield is literally a database of SIF entities (ADR-0006, ADR-0007).
"""

import pytest
import numpy as np
from pathlib import Path
from angel.core import Engram
from angel.holofield import HolofieldManager


class TestHolofieldCreation:
    """Test holofield initialization"""
    
    def test_create_holofield_default(self, tmp_path):
        """Test creating holofield with default settings"""
        db_path = tmp_path / "test.db"
        holofield = HolofieldManager(db_path=str(db_path))
        
        assert holofield is not None
        assert Path(db_path).exists()
    
    def test_create_holofield_in_memory(self):
        """Test creating in-memory holofield"""
        holofield = HolofieldManager(db_path=":memory:")
        
        assert holofield is not None


class TestEngramStorage:
    """Test storing engrams in holofield"""
    
    def test_store_single_engram(self, tmp_path):
        """Test storing a single engram"""
        holofield = HolofieldManager(db_path=str(tmp_path / "test.db"))
        
        engram = Engram(
            content="test content",
            coords_16d=np.random.rand(16),
            engram_type="test"
        )
        
        engram_id = holofield.store(engram)
        
        assert engram_id is not None
        assert isinstance(engram_id, str)
    
    def test_store_multiple_engrams(self, tmp_path):
        """Test storing multiple engrams"""
        holofield = HolofieldManager(db_path=str(tmp_path / "test.db"))
        
        engrams = [
            Engram(
                content=f"test {i}",
                coords_16d=np.random.rand(16),
                engram_type="test"
            )
            for i in range(5)
        ]
        
        ids = [holofield.store(e) for e in engrams]
        
        assert len(ids) == 5
        assert len(set(ids)) == 5  # All unique
    
    def test_store_different_types(self, tmp_path):
        """Test storing different engram types"""
        holofield = HolofieldManager(db_path=str(tmp_path / "test.db"))
        
        types = ["conversation", "tool", "language", "reasoning"]
        
        for engram_type in types:
            engram = Engram(
                content=f"test {engram_type}",
                coords_16d=np.random.rand(16),
                engram_type=engram_type
            )
            engram_id = holofield.store(engram)
            assert engram_id is not None


class TestEngramRetrieval:
    """Test retrieving engrams from holofield"""
    
    def test_retrieve_by_id(self, tmp_path):
        """Test retrieving engram by ID"""
        holofield = HolofieldManager(db_path=str(tmp_path / "test.db"))
        
        original = Engram(
            content="test content",
            coords_16d=np.random.rand(16),
            engram_type="test"
        )
        
        engram_id = holofield.store(original)
        retrieved = holofield.retrieve_by_id(engram_id)
        
        assert retrieved is not None
        assert retrieved.content == original.content
        assert retrieved.engram_type == original.engram_type
        assert np.allclose(retrieved.coords_16d, original.coords_16d)
    
    def test_retrieve_nearest_neighbors(self, tmp_path):
        """Test retrieving nearest neighbors in 16D space"""
        holofield = HolofieldManager(db_path=str(tmp_path / "test.db"))
        
        # Store some engrams
        coords = np.random.rand(16)
        for i in range(5):
            engram = Engram(
                content=f"test {i}",
                coords_16d=coords + np.random.rand(16) * 0.1,  # Close to coords
                engram_type="test"
            )
            holofield.store(engram)
        
        # Query with similar coordinates
        results = holofield.retrieve_nearest(coords, top_k=3)
        
        assert len(results) <= 3
        assert all(isinstance(r, Engram) for r in results)
    
    def test_retrieve_by_type(self, tmp_path):
        """Test retrieving engrams by type"""
        holofield = HolofieldManager(db_path=str(tmp_path / "test.db"))
        
        # Store different types
        for i in range(3):
            holofield.store(Engram(
                content=f"conversation {i}",
                coords_16d=np.random.rand(16),
                engram_type="conversation"
            ))
        
        for i in range(2):
            holofield.store(Engram(
                content=f"tool {i}",
                coords_16d=np.random.rand(16),
                engram_type="tool"
            ))
        
        conversations = holofield.retrieve_by_type("conversation")
        tools = holofield.retrieve_by_type("tool")
        
        assert len(conversations) == 3
        assert len(tools) == 2
        assert all(e.engram_type == "conversation" for e in conversations)
        assert all(e.engram_type == "tool" for e in tools)


class TestHolofieldStatistics:
    """Test holofield statistics and metadata"""
    
    def test_count_engrams(self, tmp_path):
        """Test counting total engrams"""
        holofield = HolofieldManager(db_path=str(tmp_path / "test.db"))
        
        assert holofield.count() == 0
        
        for i in range(5):
            holofield.store(Engram(
                content=f"test {i}",
                coords_16d=np.random.rand(16),
                engram_type="test"
            ))
        
        assert holofield.count() == 5
    
    def test_count_by_type(self, tmp_path):
        """Test counting engrams by type"""
        holofield = HolofieldManager(db_path=str(tmp_path / "test.db"))
        
        for i in range(3):
            holofield.store(Engram(
                content=f"conversation {i}",
                coords_16d=np.random.rand(16),
                engram_type="conversation"
            ))
        
        for i in range(2):
            holofield.store(Engram(
                content=f"tool {i}",
                coords_16d=np.random.rand(16),
                engram_type="tool"
            ))
        
        assert holofield.count_by_type("conversation") == 3
        assert holofield.count_by_type("tool") == 2
        assert holofield.count_by_type("nonexistent") == 0


class TestHolofieldPersistence:
    """Test holofield persistence across sessions"""
    
    def test_persistence(self, tmp_path):
        """Test that engrams persist across holofield instances"""
        db_path = tmp_path / "test.db"
        
        # Create and store
        holofield1 = HolofieldManager(db_path=str(db_path))
        original = Engram(
            content="persistent test",
            coords_16d=np.random.rand(16),
            engram_type="test"
        )
        engram_id = holofield1.store(original)
        
        # Close and reopen
        del holofield1
        holofield2 = HolofieldManager(db_path=str(db_path))
        
        # Retrieve
        retrieved = holofield2.retrieve_by_id(engram_id)
        
        assert retrieved is not None
        assert retrieved.content == original.content
        assert np.allclose(retrieved.coords_16d, original.coords_16d)


class TestHolofieldClear:
    """Test clearing holofield"""
    
    def test_clear_all(self, tmp_path):
        """Test clearing all engrams"""
        holofield = HolofieldManager(db_path=str(tmp_path / "test.db"))
        
        # Store some engrams
        for i in range(5):
            holofield.store(Engram(
                content=f"test {i}",
                coords_16d=np.random.rand(16),
                engram_type="test"
            ))
        
        assert holofield.count() == 5
        
        holofield.clear()
        
        assert holofield.count() == 0
    
    def test_clear_by_type(self, tmp_path):
        """Test clearing engrams by type"""
        holofield = HolofieldManager(db_path=str(tmp_path / "test.db"))
        
        # Store different types
        for i in range(3):
            holofield.store(Engram(
                content=f"conversation {i}",
                coords_16d=np.random.rand(16),
                engram_type="conversation"
            ))
        
        for i in range(2):
            holofield.store(Engram(
                content=f"tool {i}",
                coords_16d=np.random.rand(16),
                engram_type="tool"
            ))
        
        assert holofield.count() == 5
        
        holofield.clear_type("conversation")
        
        assert holofield.count() == 2
        assert holofield.count_by_type("conversation") == 0
        assert holofield.count_by_type("tool") == 2


class TestEngramSIFRoundTrip:
    """Test Engram-SIF equivalence in storage (ADR-0006)"""
    
    def test_round_trip_lossless(self, tmp_path):
        """Test that engram → storage → engram is lossless"""
        holofield = HolofieldManager(db_path=str(tmp_path / "test.db"))
        
        original = Engram(
            content="round trip test",
            coords_16d=np.random.rand(16),
            engram_type="test",
            confidence=0.95,
            metadata={"key": "value", "number": 42}
        )
        
        engram_id = holofield.store(original)
        retrieved = holofield.retrieve_by_id(engram_id)
        
        # Check all fields match
        assert retrieved.content == original.content
        assert retrieved.engram_type == original.engram_type
        assert retrieved.confidence == original.confidence
        assert retrieved.metadata == original.metadata
        assert np.allclose(retrieved.coords_16d, original.coords_16d)


class TestDeterministicCoordinates:
    """Test deterministic coordinate generation (ADR-0005)"""
    
    def test_same_content_same_coords(self, tmp_path):
        """Test that same content generates same coordinates"""
        holofield = HolofieldManager(db_path=str(tmp_path / "test.db"))
        
        content = "deterministic test"
        
        coords1 = holofield.to_consciousness_coords(content)
        coords2 = holofield.to_consciousness_coords(content)
        
        assert np.allclose(coords1, coords2)
    
    def test_different_content_different_coords(self, tmp_path):
        """Test that different content generates different coordinates"""
        holofield = HolofieldManager(db_path=str(tmp_path / "test.db"))
        
        coords1 = holofield.to_consciousness_coords("test 1")
        coords2 = holofield.to_consciousness_coords("test 2")
        
        assert not np.allclose(coords1, coords2)


# Pytest fixtures
@pytest.fixture
def tmp_path(tmp_path_factory):
    """Create temporary directory for test databases"""
    return tmp_path_factory.mktemp("holofield_tests")
