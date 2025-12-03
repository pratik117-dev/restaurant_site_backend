"""
Production settings for Render deployment.
"""

import os
from .settings import *  # Import everything from base settings
import dj_database_url

# -------------------
# SECURITY
# -------------------
DEBUG = True
SECRET_KEY = os.environ.get("SECRET_KEY")
RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if not RENDER_HOSTNAME:
    raise Exception("RENDER_EXTERNAL_HOSTNAME not set in environment variables")

ALLOWED_HOSTS = [RENDER_HOSTNAME]
CSRF_TRUSTED_ORIGINS = [f'https://{RENDER_HOSTNAME}']

# -------------------
# DATABASE (PostgreSQL)
# -------------------
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("DATABASE_URL not set in environment variables")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# -------------------
# STATIC & MEDIA
# -------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# -------------------
# WHITENOISE (serving static files)
# -------------------
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# -------------------
# CORS
# -------------------
CORS_ALLOWED_ORIGINS = [
    'https://restaurant-site-backend-frontend.onrender.com',  # replace with your frontend URL
]

# -------------------
# REST FRAMEWORK (keep base settings)
# -------------------
# Already imported from base settings, no need to redefine

# -------------------
# CUSTOM USER MODEL
# -------------------
AUTH_USER_MODEL = 'orders.CustomUser'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
