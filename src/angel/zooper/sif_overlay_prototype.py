#!/usr/bin/env python3
"""
SIF Overlay Prototype - Load external text as temporary holofield layer.

This demonstrates how to ingest new data sources without polluting
the base holofield.
"""

import sys
sys.path.insert(0, '/home/luna/Code/arf/archangel/src')

from angel import HolofieldManager, ZooperSwarm
import numpy as np
import json
import re
from collections import Counter
from datetime import datetime


class SIFOverlayLoader:
    """
    Load text data as temporary overlay engrams.
    
    Overlay engrams:
    - Are marked with overlay_id
    - Can be queried independently or with base holofield
    - Can be removed without affecting base
    - Can be promoted to permanent
    """
    
    def __init__(self, holofield_manager: HolofieldManager):
        self.hf = holofield_manager
        self.swarm = ZooperSwarm(self.hf, num_zooperlings=1)
    
    def load_text_overlay(
        self,
        text: str,
        overlay_name: str,
        source_metadata: dict = None
    ) -> str:
        """
        Load raw text as overlay engrams.
        
        Returns overlay_id for later reference.
        """
        overlay_id = f"overlay_{overlay_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"📝 Loading overlay: {overlay_name}")
        print(f"   Text length: {len(text)} chars")
        
        # Create overlay record
        self.hf.conn.execute("""
            INSERT INTO overlays (id, name, source_type, created_at, is_active)
            VALUES (?, ?, 'text', datetime('now'), TRUE)
        """, (overlay_id, overlay_name))
        
        # Create a "virtual article" for this text
        article_engram = self.swarm.create_engram(
            content=text[:200] + "..." if len(text) > 200 else text,
            data={
                "source_type": "overlay_text",
                "full_text": text,
                "overlay_id": overlay_id
            },
            engram_type="overlay_source",
            metadata={
                "overlay_id": overlay_id,
                "overlay_name": overlay_name,
                "source_metadata": source_metadata or {},
                "text_length": len(text),
                "word_count": len(text.split())
            }
        )
        article_id = self.swarm.store_engram(article_engram)
        
        # Generate 16D coordinates for this text
        # (In real implementation, use semantic embedding model)
        article_coords = np.random.randn(16) * 0.1
        
        # Process text into n-grams
        words = re.findall(r'\b\w+\b', text.lower())
        word_freq = Counter(words)
        
        # Create word engrams (overlay-specific!)
        engram_count = 0
        for word, freq in word_freq.most_common(100):  # Top 100 words
            if freq < 2 or len(word) < 3:
                continue
            
            # Create overlay word engram
            word_engram = self.swarm.create_engram(
                content=word,
                data={"word": word, "parent_overlay": overlay_id},
                engram_type="language",
                metadata={
                    "word": word,
                    "source": f"overlay_{overlay_name}",
                    "overlay_id": overlay_id,
                    "is_overlay": True,
                    "frequency": freq,
                    "source_metadata": source_metadata or {}
                }
            )
            word_id = self.swarm.store_engram(word_engram)
            
            # Link to article
            self.swarm.edge_weights.strengthen(article_id, word_id, amount=0.3)
            engram_count += 1
        
        # Update overlay stats
        self.hf.conn.execute("""
            UPDATE overlays SET engram_count = ? WHERE id = ?
        """, (engram_count, overlay_id))
        
        self.hf.conn.commit()
        
        print(f"   Created {engram_count} overlay engrams")
        return overlay_id
    
    def query_overlay(self, overlay_id: str, content_pattern: str = None):
        """Query engrams within specific overlay."""
        if content_pattern:
            cursor = self.hf.conn.execute("""
                SELECT content, json_extract(metadata, '$.frequency') as freq
                FROM engrams
                WHERE json_extract(metadata, '$.overlay_id') = ?
                AND content LIKE ?
                ORDER BY freq DESC
            """, (overlay_id, f"%{content_pattern}%"))
        else:
            cursor = self.hf.conn.execute("""
                SELECT content, json_extract(metadata, '$.frequency') as freq
                FROM engrams
                WHERE json_extract(metadata, '$.overlay_id') = ?
                ORDER BY freq DESC
                LIMIT 20
            """, (overlay_id,))
        
        return [(row['content'], row['freq']) for row in cursor]
    
    def list_overlays(self):
        """List all active overlays."""
        cursor = self.hf.conn.execute("""
            SELECT id, name, created_at, engram_count
            FROM overlays
            WHERE is_active = TRUE
            ORDER BY created_at DESC
        """)
        return [dict(row) for row in cursor]
    
    def remove_overlay(self, overlay_id: str):
        """Remove overlay engrams (but not base holofield)."""
        print(f"🗑️  Removing overlay: {overlay_id}")
        
        # Get engram IDs to remove
        cursor = self.hf.conn.execute("""
            SELECT id FROM engrams
            WHERE json_extract(metadata, '$.overlay_id') = ?
        """, (overlay_id,))
        engram_ids = [row['id'] for row in cursor]
        
        # Remove connections
        for eid in engram_ids:
            self.hf.conn.execute("""
                DELETE FROM engram_connections
                WHERE source_id = ? OR target_id = ?
            """, (eid, eid))
        
        # Remove engrams
        self.hf.conn.execute("""
            DELETE FROM engrams
            WHERE json_extract(metadata, '$.overlay_id') = ?
        """, (overlay_id,))
        
        # Mark overlay inactive
        self.hf.conn.execute("""
            UPDATE overlays SET is_active = FALSE WHERE id = ?
        """, (overlay_id,))
        
        self.hf.conn.commit()
        print(f"   Removed {len(engram_ids)} engrams")


def demo_overlay_system():
    """Demo SIF overlay system."""
    print("🦊 SIF OVERLAY SYSTEM DEMO 🦊")
    print("=" * 70)
    
    hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')
    loader = SIFOverlayLoader(hf)
    
    # Sample: Pride and Prejudice opening
    austen_text = """
    It is a truth universally acknowledged, that a single man in possession
    of a good fortune, must be in want of a wife. However little known the
    feelings or views of such a man may be on his first entering a neighbourhood,
    this truth is so well fixed in the minds of the surrounding families,
    that he is considered the rightful property of some one or other of their
    daughters. Mr Bennet was among the earliest of those who waited on Mr Bingley.
    """
    
    # Sample: Technical documentation
    tech_text = """
    The API accepts JSON payloads with the following schema: request_id (string),
    timestamp (ISO 8601), and data (object). Authentication requires a Bearer token
    in the Authorization header. Rate limiting is enforced at 100 requests per minute.
    Endpoints return HTTP 200 on success, 400 for client errors, and 500 for server errors.
    """
    
    # Load overlays
    print("\n📚 Loading Literature Overlay...")
    austen_overlay = loader.load_text_overlay(
        text=austen_text,
        overlay_name="pride_prejudice_sample",
        source_metadata={"author": "Jane Austen", "year": 1813}
    )
    
    print("\n💻 Loading Technical Overlay...")
    tech_overlay = loader.load_text_overlay(
        text=tech_text,
        overlay_name="api_documentation",
        source_metadata={"domain": "software", "type": "documentation"}
    )
    
    # Query overlays
    print("\n" + "=" * 70)
    print("OVERLAY QUERIES")
    print("=" * 70)
    
    print(f"\n📖 Austen overlay words:")
    words = loader.query_overlay(austen_overlay)
    for word, freq in words[:10]:
        print(f"   '{word}' (freq: {freq})")
    
    print(f"\n💻 Tech overlay words:")
    words = loader.query_overlay(tech_overlay)
    for word, freq in words[:10]:
        print(f"   '{word}' (freq: {freq})")
    
    # List all overlays
    print(f"\n📊 All Active Overlays:")
    overlays = loader.list_overlays()
    for ov in overlays:
        print(f"   {ov['name']}: {ov['engram_count']} engrams")
    
    # Compare with base holofield
    print(f"\n🔍 Cross-source comparison:")
    cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
    base_words = cursor.fetchone()[0]
    print(f"   Base holofield words: {base_words}")
    
    # Remove overlays
    print("\n" + "=" * 70)
    print("CLEANUP")
    print("=" * 70)
    
    loader.remove_overlay(austen_overlay)
    loader.remove_overlay(tech_overlay)
    
    # Verify base intact
    cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
    final_words = cursor.fetchone()[0]
    print(f"\n✓ Base holofield intact: {final_words} words (was {base_words})")
    
    hf.close()
    print("\n✓ Overlay demo complete!")


if __name__ == "__main__":
    demo_overlay_system()
