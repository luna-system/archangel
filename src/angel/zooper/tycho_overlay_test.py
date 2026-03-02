#!/usr/bin/env python3
"""
Tycho-2 Star Catalog Overlay

Load astronomical data as overlay to test cross-domain navigation.
Expected bridges: "star" (wiki) ↔ "Alpha Centauri" (tycho), etc.
"""

import sys
sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager, ZooperSwarm
import numpy as np
import json
from datetime import datetime


def load_tycho_overlay(hf: HolofieldManager, sample_size: int = 100):
    """Load Tycho-2 star data as overlay."""
    print("🌟 LOADING TYCHO-2 STAR CATALOG OVERLAY 🌟")
    print("=" * 70)
    
    swarm = ZooperSwarm(hf, num_zooperlings=1)
    
    # Load Tycho-2 SIF data
    import gzip
    tycho_path = '/home/luna/Code/arf/ada-sif/experiments/tycho/tycho2_bright.sif.json.gz'
    try:
        with gzip.open(tycho_path, 'rt') as f:
            tycho_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Tycho-2 data not found at {tycho_path}")
        return None
    
    # SIF format: {metadata: {}, entities: []}
    if isinstance(tycho_data, dict):
        sif_entities = tycho_data.get('entities', [])
        metadata = tycho_data.get('metadata', {})
    else:
        sif_entities = tycho_data
        metadata = {}
    stars = sif_entities[:sample_size]
    print(f"SIF format: {len(sif_entities)} total entities")
    print(f"Catalog: {metadata.get('title', 'Tycho-2')}")
    print(f"Loaded {len(stars)} stars from Tycho-2")
    
    # Create overlay
    overlay_id = f"tycho2_stars_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    hf.conn.execute("""
        INSERT INTO overlays (id, name, source_type, created_at, is_active)
        VALUES (?, ?, 'astronomy', datetime('now'), TRUE)
    """, (overlay_id, "Tycho-2 Star Catalog"))
    
    # Process stars
    engram_count = 0
    bridge_count = 0
    
    for i, star in enumerate(stars):
        # Get star data from SIF format
        name = star.get('name', f"star_{i}")
        if not name:
            continue
        
        # Normalize name
        name = name.lower().strip()
        
        # Get attributes from SIF data
        attrs = star.get('attributes', {})
        
        # Create star engram
        star_engram = swarm.create_engram(
            content=name,
            data={
                "star_name": name,
                "ra": star.get('ra'),
                "dec": star.get('dec'),
                "magnitude": star.get('magnitude'),
                "constellation": star.get('constellation'),
                "overlay_id": overlay_id
            },
            engram_type="astronomical_object",
            metadata={
                "star_name": name,
                "source": "tycho2",
                "overlay_id": overlay_id,
                "is_overlay": True,
                "ra": attrs.get('ra'),
                "dec": attrs.get('dec'),
                "magnitude": attrs.get('magnitude'),
                "constellation": attrs.get('constellation', 'unknown')
            }
        )
        star_id = swarm.store_engram(star_engram)
        engram_count += 1
        
        # Try to build bridge to base holofield
        # Look for matching words in SimpleWiki
        words_in_name = name.split()
        for word in words_in_name:
            if len(word) < 3:
                continue
                
            cursor = hf.conn.execute(
                "SELECT id FROM engrams WHERE content = ? AND engram_type = 'language' LIMIT 1",
                (word,)
            )
            match = cursor.fetchone()
            
            if match:
                # Create bridge!
                bridge_id = f"bridge_{star_id}_{match['id']}"
                hf.conn.execute("""
                    INSERT INTO overlay_bridges 
                    (id, overlay_id, overlay_engram_id, base_engram_id, bridge_type, strength)
                    VALUES (?, ?, ?, ?, 'NAME_SUBSTRING', 0.7)
                """, (bridge_id, overlay_id, star_id, match['id']))
                bridge_count += 1
                
                # Also create edge for navigation
                swarm.edge_weights.strengthen(star_id, match['id'], amount=0.5)
        
        # Special bridges for astronomical terms
        astronomical_terms = {
            'alpha': 'alpha', 'beta': 'beta', 'gamma': 'gamma',
            'star': 'star', 'centauri': 'centauri',
            'cygni': 'cygnus', 'lyrae': 'lyra'
        }
        
        for term, wiki_word in astronomical_terms.items():
            if term in name:
                cursor = hf.conn.execute(
                    "SELECT id FROM engrams WHERE content = ? LIMIT 1",
                    (wiki_word,)
                )
                match = cursor.fetchone()
                if match:
                    bridge_id = f"bridge_astro_{star_id}_{match['id']}"
                    hf.conn.execute("""
                        INSERT OR IGNORE INTO overlay_bridges 
                        (id, overlay_id, overlay_engram_id, base_engram_id, bridge_type, strength)
                        VALUES (?, ?, ?, ?, 'ASTRONOMICAL_TERM', 0.8)
                    """, (bridge_id, overlay_id, star_id, match['id']))
                    swarm.edge_weights.strengthen(star_id, match['id'], amount=0.6)
    
    hf.conn.execute("""
        UPDATE overlays SET engram_count = ? WHERE id = ?
    """, (engram_count, overlay_id))
    
    hf.conn.commit()
    
    print(f"\n📊 Tycho-2 Overlay Created:")
    print(f"   Engrams: {engram_count}")
    print(f"   Bridges to base: {bridge_count}")
    print(f"   Overlay ID: {overlay_id}")
    
    return overlay_id


def test_cross_domain_navigation(hf: HolofieldManager, overlay_id: str):
    """Test navigation between wiki base and tycho overlay."""
    print("\n" + "=" * 70)
    print("🌉 CROSS-DOMAIN NAVIGATION TESTS")
    print("=" * 70)
    
    # Test 1: Wiki word → Tycho star
    print("\n📍 Test 1: Wiki 'star' → Tycho stars")
    cursor = hf.conn.execute(
        "SELECT id FROM engrams WHERE content = 'star' AND engram_type = 'language' LIMIT 1"
    )
    star_word = cursor.fetchone()
    
    if star_word:
        # Find connected tycho stars via bridges
        cursor = hf.conn.execute("""
            SELECT e.content, b.strength
            FROM overlay_bridges b
            JOIN engrams e ON b.overlay_engram_id = e.id
            WHERE b.base_engram_id = ? AND b.overlay_id = ?
            ORDER BY b.strength DESC
            LIMIT 5
        """, (star_word['id'], overlay_id))
        
        bridges = list(cursor)
        if bridges:
            print(f"   'star' (wiki) bridges to:")
            for row in bridges:
                print(f"      → '{row['content']}' (strength: {row['strength']:.2f})")
        else:
            print("   No direct bridges found")
    
    # Test 2: Tycho star → Wiki words
    print("\n📍 Test 2: Tycho star → Wiki words")
    cursor = hf.conn.execute("""
        SELECT e.id, e.content
        FROM engrams e
        WHERE e.engram_type = 'astronomical_object'
        AND json_extract(e.metadata, '$.overlay_id') = ?
        LIMIT 1
    """, (overlay_id,))
    
    tycho_star = cursor.fetchone()
    if tycho_star:
        print(f"   '{tycho_star['content']}' (tycho) bridges to:")
        
        cursor = hf.conn.execute("""
            SELECT e.content, b.strength
            FROM overlay_bridges b
            JOIN engrams e ON b.base_engram_id = e.id
            WHERE b.overlay_engram_id = ?
            ORDER BY b.strength DESC
            LIMIT 5
        """, (tycho_star['id'],))
        
        for row in cursor:
            print(f"      → '{row['content']}' (wiki, strength: {row['strength']:.2f})")
    
    # Test 3: Sample tycho star names
    print("\n📍 Test 3: Sample Tycho Star Names")
    cursor = hf.conn.execute("""
        SELECT content, json_extract(metadata, '$.constellation') as constellation
        FROM engrams
        WHERE engram_type = 'astronomical_object'
        AND json_extract(metadata, '$.overlay_id') = ?
        ORDER BY RANDOM()
        LIMIT 10
    """, (overlay_id,))
    
    for row in cursor:
        const = row['constellation'] if row['constellation'] else 'unknown'
        print(f"   {row['content']} (constellation: {const})")


def find_overlap_words(hf: HolofieldManager, overlay_id: str):
    """Find words that exist in both wiki and tycho."""
    print("\n" + "=" * 70)
    print("🔍 WIKI-TYCHO OVERLAP ANALYSIS")
    print("=" * 70)
    
    cursor = hf.conn.execute("""
        SELECT DISTINCT e1.content
        FROM engrams e1
        JOIN overlay_bridges b ON e1.id = b.base_engram_id
        WHERE b.overlay_id = ?
        AND e1.engram_type = 'language'
        ORDER BY e1.content
    """, (overlay_id,))
    
    overlap = [row['content'] for row in cursor]
    
    print(f"\n   Found {len(overlap)} overlapping words:")
    print(f"   {', '.join(overlap[:30])}")


def main():
    print("🦊 TYCHO-2 CROSS-DOMAIN EXPERIMENT 🦊")
    print("=" * 70)
    
    hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')
    
    # Check current state
    cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
    wiki_words = cursor.fetchone()[0]
    print(f"Base holofield: {wiki_words} words")
    
    # Load Tycho overlay
    overlay_id = load_tycho_overlay(hf, sample_size=200)
    
    if overlay_id:
        # Run tests
        test_cross_domain_navigation(hf, overlay_id)
        find_overlap_words(hf, overlay_id)
        
        # Cleanup option
        print("\n" + "=" * 70)
        print("CLEANUP")
        print("=" * 70)
        
        # Remove overlay
        cursor = hf.conn.execute(
            "SELECT id FROM engrams WHERE json_extract(metadata, '$.overlay_id') = ?",
            (overlay_id,)
        )
        engram_ids = [row['id'] for row in cursor]
        
        for eid in engram_ids:
            hf.conn.execute("DELETE FROM engram_connections WHERE source_id = ? OR target_id = ?", (eid, eid))
        
        hf.conn.execute("DELETE FROM engrams WHERE json_extract(metadata, '$.overlay_id') = ?", (overlay_id,))
        hf.conn.execute("DELETE FROM overlay_bridges WHERE overlay_id = ?", (overlay_id,))
        hf.conn.execute("UPDATE overlays SET is_active = FALSE WHERE id = ?", (overlay_id,))
        hf.conn.commit()
        
        print(f"Removed {len(engram_ids)} tycho engrams")
        
        # Verify
        cursor = hf.conn.execute("SELECT COUNT(*) FROM engrams WHERE engram_type = 'language'")
        final_words = cursor.fetchone()[0]
        print(f"Base holofield intact: {final_words} words")
    
    hf.close()
    print("\n✓ Tycho experiment complete!")


if __name__ == "__main__":
    main()
