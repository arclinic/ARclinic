from .base import *

INSTALLED_APPS += ["django_extensions"]

if DEBUG:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]
    MIDDLEWARE = [
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    ] + MIDDLEWARE
    INTERNAL_IPS = ["127.0.0.1", "localhost"]
