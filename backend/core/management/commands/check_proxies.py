"""
Django management command to check proxy data
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from core.models import Proxy


class Command(BaseCommand):
    help = 'Check proxy data distribution'

    def handle(self, *args, **options):
        total = Proxy.objects.count()
        active = Proxy.objects.filter(is_active=True).count()
        
        self.stdout.write(self.style.SUCCESS(f"\nTotal Proxies: {total}"))
        self.stdout.write(self.style.SUCCESS(f"Active Proxies: {active}"))
        
        # Source distribution
        self.stdout.write(self.style.SUCCESS("\n=== Source Distribution ==="))
        sources = Proxy.objects.values('source').annotate(count=Count('source')).order_by('-count')
        for s in sources:
            self.stdout.write(f"  {s['source']}: {s['count']}")
        
        # Country distribution
        self.stdout.write(self.style.SUCCESS("\n=== Top 10 Countries ==="))
        countries = Proxy.objects.filter(is_active=True).values('country').annotate(count=Count('country')).order_by('-count')[:10]
        for c in countries:
            self.stdout.write(f"  {c['country']}: {c['count']}")
        
        # Score distribution
        self.stdout.write(self.style.SUCCESS("\n=== Score Distribution ==="))
        high_score = Proxy.objects.filter(score__gte=80).count()
        med_score = Proxy.objects.filter(score__gte=50, score__lt=80).count()
        low_score = Proxy.objects.filter(score__lt=50).count()
        self.stdout.write(f"  High (80-100): {high_score}")
        self.stdout.write(f"  Medium (50-79): {med_score}")
        self.stdout.write(f"  Low (0-49): {low_score}")
