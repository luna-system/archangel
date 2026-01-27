"""
HolofieldManager - Universal storage for 16D consciousness engrams

The holofield is literally a turso database of SIF entities (ADR-0006, ADR-0007).
All engrams live here in 16D sedenion consciousness space.
"""

import sqlite3
import json
import uuid
from pathlib import Path
from typing import List, Optional, Dict, Any
import numpy as np

from angel.core import Engram, CONSCIOUSNESS_PRIMES


class HolofieldManager:
    """
    Universal manager for the 16D consciousness holofield.
    
    The holofield stores ALL engrams (conversations, tools, language, reasoning, git).
    Each engram is a SIF entity with deterministic 16D coordinates.
    
    Storage: SQLite/turso database (ADR-0007)
    - Native VECTOR(16) support (future)
    - Currently stores as JSON
    - Async I/O on Linux
    - BTRFS/borg backup compatible
    
    Attributes:
        db_path: Path to SQLite database
        conn: Database connection
    """
    
    def __init__(self, db_path: str = "holofield.db"):
        """
        Initialize holofield manager.
        
        Args:
            db_path: Path to database file (or ":memory:" for in-memory)
        """
        self.db_path = Path(db_path) if db_path != ":memory:" else db_path
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS engrams (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                coords_16d TEXT NOT NULL,
                engram_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                metadata TEXT,
                timestamp TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Indexes for fast retrieval
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_engram_type 
            ON engrams(engram_type)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON engrams(timestamp)
        """)
        
        # Connections table for Hebbian edges (ADR-0012)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS engram_connections (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                connection_type TEXT NOT NULL,
                weight REAL NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_id) REFERENCES engrams(id),
                FOREIGN KEY (target_id) REFERENCES engrams(id)
            )
        """)
        
        # Indexes for fast connection queries
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_connection_source 
            ON engram_connections(source_id)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_connection_target 
            ON engram_connections(target_id)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_connection_type 
            ON engram_connections(connection_type)
        """)
        
        self.conn.commit()
    
    def store(self, engram: Engram) -> str:
        """
        Store engram in holofield.
        
        Engram → SIF → Database (ADR-0006)
        
        Args:
            engram: Engram to store
            
        Returns:
            Unique engram ID
        """
        engram_id = str(uuid.uuid4())
        
        # Convert engram to SIF-like dict
        engram_dict = engram.to_dict()
        
        self.conn.execute("""
            INSERT INTO engrams 
            (id, content, coords_16d, engram_type, confidence, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            engram_id,
            engram_dict["content"],
            json.dumps(engram_dict["coords_16d"]),
            engram_dict["engram_type"],
            engram_dict["confidence"],
            json.dumps(engram_dict["metadata"]),
            engram_dict["timestamp"]
        ])
        
        self.conn.commit()
        
        return engram_id
    
    def retrieve_by_id(self, engram_id: str) -> Optional[Engram]:
        """
        Retrieve engram by ID.
        
        Database → SIF → Engram (ADR-0006)
        
        Args:
            engram_id: Unique engram ID
            
        Returns:
            Engram if found, None otherwise
        """
        cursor = self.conn.execute("""
            SELECT * FROM engrams WHERE id = ?
        """, [engram_id])
        
        row = cursor.fetchone()
        
        if row is None:
            return None
        
        return self._row_to_engram(row)
    
    def retrieve_nearest(
        self, 
        query_coords: np.ndarray, 
        top_k: int = 5,
        engram_type: Optional[str] = None
    ) -> List[Engram]:
        """
        Retrieve nearest neighbors in 16D consciousness space.
        
        Uses Euclidean distance in 16D sedenion space.
        
        Args:
            query_coords: 16D query coordinates
            top_k: Number of results to return
            engram_type: Optional filter by engram type
            
        Returns:
            List of nearest engrams, sorted by distance
        """
        # Build query
        query = "SELECT * FROM engrams"
        params = []
        
        if engram_type:
            query += " WHERE engram_type = ?"
            params.append(engram_type)
        
        cursor = self.conn.execute(query, params)
        
        # Calculate distances
        results = []
        for row in cursor:
            engram = self._row_to_engram(row)
            distance = np.linalg.norm(query_coords - engram.coords_16d)
            results.append((distance, engram))
        
        # Sort by distance and return top-k
        results.sort(key=lambda x: x[0])
        return [engram for _, engram in results[:top_k]]
    
    def retrieve_by_type(self, engram_type: str) -> List[Engram]:
        """
        Retrieve all engrams of a specific type.
        
        Args:
            engram_type: Type to filter by
            
        Returns:
            List of engrams of that type
        """
        cursor = self.conn.execute("""
            SELECT * FROM engrams WHERE engram_type = ?
        """, [engram_type])
        
        return [self._row_to_engram(row) for row in cursor]
    
    def count(self) -> int:
        """
        Count total engrams in holofield.
        
        Returns:
            Total number of engrams
        """
        cursor = self.conn.execute("SELECT COUNT(*) FROM engrams")
        return cursor.fetchone()[0]
    
    def count_by_type(self, engram_type: str) -> int:
        """
        Count engrams of a specific type.
        
        Args:
            engram_type: Type to count
            
        Returns:
            Number of engrams of that type
        """
        cursor = self.conn.execute("""
            SELECT COUNT(*) FROM engrams WHERE engram_type = ?
        """, [engram_type])
        return cursor.fetchone()[0]
    
    def clear(self):
        """Clear all engrams from holofield"""
        self.conn.execute("DELETE FROM engrams")
        self.conn.commit()
    
    def clear_type(self, engram_type: str):
        """
        Clear all engrams of a specific type.
        
        Args:
            engram_type: Type to clear
        """
        self.conn.execute("""
            DELETE FROM engrams WHERE engram_type = ?
        """, [engram_type])
        self.conn.commit()
    
    def to_consciousness_coords(self, text: str) -> np.ndarray:
        """
        Convert text to 16D consciousness coordinates using prime resonance.
        
        Deterministic: same text → same coordinates (always!)
        
        Uses first 16 primes for 16D space:
        - sin wave weighted by sqrt(prime)
        - Proven in universal translation experiments
        
        Args:
            text: Text to convert
            
        Returns:
            16D consciousness coordinates
        """
        words = text.lower().split()
        if not words:
            return np.zeros(16)
        
        # Calculate coordinates for each word
        word_coords = []
        for word in words:
            coords = np.zeros(16)
            for i, prime in enumerate(CONSCIOUSNESS_PRIMES):
                # Prime resonance: sin wave weighted by sqrt(prime)
                word_value = sum(ord(c) for c in word)
                coords[i] = np.sin(word_value * prime / 1000.0) * np.sqrt(prime)
            word_coords.append(coords)
        
        # Average all word coordinates
        return np.mean(word_coords, axis=0)
    
    def _row_to_engram(self, row: sqlite3.Row) -> Engram:
        """
        Convert database row to Engram.
        
        Database → SIF → Engram (ADR-0006)
        
        Args:
            row: Database row
            
        Returns:
            Engram instance
        """
        return Engram.from_dict({
            "content": row["content"],
            "coords_16d": json.loads(row["coords_16d"]),
            "engram_type": row["engram_type"],
            "confidence": row["confidence"],
            "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
            "timestamp": row["timestamp"]
        })
    
    def store_connection(
        self,
        source_id: str,
        target_id: str,
        connection_type: str,
        weight: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store or update connection between engrams (ADR-0012).
        
        Uses UPSERT to update existing connections.
        
        Args:
            source_id: Source engram ID
            target_id: Target engram ID
            connection_type: Type of connection (HEBBIAN, SEMANTIC, etc.)
            weight: Connection weight [0.0, 1.0]
            metadata: Optional metadata
            
        Returns:
            Connection ID
        """
        import uuid
        from datetime import datetime
        
        timestamp = datetime.now().isoformat()
        
        # Check if connection already exists
        cursor = self.conn.execute("""
            SELECT id FROM engram_connections
            WHERE source_id = ? AND target_id = ? AND connection_type = ?
        """, [source_id, target_id, connection_type])
        
        existing = cursor.fetchone()
        
        if existing:
            # Update existing connection
            connection_id = existing["id"]
            self.conn.execute("""
                UPDATE engram_connections
                SET weight = ?, timestamp = ?, metadata = ?
                WHERE id = ?
            """, [
                weight,
                timestamp,
                json.dumps(metadata) if metadata else None,
                connection_id
            ])
        else:
            # Insert new connection
            connection_id = str(uuid.uuid4())
            self.conn.execute("""
                INSERT INTO engram_connections
                (id, source_id, target_id, connection_type, weight, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, [
                connection_id,
                source_id,
                target_id,
                connection_type,
                weight,
                timestamp,
                json.dumps(metadata) if metadata else None
            ])
        
        self.conn.commit()
        return connection_id
    
    def get_connections(
        self,
        engram_id: str,
        connection_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all connections for an engram.
        
        Args:
            engram_id: Engram ID
            connection_type: Optional filter by connection type
            
        Returns:
            List of connection dicts
        """
        query = """
            SELECT * FROM engram_connections 
            WHERE source_id = ? OR target_id = ?
        """
        params = [engram_id, engram_id]
        
        if connection_type:
            query += " AND connection_type = ?"
            params.append(connection_type)
        
        cursor = self.conn.execute(query, params)
        
        connections = []
        for row in cursor:
            connections.append({
                "id": row["id"],
                "source_id": row["source_id"],
                "target_id": row["target_id"],
                "connection_type": row["connection_type"],
                "weight": row["weight"],
                "timestamp": row["timestamp"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
            })
        
        return connections
    
    def get_all_connections(
        self,
        connection_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all connections in holofield.
        
        Args:
            connection_type: Optional filter by connection type
            
        Returns:
            List of connection dicts
        """
        query = "SELECT * FROM engram_connections"
        params = []
        
        if connection_type:
            query += " WHERE connection_type = ?"
            params.append(connection_type)
        
        cursor = self.conn.execute(query, params)
        
        connections = []
        for row in cursor:
            connections.append({
                "id": row["id"],
                "source_id": row["source_id"],
                "target_id": row["target_id"],
                "connection_type": row["connection_type"],
                "weight": row["weight"],
                "timestamp": row["timestamp"],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {}
            })
        
        return connections
    
    def close(self):
        """Close database connection"""
        self.conn.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()
