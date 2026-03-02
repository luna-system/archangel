#!/usr/bin/env python3
import requests

API_KEY = '9407335f06bc153e82900b6d796c0371'

print("🔍 DEBUGGING DPLA API CALL 🔍")
print("=" * 70)

# Try simple query first
url = "https://api.dp.la/v2/items"
params = {
    "q": "astronomy",
    "page_size": 5,
    "api_key": API_KEY
}

print(f"\nURL: {url}")
print(f"Params: {params}")

try:
    response = requests.get(url, params=params, timeout=10)
    print(f"\nStatus: {response.status_code}")
    print(f"Response preview: {response.text[:500]}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n✅ SUCCESS!")
        print(f"Count: {data.get('count', 0)}")
        print(f"Docs: {len(data.get('docs', []))}")
        
        if data.get('docs'):
            print("\n📚 Sample item:")
            item = data['docs'][0]
            resource = item.get('sourceResource', {})
            title = resource.get('title', 'Untitled')
            if isinstance(title, list):
                title = title[0]
            print(f"   Title: {title}")
            print(f"   Provider: {item.get('dataProvider')}")
    else:
        print(f"\n❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ Exception: {e}")
