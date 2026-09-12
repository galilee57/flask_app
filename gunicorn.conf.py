"""Portable HTTP contract; secrets are injected only at runtime."""
import os

bind = f"0.0.0.0:{int(os.getenv('PORT', '8080'))}"
workers = int(os.getenv("WEB_CONCURRENCY", "2"))
worker_class = "gthread"
threads = int(os.getenv("GUNICORN_THREADS", "4"))
timeout = 60
graceful_timeout = 30
accesslog = "-"
errorlog = "-"
# Trust the forwarded scheme only when the hosting proxy is known.
forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "127.0.0.1,::1")
