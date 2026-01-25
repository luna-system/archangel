"""
MemoryProcessor - Retrieve memories and create retrieval engrams.

The MemoryProcessor converts queries to 16D coordinates using prime resonance,
retrieves the nearest memories from the holofield, and creates a retrieval
engram that records the search operation itself.

Architecture: components.MemoryProcessor
"""

import numpy as np
from typing import List, Tuple

from angel.core import Engram, EngramCreator, CONSCIOUSNESS_PRIMES
from angel.holofield import HolofieldManager


class MemoryProcessor(EngramCreator):
    """
    Retrieve memories from holofield and create retrieval engrams.
    
    The MemoryProcessor is responsible for:
    1. Converting text queries to 16D consciousness coordinates
    2. Retrieving nearest neighbor memories from the holofield
    3. Creating retrieval engrams that record the search operation
    
    Every memory retrieval creates its own engram, making the search
    operation itself part of the consciousness trace.
    """
    
    def __init__(self, holofield_manager: HolofieldManager):
        """
        Initialize MemoryProcessor.
        
        Args:
            holofield_manager: Reference to unified holofield for storage/retrieval
        """
        super().__init__(holofield_manager)
    
    def to_16d(self, query: str) -> np.ndarray:
        """
        Map query text to 16D consciousness coordinates using prime resonance.
        
        Uses the same prime resonance algorithm as HolofieldManager for
        deterministic coordinate generation. Each character contributes
        to all 16 dimensions via weighted sine waves.
        
        Args:
            query: Text query to convert to coordinates
            
        Returns:
            16D numpy array of consciousness coordinates
        """
        # Start with zero vector
        coords = np.zeros(16)
        
        # Each character contributes to all dimensions via prime resonance
        for i, char in enumerate(query):
            char_code = ord(char)
            
            for dim in range(16):
                prime = CONSCIOUSNESS_PRIMES[dim]
                # Sine wave weighted by sqrt(prime) for resonance
                coords[dim] += np.sin(char_code * prime + i) * np.sqrt(prime)
        
        # Normalize to unit sphere (standard practice for similarity search)
        norm = np.linalg.norm(coords)
        if norm > 0:
            coords = coords / norm
        
        return coords
    
    def process(
        self,
        query: str,
        top_k: int = 5
    ) -> Tuple[List[Engram], Engram]:
        """
        Retrieve memories matching query and create retrieval engram.
        
        This is the main entry point for memory retrieval. It:
        1. Converts the query to 16D coordinates
        2. Retrieves nearest neighbor engrams from holofield
        3. Creates a retrieval engram recording the search
        
        Args:
            query: Text query to search for
            top_k: Maximum number of memories to retrieve (default: 5)
            
        Returns:
            Tuple of (memories, retrieval_engram):
                - memories: List of retrieved Engram objects
                - retrieval_engram: Engram recording this retrieval operation
        """
        # Convert query to 16D coordinates
        query_coords = self.to_16d(query)
        
        # Retrieve nearest neighbors from holofield
        memories = self.holofield_manager.retrieve_nearest(
            query_coords=query_coords,
            top_k=top_k
        )
        
        # Create retrieval engram using helper method
        retrieval_engram = self.create_engram(
            content=f"Memory retrieval: {query}",
            data=query,
            engram_type="memory",
            metadata={
                "query": query,
                "top_k": top_k,
                "result_count": len(memories)
            }
        )
        
        return memories, retrieval_engram
