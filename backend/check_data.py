import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Proxy
from django.db.models import Count

print("\n=== Source Distribution ===")
sources = Proxy.objects.values('source').annotate(count=Count('source')).order_by('-count')
for s in sources:
    print(f"{s['source']}: {s['count']}")

print("\n=== Country Distribution (Top 15) ===")
countries = Proxy.objects.values('country').annotate(count=Count('country')).order_by('-count')[:15]
for c in countries:
    print(f"{c['country']}: {c['count']}")
