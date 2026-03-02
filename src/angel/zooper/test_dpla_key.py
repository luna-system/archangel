#!/usr/bin/env python3
"""
Quick test of DPLA API with our new key!
"""
import sys
import os

# Set API key
os.environ['DPLA_API_KEY'] = '9407335f06bc153e82900b6d796c0371'

sys.path.insert(0, '/home/luna/Code/arf/archangel/src')
from angel.zooper.dpla_ingestor import DPLAIngestor

print("🌟 TESTING DPLA API KEY 🌟")
print("=" * 70)

ingestor = DPLAIngestor()

# Test search
items = ingestor.search_items("astronomy", page_size=5)

if items:
    print(f"\n✅ SUCCESS! Found {len(items)} items")
    print("\n📚 Sample items:")
    for i, item in enumerate(items[:3], 1):
        resource = item.get('sourceResource', {})
        title = resource.get('title', 'Untitled')
        if isinstance(title, list):
            title = title[0]
        print(f"\n   {i}. {title[:60]}...")
        print(f"      Provider: {item.get('dataProvider', 'Unknown')}")
        
        # Show extracted text preview
        text = ingestor.extract_text(item)
        print(f"      Text preview: {text[:80]}...")
else:
    print("\n❌ No items found")

print("\n✓ API key test complete!")
