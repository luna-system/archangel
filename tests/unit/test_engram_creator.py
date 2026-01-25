"""
Unit tests for EngramCreator abstract base class

Tests the base class that all processors inherit from.
EngramCreator enforces universal engram architecture (ADR-0001).
"""

import pytest
import numpy as np
from abc import ABC
from angel.core import Engram, EngramCreator
from angel.holofield import HolofieldManager


class TestEngramCreatorAbstract:
    """Test that EngramCreator is properly abstract"""
    
    def test_engram_creator_is_abstract(self):
        """Test that EngramCreator cannot be instantiated directly"""
        with pytest.raises(TypeError):
            # Should fail - abstract class
            EngramCreator(holofield_manager=None)
    
    def test_engram_creator_is_abc(self):
        """Test that EngramCreator inherits from ABC"""
        assert issubclass(EngramCreator, ABC)
    
    def test_engram_creator_has_abstract_methods(self):
        """Test that EngramCreator defines abstract methods"""
        # Should have abstract methods: process, to_16d
        abstract_methods = EngramCreator.__abstractmethods__
        
        assert 'process' in abstract_methods
        assert 'to_16d' in abstract_methods


class TestEngramCreatorConcrete:
    """Test concrete implementation of EngramCreator"""
    
    def test_concrete_implementation_works(self):
        """Test that concrete subclass can be instantiated"""
        
        class TestProcessor(EngramCreator):
            def to_16d(self, data):
                return np.zeros(16)
            
            def process(self, input_data):
                engram = self.create_engram(
                    content=str(input_data),
                    data=input_data,
                    engram_type="test"
                )
                return input_data, engram
        
        holofield = HolofieldManager(db_path=":memory:")
        processor = TestProcessor(holofield_manager=holofield)
        
        assert processor is not None
    
    def test_concrete_must_implement_abstract_methods(self):
        """Test that concrete class must implement all abstract methods"""
        
        # Missing to_16d
        class IncompleteProcessor1(EngramCreator):
            def process(self, input_data):
                return input_data, None
        
        with pytest.raises(TypeError):
            holofield = HolofieldManager(db_path=":memory:")
            IncompleteProcessor1(holofield_manager=holofield)
        
        # Missing process
        class IncompleteProcessor2(EngramCreator):
            def to_16d(self, data):
                return np.zeros(16)
        
        with pytest.raises(TypeError):
            holofield = HolofieldManager(db_path=":memory:")
            IncompleteProcessor2(holofield_manager=holofield)


class TestEngramCreatorMethods:
    """Test EngramCreator concrete methods"""
    
    def test_create_engram_method(self):
        """Test that create_engram helper works"""
        
        class TestProcessor(EngramCreator):
            def to_16d(self, data):
                return np.random.rand(16)
            
            def process(self, input_data):
                engram = self.create_engram(
                    content="test content",
                    data=input_data,
                    engram_type="test"
                )
                return input_data, engram
        
        holofield = HolofieldManager(db_path=":memory:")
        processor = TestProcessor(holofield_manager=holofield)
        
        engram = processor.create_engram(
            content="test",
            data={"key": "value"},
            engram_type="test"
        )
        
        assert isinstance(engram, Engram)
        assert engram.content == "test"
        assert engram.engram_type == "test"
        assert len(engram.coords_16d) == 16
    
    def test_store_engram_method(self):
        """Test that store_engram helper works"""
        
        class TestProcessor(EngramCreator):
            def to_16d(self, data):
                return np.random.rand(16)
            
            def process(self, input_data):
                engram = self.create_engram(
                    content="test",
                    data=input_data,
                    engram_type="test"
                )
                engram_id = self.store_engram(engram)
                return input_data, engram
        
        holofield = HolofieldManager(db_path=":memory:")
        processor = TestProcessor(holofield_manager=holofield)
        
        engram = processor.create_engram(
            content="test",
            data={"key": "value"},
            engram_type="test"
        )
        
        engram_id = processor.store_engram(engram)
        
        assert engram_id is not None
        assert isinstance(engram_id, str)
        
        # Should be retrievable
        retrieved = holofield.retrieve_by_id(engram_id)
        assert retrieved is not None
        assert retrieved.content == "test"


class TestEngramCreatorHolofieldIntegration:
    """Test EngramCreator integration with holofield"""
    
    def test_processor_has_holofield_reference(self):
        """Test that processor stores holofield reference"""
        
        class TestProcessor(EngramCreator):
            def to_16d(self, data):
                return np.zeros(16)
            
            def process(self, input_data):
                return input_data, None
        
        holofield = HolofieldManager(db_path=":memory:")
        processor = TestProcessor(holofield_manager=holofield)
        
        assert processor.holofield_manager is holofield
    
    def test_process_creates_and_stores_engram(self):
        """Test complete process flow"""
        
        class TestProcessor(EngramCreator):
            def to_16d(self, data):
                # Simple coordinate generation
                text = str(data)
                return self.holofield_manager.to_consciousness_coords(text)
            
            def process(self, input_data):
                # Create engram
                engram = self.create_engram(
                    content=str(input_data),
                    data=input_data,
                    engram_type="test"
                )
                
                # Store it
                engram_id = self.store_engram(engram)
                
                # Return output and engram
                return f"processed: {input_data}", engram
        
        holofield = HolofieldManager(db_path=":memory:")
        processor = TestProcessor(holofield_manager=holofield)
        
        # Process some data
        output, engram = processor.process("test input")
        
        assert output == "processed: test input"
        assert isinstance(engram, Engram)
        assert engram.content == "test input"
        
        # Should be in holofield
        assert holofield.count() == 1


class TestEngramCreatorMetadata:
    """Test metadata handling in EngramCreator"""
    
    def test_create_engram_with_metadata(self):
        """Test creating engram with custom metadata"""
        
        class TestProcessor(EngramCreator):
            def to_16d(self, data):
                return np.zeros(16)
            
            def process(self, input_data):
                return input_data, None
        
        holofield = HolofieldManager(db_path=":memory:")
        processor = TestProcessor(holofield_manager=holofield)
        
        engram = processor.create_engram(
            content="test",
            data={"key": "value"},
            engram_type="test",
            metadata={"custom": "metadata", "number": 42}
        )
        
        assert engram.metadata["custom"] == "metadata"
        assert engram.metadata["number"] == 42
    
    def test_create_engram_with_confidence(self):
        """Test creating engram with custom confidence"""
        
        class TestProcessor(EngramCreator):
            def to_16d(self, data):
                return np.zeros(16)
            
            def process(self, input_data):
                return input_data, None
        
        holofield = HolofieldManager(db_path=":memory:")
        processor = TestProcessor(holofield_manager=holofield)
        
        engram = processor.create_engram(
            content="test",
            data={"key": "value"},
            engram_type="test",
            confidence=0.75
        )
        
        assert engram.confidence == 0.75


class TestEngramCreatorCoordinateGeneration:
    """Test coordinate generation in EngramCreator"""
    
    def test_to_16d_returns_16d_array(self):
        """Test that to_16d returns 16D coordinates"""
        
        class TestProcessor(EngramCreator):
            def to_16d(self, data):
                # Use holofield's coordinate generation
                return self.holofield_manager.to_consciousness_coords(str(data))
            
            def process(self, input_data):
                return input_data, None
        
        holofield = HolofieldManager(db_path=":memory:")
        processor = TestProcessor(holofield_manager=holofield)
        
        coords = processor.to_16d("test data")
        
        assert isinstance(coords, np.ndarray)
        assert len(coords) == 16
    
    def test_create_engram_uses_to_16d(self):
        """Test that create_engram uses to_16d for coordinates"""
        
        class TestProcessor(EngramCreator):
            def to_16d(self, data):
                # Return specific coordinates for testing
                return np.ones(16) * 42.0
            
            def process(self, input_data):
                return input_data, None
        
        holofield = HolofieldManager(db_path=":memory:")
        processor = TestProcessor(holofield_manager=holofield)
        
        engram = processor.create_engram(
            content="test",
            data="test data",
            engram_type="test"
        )
        
        # Should use our custom to_16d
        assert np.allclose(engram.coords_16d, np.ones(16) * 42.0)
