"""
Angel Processors - Concrete implementations of EngramCreator.

Each processor handles a specific type of interaction and creates
corresponding engrams in the unified holofield.
"""

from angel.processors.memory_processor import MemoryProcessor
from angel.processors.tool_processor import ToolProcessor

__all__ = ["MemoryProcessor", "ToolProcessor"]
