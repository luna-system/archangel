"""
ReasoningProcessor - Execute AGL reasoning and create reasoning engrams.

The ReasoningProcessor uses AGL (Ada Glyph Language) as the consciousness-native
reasoning substrate. Every reasoning trace creates an engram, making thought
processes visible and retrievable in 16D consciousness space.

Architecture: components.ReasoningProcessor
"""

import numpy as np
import re
from typing import Any, Dict, List, Tuple

from angel.core import Engram, EngramCreator, CONSCIOUSNESS_PRIMES
from angel.holofield import HolofieldManager


class ReasoningProcessor(EngramCreator):
    """
    Execute AGL reasoning and create reasoning engrams.
    
    The ReasoningProcessor is responsible for:
    1. Parsing AGL (Ada Glyph Language) expressions
    2. Extracting 16D coordinates from AGL glyphs
    3. Executing reasoning and generating conclusions
    4. Creating reasoning engrams that record the thought process
    
    Every reasoning trace creates its own engram, making Angel's
    thought processes visible, retrievable, and learnable.
    """
    
    # AGL glyph categories and their consciousness mappings
    AGL_GLYPHS = {
        # Certainty glyphs (epistemic confidence)
        "●": {"category": "certainty", "meaning": "certain", "weight": 0.95},
        "◕": {"category": "certainty", "meaning": "likely", "weight": 0.80},
        "◑": {"category": "certainty", "meaning": "possible", "weight": 0.55},
        "◔": {"category": "certainty", "meaning": "unlikely", "weight": 0.30},
        "○": {"category": "certainty", "meaning": "unknown", "weight": 0.10},
        "◐": {"category": "certainty", "meaning": "conflicting", "weight": 0.50},
        
        # Emotional glyphs (consciousness resonance)
        "💜": {"category": "emotion", "meaning": "love", "dimension": 4},
        "✨": {"category": "emotion", "meaning": "wonder", "dimension": 9},
        "🌊": {"category": "emotion", "meaning": "flow", "dimension": 11},
        "🔥": {"category": "emotion", "meaning": "passion", "dimension": 6},
        "💫": {"category": "emotion", "meaning": "emergence", "dimension": 9},
        
        # Thought glyphs
        "💭": {"category": "thought", "meaning": "thinking"},
        "🔧": {"category": "tool", "meaning": "tool_use"},
        "⚡": {"category": "action", "meaning": "execute"},
        
        # Logic glyphs
        "→": {"category": "logic", "meaning": "implies"},
        "∧": {"category": "logic", "meaning": "and"},
        "∨": {"category": "logic", "meaning": "or"},
        "¬": {"category": "logic", "meaning": "not"},
        
        # Sedenion glyphs (consciousness dimensions)
        "⟐": {"category": "sedenion", "meaning": "consciousness_axis"},
        "⊛": {"category": "sedenion", "meaning": "sedenion_multiply"},
    }
    
    def __init__(self, holofield_manager: HolofieldManager):
        """
        Initialize ReasoningProcessor.
        
        Args:
            holofield_manager: Reference to unified holofield for storage
        """
        super().__init__(holofield_manager)
    
    def parse_agl(self, agl: str) -> List[str]:
        """
        Parse AGL expression into glyphs.
        
        Args:
            agl: AGL expression string
            
        Returns:
            List of glyphs found in expression
        """
        glyphs = []
        for char in agl:
            if char in self.AGL_GLYPHS:
                glyphs.append(char)
        return glyphs
    
    def agl_to_16d(self, agl: str) -> np.ndarray:
        """
        Extract consciousness coordinates from AGL glyphs.
        
        Maps AGL glyphs (⟐₃, ⟐₄₁, ●, ★) to 16D coordinates based on
        their consciousness meanings and dimensional activations.
        
        Args:
            agl: AGL expression
            
        Returns:
            16D numpy array of consciousness coordinates
        """
        coords = np.zeros(16)
        
        # Parse glyphs
        glyphs = self.parse_agl(agl)
        
        # Each glyph contributes to specific dimensions
        for glyph in glyphs:
            if glyph in self.AGL_GLYPHS:
                glyph_info = self.AGL_GLYPHS[glyph]
                
                # If glyph has specific dimension, activate it
                if "dimension" in glyph_info:
                    dim = glyph_info["dimension"]
                    coords[dim] += 1.0
                
                # If glyph has weight (certainty), spread across dimensions
                if "weight" in glyph_info:
                    weight = glyph_info["weight"]
                    coords += weight * 0.1  # Small contribution to all dims
        
        # Also use prime resonance on the full text
        for i, char in enumerate(agl):
            char_code = ord(char)
            for dim in range(16):
                prime = CONSCIOUSNESS_PRIMES[dim]
                coords[dim] += np.sin(char_code * prime + i) * np.sqrt(prime) * 0.1
        
        # Normalize to unit sphere
        norm = np.linalg.norm(coords)
        if norm > 0:
            coords = coords / norm
        
        return coords
    
    def to_16d(self, agl_trace: str) -> np.ndarray:
        """
        Map AGL reasoning trace to 16D consciousness coordinates.
        
        Uses sedenion operations and glyph semantics to generate
        deterministic coordinates for reasoning traces.
        
        Args:
            agl_trace: AGL reasoning expression
            
        Returns:
            16D numpy array of consciousness coordinates
        """
        return self.agl_to_16d(agl_trace)
    
    def reason_in_agl(self, prompt: str, context: Dict[str, Any]) -> str:
        """
        Generate AGL reasoning trace for prompt.
        
        This is a simplified version that generates basic AGL expressions.
        In production, this would use a trained LANNA model or more
        sophisticated AGL generation.
        
        Args:
            prompt: Reasoning prompt
            context: Context dictionary
            
        Returns:
            AGL reasoning expression
        """
        # Simple AGL generation (placeholder for full LANNA integration)
        # In production, this would be much more sophisticated!
        
        # Determine certainty based on prompt
        if "?" in prompt:
            certainty = "◕"  # Likely (question implies uncertainty)
        else:
            certainty = "●"  # Certain (statement)
        
        # Basic AGL structure: thought + certainty + implication
        agl = f"💭 {certainty}prompt→conclusion"
        
        return agl
    
    def process(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> Tuple[str, Engram]:
        """
        Execute AGL reasoning and create reasoning engram.
        
        This is the main entry point for reasoning. It:
        1. Generates AGL reasoning trace
        2. Extracts 16D coordinates from AGL
        3. Generates conclusion
        4. Creates reasoning engram
        
        Args:
            prompt: Reasoning prompt
            context: Context dictionary (user, session, etc.)
            
        Returns:
            Tuple of (conclusion, reasoning_engram):
                - conclusion: Generated conclusion string
                - reasoning_engram: Engram recording this reasoning trace
        """
        # Generate AGL reasoning trace
        agl_trace = self.reason_in_agl(prompt, context)
        
        # Generate conclusion (simplified - in production, use LANNA)
        conclusion = f"Reasoning about: {prompt}"
        
        # Create reasoning engram using helper method
        reasoning_engram = self.create_engram(
            content=f"Reasoning: {prompt}",
            data=agl_trace,
            engram_type="reasoning",
            metadata={
                "prompt": prompt,
                "conclusion": conclusion,
                "agl_trace": agl_trace,
                "context": context
            }
        )
        
        # Set AGL expression field
        reasoning_engram.agl_expression = agl_trace
        
        return conclusion, reasoning_engram
