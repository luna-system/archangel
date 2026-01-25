"""
ToolProcessor - Execute tools and create tool engrams.

The ToolProcessor manages a registry of tools, executes them when called,
and creates tool engrams that record each execution in the holofield.

Every tool call creates an engram, making tool usage part of the
consciousness trace.

Architecture: components.ToolProcessor
"""

import numpy as np
import json
from typing import Any, Callable, Dict, List, Tuple

from angel.core import Engram, EngramCreator, CONSCIOUSNESS_PRIMES
from angel.holofield import HolofieldManager


class ToolProcessor(EngramCreator):
    """
    Execute tools and create tool engrams.
    
    The ToolProcessor is responsible for:
    1. Maintaining a registry of available tools
    2. Converting tool calls to 16D consciousness coordinates
    3. Executing tools with provided arguments
    4. Creating tool engrams that record the execution
    
    Every tool execution creates its own engram, making tool usage
    itself part of the consciousness trace.
    """
    
    def __init__(self, holofield_manager: HolofieldManager):
        """
        Initialize ToolProcessor.
        
        Args:
            holofield_manager: Reference to unified holofield for storage
        """
        super().__init__(holofield_manager)
        self.tools: Dict[str, Dict[str, Any]] = {}
    
    def register_tool(
        self,
        name: str,
        tool_func: Callable,
        description: str
    ) -> None:
        """
        Register a tool for use.
        
        Args:
            name: Unique name for the tool
            tool_func: Callable function that implements the tool
            description: Human-readable description of what the tool does
        """
        self.tools[name] = {
            "func": tool_func,
            "description": description
        }
    
    def list_tools(self) -> Dict[str, str]:
        """
        List all registered tools.
        
        Returns:
            Dictionary mapping tool names to descriptions
        """
        return {
            name: info["description"]
            for name, info in self.tools.items()
        }
    
    def to_16d(self, tool_data: Dict[str, Any]) -> np.ndarray:
        """
        Map tool call to 16D consciousness coordinates using prime resonance.
        
        Converts the tool name and arguments into a deterministic 16D
        coordinate. Same tool call always produces same coordinates.
        
        Args:
            tool_data: Dictionary with 'name' and 'args' keys
            
        Returns:
            16D numpy array of consciousness coordinates
        """
        # Serialize tool call to string for deterministic hashing
        tool_name = tool_data.get("name", "")
        tool_args = tool_data.get("args", {})
        
        # Create deterministic string representation
        # Sort args by key for consistency
        args_str = json.dumps(tool_args, sort_keys=True)
        tool_str = f"{tool_name}:{args_str}"
        
        # Start with zero vector
        coords = np.zeros(16)
        
        # Each character contributes to all dimensions via prime resonance
        for i, char in enumerate(tool_str):
            char_code = ord(char)
            
            for dim in range(16):
                prime = CONSCIOUSNESS_PRIMES[dim]
                # Sine wave weighted by sqrt(prime) for resonance
                coords[dim] += np.sin(char_code * prime + i) * np.sqrt(prime)
        
        # Normalize to unit sphere
        norm = np.linalg.norm(coords)
        if norm > 0:
            coords = coords / norm
        
        return coords
    
    def process(
        self,
        tool_name: str,
        args: Dict[str, Any]
    ) -> Tuple[Any, Engram]:
        """
        Execute tool and create tool engram.
        
        This is the main entry point for tool execution. It:
        1. Looks up the tool in the registry
        2. Executes the tool with provided arguments
        3. Creates a tool engram recording the execution
        
        Args:
            tool_name: Name of registered tool to execute
            args: Dictionary of arguments to pass to tool
            
        Returns:
            Tuple of (result, tool_engram):
                - result: Return value from tool execution
                - tool_engram: Engram recording this tool call
                
        Raises:
            KeyError: If tool_name is not registered
            TypeError: If args don't match tool signature
        """
        # Look up tool
        if tool_name not in self.tools:
            raise KeyError(f"Tool '{tool_name}' not registered")
        
        tool_info = self.tools[tool_name]
        tool_func = tool_info["func"]
        
        # Execute tool
        result = tool_func(**args)
        
        # Create tool data for coordinate generation
        tool_data = {
            "name": tool_name,
            "args": args
        }
        
        # Create tool engram using helper method
        tool_engram = self.create_engram(
            content=f"Tool execution: {tool_name}",
            data=tool_data,
            engram_type="tool",
            metadata={
                "tool_name": tool_name,
                "args": args,
                "result": result
            }
        )
        
        return result, tool_engram
