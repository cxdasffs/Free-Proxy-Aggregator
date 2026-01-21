"""
Script to re-import proxy data from data.csv with correct country parsing
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Proxy

def reimport_data():
    """Re-import data from data.csv with correct country parsing"""
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data.csv')
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found")
        return
    
    print("Clearing existing proxies...")
    Proxy.objects.all().delete()
    
    print("Importing proxies from data.csv...")
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
                        print(f"Imported {count} proxies...")
                        
            except Exception as e:
                print(f"Error parsing line: {line[:50]}... - {e}")
                continue
    
    print(f"\nImport complete! Total proxies imported: {count}")
    
    # Show country distribution
    from django.db.models import Count
    country_dist = Proxy.objects.values('country').annotate(count=Count('country')).order_by('-count')[:10]
    print("\nTop 10 countries:")
    for item in country_dist:
        print(f"  {item['country']}: {item['count']}")

if __name__ == '__main__':
    reimport_data()
