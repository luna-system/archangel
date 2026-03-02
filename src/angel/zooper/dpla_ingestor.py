#!/usr/bin/env python3
"""
DPLA Ingestor - Load Digital Public Library data as SIF overlays.

Usage:
    export DPLA_API_KEY="your_key_here"
    python3 dpla_ingestor.py --query "astronomy" --limit 100
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
from typing import List, Dict, Optional

sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager, ZooperSwarm


class DPLAIngestor:
    """
    Ingest DPLA (Digital Public Library of America) data as SIF overlays.
    
    DPLA provides 45+ million digitized items from libraries, archives,
    and museums. Perfect for expanding linguistic interface vocabulary!
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize DPLA ingestor.
        
        Args:
            api_key: DPLA API key (or set DPLA_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get('DPLA_API_KEY')
        if not self.api_key:
            raise ValueError(
                "DPLA API key required. Get one at https://dp.la/api-keys "
                "or set DPLA_API_KEY environment variable."
            )
        
        self.base_url = "https://api.dp.la/v2"
        self.session = requests.Session()
    
    def search_items(
        self,
        query: str,
        page_size: int = 100,
        rights: Optional[str] = "Public Domain"
    ) -> List[Dict]:
        """
        Search DPLA for items matching query.
        
        Args:
            query: Search terms
            page_size: Results per page (max 100)
            rights: Filter by rights (e.g., "Public Domain")
            
        Returns:
            List of item documents
        """
        url = f"{self.base_url}/items"
        params = {
            "q": query,
            "page_size": min(page_size, 100),
            "api_key": self.api_key
        }
        
        if rights:
            params["rights"] = rights
        
        print(f"🔍 Querying DPLA: '{query}' (page_size={page_size})")
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            count = data.get("count", 0)
            docs = data.get("docs", [])
            
            print(f"   Found {count} total, retrieved {len(docs)} items")
            return docs
            
        except requests.RequestException as e:
            print(f"   ❌ API error: {e}")
            return []
    
    def extract_text(self, item: Dict) -> str:
        """
        Extract text content from DPLA item.
        
        Combines title, description, and subject tags.
        """
        resource = item.get("sourceResource", {})
        
        parts = []
        
        # Title (always present)
        title = resource.get("title")
        if title:
            if isinstance(title, list):
                parts.extend(title)
            else:
                parts.append(title)
        
        # Description (often contains full text or abstract)
        description = resource.get("description")
        if description:
            if isinstance(description, list):
                parts.extend(description)
            else:
                parts.append(description)
        
        # Subject tags (useful for vocabulary)
        subjects = resource.get("subject", [])
        if subjects:
            if isinstance(subjects, list):
                parts.extend(subjects)
            else:
                parts.append(subjects)
        
        # Creator/author
        creators = resource.get("creator", [])
        if creators:
            if isinstance(creators, list):
                parts.extend(creators)
            else:
                parts.append(creators)
        
        return " ".join(filter(None, parts))
    
    def filter_quality_items(self, items: List[Dict]) -> List[Dict]:
        """
        Filter items for quality text content.
        
        Removes items with:
        - No description/full text
        - Too short (< 100 chars)
        - OCR errors (heuristic)
        """
        quality_items = []
        
        for item in items:
            text = self.extract_text(item)
            
            # Must have substantial text
            if len(text) < 100:
                continue
            
            # Check for excessive OCR errors (gibberish ratio)
            # Simple heuristic: count non-alphanumeric chars
            non_alpha = sum(1 for c in text if not c.isalnum() and not c.isspace())
            if non_alpha / len(text) > 0.2:  # >20% non-alphanumeric
                continue
            
            quality_items.append(item)
        
        print(f"   Filtered to {len(quality_items)} quality items")
        return quality_items
    
    def create_sif_overlay(
        self,
        query: str,
        items: List[Dict],
        holofield_manager: HolofieldManager
    ) -> str:
        """
        Create SIF overlay from DPLA items and load into holofield.
        
        Args:
            query: Original search query
            items: DPLA items
            holofield_manager: Holofield to load into
            
        Returns:
            Overlay ID
        """
        from angel import ZooperSwarm
        
        swarm = ZooperSwarm(holofield_manager, num_zooperlings=1)
        
        # Create overlay record
        overlay_id = f"dpla_{query.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        holofield_manager.conn.execute("""
            INSERT INTO overlays (id, name, source_type, created_at, is_active)
            VALUES (?, ?, 'dpla', datetime('now'), TRUE)
        """, (overlay_id, f"DPLA: {query}"))
        
        # Process items
        total_engrams = 0
        total_bridges = 0
        
        print(f"\n📝 Processing {len(items)} items into overlay...")
        
        for i, item in enumerate(items):
            text = self.extract_text(item)
            if not text:
                continue
            
            # Create virtual article for this item
            item_title = item.get("sourceResource", {}).get("title", "Untitled")
            if isinstance(item_title, list):
                item_title = item_title[0]
            
            article_engram = swarm.create_engram(
                content=text[:500],  # Truncate for storage
                data={
                    "title": item_title,
                    "dpla_id": item.get("id"),
                    "provider": item.get("dataProvider"),
                    "rights": item.get("rights"),
                    "overlay_id": overlay_id
                },
                engram_type="dpla_item",
                metadata={
                    "source": "dpla",
                    "overlay_id": overlay_id,
                    "is_overlay": True,
                    "query": query,
                    "dpla_id": item.get("id"),
                    "provider": item.get("dataProvider")
                }
            )
            article_id = swarm.store_engram(article_engram)
            
            # Create word engrams from this item
            article_data = {"content": text}
            decomposition = swarm.parallel_decompose(article_data)
            
            word_engrams = swarm._create_word_engrams(
                decomposition, article_id, 
                np.random.randn(16) * 0.1,  # Dummy coords, should embed
                raw_content=text
            )
            
            swarm._create_hebbian_edges(article_id, word_engrams)
            total_engrams += len(word_engrams)
            
            # Build bridges to base holofield
            for word_id in word_engrams:
                cursor = holofield_manager.conn.execute(
                    "SELECT content FROM engrams WHERE id = ?",
                    (word_id,)
                )
                word_row = cursor.fetchone()
                if not word_row:
                    continue
                
                word = word_row['content']
                
                # Find matching word in base
                cursor = holofield_manager.conn.execute(
                    """
                    SELECT id FROM engrams 
                    WHERE content = ? AND engram_type = 'language'
                    AND json_extract(metadata, '$.is_overlay') IS NULL
                    LIMIT 1
                    """,
                    (word,)
                )
                base_match = cursor.fetchone()
                
                if base_match:
                    bridge_id = f"bridge_{word_id}_{base_match['id']}"
                    holofield_manager.conn.execute("""
                        INSERT OR IGNORE INTO overlay_bridges 
                        (id, overlay_id, overlay_engram_id, base_engram_id, bridge_type, strength)
                        VALUES (?, ?, ?, ?, 'DPLA_WORD_MATCH', 0.7)
                    """, (bridge_id, overlay_id, word_id, base_match['id']))
                    total_bridges += 1
            
            if (i + 1) % 10 == 0:
                print(f"   Processed {i+1}/{len(items)} items...")
        
        # Update overlay stats
        holofield_manager.conn.execute("""
            UPDATE overlays SET engram_count = ? WHERE id = ?
        """, (total_engrams, overlay_id))
        
        holofield_manager.conn.commit()
        
        print(f"\n✅ DPLA overlay created!")
        print(f"   Overlay ID: {overlay_id}")
        print(f"   Engrams: {total_engrams}")
        print(f"   Bridges: {total_bridges}")
        
        return overlay_id


def main():
    parser = argparse.ArgumentParser(description="Ingest DPLA data as SIF overlays")
    parser.add_argument("--query", required=True, help="DPLA search query")
    parser.add_argument("--limit", type=int, default=50, help="Max items to fetch")
    parser.add_argument("--db", default="/home/luna/Code/arf/archangel/data/simplewiki_holofield.db",
                        help="Holofield database path")
    parser.add_argument("--api-key", help="DPLA API key (or set DPLA_API_KEY)")
    
    args = parser.parse_args()
    
    print("🌟 DPLA INGESTOR 🌟")
    print("=" * 70)
    
    # Initialize
    try:
        ingestor = DPLAIngestor(api_key=args.api_key)
    except ValueError as e:
        print(f"❌ {e}")
        print("\nGet a free API key at: https://dp.la/api-keys")
        return 1
    
    # Search DPLA
    items = ingestor.search_items(args.query, page_size=args.limit)
    if not items:
        print("❌ No items found")
        return 1
    
    # Filter for quality
    quality_items = ingestor.filter_quality_items(items)
    if not quality_items:
        print("❌ No quality items after filtering")
        return 1
    
    # Connect to holofield
    print(f"\n📦 Connecting to holofield: {args.db}")
    hf = HolofieldManager(args.db)
    
    # Create overlay
    overlay_id = ingestor.create_sif_overlay(args.query, quality_items, hf)
    
    hf.close()
    
    print(f"\n✓ DPLA ingestion complete!")
    print(f"\nTo query the overlay:")
    print(f"  SELECT * FROM engrams WHERE json_extract(metadata, '$.overlay_id') = '{overlay_id}'")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
