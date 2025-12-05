from resturant_site.settings import *
from decouple import config

SECRET_KEY = config('SECRET_KEY')

ALLOWED_HOSTS = ["localhost", "127.0.0.1","*"]