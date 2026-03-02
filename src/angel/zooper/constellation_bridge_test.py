#!/usr/bin/env python3
"""
Cross-Domain Bridge Test with Constellations

Since Tycho uses IDs, let's test with constellation data which
has more overlap with SimpleWiki vocabulary.
"""

import sys
sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager, ZooperSwarm
import numpy as np
from datetime import datetime

print("🌌 CROSS-DOMAIN CONSTELLATION BRIDGE TEST 🌌")
print("=" * 70)

hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')
swarm = ZooperSwarm(hf, num_zooperlings=1)

# Check for astronomical terms in SimpleWiki
astronomical_terms = [
    'star', 'stars', 'sun', 'moon', 'earth', 'mars', 'jupiter', 'saturn',
    'galaxy', 'universe', 'space', 'orbit', 'planet', 'planets',
    'constellation', 'astronomy', 'light', 'year'
]

print("\n🔍 Checking SimpleWiki for astronomical terms:")
found_terms = []
for term in astronomical_terms:
    cursor = hf.conn.execute(
        "SELECT COUNT(*) FROM engrams WHERE content = ? AND engram_type = 'language'",
        (term,)
    )
    count = cursor.fetchone()[0]
    if count > 0:
        found_terms.append(term)
        print(f"   ✓ '{term}' found")

print(f"\n   Found {len(found_terms)}/{len(astronomical_terms)} astronomical terms")

# Create a constellation overlay with explicit bridges
constellations = [
    ("orion", "hunter", " prominent constellation"),
    ("ursa major", "big dipper", "great bear constellation"),
    ("cassiopeia", "queen", "W-shaped constellation"),
    ("cygnus", "swan", "northern cross constellation"),
    ("draco", "dragon", "circumpolar constellation"),
    ("leo", "lion", "zodiac constellation"),
    ("scorpius", "scorpion", "zodiac constellation"),
]

print("\n" + "=" * 70)
print("🌟 CREATING CONSTELLATION OVERLAY WITH BRIDGES")
print("=" * 70)

overlay_id = f"constellations_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

hf.conn.execute("""
    INSERT INTO overlays (id, name, source_type, created_at, is_active)
    VALUES (?, ?, 'astronomy', datetime('now'), TRUE)
""", (overlay_id, "Constellation Guide"))

bridge_count = 0
engram_count = 0

for name, nickname, description in constellations:
    # Create constellation engram
    const_engram = swarm.create_engram(
        content=name,
        data={
            "name": name,
            "nickname": nickname,
            "description": description,
            "overlay_id": overlay_id
        },
        engram_type="astronomical_object",
        metadata={
            "constellation": name,
            "nickname": nickname,
            "source": "constellation_overlay",
            "overlay_id": overlay_id,
            "is_overlay": True
        }
    )
    const_id = swarm.store_engram(const_engram)
    engram_count += 1
    
    # Build bridges to SimpleWiki words
    words_to_bridge = name.split() + nickname.split() + description.split()
    
    for word in words_to_bridge:
        word = word.lower().strip('.,')
        if len(word) < 3:
            continue
            
        cursor = hf.conn.execute(
            "SELECT id FROM engrams WHERE content = ? AND engram_type = 'language' LIMIT 1",
            (word,)
        )
        match = cursor.fetchone()
        
        if match:
            # Create bridge
            bridge_id = f"bridge_{const_id}_{match['id']}"
            hf.conn.execute("""
                INSERT INTO overlay_bridges 
                (id, overlay_id, overlay_engram_id, base_engram_id, bridge_type, strength)
                VALUES (?, ?, ?, ?, 'CONCEPTUAL', 0.8)
            """, (bridge_id, overlay_id, const_id, match['id']))
            
            # Create edge for navigation
            swarm.edge_weights.strengthen(const_id, match['id'], amount=0.6)
            bridge_count += 1
            print(f"   '{name}' → '{word}' (bridge created)")

hf.conn.execute("""
    UPDATE overlays SET engram_count = ? WHERE id = ?
""", (engram_count, overlay_id))

hf.conn.commit()

print(f"\n📊 Results:")
print(f"   Constellation engrams: {engram_count}")
print(f"   Bridges to SimpleWiki: {bridge_count}")

# Test navigation with commit first
hf.conn.commit()
print("   (committed to database)")
print("\n" + "=" * 70)
print("🌉 CROSS-DOMAIN NAVIGATION")
print("=" * 70)

print("\n📍 From 'star' (SimpleWiki) → constellations:")
cursor = hf.conn.execute(
    "SELECT id FROM engrams WHERE content = 'star' AND engram_type = 'language' LIMIT 1"
)
star_word = cursor.fetchone()

if star_word:
    cursor = hf.conn.execute("""
        SELECT e.content, b.strength
        FROM overlay_bridges b
        JOIN engrams e ON b.overlay_engram_id = e.id
        WHERE b.base_engram_id = ? AND b.overlay_id = ?
        ORDER BY b.strength DESC
    """, (star_word['id'], overlay_id))
    
    for row in cursor:
        print(f"   'star' → '{row['content']}' (strength: {row['strength']:.2f})")

print("\n📍 From 'hunter' (SimpleWiki) → constellations:")
cursor = hf.conn.execute(
    "SELECT id FROM engrams WHERE content = 'hunter' AND engram_type = 'language' LIMIT 1"
)
hunter_word = cursor.fetchone()

if hunter_word:
    cursor = hf.conn.execute("""
        SELECT e.content, b.strength
        FROM overlay_bridges b
        JOIN engrams e ON b.overlay_engram_id = e.id
        WHERE b.base_engram_id = ? AND b.overlay_id = ?
    """, (hunter_word['id'], overlay_id))
    
    for row in cursor:
        print(f"   'hunter' → '{row['content']}' (strength: {row['strength']:.2f})")

print("\n📍 From 'orion' (overlay) → SimpleWiki words:")
cursor = hf.conn.execute("""
    SELECT e.content, b.strength
    FROM overlay_bridges b
    JOIN engrams e ON b.base_engram_id = e.id
    WHERE b.overlay_engram_id IN (
        SELECT id FROM engrams WHERE content = 'orion' AND json_extract(metadata, '$.overlay_id') = ?
    )
""", (overlay_id,))

for row in cursor:
    print(f"   'orion' → '{row['content']}' (strength: {row['strength']:.2f})")

# Show final state
print("\n" + "=" * 70)
print("FINAL STATE (keeping overlay for inspection)")
print("=" * 70)

# List all active overlays
cursor = hf.conn.execute("SELECT id, name, engram_count FROM overlays WHERE is_active = TRUE")
print("\nActive overlays:")
for row in cursor:
    print(f"   {row['name']}: {row['engram_count']} engrams")

print(f"\nTo clean up later, run:")
print(f"   DELETE FROM engrams WHERE json_extract(metadata, '$.overlay_id') = '{overlay_id}'")
print(f"   DELETE FROM overlay_bridges WHERE overlay_id = '{overlay_id}'")

hf.close()
print("\n✓ Constellation bridge test complete!")
