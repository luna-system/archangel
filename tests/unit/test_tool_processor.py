"""
Tests for ToolProcessor - execute tools and create tool engrams.

The ToolProcessor is responsible for:
1. Registering tools with their definitions
2. Converting tool calls to 16D coordinates
3. Executing tools and capturing results
4. Creating tool engrams that record the execution

Architecture: components.ToolProcessor
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile

from angel.core import Engram
from angel.holofield import HolofieldManager
from angel.processors import ToolProcessor


# Test tool implementations
def simple_add(a: int, b: int) -> int:
    """Simple addition tool for testing"""
    return a + b


def echo_tool(message: str) -> str:
    """Echo back the message"""
    return f"Echo: {message}"


def failing_tool() -> None:
    """Tool that raises an exception"""
    raise ValueError("This tool always fails!")


class TestToolProcessorCreation:
    """Test ToolProcessor initialization"""
    
    def test_create_tool_processor(self):
        """Should create ToolProcessor with holofield manager"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            assert processor is not None
            assert processor.holofield_manager == holofield
    
    def test_inherits_from_engram_creator(self):
        """Should inherit from EngramCreator base class"""
        from angel.core.engram_creator import EngramCreator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            assert isinstance(processor, EngramCreator)
    
    def test_starts_with_empty_tool_registry(self):
        """Should start with no registered tools"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            assert len(processor.tools) == 0


class TestToolRegistration:
    """Test registering tools"""
    
    def test_register_simple_tool(self):
        """Should register a tool with name and function"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            processor.register_tool(
                name="add",
                tool_func=simple_add,
                description="Add two numbers"
            )
            
            assert "add" in processor.tools
            assert processor.tools["add"]["func"] == simple_add
            assert processor.tools["add"]["description"] == "Add two numbers"
    
    def test_register_multiple_tools(self):
        """Should register multiple tools"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            processor.register_tool("add", simple_add, "Add numbers")
            processor.register_tool("echo", echo_tool, "Echo message")
            
            assert len(processor.tools) == 2
            assert "add" in processor.tools
            assert "echo" in processor.tools
    
    def test_list_registered_tools(self):
        """Should list all registered tools"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            processor.register_tool("add", simple_add, "Add numbers")
            processor.register_tool("echo", echo_tool, "Echo message")
            
            tools = processor.list_tools()
            
            assert len(tools) == 2
            assert "add" in tools
            assert "echo" in tools


class TestToolCallTo16D:
    """Test converting tool calls to 16D coordinates"""
    
    def test_to_16d_returns_16d_array(self):
        """Should return exactly 16D numpy array"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            tool_data = {"name": "add", "args": {"a": 1, "b": 2}}
            coords = processor.to_16d(tool_data)
            
            assert isinstance(coords, np.ndarray)
            assert coords.shape == (16,)
    
    def test_to_16d_is_deterministic(self):
        """Should return same coordinates for same tool call"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            tool_data = {"name": "add", "args": {"a": 5, "b": 10}}
            coords1 = processor.to_16d(tool_data)
            coords2 = processor.to_16d(tool_data)
            
            np.testing.assert_array_equal(coords1, coords2)
    
    def test_to_16d_different_tools_different_coords(self):
        """Should return different coordinates for different tools"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            tool_data1 = {"name": "add", "args": {"a": 1, "b": 2}}
            tool_data2 = {"name": "echo", "args": {"message": "hello"}}
            
            coords1 = processor.to_16d(tool_data1)
            coords2 = processor.to_16d(tool_data2)
            
            assert not np.allclose(coords1, coords2)
    
    def test_to_16d_different_args_different_coords(self):
        """Should return different coordinates for different arguments"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            tool_data1 = {"name": "add", "args": {"a": 1, "b": 2}}
            tool_data2 = {"name": "add", "args": {"a": 5, "b": 10}}
            
            coords1 = processor.to_16d(tool_data1)
            coords2 = processor.to_16d(tool_data2)
            
            assert not np.allclose(coords1, coords2)


class TestToolExecution:
    """Test executing registered tools"""
    
    def test_process_executes_tool(self):
        """Should execute tool and return result"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            processor.register_tool("add", simple_add, "Add numbers")
            
            result, engram = processor.process("add", {"a": 3, "b": 7})
            
            assert result == 10
            assert isinstance(engram, Engram)
    
    def test_process_returns_tool_engram(self):
        """Should return both result and tool engram"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            processor.register_tool("echo", echo_tool, "Echo message")
            
            result, engram = processor.process("echo", {"message": "hello"})
            
            assert result == "Echo: hello"
            assert isinstance(engram, Engram)
            assert engram.engram_type == "tool"
    
    def test_process_with_no_args(self):
        """Should handle tools with no arguments"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            def no_args_tool():
                return "success"
            
            processor.register_tool("no_args", no_args_tool, "No args tool")
            
            result, engram = processor.process("no_args", {})
            
            assert result == "success"
            assert isinstance(engram, Engram)
    
    def test_process_unknown_tool_raises_error(self):
        """Should raise error for unknown tool"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            with pytest.raises(KeyError):
                processor.process("unknown_tool", {})


class TestToolEngram:
    """Test the tool engram created by process()"""
    
    def test_tool_engram_has_correct_type(self):
        """Should create engram with type 'tool'"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            processor.register_tool("add", simple_add, "Add numbers")
            _, engram = processor.process("add", {"a": 1, "b": 2})
            
            assert engram.engram_type == "tool"
    
    def test_tool_engram_contains_tool_name(self):
        """Should include tool name in engram content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            processor.register_tool("echo", echo_tool, "Echo message")
            _, engram = processor.process("echo", {"message": "test"})
            
            assert "echo" in engram.content
    
    def test_tool_engram_has_16d_coords(self):
        """Should have 16D coordinates matching tool call"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            processor.register_tool("add", simple_add, "Add numbers")
            
            tool_data = {"name": "add", "args": {"a": 5, "b": 3}}
            expected_coords = processor.to_16d(tool_data)
            
            _, engram = processor.process("add", {"a": 5, "b": 3})
            
            np.testing.assert_array_almost_equal(
                engram.coords_16d,
                expected_coords
            )
    
    def test_tool_engram_includes_metadata(self):
        """Should include tool metadata (name, args, result)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            processor.register_tool("add", simple_add, "Add numbers")
            result, engram = processor.process("add", {"a": 3, "b": 7})
            
            assert "tool_name" in engram.metadata
            assert engram.metadata["tool_name"] == "add"
            assert "args" in engram.metadata
            assert engram.metadata["args"] == {"a": 3, "b": 7}
            assert "result" in engram.metadata
            assert engram.metadata["result"] == result


class TestToolProcessorIntegration:
    """Test ToolProcessor integration with holofield"""
    
    def test_tool_engram_can_be_stored(self):
        """Should be able to store tool engram in holofield"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            processor.register_tool("add", simple_add, "Add numbers")
            _, engram = processor.process("add", {"a": 1, "b": 2})
            
            engram_id = holofield.store(engram)
            
            assert engram_id is not None
            assert len(engram_id) > 0
    
    def test_full_cycle_register_execute_store(self):
        """Should complete full cycle: register → execute → store"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            # 1. Register tool
            processor.register_tool("echo", echo_tool, "Echo message")
            
            # 2. Execute tool
            result, engram = processor.process("echo", {"message": "bagels!"})
            
            # 3. Store engram
            engram_id = holofield.store(engram)
            
            # 4. Verify we can retrieve it
            retrieved = holofield.retrieve_by_id(engram_id)
            
            assert retrieved is not None
            assert retrieved.engram_type == "tool"
            assert "echo" in retrieved.content
            assert retrieved.metadata["result"] == "Echo: bagels!"
    
    def test_multiple_tool_calls_create_separate_engrams(self):
        """Should create separate engram for each tool call"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            processor.register_tool("add", simple_add, "Add numbers")
            
            # Execute same tool multiple times
            _, engram1 = processor.process("add", {"a": 1, "b": 2})
            _, engram2 = processor.process("add", {"a": 5, "b": 10})
            _, engram3 = processor.process("add", {"a": 1, "b": 2})  # Same as first
            
            # Store all engrams
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


class TestToolProcessorErrorHandling:
    """Test error handling in tool execution"""
    
    def test_tool_execution_error_captured(self):
        """Should capture and handle tool execution errors"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            processor.register_tool("failing", failing_tool, "Always fails")
            
            with pytest.raises(ValueError):
                processor.process("failing", {})
    
    def test_wrong_args_raises_error(self):
        """Should raise error when wrong arguments provided"""
        with tempfile.TemporaryDirectory() as tmpdir:
            holofield = HolofieldManager(db_path=str(Path(tmpdir) / "test.db"))
            processor = ToolProcessor(holofield_manager=holofield)
            
            processor.register_tool("add", simple_add, "Add numbers")
            
            with pytest.raises(TypeError):
                processor.process("add", {"wrong": "args"})
