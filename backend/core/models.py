from django.db import models

class Proxy(models.Model):
    PROTOCOLS = (
        ('http', 'HTTP'),
        ('socks4', 'SOCKS4'),
        ('socks5', 'SOCKS5'),
    )

    ip = models.GenericIPAddressField()
    port = models.IntegerField()
    protocol = models.CharField(max_length=10, choices=PROTOCOLS, default='http')
    anonymity = models.CharField(max_length=20, default='unknown') # elite, anonymous, transparent
    country = models.CharField(max_length=100, default='Unknown')
    score = models.IntegerField(default=10, help_text="Score from 0 to 100")
    speed = models.IntegerField(default=0, help_text="Response time in ms")
    last_checked = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    source = models.CharField(max_length=50, default='proxifly')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('ip', 'port', 'protocol')
        ordering = ['-score', '-speed']

    def __str__(self):
        return f"{self.protocol}://{self.ip}:{self.port} (Score: {self.score})"
