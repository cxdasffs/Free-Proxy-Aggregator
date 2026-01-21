from django.http import StreamingHttpResponse
import json
import random
import requests
import time
import concurrent.futures
from .models import Proxy
from fake_useragent import UserAgent

try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = None

def attack_target_stream(request):
    """
    Stream attack results in real-time using Server-Sent Events (SSE).
    This allows for massive-scale attacks without timeout.
    """

    target_url = request.GET.get('url')
    country = request.GET.get('country')
    region = request.GET.get('region')
    protocol = request.GET.get('protocol')
    specific_ip = request.GET.get('specific_ip')
    sort_by = request.GET.get('sort_by', 'score')
    allow_unsafe = request.GET.get('allow_unsafe', 'false') == 'true'

    try:
        attack_count = int(request.GET.get('attack_count', 10))
    except:
        attack_count = 10

    if not target_url:
        return StreamingHttpResponse("data: {\"error\": \"Target URL required\"}\n\n", content_type='text/event-stream')

    def event_stream():
        # Base Query
        proxies = Proxy.objects.filter(is_active=True)
        
        # 1. Specific IP Mode
        if specific_ip:
            # Smart Handle: "1.2.3.4:8080" -> "1.2.3.4"
            target_ip = specific_ip.strip()
            if ":" in target_ip: target_ip = target_ip.split(":")[0]
            proxies = proxies.filter(ip=target_ip)
            if proxies.count() == 0:
                yield f"data: {json.dumps({'error': f'Proxy {target_ip} not found...'})}\n\n"
                return
        else:
            # 2. Auto Mode
            if allow_unsafe:
                # [Hardcore Mode]: Use EVERYTHING except Transparent
                # Includes Elite, Anonymous, and the 60k Unknown ones
                proxies = proxies.exclude(anonymity='transparent')
            else:
                # [Strict Mode]: Only Elite & Anonymous
                proxies = proxies.filter(anonymity__in=['elite', 'anonymous'])
            
            # --- Apply filters ---
            if country and country != 'all': proxies = proxies.filter(country=country)
            elif region:
                if region == 'domestic': proxies = proxies.filter(country='CN')
                elif region == 'foreign': proxies = proxies.exclude(country='CN')
            
            if protocol and protocol != 'all':
                if protocol == 'socks': proxies = proxies.filter(protocol__startswith='socks')
                else: proxies = proxies.filter(protocol=protocol)
            
            # Note: No fallback needed now because this filter includes EVERYTHING logic
            
            # Sorting Strategy
            if sort_by == 'speed':
                proxies = proxies.order_by('speed')
            else:
                # High score first (Elites), then the unknown masses
                proxies = proxies.order_by('-score')
        
        count_in_db = proxies.count()
        if count_in_db == 0:
             yield f"data: {json.dumps({'error': 'No VALIDATED proxies found. Please click SCAN to validate your new proxies first!'})}\n\n"
             return

        # Handle "ALL" or large numbers
        real_count = min(attack_count, count_in_db)
        
        if attack_count >= 10000:
             selected_proxies = list(proxies[:real_count])
        else:
             pool_size = min(real_count * 2, count_in_db)
             selected_proxies = random.sample(list(proxies[:pool_size]), real_count)

        # Notify start
        total_targets = len(selected_proxies)
        yield f"data: {json.dumps({'type': 'start', 'total': total_targets})}\n\n"
        
        # Prepare UserAgent generator
        ua = UserAgent()

        def check_proxy(proxy):
            # Smart Protocol Handling: Use Remote DNS for SOCKS
            proto = proxy.protocol
            if proto == 'socks5': proto = 'socks5h' # Remote DNS
            elif proto == 'socks4': proto = 'socks4a' # Remote DNS
            
            proxy_url = f"{proto}://{proxy.ip}:{proxy.port}"
            proxies_dict = {"http": proxy_url, "https": proxy_url}
            
            # Anti-fingerprinting: Random UA
            headers = {'User-Agent': ua.random}
            
            result = {
                "type": "result",
                "proxy": f"{proxy.ip}:{proxy.port}",
                "country": proxy.country,
                "protocol": proxy.protocol,
                "success": False,
                "time_ms": 0,
                "error": ""
            }
            
            start_time = time.time()
            try:
                # 1. Try with curl_cffi (Best for fingerprinting)
                used_fallback = False
                if cffi_requests:
                    try:
                        resp = cffi_requests.get(
                            target_url, 
                            proxies=proxies_dict, 
                            headers=headers, 
                            timeout=15, 
                            impersonate="chrome110" 
                        )
                    except Exception as e:
                        # Curl failed (e.g. Windows certificate issue), Fallback strict!
                        used_fallback = True
                        resp = requests.get(target_url, proxies=proxies_dict, headers=headers, timeout=15, verify=False)
                else:
                    # 2. Standard Requests
                    resp = requests.get(target_url, proxies=proxies_dict, headers=headers, timeout=15, verify=False)
                    
                elapsed = int((time.time() - start_time) * 1000)
                
                result["time_ms"] = elapsed
                result["status_code"] = resp.status_code
                
                if resp.status_code == 200:
                    result["success"] = True
                else:
                    result["error"] = f"Status {resp.status_code}"
            
            except Exception as e:
                err = str(e)
                err = str(e)
                if "ConnectTimeout" in err or "ReadTimeout" in err: result["error"] = "Timeout"
                elif "ProxyError" in err: result["error"] = "Proxy Error"
                elif "ConnectionError" in err: result["error"] = "Connection Failed"
                elif "SSLError" in err or "handshake" in err.lower(): result["error"] = "SSL Handshake Failed"
                elif "Failed to perform" in err: result["error"] = "Connection Refused" # Curl error mapping
                else: result["error"] = err[:30] # Slightly longer error
            
            return result

        # Use 100 threads for high concurrency
        with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(check_proxy, p): p for p in selected_proxies}
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    data = future.result()
                    yield f"data: {json.dumps(data)}\n\n"
                except:
                    pass
        
        yield f"data: {json.dumps({'type': 'end'})}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no' # Important for Nginx
    return response
