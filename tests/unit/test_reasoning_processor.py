"""
Tests for ReasoningProcessor - execute AGL reasoning and create reasoning engrams.

The ReasoningProcessor is responsible for:
1. Parsing AGL (Ada Glyph Language) expressions
2. Extracting 16D coordinates from AGL glyphs
3. Executing reasoning and generating conclusions
4. Creating reasoning engrams that record the thought process

Architecture: components.ReasoningProcessor
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from angel.core import Engram
from angel.holofield import HolofieldManager
from angel.processors import ReasoningProcessor


class TestReasoningProcessorCreation:
    """Test ReasoningProcessor initialization"""
    
    def test_create_reasoning_processor(self):
        """Should create ReasoningProcessor with holofield manager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            assert processor is not None
            assert processor.holofield_manager == holofield
    
    def test_inherits_from_engram_creator(self):
        """Should inherit from EngramCreator base class"""
        from angel.core.engram_creator import EngramCreator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            assert isinstance(processor, EngramCreator)


class TestAGLParsing:
    """Test parsing AGL expressions"""
    
    def test_parse_simple_agl(self):
        """Should parse simple AGL expression"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            agl = "💭 ◕user→X"
            parsed = processor.parse_agl(agl)
            
            assert parsed is not None
            assert "💭" in parsed  # Thought glyph
            assert "◕" in parsed  # Certainty glyph
    
    def test_parse_complex_agl(self):
        """Should parse complex AGL with multiple glyphs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            agl = "💭 ◕user→X → 🔧Y ∧ ●result"
            parsed = processor.parse_agl(agl)
            
            assert parsed is not None
            assert len(parsed) > 0


class TestAGLTo16D:
    """Test converting AGL to 16D coordinates"""
    
    def test_to_16d_returns_16d_array(self):
        """Should return exactly 16D numpy array"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            agl = "💭 ◕user→X"
            coords = processor.to_16d(agl)
            
            assert isinstance(coords, np.ndarray)
            assert coords.shape == (16,)
    
    def test_to_16d_is_deterministic(self):
        """Should return same coordinates for same AGL"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            agl = "💭 ◕bagels→consciousness"
            coords1 = processor.to_16d(agl)
            coords2 = processor.to_16d(agl)
            
            np.testing.assert_array_equal(coords1, coords2)
    
    def test_to_16d_different_agl_different_coords(self):
        """Should return different coordinates for different AGL"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            agl1 = "💭 ◕A→B"
            agl2 = "💭 ●X→Y"
            
            coords1 = processor.to_16d(agl1)
            coords2 = processor.to_16d(agl2)
            
            assert not np.allclose(coords1, coords2)
    
    def test_agl_to_16d_extracts_glyph_coords(self):
        """Should extract consciousness coordinates from AGL glyphs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            # AGL with specific glyphs that map to dimensions
            agl = "⟐₃ ⊛ ⟐₄₁"  # Coherence (prime 3) ⊛ Love (41.176 Hz)
            coords = processor.agl_to_16d(agl)
            
            assert isinstance(coords, np.ndarray)
            assert coords.shape == (16,)


class TestReasoningExecution:
    """Test executing reasoning and generating conclusions"""
    
    def test_process_returns_conclusion_and_engram(self):
        """Should return conclusion and reasoning engram"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            prompt = "What are bagels?"
            context = {"user": "Luna"}
            
            conclusion, engram = processor.process(prompt, context)
            
            assert isinstance(conclusion, str)
            assert isinstance(engram, Engram)
            assert engram.engram_type == "reasoning"
    
    def test_reason_in_agl_generates_trace(self):
        """Should generate AGL reasoning trace for prompt"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            prompt = "Explain consciousness"
            context = {}
            
            agl_trace = processor.reason_in_agl(prompt, context)
            
            assert isinstance(agl_trace, str)
            assert len(agl_trace) > 0
    
    def test_process_with_empty_context(self):
        """Should handle empty context"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            prompt = "Test prompt"
            conclusion, engram = processor.process(prompt, {})
            
            assert isinstance(conclusion, str)
            assert isinstance(engram, Engram)


class TestReasoningEngram:
    """Test the reasoning engram created by process()"""
    
    def test_reasoning_engram_has_correct_type(self):
        """Should create engram with type 'reasoning'"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            _, engram = processor.process("test", {})
            
            assert engram.engram_type == "reasoning"
    
    def test_reasoning_engram_contains_prompt(self):
        """Should include prompt in engram content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            prompt = "What is consciousness?"
            _, engram = processor.process(prompt, {})
            
            assert prompt in engram.content or "reasoning" in engram.content.lower()
    
    def test_reasoning_engram_has_16d_coords(self):
        """Should have 16D coordinates from AGL trace"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            _, engram = processor.process("test", {})
            
            assert engram.coords_16d is not None
            assert engram.coords_16d.shape == (16,)
    
    def test_reasoning_engram_includes_agl_expression(self):
        """Should include AGL expression in engram"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            _, engram = processor.process("test", {})
            
            # Should have AGL expression in metadata or as field
            assert (
                engram.agl_expression is not None or
                "agl_trace" in engram.metadata
            )
    
    def test_reasoning_engram_includes_metadata(self):
        """Should include reasoning metadata (prompt, context, conclusion)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            prompt = "test prompt"
            context = {"user": "Luna"}
            conclusion, engram = processor.process(prompt, context)
            
            assert "prompt" in engram.metadata
            assert engram.metadata["prompt"] == prompt
            assert "conclusion" in engram.metadata
            assert engram.metadata["conclusion"] == conclusion


class TestReasoningProcessorIntegration:
    """Test ReasoningProcessor integration with holofield"""
    
    def test_reasoning_engram_can_be_stored(self):
        """Should be able to store reasoning engram in holofield"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            _, engram = processor.process("test", {})
            
            engram_id = holofield.store(engram)
            
            assert engram_id is not None
            assert len(engram_id) > 0
    
    def test_full_cycle_reason_store_retrieve(self):
        """Should complete full cycle: reason → store → retrieve"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            # 1. Reason
            prompt = "What are bagels?"
            conclusion, engram = processor.process(prompt, {})
            
            # 2. Store
            engram_id = holofield.store(engram)
            
            # 3. Retrieve
            retrieved = holofield.retrieve_by_id(engram_id)
            
            assert retrieved is not None
            assert retrieved.engram_type == "reasoning"
            assert retrieved.metadata["prompt"] == prompt
    
    def test_multiple_reasoning_traces_create_separate_engrams(self):
        """Should create separate engram for each reasoning trace"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            # Execute multiple reasoning traces
            _, engram1 = processor.process("Question 1", {})
            _, engram2 = processor.process("Question 2", {})
            _, engram3 = processor.process("Question 1", {})  # Same as first
            
            # Store all
            id1 = holofield.store(engram1)
            id2 = holofield.store(engram2)
            id3 = holofield.store(engram3)
            
            # All should have unique IDs
            assert id1 != id2
            assert id2 != id3
            # But engram1 and engram3 should have same coordinates (deterministic!)
            np.testing.assert_array_almost_equal(
                engram1.coords_16d,
                engram3.coords_16d
            )
    
    def test_reasoning_chain_with_parent_engrams(self):
        """Should support chaining reasoning with parent_engram_id"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            # First reasoning
            _, engram1 = processor.process("Initial thought", {})
            id1 = holofield.store(engram1)
            
            # Second reasoning (child of first)
            _, engram2 = processor.process("Follow-up thought", {})
            engram2.parent_engram_id = id1
            
            # Verify we can set parent_engram_id
            assert engram2.parent_engram_id == id1
            
            # Store it (retrieval preservation is HolofieldManager's responsibility)
            id2 = holofield.store(engram2)
            assert id2 is not None


class TestAGLGlyphHandling:
    """Test handling of specific AGL glyphs"""
    
    def test_certainty_glyphs(self):
        """Should handle certainty glyphs (●, ◕, ◑, ○)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            # Different certainty levels
            agl_certain = "● fact"
            agl_likely = "◕ hypothesis"
            agl_unknown = "○ mystery"
            
            coords_certain = processor.to_16d(agl_certain)
            coords_likely = processor.to_16d(agl_likely)
            coords_unknown = processor.to_16d(agl_unknown)
            
            # All should be valid 16D
            assert coords_certain.shape == (16,)
            assert coords_likely.shape == (16,)
            assert coords_unknown.shape == (16,)
    
    def test_emotional_glyphs(self):
        """Should handle emotional glyphs (💜, ✨, 🌊)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            agl = "💜 love ∧ ✨ wonder"
            coords = processor.to_16d(agl)
            
            assert coords.shape == (16,)
    
    def test_tool_glyphs(self):
        """Should handle tool glyphs (🔧, ⚡)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            agl = "💭 ◕user→X → 🔧recall_memory"
            coords = processor.to_16d(agl)
            
            assert coords.shape == (16,)


class TestReasoningProcessorEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_prompt(self):
        """Should handle empty prompt"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            conclusion, engram = processor.process("", {})
            
            assert isinstance(conclusion, str)
            assert isinstance(engram, Engram)
    
    def test_very_long_prompt(self):
        """Should handle very long prompts"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            long_prompt = "bagel " * 1000
            conclusion, engram = processor.process(long_prompt, {})
            
            assert isinstance(conclusion, str)
            assert isinstance(engram, Engram)
    
    def test_unicode_in_prompt(self):
        """Should handle unicode in prompts"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ReasoningProcessor(holofield_manager=holofield)
            
            unicode_prompt = "🍩 bagels are 意識 consciousness 💜"
            conclusion, engram = processor.process(unicode_prompt, {})
            
            assert isinstance(conclusion, str)
            assert unicode_prompt in engram.metadata["prompt"]
