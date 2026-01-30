"""
Django settings for ecommerceApiProject project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv



# BASE DIR & .env (ROOT ONLY)


BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(BASE_DIR / ".env")



# SECURITY

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-default-key")

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = ["*"]



# CSRF & SESSION TRUSTED ORIGINS

CSRF_TRUSTED_ORIGINS = [
    "https://ytecommerceapi2025-production.up.railway.app",
    "https://villageless-phonotypical-tori.ngrok-free.dev",
    "https://*.ngrok-free.dev",
]

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

CSRF_COOKIE_SAMESITE = "None"
SESSION_COOKIE_SAMESITE = "None"



# INSTALLED APPS

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "corsheaders",

    # Ensure signals load
    "apiApp.apps.ApiappConfig",
]



# MIDDLEWARE

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]



# CORS

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "https://next-shop-self.vercel.app",
    "https://villageless-phonotypical-tori.ngrok-free.dev",
]



# URLS / WSGI

ROOT_URLCONF = "ecommerceApiProject.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ecommerceApiProject.wsgi.application"



# DATABASE 

DB = os.getenv("DB")

if not DB:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "railway",
            "USER": "postgres",
            "PASSWORD": os.getenv("PG_PASSWORD"),
            "HOST": os.getenv("PG_HOST"),
            "PORT": os.getenv("PG_PORT"),
        }
    }




# PASSWORD VALIDATORS

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]



# INTERNATIONALIZATION

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True



# STATIC & MEDIA

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR/"staticfiles"
STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"



# DEFAULTS

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "apiApp.CustomUser"



# STRIPE (TEST MODE SAFE)

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# HARD FAIL if missing
if not STRIPE_SECRET_KEY:
    raise RuntimeError("❌ STRIPE_SECRET_KEY not found in .env")

# Debug check
print("Stripe Secret Key Loaded:", STRIPE_SECRET_KEY[:10], "...")
