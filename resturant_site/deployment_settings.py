"""
Production settings for Railway deployment.
"""

import os
from .settings import *  # import base settings
import dj_database_url

# -------------------
# SECURITY
# -------------------
DEBUG = True

SECRET_KEY = os.environ.get("SECRET_KEY", "")

# Railway gives a wildcard domain like *.up.railway.app
ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    "https://*.railway.app"
]

# -------------------
# DATABASE (PostgreSQL)
# -------------------
# Railway provides individual environment variables
# Use them instead of DATABASE_URL

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("PGHOST"),
        "PORT": os.getenv("PGPORT", "5432"),
    }
}


# -------------------
# STATIC & MEDIA
# -------------------
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# -------------------
# WHITENOISE (serving static files)
# -------------------
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# -------------------
# CORS
# -------------------
CORS_ALLOWED_ORIGINS = [
    # replace with your actual frontend domain (Netlify or Railway)
    "https://your-frontend-domain.com",
]

# -------------------
# CUSTOM USER MODEL
# -------------------
AUTH_USER_MODEL = "orders.CustomUser"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
