import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Proxy
from django.db.models import Count

print("\n=== Unknown proxies by source ===")
unknown = Proxy.objects.filter(country='Unknown').values('source').annotate(count=Count('source'))
for u in unknown:
    print(f"{u['source']}: {u['count']}")

print("\n=== Sample Unknown proxies ===")
samples = Proxy.objects.filter(country='Unknown')[:5]
for s in samples:
    print(f"{s.protocol}://{s.ip}:{s.port} - Source: {s.source}")
