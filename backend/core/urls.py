from django.urls import path
from .views import trigger_crawl, list_proxies, proxy_stats, test_target, batch_test_proxies
from .views_stream import attack_target_stream

urlpatterns = [
    path('crawl', trigger_crawl),
    path('list', list_proxies),
    path('stats', proxy_stats),
    path('test', test_target),
    path('batch-test', batch_test_proxies),
    path('attack-stream', attack_target_stream),
]
