"""
Django management command to import proxies from Proxifly JSON format
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from core.models import Proxy
import requests


class Command(BaseCommand):
    help = 'Import proxies from Proxifly JSON API (includes score and anonymity)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n🚀 Fetching proxies from Proxifly JSON API..."))
        
        # Clear existing proxifly proxies
        deleted = Proxy.objects.filter(source='proxifly').delete()
        self.stdout.write(f"Cleared {deleted[0]} old proxifly proxies")
        
        urls = {
            'http': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.json',
            'socks4': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks4/data.json',
            'socks5': 'https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/socks5/data.json',
        }
        
        total_imported = 0
        
        for protocol, url in urls.items():
            try:
                self.stdout.write(f"\nFetching {protocol.upper()} proxies...")
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    proxies_data = response.json()
                    count = 0
                    
                    for item in proxies_data:
                        try:
                            ip = item['ip']
                            port = item['port']
                            country = item['geolocation']['country']
                            
                            # Fix ZZ to Unknown
                            if country in ['ZZ', '']:
                                country = 'Unknown'
                            
                            # Use Proxifly's score (1-10), multiply by 10 to get 10-100
                            score = item.get('score', 1) * 10
                            
                            # Create proxy
                            proxy, created = Proxy.objects.update_or_create(
                                ip=ip,
                                port=port,
                                protocol=protocol,
                                defaults={
                                    'country': country,
                                    'source': 'proxifly',
                                    'score': score,
                                    'speed': 0  # Will be updated during validation
                                }
                            )
                            
                            if created:
                                count += 1
                                
                        except Exception as e:
                            continue
                    
                    self.stdout.write(self.style.SUCCESS(f"✓ Imported {count} {protocol.upper()} proxies"))
                    total_imported += count
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Error fetching {protocol}: {e}"))
        
        self.stdout.write(self.style.SUCCESS(f"\n✅ Total imported: {total_imported} proxies"))
        
        # Show distribution
        self.stdout.write(self.style.SUCCESS("\n=== Country Distribution ==="))
        countries = Proxy.objects.filter(source='proxifly').values('country').annotate(count=Count('country')).order_by('-count')[:10]
        for c in countries:
            self.stdout.write(f"  {c['country']}: {c['count']}")
        
        # Show score distribution
        self.stdout.write(self.style.SUCCESS("\n=== Score Distribution ==="))
        high = Proxy.objects.filter(source='proxifly', score__gte=80).count()
        med = Proxy.objects.filter(source='proxifly', score__gte=50, score__lt=80).count()
        low = Proxy.objects.filter(source='proxifly', score__lt=50).count()
        self.stdout.write(f"  High (80-100): {high}")
        self.stdout.write(f"  Medium (50-79): {med}")
        self.stdout.write(f"  Low (0-49): {low}")
