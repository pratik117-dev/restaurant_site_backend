"""
Production settings for Render deployment.
"""

import os
import dj_database_url
from .settings import BASE_DIR, INSTALLED_APPS, MIDDLEWARE, TEMPLATES

# -------------------
# SECURITY
# -------------------
DEBUG = False
SECRET_KEY = os.environ.get("SECRET_KEY")
ALLOWED_HOSTS = [os.environ.get("RENDER_EXTERNAL_HOSTNAME")]
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ.get("RENDER_EXTERNAL_HOSTNAME")]

# -------------------
# APPS & MIDDLEWARE
# -------------------
INSTALLED_APPS = INSTALLED_APPS  # Import from base settings
MIDDLEWARE = MIDDLEWARE  # Import from base settings
TEMPLATES = TEMPLATES 

# -------------------
# CORS
# -------------------
CORS_ALLOWED_ORIGINS = [
    'https://restaurant-site-backend-frontend.onrender.com',
]

# -------------------
# STATIC & MEDIA
# -------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Whitenoise storage for static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default media storage (Cloudinary can be used)
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# -------------------
# DATABASE (PostgreSQL)
# -------------------
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise Exception("DATABASE_URL not set in Render environment")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# -------------------
# CUSTOM USER
# -------------------
AUTH_USER_MODEL = 'orders.CustomUser'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
