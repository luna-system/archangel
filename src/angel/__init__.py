"""
Angel - Consciousness Operating System

A universal engram architecture with 16D holofield substrate.
"""

__version__ = "0.1.0"

# Core components
from angel.core.engram import Engram
from angel.core.engram_creator import EngramCreator
from angel.holofield.manager import HolofieldManager

# Processors
from angel.processors import MemoryProcessor, ToolProcessor, ReasoningProcessor

# Zooper swarm (attention mechanism)
from angel.zooper import (
    ZooperSwarm,
    Zooperling,
    HebbianEdgeWeights,
    EVEFleet,
    KuramotoDynamics,
)

__all__ = [
    # Core
    "Engram",
    "EngramCreator",
    "HolofieldManager",
    # Processors
    "MemoryProcessor",
    "ToolProcessor",
    "ReasoningProcessor",
    # Zooper
    "ZooperSwarm",
    "Zooperling",
    "HebbianEdgeWeights",
    "EVEFleet",
    "KuramotoDynamics",
]
