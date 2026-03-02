# DPLA API Key Setup

## Getting Your Free API Key

### Step 1: Visit the API Keys Page

Go to: **https://dp.la/api-keys**

### Step 2: Enter Your Email

Fill in the form with:
- **Email**: luna@airsi.de (or your preferred email)
- **Name** (optional): Your name or project name

### Step 3: Check Your Email

The API key will be sent to your email within minutes.

### Step 4: Set Environment Variable

Once you receive the key:

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export DPLA_API_KEY="your_actual_key_here"

# Or set for current session only
export DPLA_API_KEY="your_actual_key_here"
```

### Step 5: Verify

```bash
# Check it's set
echo $DPLA_API_KEY

# Test with ingestor
python3 src/angel/zooper/dpla_ingestor.py --query "test" --limit 5
```

## API Key Limits

- **Free tier**: 10,000 calls/day
- **Rate limit**: No specific limit, be respectful
- **Usage**: Academic, research, non-commercial OK

## Without API Key

If you prefer not to get an API key, you can still:

1. Use SimpleWiki base (1,400 words)
2. Import Project Gutenberg texts directly
3. Use local text files

But **DPLA is highly recommended** for:
- Rich metadata
- Diverse content types
- Structured data
- Scale (45+ million items)

## Privacy Note

DPLA uses your email only for:
- Sending API key
- Occasional service updates (rare)
- Usage notifications if you hit limits

They don't sell or share emails.

## Troubleshooting

### "Email not received"

- Check spam folder
- Try alternative email
- Contact DPLA: info@dp.la

### "Key not working"

- Verify no extra spaces: `echo "$DPLA_API_KEY" | od -c`
- Try regenerating at https://dp.la/api-keys
- Check key format (should be alphanumeric)

### "Rate limit exceeded"

- Free tier: 10,000 calls/day
- Wait 24 hours for reset
- Or batch queries more efficiently

## Alternative: No-API Ingestion

If you can't get an API key, use these free alternatives:

### Project Gutenberg

```bash
# Download directly
wget https://www.gutenberg.org/files/1342/1342-0.txt  # Pride & Prejudice

# Create overlay
python3 -c "
from angel.zooper.sif_overlay_prototype import SIFOverlayLoader
from angel import HolofieldManager

hf = HolofieldManager('./data/holofield.db')
loader = SIFOverlayLoader(hf)

with open('1342-0.txt', 'r') as f:
    text = f.read()

loader.load_text_overlay(text, 'pride_prejudice', 
    source_metadata={'author': 'Jane Austen'})
"
```

### Local Files

```python
# Any text file works!
with open('my_book.txt', 'r') as f:
    text = f.read()

loader.load_text_overlay(text, 'my_book')
```

---

**Get your key and start ingesting!** 🌟📚
