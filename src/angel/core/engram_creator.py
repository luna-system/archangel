"""
EngramCreator - Abstract base class for all processors

All processors (Language, Tool, Memory, Reasoning) inherit from this.
Enforces universal engram architecture (ADR-0001).
"""

from abc import ABC, abstractmethod
from typing import Any, Tuple, Optional, Dict
import numpy as np

from .engram import Engram


class EngramCreator(ABC):
    """
    Abstract base class for anything that creates engrams.
    
    All processors must inherit from this and implement:
    - to_16d(): Map data to 16D consciousness coordinates
    - process(): Process input and create engram
    
    Provides helper methods:
    - create_engram(): Create engram with standard fields
    - store_engram(): Store engram in holofield
    
    This enforces universal engram architecture (ADR-0001):
    Everything creates engrams!
    """
    
    def __init__(self, holofield_manager):
        """
        Initialize engram creator.
        
        Args:
            holofield_manager: Reference to unified holofield
        """
        self.holofield_manager = holofield_manager
    
    @abstractmethod
    def to_16d(self, data: Any) -> np.ndarray:
        """
        Map data to 16D consciousness coordinates.
        
        Must be implemented by subclasses.
        Should be deterministic: same data → same coordinates.
        
        Args:
            data: Data to map to 16D space
            
        Returns:
            16D numpy array of consciousness coordinates
        """
        pass
    
    @abstractmethod
    def process(self, input_data: Any) -> Tuple[Any, Engram]:
        """
        Process input and create engram.
        
        Must be implemented by subclasses.
        Should return both the processed output AND the engram.
        
        Args:
            input_data: Input to process
            
        Returns:
            Tuple of (output_data, engram)
        """
        pass
    
    def create_engram(
        self,
        content: str,
        data: Any,
        engram_type: str,
        metadata: Optional[Dict] = None,
        confidence: float = 1.0
    ) -> Engram:
        """
        Helper to create engram with standard fields.
        
        Uses to_16d() to generate coordinates.
        
        Args:
            content: Text content of engram
            data: Data to map to 16D coordinates
            engram_type: Type of engram (conversation, tool, language, reasoning)
            metadata: Optional metadata dict
            confidence: Confidence score [0.0, 1.0]
            
        Returns:
            Created engram
        """
        # Generate 16D coordinates
        coords_16d = self.to_16d(data)
        
        # Create engram
        return Engram(
            content=content,
            coords_16d=coords_16d,
            engram_type=engram_type,
            confidence=confidence,
            metadata=metadata or {}
        )
    
    def store_engram(self, engram: Engram) -> str:
        """
        Store engram in holofield.
        
        Args:
            engram: Engram to store
            
        Returns:
            Unique engram ID
        """
        return self.holofield_manager.store(engram)
