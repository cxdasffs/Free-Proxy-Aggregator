from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Avg
from .models import Proxy
from .tasks import fetch_proxies_task, validate_proxies_task
import random
import time
import requests
import threading


@api_view(['POST'])
def trigger_crawl(request):
    """
    Trigger the crawler and quick validator.
    """
    try:
        # Try to use Celery if available
        fetch_proxies_task.delay()
        validate_proxies_task.delay()
        return Response({"status": "started", "message": "Crawl & Validation initiated in background (Celery)."})
    except Exception as e:
        # If Celery is not available, run in a background thread
        def run_tasks():
            try:
                # Fetch new proxies
                fetch_proxies_task()
                
                # Quick validation: test first 100 HTTP proxies
                from django.utils import timezone
                proxies = Proxy.objects.filter(is_active=True, protocol='http')[:100]
                
                print(f"🔍 Quick validation: testing {proxies.count()} HTTP proxies...")
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
                            
                            # Dynamic scoring
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
                            print(f"✓ {proxy.ip}:{proxy.port} - {elapsed}ms - Score: {proxy.score}")
                        else:
                            proxy.score = max(0, proxy.score - 10)
                            proxy.save()
                    except Exception:
                        proxy.score = max(0, proxy.score - 10)
                        if proxy.score <= 0:
                            proxy.is_active = False
                        proxy.save()
                    
                    if tested % 10 == 0:
                        print(f"Progress: {tested}/{proxies.count()} tested, {passed} passed")
                
                print(f"✅ Quick validation complete: {passed}/{tested} proxies passed")
                
            except Exception as task_error:
                print(f"Task error: {task_error}")
        
        thread = threading.Thread(target=run_tasks)
        thread.daemon = True
        thread.start()
        
        return Response({"status": "started", "message": "Crawl & Quick Validation initiated (testing 100 proxies in background)."})

@api_view(['GET'])
def get_proxy(request):
    """
    Get a single random high-quality proxy.
    """
    proxies = Proxy.objects.filter(is_active=True, score__gte=5).order_by('-score')[:20]
    if not proxies:
        return Response({"error": "No proxies available"}, status=503)
    
    proxy = random.choice(proxies)
    return Response({
        "proxy": f"{proxy.ip}:{proxy.port}",
        "protocol": proxy.protocol,
        "score": proxy.score
    })

@api_view(['GET'])
def list_proxies(request):
    """
    List proxies with advanced filtering and formats.
    """
    from django.http import HttpResponse
    
    source = request.query_params.get('source')
    region = request.query_params.get('region')
    protocol = request.query_params.get('protocol')
    anonymity = request.query_params.get('anonymity')
    limit = int(request.query_params.get('limit', 100))
    fmt = request.query_params.get('format', 'json')
    
    queryset = Proxy.objects.filter(is_active=True)
    
    # --- Filtering ---
    if source and source != 'all':
        queryset = queryset.filter(source=source)
        
    if region == 'domestic':
        queryset = queryset.filter(country='CN')
    elif region == 'foreign':
        queryset = queryset.exclude(country='CN')
    elif region and len(region) == 2: # Specific country code
        queryset = queryset.filter(country=region.upper())
        
    if protocol and protocol != 'all':
        if protocol == 'socks': queryset = queryset.filter(protocol__startswith='socks')
        else: queryset = queryset.filter(protocol=protocol)

    if anonymity and anonymity != 'all':
        if anonymity == 'high': # Elite + Anonymous
             queryset = queryset.filter(anonymity__in=['elite', 'anonymous'])
        else:
             queryset = queryset.filter(anonymity=anonymity)

    # --- Ordering & Limit ---
    proxies = queryset.order_by('-score', '-speed')[:limit]
    
    # --- Format Output ---
    if fmt == 'text':
        # Text format: 1.2.3.4:8080 (one per line)
        content = "\n".join([f"{p.protocol}://{p.ip}:{p.port}" for p in proxies])
        return HttpResponse(content, content_type='text/plain')
    
    # JSON format
    data = []
    for p in proxies:
        data.append({
            "id": p.id,
            "ip": p.ip,
            "port": p.port,
            "protocol": p.protocol,
            "anonymity": p.anonymity,
            "country": p.country,
            "score": p.score,
            "speed": p.speed,
            "source": p.source,
            "last_checked": p.last_checked,
            "is_active": p.is_active
        })
    return Response(data)

@api_view(['GET'])
def proxy_stats(request):
    """
    Get statistics for the dashboard.
    """
    total_active = Proxy.objects.filter(is_active=True).count()
    avg_speed = Proxy.objects.filter(is_active=True).aggregate(Avg('speed'))['speed__avg'] or 0
    
    # Country distribution
    country_dist = Proxy.objects.filter(is_active=True).values('country').annotate(count=Count('country')).order_by('-count')
    
    return Response({
        "total_active": total_active,
        "avg_speed": int(avg_speed),
        "country_distribution": list(country_dist)
    })

@api_view(['POST'])
def test_target(request):
    """
    Test a target URL using multiple proxies (simulated attack) with CONCURRENCY.
    """
    import concurrent.futures
    
    target_url = request.data.get('url')
    country = request.data.get('country')
    region = request.data.get('region')
    attack_count = request.data.get('attack_count', 1) 
    
    if not target_url:
        return Response({"error": "Target URL is required"}, status=400)
    
    # Limit attack count (Increased to effectively unlimited for this scale)
    attack_count = min(max(1, attack_count), 100000)
    
    proxies = Proxy.objects.filter(is_active=True, score__gte=5).order_by('-score')
    
    if country:
        proxies = proxies.filter(country=country)
    elif region:
        if region == 'domestic':
             proxies = proxies.filter(country='CN')
        elif region == 'foreign':
             proxies = proxies.exclude(country='CN')
        
    if not proxies.exists():
        return Response({"error": f"No active proxies found{' for country ' + country if country else ''}"}, status=404)
    
    # Check if we have enough proxies
    available_count = min(attack_count, proxies.count())
    # Use all available matches if count is high
    selected_proxies = list(proxies[:available_count])
    
    results = []
    success_count = 0
    total_time = 0
    
    # Define the single task function
    def check_proxy(proxy):
        # ... (same function) ...
        proxy_url = f"{proxy.protocol}://{proxy.ip}:{proxy.port}"
        proxies_dict = {
            "http": proxy_url,
            "https": proxy_url
        }
        
        result = {
            "proxy": f"{proxy.ip}:{proxy.port}",
            "country": proxy.country,
            "protocol": proxy.protocol,
            "time_ms": 0,
            "success": False,
            "error": ""
        }
        
        try:
            start_time = time.time()
            # Timeout 5s
            resp = requests.get(target_url, proxies=proxies_dict, timeout=5)
            elapsed = int((time.time() - start_time) * 1000)
            
            result["status_code"] = resp.status_code
            result["time_ms"] = elapsed
            if resp.status_code == 200:
                result["success"] = True
            else:
                result["error"] = f"Status {resp.status_code}"
                
        except requests.exceptions.Timeout:
            result["error"] = "Timeout"
        except requests.exceptions.ProxyError:
            result["error"] = "Proxy Error"
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection Failed"
        except Exception as e:
            result["error"] = str(e)[:30]
            
        return result

    # Execute in parallel
    # Increased workers to 100 for massive attacks
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_proxy = {executor.submit(check_proxy, p): p for p in selected_proxies}
        for future in concurrent.futures.as_completed(future_to_proxy):
            data = future.result()
            results.append(data)
            if data["success"]:
                success_count += 1
                total_time += data["time_ms"]

    # Return comprehensive results
    return Response({
        "status": "success" if success_count > 0 else "failure",
        "attack_count": attack_count,
        "success_count": success_count,
        "failure_count": attack_count - success_count,
        "success_rate": f"{(success_count/attack_count*100):.1f}%" if attack_count > 0 else "0%",
        "avg_latency": int(total_time / success_count) if success_count > 0 else 0,
        "results": results
    })

@api_view(['POST'])
def batch_test_proxies(request):
    """
    Batch test proxies from a specific country/region.
    """
    country = request.data.get('country')
    region = request.data.get('region')
    count = request.data.get('count', 10)  # Default test 10 proxies
    test_url = request.data.get('test_url', 'http://www.baidu.com')
    
    # Get proxies to test
    queryset = Proxy.objects.filter(is_active=True)
    
    if country and country != 'all':
        queryset = queryset.filter(country=country)
    elif region:
        if region == 'domestic':
            queryset = queryset.filter(country='CN')
        elif region == 'foreign':
            queryset = queryset.exclude(country='CN')
    
    proxies = queryset.order_by('-score')[:count]
    
    if not proxies.exists():
        return Response({"error": "No proxies found for the selected filter"}, status=404)
    
    results = []
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
            response = requests.get(test_url, proxies=proxies_dict, timeout=5)
            elapsed = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                passed += 1
                results.append({
                    "proxy": f"{proxy.ip}:{proxy.port}",
                    "country": proxy.country,
                    "protocol": proxy.protocol,
                    "source": proxy.source,
                    "status": "success",
                    "status_code": response.status_code,
                    "latency_ms": elapsed,
                    "score": proxy.score,
                    "success": True
                })
            else:
                results.append({
                    "proxy": f"{proxy.ip}:{proxy.port}",
                    "country": proxy.country,
                    "protocol": proxy.protocol,
                    "source": proxy.source,
                    "status": "failed",
                    "status_code": response.status_code,
                    "latency_ms": elapsed,
                    "score": proxy.score,
                    "success": False
                })
        except Exception as e:
            results.append({
                "proxy": f"{proxy.ip}:{proxy.port}",
                "country": proxy.country,
                "protocol": proxy.protocol,
                "source": proxy.source,
                "status": "error",
                "error": str(e)[:100],
                "latency_ms": 0,
                "score": proxy.score,
                "success": False
            })
    
    return Response({
        "total_tested": tested,
        "total_passed": passed,
        "success_rate": f"{(passed/tested*100):.1f}%" if tested > 0 else "0%",
        "test_url": test_url,
        "filter": {
            "country": country,
            "region": region
        },
        "results": results
    })