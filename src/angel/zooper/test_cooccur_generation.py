#!/usr/bin/env python3
"""
Test Markov generation WITH co-occurrence edges!
"""
import sys
sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel import HolofieldManager
import numpy as np
import random

hf = HolofieldManager('/home/luna/Code/arf/archangel/data/simplewiki_holofield.db')

print("🔗 TESTING CO-OCCURRENCE GENERATION 🔗")
print("=" * 70)

# Check edges for 'year'
cursor = hf.conn.execute("""
    SELECT e.content, c.weight, c.connection_type
    FROM engram_connections c
    JOIN engrams e ON c.target_id = e.id
    JOIN engrams src ON c.source_id = src.id
    WHERE src.content = 'year' AND src.engram_type = 'language'
    AND c.connection_type = 'CO_OCCUR'
    ORDER BY c.weight DESC
    LIMIT 15
""")

print("\n📊 'year' co-occurs with:")
for row in cursor:
    print(f"   → '{row['content']}' (weight: {row['weight']:.2f}, type: {row['connection_type']})")

# Simple generation test
def generate_from_word(start_word, length=15):
    """Simple Markov using CO_OCCUR edges."""
    words = [start_word]
    current = start_word
    
    for _ in range(length - 1):
        # Get co-occurring words
        cursor = hf.conn.execute("""
            SELECT e.content, c.weight
            FROM engram_connections c
            JOIN engrams e ON c.target_id = e.id
            JOIN engrams src ON c.source_id = src.id
            WHERE src.content = ? AND src.engram_type = 'language'
            AND c.connection_type = 'CO_OCCUR'
            ORDER BY c.weight DESC
            LIMIT 10
        """, (current,))
        
        neighbors = [(row['content'], row['weight']) for row in cursor]
        
        if not neighbors:
            break
        
        # Weighted random choice
        total_weight = sum(w for _, w in neighbors)
        r = random.uniform(0, total_weight)
        cumulative = 0
        for word, weight in neighbors:
            cumulative += weight
            if r <= cumulative:
                current = word
                words.append(word)
                break
    
    return " ".join(words)

# Test generation
print("\n" + "=" * 70)
print("GENERATION TESTS")
print("=" * 70)

test_words = ['year', 'january', 'china', 'republic', 'calendar']
for word in test_words:
    print(f"\n📝 From '{word}':")
    for i in range(3):
        text = generate_from_word(word, length=12)
        print(f"   {i+1}. {text}")

hf.close()
print("\n✓ Generation test complete!")
