import requests
import json

response = requests.get('http://127.0.0.1:8000/api/proxy/stats')
data = response.json()

print("=== API Response ===")
print(json.dumps(data, indent=2, ensure_ascii=False))

print("\n=== Country Distribution ===")
for item in data.get('country_distribution', [])[:10]:
    print(f"{item['country']}: {item['count']}")
