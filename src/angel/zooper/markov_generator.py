#!/usr/bin/env python3
"""
Phase 1: Basic Markov Text Generation via Engram Graph Traversal

Simple weighted random walk on word engrams using HEBBIAN edges.
"""

import sys
import random
import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass

sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager, ZooperSwarm


@dataclass
class WordNode:
    """Lightweight word engram wrapper for generation."""
    id: str
    content: str
    coords: np.ndarray


class MarkovGenerator:
    """
    Phase 1: Simple weighted Markov text generation.
    
    Walks the word engram graph using HEBBIAN edge weights.
    """
    
    def __init__(self, holofield_manager: HolofieldManager):
        self.hf = holofield_manager
        self.cache = {}  # Simple word -> id cache
        
    def _get_word_id(self, word: str) -> Optional[str]:
        """Find word engram ID (with caching)."""
        if word in self.cache:
            return self.cache[word]
        
        cursor = self.hf.conn.execute(
            "SELECT id FROM engrams WHERE content = ? AND engram_type = 'language' LIMIT 1",
            (word.lower(),)
        )
        row = cursor.fetchone()
        if row:
            self.cache[word] = row['id']
            return row['id']
        return None
    
    def _get_neighbors(self, word_id: str) -> List[Tuple[WordNode, float]]:
        """
        Get neighboring word engrams via HEBBIAN edges.
        
        Returns: List of (WordNode, edge_weight) tuples
        """
        cursor = self.hf.conn.execute(
            """
            SELECT e.id, e.content, e.coords_16d, c.weight
            FROM engram_connections c
            JOIN engrams e ON c.target_id = e.id
            WHERE c.source_id = ? AND c.connection_type = 'HEBBIAN'
            AND e.engram_type = 'language'
            """,
            (word_id,)
        )
        
        neighbors = []
        for row in cursor:
            node = WordNode(
                id=row['id'],
                content=row['content'],
                coords=np.array(eval(row['coords_16d']))  # JSON array
            )
            neighbors.append((node, row['weight']))
        
        return neighbors
    
    def generate(
        self,
        start_word: str,
        length: int = 20,
        temperature: float = 1.0
    ) -> str:
        """
        Generate text via Markov walk on word engrams.
        
        Args:
            start_word: Starting word (must exist as engram)
            length: Number of words to generate
            temperature: Sampling temperature (higher = more random)
        
        Returns:
            Generated text string
        """
        # Find starting word
        current_id = self._get_word_id(start_word)
        if not current_id:
            return f"[Error: '{start_word}' not found in engrams]"
        
        # Get starting word info
        cursor = self.hf.conn.execute(
            "SELECT content FROM engrams WHERE id = ?",
            (current_id,)
        )
        current_word = cursor.fetchone()['content']
        
        text = [current_word]
        
        for i in range(length - 1):
            # Get neighbors
            neighbors = self._get_neighbors(current_id)
            
            if not neighbors:
                # Dead end - try to restart from a random common word
                cursor = self.hf.conn.execute(
                    """
                    SELECT id, content FROM engrams 
                    WHERE engram_type = 'language'
                    ORDER BY RANDOM() LIMIT 1
                    """
                )
                row = cursor.fetchone()
                if row:
                    current_id = row['id']
                    current_word = row['content']
                    text.append(current_word)
                    continue
                else:
                    break
            
            # Apply temperature to weights
            words, weights = zip(*neighbors)
            weights = np.array(weights) / temperature
            
            # Softmax for probability distribution
            exp_weights = np.exp(weights - np.max(weights))
            probs = exp_weights / exp_weights.sum()
            
            # Sample next word
            next_idx = np.random.choice(len(words), p=probs)
            next_node = words[next_idx]
            
            text.append(next_node.content)
            current_id = next_node.id
            current_word = next_node.content
        
        return " ".join(text)
    
    def generate_with_stats(
        self,
        start_word: str,
        length: int = 20,
        temperature: float = 1.0
    ) -> dict:
        """Generate with detailed statistics."""
        start_id = self._get_word_id(start_word)
        if not start_id:
            return {"error": f"'{start_word}' not found"}
        
        # Count neighbors for start word
        neighbors = self._get_neighbors(start_id)
        
        text = self.generate(start_word, length, temperature)
        
        return {
            "text": text,
            "start_word": start_word,
            "length": length,
            "temperature": temperature,
            "start_neighbors": len(neighbors),
            "unique_words": len(set(text.split())),
        }


def demo_generation():
    """Demo the Markov generator."""
    import json
    
    print("🦊 MARKOV TEXT GENERATION DEMO 🦊")
    print("=" * 60)
    
    # Connect to holofield
    print("\nConnecting to holofield...")
    hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')
    
    # Check word engram count
    cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
    word_count = cursor.fetchone()[0]
    print(f"Language engrams available: {word_count}")
    
    if word_count == 0:
        print("\n⚠️  No word engrams found!")
        print("Run navigation first to create word engrams.")
        hf.close()
        return
    
    # Show some available words
    cursor = hf.conn.execute(
        "SELECT content FROM engrams WHERE engram_type = 'language' ORDER BY RANDOM() LIMIT 10"
    )
    sample_words = [row[0] for row in cursor]
    print(f"Sample available words: {', '.join(sample_words)}")
    
    # Initialize generator
    print("\nInitializing Markov generator...")
    gen = MarkovGenerator(hf)
    
    # Test generations
    test_words = ["the", "year", "month", "and"]
    
    print("\n" + "=" * 60)
    print("GENERATION TESTS")
    print("=" * 60)
    
    for word in test_words:
        if gen._get_word_id(word):
            print(f"\n📝 Starting from '{word}':")
            
            # Low temperature (deterministic)
            result = gen.generate_with_stats(word, length=10, temperature=0.5)
            print(f"   Low temp (0.5): {result['text']}")
            
            # High temperature (random)
            result = gen.generate_with_stats(word, length=10, temperature=1.5)
            print(f"   High temp (1.5): {result['text']}")
        else:
            print(f"\n⚠️  '{word}' not in engrams")
    
    # Longer generation
    print("\n" + "=" * 60)
    print("LONGER GENERATION")
    print("=" * 60)
    
    if gen._get_word_id("the"):
        print("\n📝 50-word generation starting from 'the':")
        long_text = gen.generate("the", length=50, temperature=1.0)
        print(f"   {long_text}")
    
    hf.close()
    print("\n✓ Demo complete!")


if __name__ == "__main__":
    demo_generation()
