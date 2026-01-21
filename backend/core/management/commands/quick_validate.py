"""
Django management command to validate a sample of proxies
"""
from django.core.management.base import BaseCommand
from core.models import Proxy
import requests
import time
from django.utils import timezone


class Command(BaseCommand):
    help = 'Validate a sample of proxies to find working ones'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=100, help='Number of proxies to test')

    def handle(self, *args, **options):
        count = options['count']
        
        # Test HTTP proxies first (easier to test)
        proxies = Proxy.objects.filter(is_active=True, protocol='http')[:count]
        
        self.stdout.write(self.style.SUCCESS(f"\nTesting {proxies.count()} HTTP proxies..."))
        
        tested = 0
        passed = 0
        
        for proxy in proxies:
            tested += 1
            proxy_url = f"{proxy.protocol}://{proxy.ip}:{proxy.port}"
            proxies_dict = {
                "http": proxy_url,
                "https": proxy_url
            }
            
            start_time = time.time()
            try:
                response = requests.get("http://www.baidu.com", proxies=proxies_dict, timeout=5)
                if response.status_code == 200:
                    elapsed = int((time.time() - start_time) * 1000)
                    proxy.speed = elapsed
                    
                    # Dynamic scoring based on speed
                    if elapsed < 200:
                        new_score = min(100, 90 + (200 - elapsed) // 20)
                    elif elapsed < 500:
                        new_score = 70 + (500 - elapsed) // 15
                    elif elapsed < 1000:
                        new_score = 50 + (1000 - elapsed) // 25
                    elif elapsed < 2000:
                        new_score = 30 + (2000 - elapsed) // 50
                    else:
                        new_score = max(10, 30 - (elapsed - 2000) // 100)
                    
                    proxy.score = int((proxy.score + new_score) / 2)
                    proxy.last_checked = timezone.now()
                    proxy.save()
                    passed += 1
                    self.stdout.write(self.style.SUCCESS(f"✓ {proxy.ip}:{proxy.port} - {elapsed}ms - Score: {proxy.score}"))
                else:
                    proxy.score = max(0, proxy.score - 10)
                    proxy.save()
                    self.stdout.write(self.style.WARNING(f"✗ {proxy.ip}:{proxy.port} - Status: {response.status_code}"))
            except Exception as e:
                proxy.score = max(0, proxy.score - 10)
                if proxy.score <= 0:
                    proxy.is_active = False
                proxy.save()
                self.stdout.write(self.style.ERROR(f"✗ {proxy.ip}:{proxy.port} - {str(e)[:50]}"))
            
            if tested % 10 == 0:
                self.stdout.write(f"Progress: {tested}/{proxies.count()} tested, {passed} passed")
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Validation complete!"))
        self.stdout.write(f"Tested: {tested}")
        self.stdout.write(f"Passed: {passed}")
        self.stdout.write(f"Success rate: {(passed/tested*100):.1f}%")
