import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from .models import Proxy
import time
import re
import json

try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = None

ua = UserAgent()

def get_html(url, impersonate="chrome110"):
    """
    Robust HTML fetcher using curl_cffi (with masquerade) or requests (fallback)
    """
    headers = {'User-Agent': ua.random}
    try:
        if cffi_requests:
            # Use curl_cffi to bypass Cloudflare/WAF
            resp = cffi_requests.get(url, headers=headers, impersonate=impersonate, timeout=20)
            return resp.text, resp.status_code
    except Exception as e:
        pass
    
    # Fallback
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        # Handle encoding for some chinese sites
        if 'gbk' in resp.headers.get('content-type', '').lower() or 'gb2312' in resp.headers.get('content-type', '').lower():
            resp.encoding = 'gbk'
        return resp.text, resp.status_code
    except Exception as e:
        return None, 0

def save_proxy(ip, port, protocol, country, source, anonymity='unknown'):
    try:
        # Normalize protocol
        protocol = protocol.lower().strip()
        if 'socks5' in protocol: protocol = 'socks5'
        elif 'socks4' in protocol: protocol = 'socks4'
        else: protocol = 'http'
        
        # Validation
        if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip): return False
        
        # Deduplication
        Proxy.objects.get_or_create(
            ip=ip,
            port=int(port),
            protocol=protocol,
            defaults={
                'country': country, 
                'source': source,
                'anonymity': anonymity,
                'is_active': True
            }
        )
        return True
    except: return False

# --- Github / Text Sources ---

def fetch_fate0():
    # https://github.com/fate0/proxylist
    print("Fetching Fate0...")
    url = "https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list"
    text, _ = get_html(url)
    if not text: return 0
    count = 0
    for line in text.splitlines():
        try:
            data = json.loads(line)
            if save_proxy(data.get('host'), data.get('port'), data.get('type'), data.get('country'), 'fate0', data.get('anonymity', 'unknown')):
                count += 1
        except: pass
    return count

def fetch_thespeedx():
    # https://github.com/TheSpeedX/PROXY-LIST
    print("Fetching TheSpeedX...")
    urls = [
        ("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt", "http"),
        ("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt", "socks5"),
        ("https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt", "socks4")
    ]
    count = 0
    for url, proto in urls:
        text, _ = get_html(url)
        if not text: continue
        for line in text.splitlines():
            try:
                if ":" in line:
                    ip, port = line.strip().split(":")
                    if save_proxy(ip, port, proto, 'Unknown', 'TheSpeedX'):
                        count += 1
            except: pass
    return count

def fetch_jiangxianli():
    # https://github.com/jiangxianli/ProxyIpLib
    print("Fetching Jiangxianli...")
    url = "https://raw.githubusercontent.com/jiangxianli/ProxyIpLib/master/ip.txt"
    text, _ = get_html(url)
    if not text: return 0
    count = 0
    for line in text.splitlines():
        try:
            if ":" in line:
                ip, port = line.strip().split(":")
                # Determine protocol/country is hard, assume http/CN mostly
                if save_proxy(ip, port, 'http', 'Unknown', 'jiangxianli'):
                    count += 1
        except: pass
    return count

# --- Web / HTML Sources ---

def fetch_kuaidaili():
    # https://www.kuaidaili.com/free/inha/
    print("Fetching Kuaidaili...")
    count = 0
    for page in range(1, 4): # Fetch first 3 pages
        url = f"https://www.kuaidaili.com/free/inha/{page}/"
        html, code = get_html(url)
        if not html: continue
        
        soup = BeautifulSoup(html, 'html.parser')
        # Structure: <tr><td data-title="IP">...</td>...</tr>
        for row in soup.select('tbody tr'):
            try:
                cols = row.find_all('td')
                if len(cols) < 4: continue
                ip = cols[0].get_text(strip=True)
                port = cols[1].get_text(strip=True)
                anonymity = 'elite' if '高匿' in cols[2].get_text() else 'anonymous'
                proto = cols[3].get_text(strip=True)
                if save_proxy(ip, port, proto, 'CN', 'kuaidaili', anonymity):
                    count += 1
            except: pass
        time.sleep(1)
    return count

def fetch_89ip():
    # http://www.89ip.cn/
    print("Fetching 89ip...")
    url = "http://www.89ip.cn/tqdl.html?api=1&num=100&port=&address=&isp="
    html, _ = get_html(url)
    if not html: return 0
    count = 0
    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):(\d+)')
    matches = pattern.findall(html)
    for ip, port in matches:
        if save_proxy(ip, port, 'http', 'CN', '89ip'):
            count += 1
    return count

def fetch_ip3366():
    # http://www.ip3366.net/free/?stype=1
    print("Fetching IP3366...")
    count = 0
    for page in range(1, 3):
        url = f"http://www.ip3366.net/free/?stype=1&page={page}"
        html, _ = get_html(url)
        if not html: continue
        # Simple regex often works better for chinese sites with weird encoding
        matches = re.findall(r'<td>(\d+\.\d+\.\d+\.\d+)</td>\s*<td>(\d+)</td>.*?<td>(HTTP|HTTPS|SOCKS)</td>', html, re.S)
        for ip, port, proto in matches:
            if save_proxy(ip, port, proto, 'CN', 'ip3366', 'elite'):
                count += 1
        time.sleep(1)
    return count

def fetch_kxdaili():
    # http://www.kxdaili.com/dailiip/1/1.html
    print("Fetching Kxdaili...")
    count = 0
    for page in range(1, 3):
        url = f"http://www.kxdaili.com/dailiip/1/{page}.html"
        html, _ = get_html(url)
        if not html: continue
        soup = BeautifulSoup(html, 'html.parser')
        for row in soup.select('table tbody tr'):
            try:
                cols = row.find_all('td')
                if len(cols) < 4: continue
                ip = cols[0].get_text(strip=True)
                port = cols[1].get_text(strip=True)
                # 3rd col might be anonymity or protocol
                if save_proxy(ip, port, 'http', 'CN', 'kxdaili'):
                    count += 1
            except: pass
        time.sleep(1)
    return count

def fetch_free_proxy_list():
    # https://free-proxy-list.net/ (Also us-proxy.org, uk-proxy.org etc share same structure)
    print("Fetching Free-Proxy-List.net...")
    url = "https://free-proxy-list.net/"
    html, _ = get_html(url)
    if not html: return 0
    
    # Raw HTML parsing for reliable extraction (usually in a textarea or table)
    # They have a textarea with raw list usually
    matches = re.findall(r'(\d+\.\d+\.\d+\.\d+):(\d+)', html)
    count = 0
    for ip, port in matches:
        if save_proxy(ip, port, 'http', 'Unknown', 'free-proxy-list'):
            count += 1
    return count

def fetch_geonode():
    # https://geonode.com/free-proxy-list
    # This acts as an API usually
    print("Fetching Geonode...")
    url = "https://proxylist.geonode.com/api/proxy-list?limit=100&page=1&sort_by=lastChecked&sort_type=desc"
    text, _ = get_html(url)
    if not text: return 0
    try:
        data = json.loads(text)
        count = 0
        for item in data.get('data', []):
            mapped_proto = item.get('protocols', ['http'])[0]
            if save_proxy(item.get('ip'), item.get('port'), mapped_proto, item.get('country'), 'geonode', item.get('anonymityLevel', 'unknown')):
                count += 1
        return count
    except: return 0

# Wrapper to call all
def fetch_all_sources():
    total = 0
    total += fetch_fate0()
    total += fetch_thespeedx()
    total += fetch_jiangxianli()
    total += fetch_kuaidaili()
    total += fetch_89ip()
    total += fetch_ip3366()
    total += fetch_kxdaili()
    total += fetch_free_proxy_list()
    total += fetch_geonode()
    return total
