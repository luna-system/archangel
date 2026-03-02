#!/usr/bin/env python3
"""
Investigate DPLA API for linguistic data ingestion.

DPLA (Digital Public Library of America) aggregates metadata from 
libraries, archives, and museums. Potential goldmine for text data!
"""

import json
import urllib.request
import urllib.parse

# First, let's understand the API structure from documentation
docs_url = "https://pro.dp.la/developers/api-codex"

print("🔍 INVESTIGATING DPLA API 🔍")
print("=" * 70)

# DPLA API structure (from documentation)
print("\n📚 API Structure (from docs):")
print("-" * 70)

api_structure = """
Base URL: https://api.dp.la/v2/

Endpoints:
  /items          - Search digitized items (books, photos, etc.)
  /collections    - Browse collections

Key Parameters:
  q               - Full-text search query
  sourceResource  - Filter by metadata fields
  provider        - Filter by contributing institution
  rights          - Filter by rights statement (public domain!)
  page_size       - Results per page (max 100)

Response Format:
  {
    "count": 12345,
    "docs": [
      {
        "id": "item-123",
        "sourceResource": {
          "title": "Book Title",
          "description": "Full text or abstract",
          "creator": ["Author Name"],
          "date": "1920",
          "subject": ["Astronomy", "Physics"],
          "language": ["English"]
        },
        "dataProvider": "Library of Congress",
        "rights": "Public Domain"
      }
    ]
  }
"""

print(api_structure)

# What makes this PERFECT for our needs:
print("\n✅ WHY DPLA IS PERFECT FOR LINGUISTIC INTERFACE:")
print("-" * 70)

benefits = """
1. DIVERSE VOCABULARY:
   - Historical texts (different eras = different language)
   - Academic papers (technical terminology)
   - Literary works (rich prose)
   - Newspapers (journalistic style)
   - Personal letters (conversational)

2. PUBLIC DOMAIN CONTENT:
   - Filter by rights="Public Domain"
   - No copyright concerns for ingestion
   - Pre-1928 books freely usable

3. RICH METADATA:
   - Subject tags for thematic organization
   - Dates for temporal navigation
   - Authors for stylistic clustering
   - Languages for multilingual support

4. STRUCTURED DATA:
   - Title, description, full text (when available)
   - Consistent JSON format
   - Easy to parse into SIF overlays

5. SCALE:
   - 45+ million items
   - 3,000+ contributing institutions
   - Massive diversity
"""

print(benefits)

# Use cases for our overlays:
print("\n🎯 USE CASES FOR SIF OVERLAYS:")
print("-" * 70)

use_cases = """
1. PROJECT GUTENBERG ALTERNATIVE:
   Query: q=pride+prejudice&rights=Public+Domain
   → Overlay with "Pride and Prejudice" full text

2. SCIENTIFIC PAPERS:
   Query: q=astronomy&sourceResource.subject=Physics
   → Technical vocabulary overlay

3. HISTORICAL NEWSPAPERS:
   Query: sourceResource.type=Newspaper&date=1900
   → Early 20th century language patterns

4. CHILDREN'S BOOKS:
   Query: q=children&sourceResource.subject=Juvenile
   → Simple language overlay

5. MULTILINGUAL:
   Query: sourceResource.language=French
   → French language overlay
"""

print(use_cases)

# Sample ingestion workflow:
print("\n🔄 INGESTION WORKFLOW:")
print("-" * 70)

workflow = """
1. QUERY DPLA API:
   GET /v2/items?q=astronomy&page_size=100&api_key=KEY

2. FILTER FOR FULL TEXT:
   Check for sourceResource.description or full text fields

3. EXTRACT TEXT:
   title + description + full_text (when available)

4. GENERATE EMBEDDINGS:
   Create 16D coordinates via semantic embedding model

5. CREATE SIF OVERLAY:
   {
     "overlay_id": "dpla_astronomy_batch_001",
     "source": "DPLA",
     "query": "astronomy",
     "engrams": [...],
     "bridges": [...]
   }

6. LOAD INTO HOLOFIELD:
   loader.load_sif_overlay("dpla_astronomy_batch_001.sif")

7. BUILD CROSS-DOMAIN BRIDGES:
   "telescope" (DPLA) → "telescope" (SimpleWiki)
   "galaxy" (DPLA) → "galaxy" (SimpleWiki)
"""

print(workflow)

# Challenges:
print("\n⚠️  CHALLENGES & MITIGATIONS:")
print("-" * 70)

challenges = """
1. API KEY REQUIRED:
   → Free signup at https://dp.la/api-keys
   → Rate limits apply (10,000 calls/day free)

2. NOT ALL ITEMS HAVE FULL TEXT:
   → Many items are metadata-only
   → Filter for items with description/full_text
   → Still valuable for vocabulary even without full text

3. OCR QUALITY VARIES:
   → Historical texts may have OCR errors
   → Clean/normalize text before ingestion
   → Quality thresholds filter noise

4. COORDINATE DRIFT:
   → Different embedding models = different coordinate spaces
   → Use consistent model for all DPLA ingestion
   → Re-embed if model changes
"""

print(challenges)

# Implementation sketch:
print("\n💻 IMPLEMENTATION SKETCH:")
print("-" * 70)

code = '''
class DPLAIngestor:
    """Ingest DPLA data as SIF overlays."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.dp.la/v2"
    
    def search_items(self, query: str, page_size: int = 100) -> list:
        """Search DPLA for items."""
        url = f"{self.base_url}/items"
        params = {
            "q": query,
            "page_size": page_size,
            "api_key": self.api_key
        }
        response = requests.get(url, params=params)
        return response.json()["docs"]
    
    def extract_text(self, item: dict) -> str:
        """Extract text content from DPLA item."""
        resource = item.get("sourceResource", {})
        parts = [
            resource.get("title", ""),
            resource.get("description", ""),
            " ".join(resource.get("subject", [])),
        ]
        return " ".join(filter(None, parts))
    
    def create_overlay(self, query: str, items: list) -> str:
        """Create SIF overlay from DPLA items."""
        overlay = {
            "sif_version": "0.1.0",
            "overlay_id": f"dpla_{query}_{datetime.now():%Y%m%d}",
            "source_type": "dpla",
            "source_metadata": {
                "query": query,
                "item_count": len(items),
                "source": "Digital Public Library of America"
            },
            "engrams": [],
            "connections": [],
            "bridge_points": []
        }
        
        for item in items:
            text = self.extract_text(item)
            if not text:
                continue
            
            # Create engrams from text (using our existing n-gram pipeline!)
            engrams = self.text_to_engrams(text)
            overlay["engrams"].extend(engrams)
            
            # Build bridges to base holofield
            bridges = self.find_bridges(engrams)
            overlay["bridge_points"].extend(bridges)
        
        return overlay

# Usage:
ingestor = DPLAIngestor(api_key="your_key_here")
items = ingestor.search_items("astronomy", page_size=100)
overlay = ingestor.create_overlay("astronomy", items)
loader.load_sif_overlay(overlay)
'''

print(code)

print("\n" + "=" * 70)
print("📊 FEASIBILITY: HIGH ✅")
print("=" * 70)

feasibility = """
✅ API is well-documented
✅ JSON format (easy to parse)
✅ Public domain content available
✅ Rich metadata for organization
✅ Scalable (batch queries)
✅ Fits our SIF overlay architecture perfectly

NEXT STEPS:
1. Get API key from https://dp.la/api-keys
2. Test with small query (q=astronomy, page_size=10)
3. Build DPLAIngestor class
4. Create first DPLA overlay
5. Test cross-domain navigation
"""

print(feasibility)

print("\n✓ DPLA investigation complete!")
