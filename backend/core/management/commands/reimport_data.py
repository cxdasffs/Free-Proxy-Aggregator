"""
Django management command to re-import proxy data from data.csv
"""
from django.core.management.base import BaseCommand
from django.db.models import Count
from core.models import Proxy
import os


class Command(BaseCommand):
    help = 'Re-import proxy data from data.csv with correct country parsing'

    def handle(self, *args, **options):
        # Get project root - go up from backend/core/management/commands/
        current_file = os.path.abspath(__file__)
        commands_dir = os.path.dirname(current_file)  # commands/
        management_dir = os.path.dirname(commands_dir)  # management/
        core_dir = os.path.dirname(management_dir)  # core/
        backend_dir = os.path.dirname(core_dir)  # backend/
        project_root = os.path.dirname(backend_dir)  # project root
        csv_path = os.path.join(project_root, 'data.csv')
        
        self.stdout.write(f"Looking for CSV at: {csv_path}")
        
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f"Error: {csv_path} not found"))
            return
        
        self.stdout.write(self.style.WARNING("Clearing existing proxies..."))
        Proxy.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS("Importing proxies from data.csv..."))
        count = 0
        with open(csv_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    line = line.strip()
                    if not line:
                        continue
                    
                    parts = line.split(',')
                    proxy_str = parts[0]
                    # parts[1] is the COUNTRY CODE (e.g., SG, FR, US)
                    # parts[2] is the City (e.g., Unknown, Singapore, etc.) - we ignore this
                    country = parts[1].strip() if len(parts) > 1 else 'Unknown'
                    
                    # Fix common bad country codes - ZZ means unknown, keep actual country codes
                    if country in ['ZZ', '', 'Unknown']:
                        country = 'Unknown'
                    
                    if "://" in proxy_str:
                        protocol, rest = proxy_str.split("://")
                        ip, port = rest.split(":")
                    elif ":" in proxy_str:
                        protocol = "http"
                        ip, port = proxy_str.split(":")
                    else:
                        continue
                    
                    # Determine source based on existing data (default to proxifly)
                    source = 'proxifly'
                    
                    # Create or update proxy
                    proxy, created = Proxy.objects.update_or_create(
                        ip=ip,
                        port=int(port),
                        protocol=protocol,
                        defaults={'country': country, 'source': source}
                    )
                    
                    if created:
                        count += 1
                        if count % 100 == 0:
                            self.stdout.write(f"Imported {count} proxies...")
                            
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error parsing line: {line[:50]}... - {e}"))
                    continue
        
        self.stdout.write(self.style.SUCCESS(f"\nImport complete! Total proxies imported: {count}"))
        
        # Show country distribution
        country_dist = Proxy.objects.values('country').annotate(count=Count('country')).order_by('-count')[:10]
        self.stdout.write(self.style.SUCCESS("\nTop 10 countries:"))
        for item in country_dist:
            self.stdout.write(f"  {item['country']}: {item['count']}")
