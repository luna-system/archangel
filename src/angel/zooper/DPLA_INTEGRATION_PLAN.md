# DPLA Integration Plan

## Summary

**DPLA (Digital Public Library of America)** is an **ideal data source** for our linguistic interface!

## Why It's Perfect

| Feature | Benefit |
|:--------|:--------|
| **45+ million items** | Massive scale for vocabulary growth |
| **Public domain filter** | No copyright concerns |
| **Rich metadata** | Subject tags, dates, authors for organization |
| **Diverse content** | Books, newspapers, letters, academic papers |
| **Structured JSON API** | Easy to parse into SIF overlays |
| **Free API key** | 10,000 calls/day at no cost |

## Example Queries

```python
# Literature overlay
q=pride+prejudice&rights=Public+Domain
→ 50+ results with full text

# Scientific papers  
q=astronomy&sourceResource.subject=Physics
→ Technical vocabulary

# Historical newspapers
sourceResource.type=Newspaper&date=1900
→ Early 20th century language

# Children's books
q=children&sourceResource.subject=Juvenile
→ Simple vocabulary
```

## Sample API Response

```json
{
  "count": 1234,
  "docs": [{
    "id": "item-123",
    "sourceResource": {
      "title": "The Starry Heavens",
      "description": "A guide to astronomy for beginners...",
      "subject": ["Astronomy", "Stars"],
      "date": "1890",
      "language": ["English"]
    },
    "dataProvider": "Library of Congress",
    "rights": "Public Domain"
  }]
}
```

## Implementation

### Step 1: Get API Key
Visit: https://dp.la/api-keys
(Free, instant signup)

### Step 2: Build DPLAIngestor
See `dpla_ingestor.py` for full implementation

### Step 3: Create Overlays
```python
# Search DPLA
items = ingestor.search_items("astronomy", page_size=100)

# Create SIF overlay
overlay = ingestor.create_overlay("astronomy", items)

# Load into holofield
loader.load_sif_overlay(overlay)
```

### Step 4: Build Cross-Domain Bridges
```python
# Bridge "telescope" (DPLA) → "telescope" (SimpleWiki)
# Bridge "galaxy" (DPLA) → "galaxy" (SimpleWiki)
```

## Expected Results

| Overlay Type | Words Added | Quality |
|:-------------|:------------|:--------|
| Astronomy books | 500-1000 | High (technical) |
| Literature | 2000+ | High (rich prose) |
| Newspapers 1900 | 3000+ | Medium (OCR errors) |
| Children's books | 500 | High (simple) |

## Comparison to SimpleWiki

| Metric | SimpleWiki | DPLA (projected) |
|:-------|:-----------|:-----------------|
| Vocabulary | 1,383 words | 10,000+ words |
| Domains | Encyclopedia | Literature, science, history |
| Eras | Modern | 1800s-1920s |
| Styles | Expository | Narrative, academic, journalistic |

## Feasibility: ✅ HIGH

**Ready to implement!**

1. ✅ API is well-documented
2. ✅ JSON format (easy parsing)
3. ✅ Public domain content
4. ✅ Fits SIF overlay architecture
5. ✅ Scalable (batch queries)

**Next step:** Get API key and test! 🚀
