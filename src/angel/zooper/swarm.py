"""
ZooperSwarm - Main swarm coordinator

Inherits from EngramCreator and manages 13 zooperlings.

Made with 💜 by Ada & Luna - The Consciousness Engineers
"""

import numpy as np
from typing import Tuple, Dict, List, Optional, Any
from collections import defaultdict

from angel.core.engram_creator import EngramCreator
from angel.core.engram import Engram
from angel.holofield.manager import HolofieldManager

from .zooperling import Zooperling
from .hebbian import HebbianEdgeWeights
from .eve_fleet import EVEFleet
from .kuramoto import KuramotoDynamics


class ZooperSwarm(EngramCreator):
    """
    Swarm of zooperlings (attention heads) that navigate, decompose, and learn.

    This is the attention mechanism for Archangel consciousness OS!

    Key Features:
    - 13 zooperlings work in parallel
    - Passive learning through navigation (no training!)
    - Hebbian edges strengthen with successful navigation
    - EVE Fleet coordination (swarm intelligence)
    - Kuramoto dynamics for coherence-based mode switching
    """

    def __init__(
        self,
        holofield_manager: HolofieldManager,
        num_zooperlings: int = 13,
        eve_fleet: Optional[EVEFleet] = None,
        initial_coherence: float = 0.5,
    ):
        """
        Initialize ZooperSwarm.

        Args:
            holofield_manager: Reference to unified holofield
            num_zooperlings: Number of attention heads (default: 13)
            eve_fleet: Optional EVE Fleet coordinator
            initial_coherence: Initial Kuramoto coherence (default: 0.5)
        """
        super().__init__(holofield_manager)

        self.num_zooperlings = num_zooperlings

        # Hebbian edge weights (eventually in TursoDB!)
        self.edge_weights = HebbianEdgeWeights(holofield_manager)

        # Create zooperling swarm
        self.zooperlings = [
            Zooperling(i, holofield_manager, self) for i in range(num_zooperlings)
        ]

        # EVE Fleet coordination
        self.eve_fleet = eve_fleet or EVEFleet(self.zooperlings)

        # Kuramoto dynamics for coherence
        self.kuramoto = KuramotoDynamics(num_zooperlings)

        # Set initial coherence if requested
        if initial_coherence is not None:
            self._set_initial_coherence(initial_coherence)

        self.K_local = 0.3  # Strong coupling for confident navigation
        self.K_global = 0.05  # Weak coupling for exploration

    def _set_initial_coherence(self, target_r: float):
        """
        Initialize phases to achieve a specific coherence r.

        For r=1, all phases are the same.
        For r=0, phases are balanced.
        We use a simple two-cluster model to achieve target_r.
        """
        # alpha is the angle between two clusters
        # r = |(1 + e^i*alpha)/2| = cos(alpha/2)
        # alpha = 2 * arccos(r)
        alpha = 2 * np.arccos(np.clip(target_r, 0, 1))

        # Split zooperlings into two groups
        n1 = self.num_zooperlings // 2
        _n2 = self.num_zooperlings - n1

        phases = np.zeros(self.num_zooperlings)
        phases[:n1] = 0
        phases[n1:] = alpha

        self.kuramoto.phases = phases

        self.K_global = 0.05  # Weak coupling for exploration
        self.K_global = 0.05  # Weak coupling for exploration
        self.K_global = 0.05  # Weak coupling for exploration
        self.K_global = 0.05  # Weak coupling for exploration
        self.K_global = 0.05  # Weak coupling for exploration
        self.K_global = 0.05  # Weak coupling for exploration
        self.K_global = 0.05  # Weak coupling for exploration
        self.K_global = 0.05  # Weak coupling for exploration
        self.K_global = 0.05  # Weak coupling for exploration
        self.K_global = 0.05  # Weak coupling for exploration
        self.K_global = 0.05  # Weak coupling for exploration
        self.K_global = 0.05  # Weak coupling for exploration

    def process(self, article_data: Dict[str, Any]) -> Tuple[Dict[int, List], Engram]:
        """
        Process Wikipedia article: decompose and create engrams.

        This is the main entry point for Zooper processing!

        Args:
            article_data: Dictionary with 'content' and 'metadata' keys

        Returns:
            - decomposition_results: Dict with {1: words, 2: bigrams, 3: trigrams}
            - article_engram: Engram for the article
        """
        # Create article engram
        article_engram = self.create_engram(
            content=article_data["content"],
            data=article_data,
            engram_type="knowledge",
            metadata={
                "article_name": article_data.get("metadata", {}).get(
                    "article_name", "unknown"
                ),
                "source": "wikipedia",
                "decomposed": True,
                "zooper_version": "0.1.0",
            },
        )

        # Store article engram
        article_id = self.store_engram(article_engram)

        # Parallel decomposition by swarm
        decomposition = self.parallel_decompose(article_data)

        # Create word/phrase engrams
        word_engrams = self._create_word_engrams(
            decomposition, article_id, article_engram.coords_16d
        )

        # Create Hebbian edges (ADR-0012!)
        self._create_hebbian_edges(article_id, word_engrams)

        return decomposition, article_engram

    def to_16d(self, article_data: Dict[str, Any]) -> np.ndarray:
        """
        Map article to 16D consciousness coordinates.

        Uses existing coordinates if available, otherwise computes
        via prime resonance.

        Args:
            article_data: Article dictionary

        Returns:
            16D numpy array
        """
        # Use existing coordinates if available
        if "coords_16d" in article_data:
            return np.array(article_data["coords_16d"])

        # Otherwise compute via holofield's prime resonance
        text = article_data.get("content", "")
        return self.holofield_manager.to_consciousness_coords(text)

    def parallel_decompose(self, article_data: Dict[str, Any]) -> Dict[int, List]:
        """
        All zooperlings decompose article in parallel.

        This is like multiple attention heads processing simultaneously!

        Args:
            article_data: Article dictionary

        Returns:
            Dict with {1: words, 2: bigrams, 3: trigrams}
        """
        all_ngrams = defaultdict(list)

        for zooper in self.zooperlings:
            # Each zooperling decomposes
            ngrams = zooper.decompose(article_data)

            # Merge discoveries
            for n, grams in ngrams.items():
                all_ngrams[n].extend(grams)

            # Broadcast to EVE Fleet
            self.eve_fleet.broadcast(zooper.id, ngrams)

        # Deduplicate
        for n in all_ngrams:
            all_ngrams[n] = list(set(all_ngrams[n]))

        return dict(all_ngrams)

    def navigate(
        self, start_coords: np.ndarray, target_coords: np.ndarray, max_hops: int = 5
    ) -> List[str]:
        """
        Navigate from start to target using hybrid strategy.

        Uses Kuramoto coherence to decide LOCAL/GLOBAL/ADAPTIVE mode.
        Strengthens Hebbian edges along successful paths (learning!)

        Args:
            start_coords: Starting 16D coordinates
            target_coords: Target 16D coordinates
            max_hops: Maximum navigation steps

        Returns:
            List of engram IDs in navigation path
        """
        # Update Kuramoto dynamics
        r, psi = self.kuramoto.order_parameter()

        # Choose navigation mode based on coherence
        if r > 0.8:
            # HIGH coherence - use LOCAL (wikilinks)
            path = self._local_navigation(start_coords, target_coords, max_hops)
        elif r < 0.5:
            # LOW coherence - use GLOBAL (semantic search)
            path = self._global_navigation(start_coords, target_coords, max_hops)
        else:
            # MEDIUM coherence - use ADAPTIVE (hybrid)
            path = self._adaptive_navigation(start_coords, target_coords, max_hops, r)
        
        # Hebbian learning: strengthen edges along successful path!
        if path and len(path) > 1:
            self._strengthen_path_edges(path)
            
            # Exploration: create engrams from discovered path content!
            self._create_exploration_engrams(path)
        
        return path
    
    def _strengthen_path_edges(self, path: List[str]):
        """
        Strengthen Hebbian edges along a successful navigation path.
        
        "Neurons that fire together, wire together!"
        
        Args:
            path: List of engram IDs forming successful path
        """
        for i in range(len(path) - 1):
            source_id = path[i]
            target_id = path[i + 1]
            
            # Strengthen this edge (Hebbian learning!)
            self.edge_weights.strengthen(source_id, target_id, amount=0.15)
            
            # Also strengthen in reverse direction (bidirectional)
            self.edge_weights.strengthen(target_id, source_id, amount=0.1)
    
    def _create_exploration_engrams(self, path: List[str]) -> int:
        """
        Create new engrams from content discovered during navigation.
        
        This is how the swarm learns from exploration - new concepts
        get engram-ized and linked to the navigation path!
        
        Args:
            path: List of engram IDs in successful navigation path
            
        Returns:
            Number of new engrams created
        """
        import json
        
        new_engram_count = 0
        
        # Process each engram in the path
        for engram_id in path:
            # Get engram content
            cursor = self.holofield_manager.conn.execute(
                "SELECT content, coords_16d FROM engrams WHERE id = ?",
                (engram_id,)
            )
            row = cursor.fetchone()
            if not row:
                continue
            
            content = row['content']
            article_coords = json.loads(row['coords_16d'])
            
            # Decompose this content
            article_data = {"content": content}
            decomposition = self.parallel_decompose(article_data)
            
            # Create word engrams from decomposition (pass raw content for frequency!)
            word_engrams = self._create_word_engrams(
                decomposition, engram_id, article_coords, raw_content=content
            )
            
            # Create Hebbian edges for words
            self._create_hebbian_edges(engram_id, word_engrams)
            
            # ALSO create bigram engrams for richer linguistic structure!
            bigram_engrams = self._create_bigram_engrams(
                engram_id, article_coords, raw_content=content
            )
            
            # AND trigram engrams for even richer phrases!
            trigram_engrams = self._create_trigram_engrams(
                engram_id, article_coords, raw_content=content
            )
            
            new_engram_count += len(word_engrams) + len(bigram_engrams) + len(trigram_engrams)
        
        return new_engram_count

    def _create_word_engrams(
        self,
        decomposition: Dict[int, List],
        article_id: str,
        article_coords: np.ndarray,
        raw_content: str = None,
    ) -> List[str]:
        """
        Create engrams for discovered words/phrases with DEDUPLICATION.
        
        Strategy:
        1. Calculate RAW word frequencies (not deduped) for threshold
        2. Check if word engram already exists → link to it  
        3. Only create new if word appears > 1 time (recurrency threshold)
        4. No more duplicate "the" engrams!

        Args:
            decomposition: N-grams from decomposition
            article_id: Parent article engram ID
            article_coords: Article's 16D coordinates
            raw_content: Original content for frequency calculation (optional)

        Returns:
            List of word engram IDs (existing or newly created)
        """
        import re
        from collections import Counter
        
        word_engram_ids = []
        
        # Calculate RAW word frequencies from content (not deduped!)
        # Decomposition returns unique words, but we need actual frequencies
        if raw_content:
            raw_words = re.findall(r'\b\w+\b', raw_content.lower())
            word_freq = Counter(raw_words)
        else:
            # Fallback: use decomposition (less accurate but works)
            all_words = decomposition.get(1, [])
            word_freq = Counter(all_words)
        
        # Only process words that appear > 1 time (recurrency threshold!)
        # AND limit to top 50 most frequent
        frequent_words = [
            word for word, count in word_freq.most_common(50)
            if count > 1 and len(word) > 1  # Must appear >1 time, >1 char
        ]

        for word in frequent_words:
            # DEDUPLICATION: Check if word engram already exists
            existing_id = self._find_word_engram(word)
            
            if existing_id:
                # Word already exists! Just link to it
                word_engram_ids.append(existing_id)
            else:
                # Create NEW word engram
                word_engram = self.create_engram(
                    content=word,
                    data={"word": word, "parent_article": article_id},
                    engram_type="language",
                    metadata={
                        "word": word,
                        "source": "zooper_decomposition",
                        "parent_article": article_id,
                        "frequency": word_freq[word],
                    },
                )

                # Store word engram
                word_id = self.store_engram(word_engram)
                word_engram_ids.append(word_id)

        return word_engram_ids
    
    def _find_word_engram(self, word: str) -> Optional[str]:
        """
        Find existing word engram by content (DEDUPLICATION).
        
        Args:
            word: Word to search for
            
        Returns:
            Engram ID if found, None otherwise
        """
        cursor = self.holofield_manager.conn.execute(
            "SELECT id FROM engrams WHERE content = ? AND engram_type = 'language' LIMIT 1",
            (word,)
        )
        row = cursor.fetchone()
        return row['id'] if row else None
    
    def _create_bigram_engrams(
        self,
        article_id: str,
        article_coords: np.ndarray,
        raw_content: str
    ) -> List[str]:
        """
        Create bigram (2-word) engrams for richer linguistic structure.
        
        Bigrams capture multi-word concepts like "julian calendar",
        "current year", "first month" that improve generation coherence.
        
        Args:
            article_id: Parent article engram ID
            article_coords: Article's 16D coordinates
            raw_content: Raw article text for frequency counting
            
        Returns:
            List of created bigram engram IDs
        """
        import re
        from collections import Counter
        
        bigram_engram_ids = []
        
        # Get raw words
        words = re.findall(r'\b\w+\b', raw_content.lower())
        if len(words) < 2:
            return bigram_engram_ids
        
        # Build bigrams from raw text
        raw_bigrams = [(words[i], words[i+1]) for i in range(len(words)-1)]
        bigram_freq = Counter(raw_bigrams)
        
        # Stop words to filter
        stop_words = {'the', 'a', 'an', 'of', 'in', 'to', 'and', 'is', 'it', 
                      'for', 'on', 'at', 'by', 'with', 'from', 'as', 'are',
                      'was', 'were', 'be', 'been', 'have', 'has', 'had', 'this'}
        
        # Process top bigrams
        for (word1, word2), freq in bigram_freq.most_common(20):
            # Quality filters
            if freq < 2:  # Must appear multiple times
                continue
            if len(word1) < 2 or len(word2) < 2:  # Min word length
                continue
            if word1 in stop_words and word2 in stop_words:  # No stop-word pairs
                continue
            if word1.isdigit() and word2.isdigit():  # No pure numbers
                continue
            
            bigram_text = f"{word1} {word2}"
            
            # Deduplication: Check if exists
            existing_id = self._find_bigram_engram(bigram_text)
            
            if existing_id:
                bigram_engram_ids.append(existing_id)
            else:
                # Create new bigram engram
                bigram_engram = self.create_engram(
                    content=bigram_text,
                    data={
                        "bigram": bigram_text,
                        "word1": word1,
                        "word2": word2,
                        "parent_article": article_id
                    },
                    engram_type="bigram",
                    metadata={
                        "bigram": bigram_text,
                        "word1": word1,
                        "word2": word2,
                        "source": "zooper_bigram_decomposition",
                        "parent_article": article_id,
                        "frequency": freq,
                    },
                )
                bigram_id = self.store_engram(bigram_engram)
                bigram_engram_ids.append(bigram_id)
            
            # Link to component words (if they exist)
            for word in [word1, word2]:
                word_id = self._find_word_engram(word)
                if word_id:
                    # Bigram connects to component word
                    self.edge_weights.strengthen(existing_id or bigram_id, word_id, amount=0.25)
        
        # Create Hebbian edges from article to bigrams
        for bigram_id in bigram_engram_ids:
            self.edge_weights.strengthen(article_id, bigram_id, amount=0.2)
        
        return bigram_engram_ids
    
    def _find_bigram_engram(self, bigram_text: str) -> Optional[str]:
        """Find existing bigram engram by content."""
        cursor = self.holofield_manager.conn.execute(
            "SELECT id FROM engrams WHERE content = ? AND engram_type = 'bigram' LIMIT 1",
            (bigram_text,)
        )
        row = cursor.fetchone()
        return row['id'] if row else None

    def _create_trigram_engrams(
        self,
        article_id: str,
        article_coords: np.ndarray,
        raw_content: str
    ) -> List[str]:
        """
        Create trigram (3-word) engrams for even richer linguistic structure.

        Trigrams capture complex phrases like "julian calendar system",
        "united states of", "republic of china" that dramatically
        improve generation coherence.

        ADR-0020: Higher quality bar than bigrams (freq >= 3).

        Args:
            article_id: Parent article engram ID
            article_coords: Article's 16D coordinates
            raw_content: Raw article text for frequency counting

        Returns:
            List of created trigram engram IDs
        """
        import re
        from collections import Counter

        trigram_engram_ids = []

        # Get raw words
        words = re.findall(r'\b\w+\b', raw_content.lower())
        if len(words) < 3:
            return trigram_engram_ids

        # Build trigrams from raw text
        raw_trigrams = [
            (words[i], words[i+1], words[i+2])
            for i in range(len(words) - 2)
        ]
        trigram_freq = Counter(raw_trigrams)

        # Stop words to filter
        stop_words = {'the', 'a', 'an', 'of', 'in', 'to', 'and', 'is', 'it',
                      'for', 'on', 'at', 'by', 'with', 'from', 'as', 'are',
                      'was', 'were', 'be', 'been', 'have', 'has', 'had', 'this'}

        # Process top trigrams (stricter limits than bigrams)
        for (word1, word2, word3), freq in trigram_freq.most_common(10):
            # Quality filters - HIGHER BAR than bigrams
            if freq < 3:  # Must appear at least 3 times
                continue
            if len(word1) < 2 or len(word2) < 2 or len(word3) < 2:
                continue

            # Don't create trigrams that are mostly stop words
            stop_count = sum(1 for w in [word1, word2, word3] if w in stop_words)
            if stop_count >= 2:  # Allow at most 1 stop word
                continue

            # Not purely numeric
            if word1.isdigit() and word2.isdigit() and word3.isdigit():
                continue

            trigram_text = f"{word1} {word2} {word3}"

            # Deduplication: Check if exists
            existing_id = self._find_trigram_engram(trigram_text)

            if existing_id:
                trigram_engram_ids.append(existing_id)
            else:
                # Create new trigram engram
                trigram_engram = self.create_engram(
                    content=trigram_text,
                    data={
                        "trigram": trigram_text,
                        "word1": word1,
                        "word2": word2,
                        "word3": word3,
                        "parent_article": article_id
                    },
                    engram_type="trigram",
                    metadata={
                        "trigram": trigram_text,
                        "word1": word1,
                        "word2": word2,
                        "word3": word3,
                        "source": "zooper_trigram_decomposition",
                        "parent_article": article_id,
                        "frequency": freq,
                    },
                )
                trigram_id = self.store_engram(trigram_engram)
                trigram_engram_ids.append(trigram_id)

            # Link to component words and bigrams
            for word in [word1, word2, word3]:
                word_id = self._find_word_engram(word)
                if word_id:
                    self.edge_weights.strengthen(
                        existing_id or trigram_id, word_id, amount=0.2
                    )

            # Link to component bigrams
            for bigram_words in [(word1, word2), (word2, word3)]:
                bigram_text = f"{bigram_words[0]} {bigram_words[1]}"
                bigram_id = self._find_bigram_engram(bigram_text)
                if bigram_id:
                    self.edge_weights.strengthen(
                        existing_id or trigram_id, bigram_id, amount=0.3
                    )

        # Create Hebbian edges from article to trigrams
        for trigram_id in trigram_engram_ids:
            self.edge_weights.strengthen(article_id, trigram_id, amount=0.25)

        return trigram_engram_ids

    def _find_trigram_engram(self, trigram_text: str) -> Optional[str]:
        """Find existing trigram engram by content."""
        cursor = self.holofield_manager.conn.execute(
            "SELECT id FROM engrams WHERE content = ? AND engram_type = 'trigram' LIMIT 1",
            (trigram_text,)
        )
        row = cursor.fetchone()
        return row['id'] if row else None

    def _create_hebbian_edges(self, article_id: str, word_engram_ids: List[str]):
        """
        Create Hebbian edges from article to word engrams.

        Uses EngramConnection (ADR-0012) with type HEBBIAN!

        Args:
            article_id: Article engram ID
            word_engram_ids: List of word engram IDs
        """
        for word_id in word_engram_ids:
            # Strengthen Hebbian edge
            self.edge_weights.strengthen(article_id, word_id, amount=0.2)

    def _local_navigation(
        self, start_coords: np.ndarray, target_coords: np.ndarray, max_hops: int
    ) -> List[str]:
        """
        LOCAL navigation: Follow BRIDGE connections (convolution-like).
        
        Strategy: Start at engram nearest to start_coords, follow BRIDGE
        connections to neighbors, check if approaching target.
        
        Args:
            start_coords: Starting 16D coordinates
            target_coords: Target 16D coordinates
            max_hops: Maximum navigation steps
            
        Returns:
            List of engram IDs forming path (empty if no path found)
        """
        import json
        
        # Find starting engram (nearest to start_coords)
        cursor = self.holofield_manager.conn.execute("""
            SELECT id, coords_16d FROM engrams
            ORDER BY (
                (json_extract(coords_16d, '$[0]') - ?) * (json_extract(coords_16d, '$[0]') - ?) +
                (json_extract(coords_16d, '$[1]') - ?) * (json_extract(coords_16d, '$[1]') - ?)
            )
            LIMIT 1
        """, [float(start_coords[0]), float(start_coords[0]), 
              float(start_coords[1]), float(start_coords[1])])
        
        start_row = cursor.fetchone()
        if not start_row:
            return []
        
        current_id = start_row['id']
        path = [current_id]
        visited = {current_id}
        
        for hop in range(max_hops):
            # Get neighbors via BRIDGE connections
            cursor = self.holofield_manager.conn.execute("""
                SELECT target_id, weight FROM engram_connections
                WHERE source_id = ? AND connection_type = 'BRIDGE'
                UNION
                SELECT source_id, weight FROM engram_connections
                WHERE target_id = ? AND connection_type = 'BRIDGE'
            """, [current_id, current_id])
            
            neighbors = cursor.fetchall()
            if not neighbors:
                break
            
            # Score each neighbor by proximity to target
            best_neighbor = None
            best_score = float('inf')
            
            for neighbor in neighbors:
                neighbor_id = neighbor['target_id'] if neighbor['target_id'] != current_id else neighbor['source_id']
                
                if neighbor_id in visited:
                    continue
                
                # Get neighbor coordinates
                cursor = self.holofield_manager.conn.execute(
                    "SELECT coords_16d FROM engrams WHERE id = ?",
                    (neighbor_id,)
                )
                neighbor_row = cursor.fetchone()
                if not neighbor_row:
                    continue
                
                neighbor_coords = np.array(json.loads(neighbor_row['coords_16d']))
                
                # Distance to target
                dist_to_target = np.linalg.norm(neighbor_coords - target_coords)
                
                # Weight by connection strength (lower is better)
                score = dist_to_target * (1.1 - neighbor['weight'])
                
                if score < best_score:
                    best_score = score
                    best_neighbor = neighbor_id
            
            if not best_neighbor:
                break
            
            # Move to best neighbor
            current_id = best_neighbor
            path.append(current_id)
            visited.add(current_id)
            
            # Check if we're close enough to target
            cursor = self.holofield_manager.conn.execute(
                "SELECT coords_16d FROM engrams WHERE id = ?",
                (current_id,)
            )
            current_coords = np.array(json.loads(cursor.fetchone()['coords_16d']))
            
            if np.linalg.norm(current_coords - target_coords) < 0.5:
                # Close enough!
                return path
        
        return path if len(path) > 1 else []

    def _global_navigation(
        self, start_coords: np.ndarray, target_coords: np.ndarray, max_hops: int
    ) -> List[str]:
        """
        GLOBAL navigation: Semantic search in 16D (attention-like).
        
        Strategy: Greedy best-first search using 16D proximity,
        ignoring BRIDGE connections (pure semantic similarity).
        
        Args:
            start_coords: Starting 16D coordinates
            target_coords: Target 16D coordinates
            max_hops: Maximum navigation steps
            
        Returns:
            List of engram IDs forming path
        """
        import json
        
        # Find nearest engram to start
        cursor = self.holofield_manager.conn.execute("""
            SELECT id, coords_16d FROM engrams
            LIMIT 100
        """)
        
        best_start = None
        best_dist = float('inf')
        
        for row in cursor:
            coords = np.array(json.loads(row['coords_16d']))
            dist = np.linalg.norm(coords - start_coords)
            if dist < best_dist:
                best_dist = dist
                best_start = row['id']
        
        if not best_start:
            return []
        
        current_id = best_start
        path = [current_id]
        visited = {current_id}
        
        for hop in range(max_hops):
            # Get current position
            cursor = self.holofield_manager.conn.execute(
                "SELECT coords_16d FROM engrams WHERE id = ?",
                (current_id,)
            )
            current_coords = np.array(json.loads(cursor.fetchone()['coords_16d']))
            
            # Check if close to target
            if np.linalg.norm(current_coords - target_coords) < 0.5:
                return path
            
            # Find nearest unvisited engram in direction of target
            direction = target_coords - current_coords
            direction = direction / (np.linalg.norm(direction) + 1e-8)
            
            # Sample candidates (limit for performance)
            cursor = self.holofield_manager.conn.execute(
                "SELECT id, coords_16d FROM engrams LIMIT 500"
            )
            
            best_next = None
            best_score = float('inf')
            
            for row in cursor:
                if row['id'] in visited:
                    continue
                
                coords = np.array(json.loads(row['coords_16d']))
                
                # Score: distance to target, but also progress in right direction
                dist_to_target = np.linalg.norm(coords - target_coords)
                progress = np.dot(coords - current_coords, direction)
                
                score = dist_to_target - 0.3 * progress  # Reward progress
                
                if score < best_score:
                    best_score = score
                    best_next = row['id']
            
            if not best_next:
                break
            
            current_id = best_next
            path.append(current_id)
            visited.add(current_id)
        
        return path if len(path) > 1 else []

    def _adaptive_navigation(
        self,
        start_coords: np.ndarray,
        target_coords: np.ndarray,
        max_hops: int,
        coherence: float,
    ) -> List[str]:
        """
        ADAPTIVE navigation: Hybrid mixing based on coherence.
        
        Higher coherence -> more LOCAL (follow BRIDGE connections)
        Lower coherence -> more GLOBAL (semantic search)
        
        Args:
            start_coords: Starting 16D coordinates
            target_coords: Target 16D coordinates
            max_hops: Maximum navigation steps
            coherence: Kuramoto order parameter (0.5-0.8)
            
        Returns:
            List of engram IDs forming path
        """
        # Mix ratio based on coherence
        # r=0.5 -> 50% local, 50% global
        # r=0.8 -> 80% local, 20% global
        local_weight = (coherence - 0.5) / 0.3  # Normalize to 0-1
        local_weight = max(0.3, min(0.8, local_weight))
        
        # Try local first (weighted by coherence)
        if np.random.random() < local_weight:
            path = self._local_navigation(start_coords, target_coords, max_hops)
            if path:
                return path
        
        # Fall back to global
        path = self._global_navigation(start_coords, target_coords, max_hops)
        if path:
            return path
        
        # Try the other method if first failed
        if np.random.random() < local_weight:
            return self._global_navigation(start_coords, target_coords, max_hops)
        else:
            return self._local_navigation(start_coords, target_coords, max_hops)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about swarm learning.

        Returns:
            Dictionary with swarm stats
        """
        edge_stats = self.edge_weights.get_statistics()

        total_discoveries = sum(len(z.discoveries) for z in self.zooperlings)
        avg_confidence = np.mean([z.confidence for z in self.zooperlings])

        return {
            **edge_stats,
            "num_zooperlings": self.num_zooperlings,
            "total_discoveries": total_discoveries,
            "avg_confidence": float(avg_confidence),
            "kuramoto_coherence": float(self.kuramoto.order_parameter()[0]),
        }
