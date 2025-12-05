"""
WSGI config for resturant_site project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os
from django.core.wsgi import get_wsgi_application

# If running on Railway, load deployment settings
# Railway always sets the variable "RAILWAY_ENVIRONMENT"
if "RAILWAY_ENVIRONMENT" in os.environ:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "resturant_site.deployment_settings")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "resturant_site.settings")

application = get_wsgi_application()
