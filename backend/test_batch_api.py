import requests
import json

# Test batch test API
url = 'http://127.0.0.1:8000/api/proxy/batch-test'
data = {
    'country': 'CN',
    'count': 5,
    'test_url': 'http://www.baidu.com'
}

print("Testing batch test API...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")
print("\nSending request...")

try:
    response = requests.post(url, json=data, timeout=60)
    print(f"\nStatus Code: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"\nError: {e}")
