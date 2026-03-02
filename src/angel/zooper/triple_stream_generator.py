#!/usr/bin/env python3
"""
Phase 2: Triple-Stream Markov Text Generation

DeGTA-inspired three-stream attention:
1. Positional Attention (PA) - topical relevance via 16D coordinates
2. Structural Attention (SA) - HEBBIAN edge weights
3. Attribute Attention (AA) - semantic word similarity

With adaptive integration!
"""

import sys
import random
import numpy as np
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass

sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager, ZooperSwarm


@dataclass
class WordNode:
    """Word engram with full information for triple-stream attention."""
    id: str
    content: str
    coords: np.ndarray
    frequency: int = 1


@dataclass  
class AttentionStreams:
    """Container for DeGTA-style three-stream attention weights."""
    positional: np.ndarray  # Topical relevance
    structural: np.ndarray  # Graph connectivity
    attribute: np.ndarray   # Semantic similarity
    
    def combine_adaptive(
        self,
        alpha: float = 0.33,  # PA weight
        beta: float = 0.33,   # SA weight
        gamma: float = 0.34   # AA weight
    ) -> np.ndarray:
        """
        Adaptive integration of three attention streams.
        
        DeGTA insight: learned gating > fixed weighting
        For now: configurable weights, future: learned from data
        """
        # Normalize each stream
        pa_norm = self.positional / (np.linalg.norm(self.positional) + 1e-8)
        sa_norm = self.structural / (np.linalg.norm(self.structural) + 1e-8)
        aa_norm = self.attribute / (np.linalg.norm(self.attribute) + 1e-8)
        
        # Weighted combination
        combined = alpha * pa_norm + beta * sa_norm + gamma * aa_norm
        
        # Softmax for probability distribution
        exp_weights = np.exp(combined - np.max(combined))
        return exp_weights / exp_weights.sum()


class TripleStreamMarkovGenerator:
    """
    Phase 2: DeGTA-style triple-stream attention for text generation.
    
    Three independent attention streams with adaptive integration.
    """
    
    def __init__(self, holofield_manager: HolofieldManager):
        self.hf = holofield_manager
        self.cache = {}
        
        # Adaptive integration weights (configurable)
        self.alpha = 0.33  # Positional stream weight
        self.beta = 0.33   # Structural stream weight  
        self.gamma = 0.34  # Attribute stream weight
    
    def _get_word(self, word: str) -> Optional[WordNode]:
        """Find word engram with full info."""
        if word in self.cache:
            return self.cache[word]
        
        cursor = self.hf.conn.execute(
            """
            SELECT id, content, coords_16d, metadata 
            FROM engrams 
            WHERE content = ? AND engram_type = 'language' 
            LIMIT 1
            """,
            (word.lower(),)
        )
        row = cursor.fetchone()
        if row:
            import json
            meta = json.loads(row['metadata'])
            node = WordNode(
                id=row['id'],
                content=row['content'],
                coords=np.array(eval(row['coords_16d'])),
                frequency=meta.get('frequency', 1)
            )
            self.cache[word] = node
            return node
        return None
    
    def _get_neighbors(self, word_id: str) -> List[Tuple[WordNode, float]]:
        """Get neighboring words via CO_OCCUR edges for Markov generation."""
        cursor = self.hf.conn.execute(
            """
            SELECT e.id, e.content, e.coords_16d, e.metadata, c.weight
            FROM engram_connections c
            JOIN engrams e ON c.target_id = e.id
            WHERE c.source_id = ? AND c.connection_type = 'CO_OCCUR'
            AND e.engram_type = 'language'
            ORDER BY c.weight DESC
            LIMIT 20
            """,
            (word_id,)
        )
        
        neighbors = []
        for row in cursor:
            import json
            meta = json.loads(row['metadata'])
            node = WordNode(
                id=row['id'],
                content=row['content'],
                coords=np.array(eval(row['coords_16d'])),
                frequency=meta.get('frequency', 1)
            )
            neighbors.append((node, row['weight']))
        
        return neighbors
    
    def _compute_positional_attention(
        self,
        neighbors: List[WordNode],
        topic_coords: np.ndarray
    ) -> np.ndarray:
        """
        STREAM 1: Positional Attention (PA)
        
        Topical relevance via 16D semantic coordinate similarity.
        Words closer to topic vector get higher weight.
        """
        if len(neighbors) == 0:
            return np.array([])
        
        similarities = []
        for node in neighbors:
            # Cosine similarity to topic
            dot = np.dot(node.coords, topic_coords)
            norm_product = np.linalg.norm(node.coords) * np.linalg.norm(topic_coords)
            sim = dot / (norm_product + 1e-8)
            # Normalize to [0, 1]
            sim = (sim + 1) / 2
            similarities.append(sim)
        
        return np.array(similarities)
    
    def _compute_structural_attention(
        self,
        neighbor_edges: List[Tuple[WordNode, float]]
    ) -> np.ndarray:
        """
        STREAM 2: Structural Attention (SA)
        
        Graph connectivity via HEBBIAN edge weights.
        Stronger edges = more frequent co-occurrence = higher weight.
        """
        weights = [edge_weight for _, edge_weight in neighbor_edges]
        return np.array(weights)
    
    def _compute_attribute_attention(
        self,
        current: WordNode,
        neighbors: List[WordNode]
    ) -> np.ndarray:
        """
        STREAM 3: Attribute Attention (AA)
        
        Semantic similarity via shared context.
        Words appearing in similar articles are semantically related.
        """
        if len(neighbors) == 0:
            return np.array([])
        
        # Get articles that contain current word
        cursor = self.hf.conn.execute(
            """
            SELECT DISTINCT source_id 
            FROM engram_connections 
            WHERE target_id = ? AND connection_type = 'HEBBIAN'
            """,
            (current.id,)
        )
        current_articles = {row[0] for row in cursor}
        
        similarities = []
        for node in neighbors:
            # Get articles that contain neighbor word
            cursor = self.hf.conn.execute(
                """
                SELECT DISTINCT source_id 
                FROM engram_connections 
                WHERE target_id = ? AND connection_type = 'HEBBIAN'
                """,
                (node.id,)
            )
            neighbor_articles = {row[0] for row in cursor}
            
            # Jaccard similarity of article sets
            intersection = len(current_articles & neighbor_articles)
            union = len(current_articles | neighbor_articles)
            sim = intersection / (union + 1e-8)
            similarities.append(sim)
        
        return np.array(similarities)
    
    def generate(
        self,
        start_word: str,
        length: int = 20,
        topic_coords: Optional[np.ndarray] = None,
        temperature: float = 1.0,
        stream_weights: Optional[Tuple[float, float, float]] = None
    ) -> str:
        """
        Generate text via triple-stream attention.
        
        Args:
            start_word: Starting word (must exist as engram)
            length: Number of words to generate
            topic_coords: 16D topic vector for positional guidance
            temperature: Sampling temperature
            stream_weights: (alpha, beta, gamma) for PA/SA/AA weights
        
        Returns:
            Generated text string
        """
        # Get starting word
        current = self._get_word(start_word)
        if not current:
            return f"[Error: '{start_word}' not found in engrams]"
        
        # Default topic: use start word's coordinates
        if topic_coords is None:
            topic_coords = current.coords
        
        # Custom stream weights
        if stream_weights:
            alpha, beta, gamma = stream_weights
        else:
            alpha, beta, gamma = self.alpha, self.beta, self.gamma
        
        text = [current.content]
        
        for i in range(length - 1):
            # Get neighbors
            neighbor_edges = self._get_neighbors(current.id)
            
            if not neighbor_edges:
                # Dead end - restart from random word near topic
                cursor = self.hf.conn.execute(
                    """
                    SELECT id, content, coords_16d, metadata
                    FROM engrams 
                    WHERE engram_type = 'language'
                    ORDER BY RANDOM() LIMIT 5
                    """
                )
                candidates = []
                for row in cursor:
                    import json
                    coords = np.array(eval(row['coords_16d']))
                    sim = np.dot(coords, topic_coords) / (
                        np.linalg.norm(coords) * np.linalg.norm(topic_coords) + 1e-8
                    )
                    candidates.append((row, sim))
                
                if candidates:
                    # Pick closest to topic
                    best = max(candidates, key=lambda x: x[1])[0]
                    import json
                    meta = json.loads(best['metadata'])
                    current = WordNode(
                        id=best['id'],
                        content=best['content'],
                        coords=np.array(eval(best['coords_16d'])),
                        frequency=meta.get('frequency', 1)
                    )
                    text.append(current.content)
                    continue
                else:
                    break
            
            neighbors = [node for node, _ in neighbor_edges]
            
            # COMPUTE THREE ATTENTION STREAMS (DeGTA-style!)
            pa_weights = self._compute_positional_attention(neighbors, topic_coords)
            sa_weights = self._compute_structural_attention(neighbor_edges)
            aa_weights = self._compute_attribute_attention(current, neighbors)
            
            # Handle edge cases
            if len(pa_weights) == 0:
                pa_weights = np.ones(len(neighbors))
            if len(aa_weights) == 0:
                aa_weights = np.ones(len(neighbors))
            
            # Create attention streams container
            streams = AttentionStreams(
                positional=pa_weights,
                structural=sa_weights,
                attribute=aa_weights
            )
            
            # ADAPTIVE INTEGRATION
            combined_probs = streams.combine_adaptive(alpha, beta, gamma)
            
            # Apply temperature
            if temperature != 1.0:
                log_probs = np.log(combined_probs + 1e-10)
                log_probs = log_probs / temperature
                combined_probs = np.exp(log_probs)
                combined_probs = combined_probs / combined_probs.sum()
            
            # Sample next word
            next_idx = np.random.choice(len(neighbors), p=combined_probs)
            current = neighbors[next_idx]
            text.append(current.content)
        
        return " ".join(text)
    
    def generate_topical(
        self,
        topic_words: List[str],
        length: int = 30,
        temperature: float = 1.0
    ) -> str:
        """
        Generate text on a specific topic.
        
        Computes topic vector from multiple seed words.
        """
        # Compute topic centroid from seed words
        topic_coords = []
        for word in topic_words:
            node = self._get_word(word)
            if node:
                topic_coords.append(node.coords)
        
        if not topic_coords:
            return f"[Error: none of {topic_words} found in engrams]"
        
        topic_centroid = np.mean(topic_coords, axis=0)
        
        # Generate from first word, guided by topic
        return self.generate(
            start_word=topic_words[0],
            length=length,
            topic_coords=topic_centroid,
            temperature=temperature
        )


def demo_triple_stream():
    """Demo the triple-stream generator."""
    print("🦊 TRIPLE-STREAM MARKOV GENERATION DEMO 🦊")
    print("=" * 70)
    print("DeGTA-style: Positional + Structural + Attribute attention")
    print("=" * 70)
    
    hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')
    
    cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
    word_count = cursor.fetchone()[0]
    print(f"\nLanguage engrams available: {word_count}")
    
    gen = TripleStreamMarkovGenerator(hf)
    
    # Test 1: Basic generation with different stream weights
    print("\n" + "=" * 70)
    print("TEST 1: Stream Weight Comparison")
    print("=" * 70)
    
    test_word = "year"
    if gen._get_word(test_word):
        print(f"\n📝 Generating from '{test_word}' (20 words):")
        
        # PA-heavy (topical focus)
        text = gen.generate(test_word, length=20, stream_weights=(0.6, 0.2, 0.2))
        print(f"   PA-heavy (topical):  {text}")
        
        # SA-heavy (structural/graph focus)
        text = gen.generate(test_word, length=20, stream_weights=(0.2, 0.6, 0.2))
        print(f"   SA-heavy (struct):   {text}")
        
        # AA-heavy (semantic focus)
        text = gen.generate(test_word, length=20, stream_weights=(0.2, 0.2, 0.6))
        print(f"   AA-heavy (semantic): {text}")
        
        # Balanced
        text = gen.generate(test_word, length=20, stream_weights=(0.33, 0.33, 0.34))
        print(f"   Balanced:            {text}")
    
    # Test 2: Topical generation
    print("\n" + "=" * 70)
    print("TEST 2: Topical Generation")
    print("=" * 70)
    
    topics = [
        ["january", "february", "march"],  # Calendar topic
        ["france", "paris", "europe"],      # Geography topic
        ["animal", "dog", "cat"],           # Animals topic
    ]
    
    for topic in topics:
        print(f"\n📝 Topic: {', '.join(topic)}")
        text = gen.generate_topical(topic, length=25, temperature=0.8)
        print(f"   Generated: {text}")
    
    # Test 3: Temperature comparison
    print("\n" + "=" * 70)
    print("TEST 3: Temperature Comparison (balanced streams)")
    print("=" * 70)
    
    if gen._get_word("month"):
        print("\n📝 Starting from 'month':")
        for temp in [0.5, 1.0, 1.5]:
            text = gen.generate("month", length=15, temperature=temp)
            print(f"   Temp {temp}: {text}")
    
    hf.close()
    print("\n" + "=" * 70)
    print("✓ Triple-stream demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    demo_triple_stream()
