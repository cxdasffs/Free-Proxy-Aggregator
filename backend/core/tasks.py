import requests
from celery import shared_task
from .models import Proxy
import time
from django.utils import timezone

@shared_task
def fetch_proxies_task():
    """
    Fetches proxies from various sources using the unified fetcher.
    Includes Fate0, TheSpeedX, Jiangxianli, Kuaidaili, 89ip, etc.
    """
    count = 0
    
    # 1. New Powerful Unified Fetcher
    try:
        from .fetchers import fetch_all_sources
        fetched_count = fetch_all_sources()
        count += fetched_count
        print(f"Unified Fetcher: Got {fetched_count} proxies")
    except Exception as e:
        print(f"Unified Fetcher Error: {e}")
    
    # 2. Keep Proxifly as it's a stable CDN source (backup/supplement)
    try:
        proxifly_urls = [
            "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/all/data.txt",
        ]
        for url in proxifly_urls:
             try:
                 resp = requests.get(url, timeout=10)
                 if resp.status_code == 200:
                     for line in resp.text.splitlines():
                        try:
                            line = line.strip()
                            if not line: continue
                            parts = line.split(',')
                            proxy_str = parts[0]
                            country = parts[1].strip() if len(parts) > 1 else 'Unknown'
                            if country in ['ZZ', '', 'Unknown']: country = 'Unknown'

                            if "://" in proxy_str:
                                protocol, rest = proxy_str.split("://")
                                ip, port = rest.split(":")
                            elif ":" in proxy_str:
                                protocol = "http"
                                ip, port = proxy_str.split(":")
                            else: continue
                            
                            # Update or create
                            p, created = Proxy.objects.update_or_create(
                                ip=ip,
                                port=int(port),
                                protocol=protocol,
                                defaults={'country': country, 'source': 'proxifly'}
                            )
                            if created: count += 1
                        except: pass
             except: pass
    except Exception as e:
        print(f"Proxifly Error: {e}")
    
    return f"Fetched {count} new proxies"

@shared_task
def validate_proxies_task():
    """
    Validates proxies via Multi-threading to process 60k+ proxies efficiently.
    Target: Bing (Less strict WAF) & Xiaomi (Fast check)
    """
    import random
    import concurrent.futures
    from fake_useragent import UserAgent
    ua = UserAgent()
    
    # Increase batch size significantly: 200 -> 1000
    proxies = list(Proxy.objects.filter(is_active=True).order_by('last_checked')[:1000])
    if not proxies: return "No proxies to validate"

    print(f"Starting validation for {len(proxies)} proxies...")
    
    def validate_one(proxy):
        proxy_url = f"{proxy.protocol}://{proxy.ip}:{proxy.port}"
        proxies_dict = {"http": proxy_url, "https": proxy_url}
        headers = {'User-Agent': ua.random}
        
        start_time = time.time()
        try:
            # Switch target to Bing (more stable for bulk requests) or Xiaomi
            # verify=False for speed
            resp = requests.get("http://www.bing.com", proxies=proxies_dict, headers=headers, timeout=8, verify=False)
            
            if resp.status_code == 200:
                elapsed = int((time.time() - start_time) * 1000)
                proxy.speed = elapsed
                
                # Dynamic scoring
                if elapsed < 500: new_score = 100
                elif elapsed < 1500: new_score = 80
                elif elapsed < 3000: new_score = 60
                else: new_score = 40
                
                # Revival mechanism: if it was low score, boost it back up
                proxy.score = int((proxy.score + new_score) / 2)
                proxy.last_checked = timezone.now()
                
                # --- GeoIP Correction (if missing) ---
                if proxy.country in ['Unknown', 'XX', '', 'None']:
                    try:
                         # Use a fast random delay to avoid rate limit
                        if random.random() < 0.1:
                            r = requests.get(f"http://ip-api.com/json/{proxy.ip}?fields=countryCode", timeout=3)
                            if r.status_code == 200: proxy.country = r.json().get('countryCode', 'XX')
                    except: pass

                # --- Anonymity Check (Random sample) ---
                if proxy.score > 60 and (proxy.anonymity == 'unknown' or random.random() < 0.05):
                    try:
                        anon_resp = requests.get("http://httpbin.org/get?show_env=1", proxies=proxies_dict, headers=headers, timeout=10)
                        if anon_resp.status_code == 200:
                            data = anon_resp.json()
                            headers_info = data.get('headers', {})
                            origin = data.get('origin', '')
                            if 'Via' in headers_info or 'X-Forwarded-For' in headers_info: proxy.anonymity = 'transparent'
                            elif ',' in origin: proxy.anonymity = 'transparent'
                            else: proxy.anonymity = 'elite'
                    except: pass # Keep alive even if anonymity check fails
                
                proxy.save()
                return True
            else:
                # Penalty
                proxy.score = max(0, proxy.score - 20) # Heavy penalty for non-200
                proxy.save()
                return False
        except Exception:
            # Timeout / Error
            proxy.score = max(0, proxy.score - 20)
            if proxy.score <= 0: proxy.is_active = False # Kill dead proxy
            proxy.save()
            return False

    # Run in parallel
    passed = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(validate_one, proxies))
        passed = sum(1 for r in results if r)

    return f"Validated {len(proxies)} proxies, {passed} passed"
