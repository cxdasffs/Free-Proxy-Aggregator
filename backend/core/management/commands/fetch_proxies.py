"""
Django management command to manually fetch proxies from all sources
"""
from django.core.management.base import BaseCommand
from core.tasks import fetch_proxies_task


class Command(BaseCommand):
    help = 'Manually fetch proxies from all sources (89ip, ip3366, proxifly)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting proxy fetch from all sources..."))
        result = fetch_proxies_task()
        self.stdout.write(self.style.SUCCESS(f"\nResult: {result}"))
