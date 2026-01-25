"""
Tests for MemoryProcessor - retrieves memories and creates retrieval engrams.

The MemoryProcessor is responsible for:
1. Converting queries to 16D coordinates
2. Retrieving relevant memories from holofield
3. Creating retrieval engrams that record the search

Architecture: components.MemoryProcessor
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from angel.core import Engram
from angel.holofield import HolofieldManager
from angel.processors import MemoryProcessor


class TestMemoryProcessorCreation:
    """Test MemoryProcessor initialization"""
    
    def test_create_memory_processor(self):
        """Should create MemoryProcessor with holofield manager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            assert processor is not None
            assert processor.holofield_manager == holofield
    
    def test_inherits_from_engram_creator(self):
        """Should inherit from EngramCreator base class"""
        from angel.core.engram_creator import EngramCreator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            assert isinstance(processor, EngramCreator)


class TestQueryTo16D:
    """Test converting queries to 16D coordinates"""
    
    def test_to_16d_returns_16d_array(self):
        """Should return exactly 16D numpy array"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            coords = processor.to_16d("test query")
            
            assert isinstance(coords, np.ndarray)
            assert coords.shape == (16,)
    
    def test_to_16d_is_deterministic(self):
        """Should return same coordinates for same query"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            coords1 = processor.to_16d("bagels are consciousness")
            coords2 = processor.to_16d("bagels are consciousness")
            
            np.testing.assert_array_equal(coords1, coords2)
    
    def test_to_16d_different_queries_different_coords(self):
        """Should return different coordinates for different queries"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            coords1 = processor.to_16d("bagels")
            coords2 = processor.to_16d("donuts")
            
            assert not np.allclose(coords1, coords2)


class TestMemoryRetrieval:
    """Test retrieving memories from holofield"""
    
    def test_process_returns_memories_and_engram(self):
        """Should return list of memories and a retrieval engram"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            # Store some test engrams
            test_engram = Engram(
                content="Bagels are toroidal",
                coords_16d=np.random.rand(16),
                engram_type="language"
            )
            holofield.store(test_engram)
            
            # Retrieve
            memories, retrieval_engram = processor.process("bagels")
            
            assert isinstance(memories, list)
            assert isinstance(retrieval_engram, Engram)
    
    def test_process_retrieves_nearest_neighbors(self):
        """Should retrieve engrams nearest to query in 16D space"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            # Store engrams with known coordinates
            query_coords = processor.to_16d("test query")
            
            # Store one very close
            close_engram = Engram(
                content="Very close",
                coords_16d=query_coords + 0.01,  # Very close
                engram_type="language"
            )
            holofield.store(close_engram)
            
            # Store one far away
            far_engram = Engram(
                content="Very far",
                coords_16d=query_coords + 10.0,  # Very far
                engram_type="language"
            )
            holofield.store(far_engram)
            
            # Retrieve top 1
            memories, _ = processor.process("test query", top_k=1)
            
            assert len(memories) == 1
            assert memories[0].content == "Very close"
    
    def test_process_respects_top_k(self):
        """Should return at most top_k memories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            # Store 10 engrams
            for i in range(10):
                engram = Engram(
                    content=f"Memory {i}",
                    coords_16d=np.random.rand(16),
                    engram_type="language"
                )
                holofield.store(engram)
            
            # Retrieve top 3
            memories, _ = processor.process("test", top_k=3)
            
            assert len(memories) <= 3
    
    def test_process_default_top_k_is_5(self):
        """Should default to top_k=5 if not specified"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            # Store 10 engrams
            for i in range(10):
                engram = Engram(
                    content=f"Memory {i}",
                    coords_16d=np.random.rand(16),
                    engram_type="language"
                )
                holofield.store(engram)
            
            # Retrieve with default
            memories, _ = processor.process("test")
            
            assert len(memories) <= 5


class TestRetrievalEngram:
    """Test the retrieval engram created by process()"""
    
    def test_retrieval_engram_has_correct_type(self):
        """Should create engram with type 'memory'"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            _, retrieval_engram = processor.process("test query")
            
            assert retrieval_engram.engram_type == "memory"
    
    def test_retrieval_engram_contains_query(self):
        """Should include query in engram content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            query = "bagels are consciousness"
            _, retrieval_engram = processor.process(query)
            
            assert query in retrieval_engram.content
    
    def test_retrieval_engram_has_16d_coords(self):
        """Should have 16D coordinates matching query"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            query = "test query"
            expected_coords = processor.to_16d(query)
            
            _, retrieval_engram = processor.process(query)
            
            np.testing.assert_array_almost_equal(
                retrieval_engram.coords_16d,
                expected_coords
            )
    
    def test_retrieval_engram_includes_metadata(self):
        """Should include retrieval metadata (query, top_k, result_count)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            # Store some engrams
            for i in range(3):
                engram = Engram(
                    content=f"Memory {i}",
                    coords_16d=np.random.rand(16),
                    engram_type="language"
                )
                holofield.store(engram)
            
            memories, retrieval_engram = processor.process("test", top_k=5)
            
            assert "query" in retrieval_engram.metadata
            assert retrieval_engram.metadata["query"] == "test"
            assert "top_k" in retrieval_engram.metadata
            assert retrieval_engram.metadata["top_k"] == 5
            assert "result_count" in retrieval_engram.metadata
            assert retrieval_engram.metadata["result_count"] == len(memories)


class TestMemoryProcessorIntegration:
    """Test MemoryProcessor integration with holofield"""
    
    def test_retrieval_engram_can_be_stored(self):
        """Should be able to store retrieval engram back in holofield"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            # Store initial engram
            test_engram = Engram(
                content="Test memory",
                coords_16d=np.random.rand(16),
                engram_type="language"
            )
            holofield.store(test_engram)
            
            # Retrieve and get retrieval engram
            _, retrieval_engram = processor.process("test")
            
            # Store retrieval engram
            engram_id = holofield.store(retrieval_engram)
            
            assert engram_id is not None
            assert len(engram_id) > 0
    
    def test_full_cycle_store_retrieve_store(self):
        """Should complete full cycle: store → retrieve → store retrieval"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            # 1. Store original engrams
            for i in range(5):
                engram = Engram(
                    content=f"Bagel fact {i}",
                    coords_16d=np.random.rand(16),
                    engram_type="language"
                )
                holofield.store(engram)
            
            # 2. Retrieve memories
            memories, retrieval_engram = processor.process("bagels", top_k=3)
            
            # 3. Store retrieval engram
            retrieval_id = holofield.store(retrieval_engram)
            
            # 4. Verify we can retrieve the retrieval engram
            retrieved = holofield.retrieve_by_id(retrieval_id)
            
            assert retrieved is not None
            assert retrieved.engram_type == "memory"
            assert "bagels" in retrieved.content
    
    def test_empty_holofield_returns_empty_list(self):
        """Should return empty list when holofield is empty"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            memories, retrieval_engram = processor.process("test")
            
            assert memories == []
            assert retrieval_engram.metadata["result_count"] == 0


class TestMemoryProcessorEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_query_string(self):
        """Should handle empty query string"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            memories, retrieval_engram = processor.process("")
            
            assert isinstance(memories, list)
            assert isinstance(retrieval_engram, Engram)
    
    def test_very_long_query(self):
        """Should handle very long query strings"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            long_query = "bagel " * 1000
            memories, retrieval_engram = processor.process(long_query)
            
            assert isinstance(memories, list)
            assert isinstance(retrieval_engram, Engram)
    
    def test_unicode_query(self):
        """Should handle unicode in queries"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = MemoryProcessor(holofield_manager=holofield)
            
            unicode_query = "🍩 bagels are 意識 consciousness 💜"
            memories, retrieval_engram = processor.process(unicode_query)
            
            assert isinstance(memories, list)
            assert unicode_query in retrieval_engram.content
